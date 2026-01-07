"""
Live Vision Service.
Real-time camera feed processing with AR overlays using streamlit-webrtc.
Includes fast-pass detection with YOLO and AR bubble rendering.
"""

try:
    import cv2
except ImportError:
    print("⚠️ OpenCV not available. Please install: pip install opencv-python-headless")
    cv2 = None
import numpy as np
from typing import Tuple, Optional, List, Dict, Any
import asyncio
import logging
from datetime import datetime
from models.schemas import DetectionResult
from app_config.settings import (
    YOLO_MODEL, CONFIDENCE_THRESHOLD, DETECTION_FPS,
    FRAME_RESIZE_WIDTH, FRAME_RESIZE_HEIGHT,
    AR_BUBBLE_COLOR, AR_BUBBLE_THICKNESS, AR_TEXT_SCALE,
)

# Try importing YOLO, fallback to mock if not available
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("⚠️ YOLOv8 not available. Using mock detection.")


class LiveVisionService:
    """Real-time vision processing with AR overlays."""
    
    def __init__(self):
        """Initialize vision service."""
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.frame_count = 0
        self.detection_interval = int(30 / DETECTION_FPS)  # Every Nth frame
        self.detections_cache = []
        self.last_detection_time = None
        
        if YOLO_AVAILABLE:
            self._init_yolo()
        else:
            self.logger.info("🚀 Vision service initialized in mock mode")
    
    def _init_yolo(self):
        """Initialize YOLO model for food object detection."""
        try:
            self.model = YOLO(YOLO_MODEL)
            self.logger.info(f"✅ YOLO model loaded: {YOLO_MODEL}")
        except Exception as e:
            self.logger.error(f"❌ Failed to load YOLO: {e}")
            self.model = None
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[DetectionResult]]:
        """
        Process a single video frame.
        Returns: (annotated_frame, detections)
        """
        self.frame_count += 1
        detections = []
        
        # Resize frame for faster processing
        resized_frame = cv2.resize(
            frame,
            (FRAME_RESIZE_WIDTH, FRAME_RESIZE_HEIGHT)
        )
        
        # Fast-pass detection at set interval
        if self.frame_count % self.detection_interval == 0:
            detections = self._detect_objects(resized_frame)
            self.last_detection_time = datetime.now()
        else:
            # Use cached detections from last frame
            detections = self.detections_cache
        
        # Draw AR overlays
        annotated_frame = self._draw_ar_overlays(resized_frame, detections)
        
        # Cache detections
        self.detections_cache = detections
        
        return annotated_frame, detections
    
    def _detect_objects(self, frame: np.ndarray) -> List[DetectionResult]:
        """Run YOLO detection or mock detection."""
        if not self.model and YOLO_AVAILABLE:
            return []
        
        if self.model:
            return self._yolo_detect(frame)
        else:
            return self._mock_detect(frame)
    
    def _yolo_detect(self, frame: np.ndarray) -> List[DetectionResult]:
        """Run actual YOLO detection."""
        try:
            results = self.model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
            detections = []
            
            for result in results:
                for box in result.boxes:
                    conf = float(box.conf)
                    if conf >= CONFIDENCE_THRESHOLD:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Map COCO classes to food categories (simplified)
                        class_id = int(box.cls)
                        object_type = self._map_yolo_class(class_id)
                        
                        # Create micro-summary
                        micro_summary = f"{object_type} - {conf:.0%}"
                        
                        detection = DetectionResult(
                            object_type=object_type,
                            confidence=conf,
                            bounding_box={'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2},
                            micro_summary=micro_summary,
                        )
                        detections.append(detection)
            
            return detections
        except Exception as e:
            self.logger.error(f"❌ YOLO detection error: {e}")
            return []
    
    def _mock_detect(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Mock detection for testing.
        Detects bright regions as potential food objects.
        """
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create binary mask for potential food colors (warm tones)
            lower_warm = np.array([0, 50, 50])
            upper_warm = np.array([25, 255, 255])
            mask = cv2.inRange(hsv, lower_warm, upper_warm)
            
            # Find contours
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            detections = []
            for contour in contours[:5]:  # Limit to top 5
                area = cv2.contourArea(contour)
                if area > 500:  # Minimum area threshold
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    detection = DetectionResult(
                        object_type="Food Object",
                        confidence=0.85,
                        bounding_box={'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h},
                        micro_summary=f"Food Object - 85%",
                    )
                    detections.append(detection)
            
            return detections
        except Exception as e:
            self.logger.error(f"❌ Mock detection error: {e}")
            return []
    
    def _map_yolo_class(self, class_id: int) -> str:
        """Map YOLO class ID to food category."""
        # COCO classes that might be food
        food_classes = {
            54: "apple", 55: "orange", 56: "broccoli", 57: "carrot",
            58: "hot dog", 59: "pizza", 60: "donut", 61: "cake",
            47: "banana", 51: "bowl", 52: "wine glass", 53: "cup",
        }
        return food_classes.get(class_id, "Object")
    
    def _draw_ar_overlays(
        self,
        frame: np.ndarray,
        detections: List[DetectionResult]
    ) -> np.ndarray:
        """Draw AR overlays on frame."""
        annotated = frame.copy()
        
        for detection in detections:
            bbox = detection.bounding_box
            x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
            
            # Draw bounding box
            cv2.rectangle(
                annotated,
                (x1, y1), (x2, y2),
                AR_BUBBLE_COLOR,
                AR_BUBBLE_THICKNESS
            )
            
            # Draw floating bubble with micro-summary
            bubble_y = max(20, y1 - 10)
            cv2.putText(
                annotated,
                detection.micro_summary,
                (x1, bubble_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                AR_TEXT_SCALE,
                AR_BUBBLE_COLOR,

            )
            
            # Draw circle indicator for clickable area
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            radius = 5
            cv2.circle(annotated, (center_x, center_y), radius, AR_BUBBLE_COLOR, -1)
        
        # Add FPS counter
        if self.last_detection_time:
            fps_text = f"Detections: {len(detections)} | FPS: {DETECTION_FPS}"
            cv2.putText(
                annotated,
                fps_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )
        
        return annotated
    
    def capture_high_quality_frame(
        self,
        frame: np.ndarray,
        detection_bbox: Optional[Dict[str, int]] = None
    ) -> np.ndarray:
        """
        Capture high-quality frame for deep analysis.
        Optionally crops to detected region.
        """
        if detection_bbox:
            x1, y1, x2, y2 = (
                detection_bbox['x1'], detection_bbox['y1'],
                detection_bbox['x2'], detection_bbox['y2']
            )
            # Add padding
            padding = 20
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(frame.shape[1], x2 + padding)
            y2 = min(frame.shape[0], y2 + padding)
            
            return frame[y1:y2, x1:x2]
        
        return frame
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            'frames_processed': self.frame_count,
            'model_loaded': self.model is not None if YOLO_AVAILABLE else False,
            'detection_fps': DETECTION_FPS,
            'last_detection': self.last_detection_time.isoformat() if self.last_detection_time else None,
            'cached_detections': len(self.detections_cache),
        }


# Global instance
live_vision = None


def get_live_vision_service() -> LiveVisionService:
    """Get or create global live vision service instance."""
    global live_vision
    if live_vision is None:
        live_vision = LiveVisionService()
    return live_vision
