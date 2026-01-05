"""
Video Processor Service
Handles real-time video processing with streamlit-webrtc.
Separates processing logic from UI concerns.
"""

import queue
import logging
from typing import List, Optional, Dict, Any
import numpy as np
from datetime import datetime

try:
    from streamlit_webrtc import VideoProcessorBase
    import av
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    VideoProcessorBase = object  # Fallback

from services.live_vision import get_live_vision_service
from services.barcode_scanner import get_barcode_scanner
from models.schemas import DetectionResult


class BioGuardVideoProcessor(VideoProcessorBase):
    """
    Video processor for BioGuard AR camera.
    Processes frames independently and pushes results to queues.
    """
    
    def __init__(self):
        """Initialize video processor with result queues."""
        self.logger = logging.getLogger(__name__)
        self.vision_service = get_live_vision_service()
        self.barcode_scanner = get_barcode_scanner()
        
        # Result queues (thread-safe communication with UI)
        self.detection_queue = queue.Queue(maxsize=10)
        self.barcode_queue = queue.Queue(maxsize=5)
        self.frame_queue = queue.Queue(maxsize=2)  # For capture
        
        # Processing state
        self.frame_count = 0
        self.barcode_scan_interval = 30  # Scan every 30 frames
        self.is_scanning = True
        self.last_barcode = None
        
        # Cache for latest data
        self.current_detections: List[DetectionResult] = []
        self.annotated_frame: Optional[np.ndarray] = None
        
        self.logger.info("✅ BioGuardVideoProcessor initialized")
    
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """
        Process incoming video frame.
        This is called for every frame from the camera.
        
        Args:
            frame: Input video frame from WebRTC
            
        Returns:
            Processed frame with AR overlays
        """
        try:
            # Convert to numpy array
            img = frame.to_ndarray(format="bgr24")
            
            # Process frame with vision service
            annotated_img, detections = self.vision_service.process_frame(img)
            
            # Update cache
            self.current_detections = detections
            self.annotated_frame = annotated_img
            self.frame_count += 1
            
            # Push detections to queue (non-blocking)
            if detections:
                try:
                    self.detection_queue.put_nowait({
                        'detections': detections,
                        'frame_id': self.frame_count,
                        'timestamp': datetime.now().isoformat(),
                    })
                except queue.Full:
                    pass  # Skip if queue is full
            
            # Barcode scanning at intervals
            if self.is_scanning and self.frame_count % self.barcode_scan_interval == 0:
                self._scan_barcode(img)
            
            # Convert back to VideoFrame
            return av.VideoFrame.from_ndarray(annotated_img, format="bgr24")
            
        except Exception as e:
            self.logger.error(f"❌ Frame processing error: {e}")
            # Return original frame on error
            return frame
    
    def _scan_barcode(self, frame: np.ndarray) -> None:
        """Scan frame for barcodes."""
        try:
            barcode_result = self.barcode_scanner.scan_frame(frame)
            
            if barcode_result and barcode_result != self.last_barcode:
                self.last_barcode = barcode_result
                
                # Push to barcode queue
                try:
                    self.barcode_queue.put_nowait({
                        'barcode': barcode_result,
                        'timestamp': datetime.now().isoformat(),
                    })
                    self.logger.info(f"📊 Barcode detected: {barcode_result}")
                except queue.Full:
                    pass
                    
        except Exception as e:
            self.logger.error(f"❌ Barcode scan error: {e}")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture current high-quality frame for analysis.
        
        Returns:
            Captured frame or None if not available
        """
        if self.annotated_frame is not None and self.current_detections:
            # Get bounding box of first detection
            bbox = self.current_detections[0].bounding_box if self.current_detections else None
            
            # Capture high-quality region
            captured = self.vision_service.capture_high_quality_frame(
                self.annotated_frame,
                bbox
            )
            
            # Push to frame queue
            try:
                self.frame_queue.put_nowait({
                    'frame': captured,
                    'detections': self.current_detections,
                    'timestamp': datetime.now().isoformat(),
                })
                self.logger.info("📸 Frame captured for analysis")
                return captured
            except queue.Full:
                self.logger.warning("⚠️ Frame queue full")
                return captured
                
        return None
    
    def get_detection_result(self, timeout: float = 0.1) -> Optional[Dict[str, Any]]:
        """
        Get latest detection result from queue.
        
        Args:
            timeout: How long to wait for result (seconds)
            
        Returns:
            Detection result dict or None
        """
        try:
            return self.detection_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_barcode_result(self, timeout: float = 0.1) -> Optional[Dict[str, Any]]:
        """
        Get latest barcode result from queue.
        
        Args:
            timeout: How long to wait for result (seconds)
            
        Returns:
            Barcode result dict or None
        """
        try:
            return self.barcode_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_captured_frame(self, timeout: float = 0.1) -> Optional[Dict[str, Any]]:
        """
        Get latest captured frame from queue.
        
        Args:
            timeout: How long to wait for result (seconds)
            
        Returns:
            Captured frame dict or None
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def toggle_scanning(self, enabled: bool) -> None:
        """Enable or disable barcode scanning."""
        self.is_scanning = enabled
        self.logger.info(f"🔄 Barcode scanning: {'enabled' if enabled else 'disabled'}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        return {
            'frames_processed': self.frame_count,
            'active_detections': len(self.current_detections),
            'queue_sizes': {
                'detections': self.detection_queue.qsize(),
                'barcodes': self.barcode_queue.qsize(),
                'frames': self.frame_queue.qsize(),
            },
            'scanning_enabled': self.is_scanning,
            'last_barcode': self.last_barcode,
        }
    
    def clear_queues(self) -> None:
        """Clear all result queues."""
        while not self.detection_queue.empty():
            try:
                self.detection_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.barcode_queue.empty():
            try:
                self.barcode_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
        
        self.logger.info("🧹 Queues cleared")


def get_video_processor_factory():
    """
    Factory function for creating video processor instances.
    Used by streamlit-webrtc.
    """
    return BioGuardVideoProcessor
