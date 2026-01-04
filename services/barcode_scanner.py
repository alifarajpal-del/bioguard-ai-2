"""
Barcode and OCR Scanner Service.
Handles barcode detection, OCR text extraction, and nutrition label parsing.
"""

import logging
from typing import Optional, Dict, Any, List
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None
    logging.warning("⚠️ OpenCV not available for barcode scanning")

try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    logging.warning("⚠️ pyzbar not available. Barcode scanning disabled. Install: pip install pyzbar")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("⚠️ pytesseract not available. OCR disabled. Install: pip install pytesseract")

import requests
from datetime import datetime


logger = logging.getLogger(__name__)


class BarcodeScannerService:
    """Service for barcode scanning and nutrition label OCR."""
    
    def __init__(self):
        """Initialize barcode scanner."""
        self.logger = logging.getLogger(__name__)
        self.cache = {}  # Cache for barcode lookups
    
    def scan_barcode(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Scan image for barcodes and return product info.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary with barcode data or None
        """
        if not PYZBAR_AVAILABLE or cv2 is None:
            return None
        
        try:
            # Convert to grayscale for better detection
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Detect barcodes
            barcodes = pyzbar.decode(gray)
            
            if not barcodes:
                return None
            
            # Process first detected barcode
            barcode = barcodes[0]
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            
            self.logger.info(f"✅ Barcode detected: {barcode_type} - {barcode_data}")
            
            # Lookup product information
            product_info = self._lookup_barcode(barcode_data, barcode_type)
            
            return {
                'barcode': barcode_data,
                'type': barcode_type,
                'product_info': product_info,
                'detected_at': datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            self.logger.error(f"❌ Barcode scanning error: {e}")
            return None
    
    def _lookup_barcode(self, barcode: str, barcode_type: str) -> Optional[Dict[str, Any]]:
        """
        Look up barcode in external databases.
        
        Args:
            barcode: Barcode number
            barcode_type: Type of barcode (EAN13, UPC-A, etc.)
            
        Returns:
            Product information or None
        """
        # Check cache first
        if barcode in self.cache:
            self.logger.info(f"📦 Using cached data for barcode: {barcode}")
            return self.cache[barcode]
        
        # Try OpenFoodFacts API
        product_info = self._query_openfoodfacts(barcode)
        
        if product_info:
            # Cache the result
            self.cache[barcode] = product_info
            return product_info
        
        # Fallback to USDA or other APIs
        # TODO: Add more API sources
        
        return None
    
    def _query_openfoodfacts(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Query OpenFoodFacts API for product information.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Product data or None
        """
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 1:
                    product = data.get('product', {})
                    
                    # Extract relevant information
                    return {
                        'name': product.get('product_name', 'Unknown Product'),
                        'brands': product.get('brands', ''),
                        'categories': product.get('categories', ''),
                        'ingredients': product.get('ingredients_text', ''),
                        'nutrition_grade': product.get('nutrition_grades', 'unknown'),
                        'nova_group': product.get('nova_group', 0),
                        'nutriments': product.get('nutriments', {}),
                        'allergens': product.get('allergens', ''),
                        'additives': product.get('additives_tags', []),
                        'image_url': product.get('image_url', ''),
                        'source': 'OpenFoodFacts',
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ OpenFoodFacts API error: {e}")
            return None
    
    def extract_text_ocr(self, image: np.ndarray) -> Optional[str]:
        """
        Extract text from image using OCR.
        
        Args:
            image: Input image
            
        Returns:
            Extracted text or None
        """
        if not TESSERACT_AVAILABLE or cv2 is None:
            return None
        
        try:
            # Preprocess image for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh)
            
            # Extract text
            text = pytesseract.image_to_string(denoised, lang='eng+ara')
            
            self.logger.info(f"📝 OCR extracted {len(text)} characters")
            
            return text.strip() if text else None
            
        except Exception as e:
            self.logger.error(f"❌ OCR error: {e}")
            return None
    
    def parse_nutrition_label(self, ocr_text: str) -> Dict[str, Any]:
        """
        Parse nutrition information from OCR text.
        
        Args:
            ocr_text: Text extracted from nutrition label
            
        Returns:
            Parsed nutrition data
        """
        nutrition_data = {
            'calories': None,
            'protein': None,
            'carbohydrates': None,
            'fat': None,
            'sodium': None,
            'sugar': None,
            'fiber': None,
        }
        
        try:
            import re
            
            # Common patterns for nutrition labels
            patterns = {
                'calories': r'calories?\s*[:=]?\s*(\d+)',
                'protein': r'protein\s*[:=]?\s*(\d+\.?\d*)\s*g',
                'carbohydrates': r'carb(?:ohydrate)?s?\s*[:=]?\s*(\d+\.?\d*)\s*g',
                'fat': r'(?:total\s+)?fat\s*[:=]?\s*(\d+\.?\d*)\s*g',
                'sodium': r'sodium\s*[:=]?\s*(\d+\.?\d*)\s*mg',
                'sugar': r'sugar?s?\s*[:=]?\s*(\d+\.?\d*)\s*g',
                'fiber': r'fiber\s*[:=]?\s*(\d+\.?\d*)\s*g',
            }
            
            text_lower = ocr_text.lower()
            
            for nutrient, pattern in patterns.items():
                match = re.search(pattern, text_lower)
                if match:
                    try:
                        nutrition_data[nutrient] = float(match.group(1))
                    except ValueError:
                        pass
            
            self.logger.info(f"📊 Parsed nutrition data: {nutrition_data}")
            
        except Exception as e:
            self.logger.error(f"❌ Nutrition parsing error: {e}")
        
        return nutrition_data
    
    def extract_ingredients_list(self, ocr_text: str) -> List[str]:
        """
        Extract ingredients list from OCR text.
        
        Args:
            ocr_text: Text from product label
            
        Returns:
            List of ingredients
        """
        try:
            import re
            
            # Look for "ingredients:" section
            pattern = r'ingredients?\s*[:=]\s*([^.]+)'
            match = re.search(pattern, ocr_text.lower())
            
            if match:
                ingredients_text = match.group(1)
                
                # Split by comma or semicolon
                ingredients = [
                    ing.strip() 
                    for ing in re.split(r'[,;]', ingredients_text)
                    if ing.strip()
                ]
                
                self.logger.info(f"🧪 Found {len(ingredients)} ingredients")
                return ingredients
            
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Ingredients extraction error: {e}")
            return []


# Global instance
barcode_scanner = None


def get_barcode_scanner() -> BarcodeScannerService:
    """Get or create global barcode scanner instance."""
    global barcode_scanner
    if barcode_scanner is None:
        barcode_scanner = BarcodeScannerService()
    return barcode_scanner
