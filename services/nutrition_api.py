"""
Unified Nutrition API wrapper for multiple data sources.
Provides consistent nutrient structure across providers with retry logic and pre-confidence.
"""

import os
import json
import time
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from database.db_manager import get_db_manager
from app_config.settings import CACHE_ENABLED
from utils.logging_setup import get_logger

logger = get_logger(__name__)


def get_pre_confidence(input_type: str) -> float:
    """Get initial confidence score based on input type before API verification.
    
    Args:
        input_type: Type of input ('barcode', 'query', 'vision')
    
    Returns:
        Pre-confidence score (0.0 to 1.0)
    """
    confidence_map = {
        'barcode': 0.95,  # High confidence - exact match expected
        'query': 0.70,    # Medium confidence - text search
        'vision': 0.55,   # Lower confidence - image recognition
    }
    return confidence_map.get(input_type, 0.50)


def create_retry_session(max_retries: int = 2, backoff_factor: float = 0.3) -> requests.Session:
    """Create a requests session with retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Backoff factor for exponential delay
    
    Returns:
        Configured requests session
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class NutritionAPI:
    """
    Unified wrapper for supported nutrition data sources with retry and error handling.
    """

    def __init__(self):
        self.openfoodfacts_url = "https://world.openfoodfacts.org/api/v2/product/{}.json"
        self.fooddata_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        self.fooddata_key = os.getenv("USDA_API_KEY")
        self.edamam_url = "https://api.edamam.com/api/food-database/v2/parser"
        self.edamam_app_id = os.getenv("EDAMAM_APP_ID")
        self.edamam_app_key = os.getenv("EDAMAM_APP_KEY")
        self.edamam_vision_url = "https://api.edamam.com/api/food-database/v2/vision"
        self.nutritionix_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        self.nutritionix_app_id = os.getenv("NUTRITIONIX_APP_ID")
        self.nutritionix_api_key = os.getenv("NUTRITIONIX_API_KEY")
        
        # Create retry-enabled session
        self.session = create_retry_session()

    def _format_response(
        self,
        data: Dict[str, Any],
        source: str,
        confidence: float = 0.7,
        source_url: Optional[str] = None,
        is_cached: bool = False
    ) -> Dict[str, Any]:
        """Return a normalized structure for core nutrient values with trust metadata."""
        return {
            "source": source,
            "source_url": source_url,
            "confidence": confidence,
            "is_cached": is_cached,
            "timestamp": datetime.utcnow().isoformat(),
            "calories": data.get("calories"),
            "carbs": data.get("carbohydrates"),
            "fat": data.get("fat"),
            "protein": data.get("protein"),
            "sugar": data.get("sugars"),
            "raw": data,
        }

    def fetch_from_openfoodfacts(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Fetch product data from Open Food Facts by barcode with retry."""
        start_time = time.time()
        try:
            resp = self.session.get(
                self.openfoodfacts_url.format(barcode),
                timeout=10
            )
            duration_ms = (time.time() - start_time) * 1000
            
            if resp.status_code == 200:
                product = resp.json().get("product")
                if product:
                    nutr = product.get("nutriments", {})
                    logger.info(
                        f"OpenFoodFacts API success for barcode {barcode}",
                        extra={'duration_ms': duration_ms}
                    )
                    return self._format_response(
                        {
                            "calories": nutr.get("energy-kcal_100g"),
                            "carbohydrates": nutr.get("carbohydrates_100g"),
                            "fat": nutr.get("fat_100g"),
                            "protein": nutr.get("proteins_100g"),
                            "sugars": nutr.get("sugars_100g"),
                            "product_name": product.get("product_name"),
                            "brand": product.get("brands"),
                            "barcode": barcode,
                            "source_url": product.get("url"),
                        },
                        source="openfoodfacts",
                        confidence=0.95,
                        source_url=product.get("url"),
                    )
            
            logger.warning(f"OpenFoodFacts API returned status {resp.status_code} for barcode {barcode}")
            return None
            
        except requests.exceptions.Timeout:
            logger.warning(f"OpenFoodFacts API timeout for barcode {barcode}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenFoodFacts API error for barcode {barcode}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in OpenFoodFacts fetch: {str(e)}")
            return None

    def fetch_from_fooddata(self, query: str) -> Optional[Dict[str, Any]]:
        """Fetch food data by name from FoodData Central with retry."""
        if not self.fooddata_key:
            logger.warning("FoodData Central API key not configured")
            return None
        
        start_time = time.time()
        params = {"query": query, "api_key": self.fooddata_key, "pageSize": 1}
        
        try:
            resp = self.session.get(self.fooddata_url, params=params, timeout=10)
            duration_ms = (time.time() - start_time) * 1000
            
            if resp.status_code == 200:
                foods = resp.json().get("foods")
                if foods:
                    nutrients = {n.get("name"): n.get("amount") for n in foods[0].get("foodNutrients", [])}
                    logger.info(
                        f"FoodData Central API success for query '{query}'",
                        extra={'duration_ms': duration_ms}
                    )
                    return self._format_response(
                        {
                            "calories": nutrients.get("Energy"),
                            "carbohydrates": nutrients.get("Carbohydrate, by difference"),
                            "fat": nutrients.get("Total lipid (fat)"),
                            "protein": nutrients.get("Protein"),
                            "sugars": nutrients.get("Sugars, total"),
                            "product_name": foods[0].get("description"),
                        },
                        source="fooddata",
                        confidence=0.75,
                    )
            
            logger.warning(f"FoodData Central API returned status {resp.status_code} for query '{query}'")
            return None
            
        except requests.exceptions.Timeout:
            logger.warning(f"FoodData Central API timeout for query '{query}'")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"FoodData Central API error for query '{query}': {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in FoodData Central fetch: {str(e)}")
            return None

    def fetch_from_edamam(self, ingredient: str) -> Optional[Dict[str, Any]]:
        """Use Edamam Food API to parse natural language ingredient names."""
        if not (self.edamam_app_id and self.edamam_app_key):
            return None
        params = {"app_id": self.edamam_app_id, "app_key": self.edamam_app_key, "ingr": ingredient}
        try:
            resp = requests.get(self.edamam_url, params=params, timeout=10)
        except Exception:
            return None
        if resp.status_code == 200:
            hints = resp.json().get("hints", [])
            if hints:
                nutr = hints[0].get("food", {}).get("nutrients", {})
                return self._format_response(
                    {
                        "calories": nutr.get("ENERC_KCAL"),
                        "carbohydrates": nutr.get("CHOCDF"),
                        "fat": nutr.get("FAT"),
                        "protein": nutr.get("PROCNT"),
                        "sugars": nutr.get("SUGAR"),
                        "product_name": hints[0].get("food", {}).get("label"),
                    },
                    source="edamam",
                    confidence=0.7,
                )
        return None

    def fetch_from_edamam_vision(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """Use Edamam Vision API to interpret a food image (optional)."""
        if not (self.edamam_app_id and self.edamam_app_key):
            return None
        files = {"image": ("capture.jpg", image_bytes, "image/jpeg")}
        params = {"app_id": self.edamam_app_id, "app_key": self.edamam_app_key}
        try:
            resp = requests.post(self.edamam_vision_url, params=params, files=files, timeout=15)
        except Exception:
            return None
        if resp.status_code == 200:
            data = resp.json()
            foods = data.get("ingredients", [{}])[0].get("parsed", [])
            if foods:
                nutr = foods[0].get("nutrients", {})
                return self._format_response(
                    {
                        "calories": nutr.get("ENERC_KCAL"),
                        "carbohydrates": nutr.get("CHOCDF"),
                        "fat": nutr.get("FAT"),
                        "protein": nutr.get("PROCNT"),
                        "sugars": nutr.get("SUGAR"),
                        "product_name": foods[0].get("food"),
                    },
                    source="edamam_vision",
                    confidence=0.55,
                )
        return None

    def fetch_from_nutritionix(self, query: str) -> Optional[Dict[str, Any]]:
        """Use Nutritionix to interpret natural language or voice-derived food names."""
        if not (self.nutritionix_app_id and self.nutritionix_api_key):
            return None
        headers = {
            "x-app-id": self.nutritionix_app_id,
            "x-app-key": self.nutritionix_api_key,
            "Content-Type": "application/json",
        }
        data = {"query": query}
        try:
            resp = requests.post(self.nutritionix_url, headers=headers, json=data, timeout=10)
        except Exception:
            return None
        if resp.status_code == 200:
            items = resp.json().get("foods")
            if items:
                item = items[0]
                return self._format_response(
                    {
                        "calories": item.get("nf_calories"),
                        "carbohydrates": item.get("nf_total_carbohydrate"),
                        "fat": item.get("nf_total_fat"),
                        "protein": item.get("nf_protein"),
                        "sugars": item.get("nf_sugars"),
                        "product_name": item.get("food_name"),
                    },
                    source="nutritionix",
                    confidence=0.7,
                )
        return None

    def _cache_key(self, barcode: Optional[str], query: Optional[str]) -> Optional[str]:
        if barcode:
            return f"barcode::{barcode}"
        if query:
            return f"query::{query.strip().lower()}"
        return None

    def get_nutrition(
        self,
        barcode: Optional[str] = None,
        query: Optional[str] = None,
        preferred_sources: Optional[List[str]] = None,
        image_bytes: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """
        Try sources in preferred order; returns first successful result or an empty payload.
        Includes cache lookup and write-through with metadata.
        """
        cache_key = self._cache_key(barcode, query)
        db = get_db_manager()

        # Check cache first
        if CACHE_ENABLED and cache_key:
            cached = db.get_cached_nutrition(cache_key)
            if cached:
                cached["is_cached"] = True
                cached["cached"] = True  # Backward compatibility
                logger.info(f"Cache hit for {cache_key}")
                return cached

        # Attempt API calls
        sources = preferred_sources or ["fooddata", "openfoodfacts", "edamam", "nutritionix"]
        
        for source in sources:
            result = None
            try:
                if source == "openfoodfacts" and barcode:
                    result = self.fetch_from_openfoodfacts(barcode)
                elif source == "fooddata" and query:
                    result = self.fetch_from_fooddata(query)
                elif source == "edamam" and query:
                    result = self.fetch_from_edamam(query)
                elif source == "edamam_vision" and image_bytes:
                    result = self.fetch_from_edamam_vision(image_bytes)
                elif source == "nutritionix" and query:
                    result = self.fetch_from_nutritionix(query)
                    
                if result:
                    result["is_cached"] = False
                    if cache_key and CACHE_ENABLED:
                        db.save_nutrition_cache(cache_key, result)
                        logger.info(f"Cached result for {cache_key} from {source}")
                    return result
                    
            except Exception as e:
                logger.error(f"Error fetching from {source}: {str(e)}")
                continue
        
        # No results found
        logger.warning(f"No nutrition data found for barcode={barcode} query={query}")
        return {
            "source": None,
            "confidence": 0.0,
            "is_cached": False,
            "timestamp": datetime.utcnow().isoformat(),
            "raw": None
        }
