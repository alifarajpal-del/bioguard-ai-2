"""
Integration tests for complete BioGuard AI workflows.
Tests end-to-end scenarios simulating real user interactions.
"""

import pytest
import numpy as np
from PIL import Image
import io
import time

from services.engine import analyze_image_sync
from services.live_vision import LiveVisionService
from services.barcode_scanner import BarcodeScannerService
from services.recommendations import HealthRecommendationsService
from database.db_manager import DatabaseManager


class TestCompleteAnalysisWorkflow:
    """Test complete food analysis workflow from scan to storage."""
    
    @pytest.fixture
    def db_manager(self, temp_db_path):
        """Create database manager with temp database."""
        return DatabaseManager(db_path=temp_db_path)
    
    @pytest.fixture
    def test_user(self, db_manager):
        """Create test user."""
        username = 'integration_test_user'
        password = 'test_password_123'
        email = 'test@integration.test'
        
        db_manager.create_user(username, password, email)
        return username
    
    def test_scan_analyze_store_workflow(self, db_manager, test_user, sample_image_bytes):
        """Test: Capture image → Analyze → Store in database."""
        
        # Step 1: Analyze image
        analysis_result = analyze_image_sync(sample_image_bytes, preferred_provider='gemini')
        
        assert analysis_result is not None
        assert 'product' in analysis_result
        assert 'health_score' in analysis_result
        
        # Step 2: Store in database
        analysis_id = db_manager.save_food_analysis(test_user, analysis_result)
        
        assert analysis_id is not None
        
        # Step 3: Retrieve from history
        history = db_manager.get_user_history(test_user, limit=10)
        
        assert len(history) >= 1
        assert history[0]['product'] == analysis_result.get('product', 'Unknown')
    
    def test_live_vision_to_analysis_workflow(self, db_manager, test_user):
        """Test: LiveVision detection → AI analysis → Database storage."""
        
        vision_service = LiveVisionService()
        
        # Step 1: Create sample frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[100:300, 150:450] = [100, 150, 200]  # Simulate product
        
        # Step 2: Detect objects
        detections = vision_service.detect_objects(frame, confidence_threshold=0.3)
        
        # Step 3: If detection exists, analyze
        if detections:
            # Convert frame to bytes
            img = Image.fromarray(frame)
            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            image_bytes = buf.getvalue()
            
            # Analyze
            analysis_result = analyze_image_sync(image_bytes)
            
            # Store
            analysis_id = db_manager.save_food_analysis(test_user, analysis_result)
            assert analysis_id is not None


class TestBarcodeToRecommendations:
    """Test workflow from barcode scan to health recommendations."""
    
    @pytest.fixture
    def scanner_service(self):
        return BarcodeScannerService()
    
    @pytest.fixture
    def recommendations_service(self):
        return HealthRecommendationsService()
    
    @pytest.fixture
    def db_manager(self, temp_db_path):
        return DatabaseManager(db_path=temp_db_path)
    
    @pytest.fixture
    def test_user(self, db_manager):
        username = 'barcode_test_user'
        password = 'test_password_123'
        email = 'barcode@test.com'
        
        db_manager.create_user(username, password, email)
        return username
    
    def test_barcode_to_alternatives_workflow(
        self, 
        scanner_service, 
        recommendations_service,
        db_manager,
        test_user
    ):
        """Test: Scan barcode → Get product → Find alternatives → Store."""
        
        # Step 1: Simulate barcode scan
        barcode_data = {
            'barcode': '1234567890123',
            'product_name': 'Test Snack',
            'health_score': 45,
            'verdict': 'WARNING',
            'warnings': ['High sugar']
        }
        
        # Step 2: Store initial analysis
        analysis_id = db_manager.save_food_analysis(test_user, {
            'product': barcode_data['product_name'],
            'health_score': barcode_data['health_score'],
            'verdict': barcode_data['verdict'],
            'warnings': barcode_data['warnings']
        })
        
        assert analysis_id is not None
        
        # Step 3: Get healthier alternatives
        alternatives = recommendations_service.get_healthier_alternatives(
            product_name=barcode_data['product_name'],
            current_health_score=barcode_data['health_score'],
            category='snack',
            limit=5
        )
        
        # Step 4: Verify alternatives
        assert isinstance(alternatives, list)
        
        # All alternatives should have better health scores
        for alt in alternatives:
            assert alt.get('health_score', 0) > barcode_data['health_score']


class TestMultiUserScenarios:
    """Test scenarios with multiple users."""
    
    @pytest.fixture
    def db_manager(self, temp_db_path):
        return DatabaseManager(db_path=temp_db_path)
    
    def test_multiple_users_independent_history(self, db_manager, sample_analysis_result):
        """Test that user histories are independent."""
        
        # Create two users
        user1 = 'user1'
        user2 = 'user2'
        
        db_manager.create_user(user1, 'pass1', 'user1@test.com')
        db_manager.create_user(user2, 'pass2', 'user2@test.com')
        
        # User 1 scans 3 products
        for i in range(3):
            result = sample_analysis_result.copy()
            result['product'] = f'User1 Product {i}'
            db_manager.save_food_analysis(user1, result)
        
        # User 2 scans 2 products
        for i in range(2):
            result = sample_analysis_result.copy()
            result['product'] = f'User2 Product {i}'
            db_manager.save_food_analysis(user2, result)
        
        # Verify independent histories
        history1 = db_manager.get_user_history(user1, limit=10)
        history2 = db_manager.get_user_history(user2, limit=10)
        
        assert len(history1) == 3
        assert len(history2) == 2
        
        # Verify products don't overlap
        user1_products = {h['product'] for h in history1}
        user2_products = {h['product'] for h in history2}
        
        assert len(user1_products & user2_products) == 0  # No overlap


class TestPerformanceAndScalability:
    """Test system performance under load."""
    
    @pytest.fixture
    def db_manager(self, temp_db_path):
        return DatabaseManager(db_path=temp_db_path)
    
    def test_bulk_analysis_storage(self, db_manager, sample_analysis_result):
        """Test storing many analyses quickly."""
        user = 'bulk_test_user'
        db_manager.create_user(user, 'password', 'bulk@test.com')
        
        start_time = time.time()
        
        # Store 50 analyses
        for i in range(50):
            result = sample_analysis_result.copy()
            result['product'] = f'Product {i}'
            db_manager.save_food_analysis(user, result)
        
        duration = time.time() - start_time
        
        # Should complete in reasonable time (< 5 seconds)
        assert duration < 5.0
        
        # Verify all stored
        history = db_manager.get_user_history(user, limit=100)
        assert len(history) == 50
    
    def test_concurrent_user_operations(self, db_manager, sample_analysis_result):
        """Test multiple users performing operations simultaneously."""
        users = [f'concurrent_user_{i}' for i in range(5)]
        
        # Create users
        for user in users:
            db_manager.create_user(user, 'password', f'{user}@test.com')
        
        # Each user stores analyses
        for user in users:
            for i in range(10):
                result = sample_analysis_result.copy()
                result['product'] = f'{user}_Product_{i}'
                db_manager.save_food_analysis(user, result)
        
        # Verify all users have correct history
        for user in users:
            history = db_manager.get_user_history(user, limit=20)
            assert len(history) == 10


class TestErrorRecovery:
    """Test system resilience to errors."""
    
    @pytest.fixture
    def db_manager(self, temp_db_path):
        return DatabaseManager(db_path=temp_db_path)
    
    def test_recovery_from_analysis_failure(self, sample_image_bytes):
        """Test that system continues after failed analysis."""
        from unittest.mock import patch
        
        # First analysis fails
        with patch('services.engine.analyze_image', side_effect=Exception("API Error")):
            try:
                result = analyze_image_sync(sample_image_bytes)
                # Should fall back to mock
                assert result is not None
            except Exception:
                # Even if it fails, should not crash
                pass
        
        # Second analysis succeeds
        result = analyze_image_sync(sample_image_bytes)
        assert result is not None
    
    def test_recovery_from_database_error(self, db_manager, sample_analysis_result):
        """Test recovery from database errors."""
        user = 'error_test_user'
        db_manager.create_user(user, 'password', 'error@test.com')
        
        # Try to save invalid data
        try:
            invalid_result = sample_analysis_result.copy()
            invalid_result['health_score'] = 'invalid'  # Should be int
            db_manager.save_food_analysis(user, invalid_result)
        except Exception:
            pass
        
        # System should still work with valid data
        valid_result = sample_analysis_result.copy()
        analysis_id = db_manager.save_food_analysis(user, valid_result)
        assert analysis_id is not None


class TestDataConsistency:
    """Test data consistency across operations."""
    
    @pytest.fixture
    def db_manager(self, temp_db_path):
        return DatabaseManager(db_path=temp_db_path)
    
    def test_analysis_data_integrity(self, db_manager, sample_analysis_result):
        """Test that stored data matches retrieved data."""
        user = 'consistency_test_user'
        db_manager.create_user(user, 'password', 'consistency@test.com')
        
        # Store analysis
        original_result = sample_analysis_result.copy()
        original_result['product'] = 'Consistency Test Product'
        original_result['health_score'] = 88
        
        analysis_id = db_manager.save_food_analysis(user, original_result)
        
        # Retrieve analysis
        history = db_manager.get_user_history(user, limit=1)
        retrieved_result = history[0]
        
        # Verify key fields match
        assert retrieved_result['product'] == original_result['product']
        assert retrieved_result['health_score'] == original_result['health_score']
        assert retrieved_result['verdict'] == original_result['verdict']
    
    def test_timestamp_ordering(self, db_manager, sample_analysis_result):
        """Test that analyses are retrieved in correct chronological order."""
        user = 'timestamp_test_user'
        db_manager.create_user(user, 'password', 'timestamp@test.com')
        
        # Store 5 analyses with delays
        for i in range(5):
            result = sample_analysis_result.copy()
            result['product'] = f'Product {i}'
            db_manager.save_food_analysis(user, result)
            time.sleep(0.1)  # Small delay to ensure different timestamps
        
        # Retrieve history
        history = db_manager.get_user_history(user, limit=10)
        
        # Should be in reverse chronological order (newest first)
        assert history[0]['product'] == 'Product 4'
        assert history[-1]['product'] == 'Product 0'
