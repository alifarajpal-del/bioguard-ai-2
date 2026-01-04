"""
Tests for LiveVision Service (services/live_vision.py)
"""

import pytest
import numpy as np
from PIL import Image
import io

from services.live_vision import LiveVisionService


class TestLiveVisionService:
    """Test LiveVision real-time detection service."""
    
    @pytest.fixture
    def vision_service(self):
        """Create LiveVision service instance."""
        return LiveVisionService()
    
    @pytest.fixture
    def sample_frame(self):
        """Create sample video frame (numpy array)."""
        # Create 640x480 RGB frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some content (red rectangle)
        frame[100:200, 100:200] = [255, 0, 0]
        return frame
    
    def test_service_initialization(self, vision_service):
        """Test that service initializes correctly."""
        assert vision_service is not None
        assert hasattr(vision_service, 'yolo_model')
    
    def test_detect_objects_returns_list(self, vision_service, sample_frame):
        """Test that object detection returns a list."""
        detections = vision_service.detect_objects(sample_frame)
        assert isinstance(detections, list)
    
    def test_detect_objects_with_threshold(self, vision_service, sample_frame):
        """Test detection with confidence threshold."""
        detections = vision_service.detect_objects(sample_frame, confidence_threshold=0.5)
        
        # All detections should meet threshold
        for detection in detections:
            assert detection.get('confidence', 0) >= 0.5
    
    def test_draw_detections(self, vision_service, sample_frame):
        """Test drawing detection boxes on frame."""
        detections = [
            {
                'bbox': [100, 100, 200, 200],
                'class': 'bottle',
                'confidence': 0.95
            }
        ]
        
        annotated_frame = vision_service.draw_detections(sample_frame.copy(), detections)
        
        assert annotated_frame is not None
        assert annotated_frame.shape == sample_frame.shape
        # Frame should be modified (not identical)
        assert not np.array_equal(annotated_frame, sample_frame)
    
    def test_empty_frame_handling(self, vision_service):
        """Test handling of empty/invalid frames."""
        empty_frame = np.zeros((0, 0, 3), dtype=np.uint8)
        
        detections = vision_service.detect_objects(empty_frame)
        assert isinstance(detections, list)
        assert len(detections) == 0
    
    def test_frame_preprocessing(self, vision_service, sample_frame):
        """Test frame preprocessing before detection."""
        # Test with different frame sizes
        small_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        large_frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
        
        detections_small = vision_service.detect_objects(small_frame)
        detections_large = vision_service.detect_objects(large_frame)
        
        assert isinstance(detections_small, list)
        assert isinstance(detections_large, list)


class TestYOLOIntegration:
    """Test YOLO model integration."""
    
    @pytest.fixture
    def vision_service(self):
        return LiveVisionService()
    
    def test_yolo_model_loaded(self, vision_service):
        """Test that YOLO model is loaded."""
        assert vision_service.yolo_model is not None
    
    def test_yolo_prediction_format(self, vision_service, sample_frame):
        """Test that YOLO predictions return expected format."""
        detections = vision_service.detect_objects(sample_frame)
        
        for detection in detections:
            assert 'bbox' in detection
            assert 'class' in detection
            assert 'confidence' in detection
            assert len(detection['bbox']) == 4  # [x1, y1, x2, y2]


class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.fixture
    def vision_service(self):
        return LiveVisionService()
    
    def test_detection_speed(self, vision_service, sample_frame):
        """Test that detection completes in reasonable time."""
        import time
        
        start = time.time()
        vision_service.detect_objects(sample_frame)
        duration = time.time() - start
        
        # Should complete in under 1 second on most hardware
        assert duration < 1.0
    
    def test_multiple_detections(self, vision_service, sample_frame):
        """Test multiple consecutive detections."""
        for _ in range(5):
            detections = vision_service.detect_objects(sample_frame)
            assert isinstance(detections, list)


class TestIntegrationScenarios:
    """Test real-world usage scenarios."""
    
    @pytest.fixture
    def vision_service(self):
        return LiveVisionService()
    
    def test_food_product_detection_workflow(self, vision_service):
        """Test complete workflow: detect → analyze → display."""
        # Create frame with product-like shape
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add rectangular object
        frame[150:350, 200:400] = [100, 150, 200]
        
        # Step 1: Detect
        detections = vision_service.detect_objects(frame, confidence_threshold=0.3)
        
        # Step 2: Draw
        annotated = vision_service.draw_detections(frame.copy(), detections)
        
        # Step 3: Verify output
        assert annotated is not None
        assert annotated.shape == frame.shape
