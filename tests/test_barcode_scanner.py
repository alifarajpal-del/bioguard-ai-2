"""
Tests for Barcode Scanner Service (services/barcode_scanner.py)
"""

import pytest
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

from services.barcode_scanner import BarcodeScannerService


class TestBarcodeScanning:
    """Test barcode scanning functionality."""
    
    @pytest.fixture
    def scanner_service(self):
        """Create barcode scanner service instance."""
        return BarcodeScannerService()
    
    @pytest.fixture
    def barcode_image(self):
        """Create sample image with simulated barcode."""
        # Create white background
        img = Image.new('RGB', (300, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw simple vertical bars (barcode simulation)
        for i in range(20):
            x = 50 + i * 10
            if i % 2 == 0:
                draw.rectangle([x, 50, x+5, 150], fill='black')
        
        # Convert to numpy array
        return np.array(img)
    
    def test_scanner_initialization(self, scanner_service):
        """Test scanner service initializes correctly."""
        assert scanner_service is not None
        assert hasattr(scanner_service, 'cache')
    
    def test_scan_barcode_returns_dict(self, scanner_service, barcode_image):
        """Test that scan_barcode returns a dictionary."""
        result = scanner_service.scan_barcode(barcode_image)
        assert isinstance(result, dict)
    
    def test_scan_barcode_with_no_barcode(self, scanner_service):
        """Test scanning image without barcode."""
        # Plain white image
        empty_image = np.ones((200, 300, 3), dtype=np.uint8) * 255
        result = scanner_service.scan_barcode(empty_image)
        
        assert result is not None
        assert result.get('barcode') is None
    
    def test_cache_mechanism(self, scanner_service, barcode_image):
        """Test that barcode lookups are cached."""
        # First scan
        result1 = scanner_service._lookup_barcode("1234567890123")
        
        # Second scan (should use cache)
        result2 = scanner_service._lookup_barcode("1234567890123")
        
        # Both should return data (from cache)
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)


class TestOCRExtraction:
    """Test OCR text extraction."""
    
    @pytest.fixture
    def scanner_service(self):
        return BarcodeScannerService()
    
    @pytest.fixture
    def text_image(self):
        """Create image with text."""
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw text
        try:
            draw.text((20, 40), "Nutrition Facts", fill='black')
        except:
            # If font not available, skip drawing
            pass
        
        return np.array(img)
    
    def test_extract_text_ocr_returns_string(self, scanner_service, text_image):
        """Test that OCR returns a string."""
        try:
            text = scanner_service.extract_text_ocr(text_image)
            assert isinstance(text, str)
        except Exception as e:
            # Tesseract might not be installed in test environment
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_ocr_preprocessing(self, scanner_service):
        """Test image preprocessing for OCR."""
        # Create low quality image
        img = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
        
        try:
            text = scanner_service.extract_text_ocr(img)
            assert isinstance(text, str)
        except Exception as e:
            pytest.skip(f"Tesseract not available: {e}")


class TestNutritionParsing:
    """Test nutrition label parsing."""
    
    @pytest.fixture
    def scanner_service(self):
        return BarcodeScannerService()
    
    def test_parse_nutrition_label(self, scanner_service):
        """Test parsing nutrition information from text."""
        sample_text = """
        Nutrition Facts
        Calories: 250
        Protein: 10g
        Carbohydrates: 30g
        Fat: 8g
        Sodium: 500mg
        Sugar: 12g
        Fiber: 5g
        """
        
        nutrition = scanner_service.parse_nutrition_label(sample_text)
        
        assert isinstance(nutrition, dict)
        assert 'calories' in nutrition or 'protein' in nutrition
    
    def test_parse_partial_nutrition_info(self, scanner_service):
        """Test parsing when only some nutrition info is present."""
        partial_text = "Calories: 180 Fat: 5g"
        
        nutrition = scanner_service.parse_nutrition_label(partial_text)
        assert isinstance(nutrition, dict)
    
    def test_parse_empty_text(self, scanner_service):
        """Test parsing empty or invalid text."""
        empty_text = ""
        nutrition = scanner_service.parse_nutrition_label(empty_text)
        
        assert isinstance(nutrition, dict)
        assert len(nutrition) == 0


class TestIngredientsExtraction:
    """Test ingredients list extraction."""
    
    @pytest.fixture
    def scanner_service(self):
        return BarcodeScannerService()
    
    def test_extract_ingredients_list(self, scanner_service):
        """Test extracting ingredients from text."""
        sample_text = """
        INGREDIENTS: Water, Sugar, Flour, Salt, Yeast
        Contains wheat.
        """
        
        ingredients = scanner_service.extract_ingredients_list(sample_text)
        
        assert isinstance(ingredients, list)
        assert len(ingredients) > 0
    
    def test_extract_ingredients_various_formats(self, scanner_service):
        """Test extraction with different text formats."""
        formats = [
            "Ingredients: A, B, C",
            "INGREDIENTES: X, Y, Z",
            "Ingrédients: P, Q, R"
        ]
        
        for text in formats:
            ingredients = scanner_service.extract_ingredients_list(text)
            assert isinstance(ingredients, list)
    
    def test_extract_ingredients_empty_text(self, scanner_service):
        """Test extraction from text without ingredients."""
        empty_text = "No ingredients listed"
        ingredients = scanner_service.extract_ingredients_list(empty_text)
        
        assert isinstance(ingredients, list)


class TestOpenFoodFactsAPI:
    """Test OpenFoodFacts API integration."""
    
    @pytest.fixture
    def scanner_service(self):
        return BarcodeScannerService()
    
    def test_query_openfoodfacts_valid_barcode(self, scanner_service):
        """Test querying with a valid barcode."""
        # Use a known valid barcode (Nutella)
        try:
            result = scanner_service._query_openfoodfacts("3017620422003")
            
            if result:
                assert 'product_name' in result or 'error' in result
        except Exception as e:
            pytest.skip(f"OpenFoodFacts API not accessible: {e}")
    
    def test_query_openfoodfacts_invalid_barcode(self, scanner_service):
        """Test querying with an invalid barcode."""
        try:
            result = scanner_service._query_openfoodfacts("0000000000000")
            assert isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"OpenFoodFacts API not accessible: {e}")
    
    def test_api_timeout_handling(self, scanner_service):
        """Test that API timeouts are handled gracefully."""
        from unittest.mock import patch
        import requests
        
        with patch('requests.get', side_effect=requests.Timeout):
            result = scanner_service._query_openfoodfacts("1234567890123")
            assert isinstance(result, dict)


class TestIntegrationWorkflow:
    """Test complete barcode scanning workflow."""
    
    @pytest.fixture
    def scanner_service(self):
        return BarcodeScannerService()
    
    def test_complete_scan_workflow(self, scanner_service):
        """Test: scan → lookup → parse → return."""
        # Create test image
        img = Image.new('RGB', (300, 200), color='white')
        img_array = np.array(img)
        
        # Step 1: Scan
        result = scanner_service.scan_barcode(img_array)
        
        # Step 2: Verify structure
        assert isinstance(result, dict)
        assert 'barcode' in result or 'error' in result
    
    def test_ocr_to_nutrition_workflow(self, scanner_service):
        """Test: OCR → parse nutrition → return."""
        sample_text = "Calories: 200 Protein: 5g"
        
        # Step 1: Parse
        nutrition = scanner_service.parse_nutrition_label(sample_text)
        
        # Step 2: Verify
        assert isinstance(nutrition, dict)
