"""
Unified Nutrition API wrapper for multiple data sources.
Provides consistent nutrient structure across providers.
"""

import os
from typing import Optional, Dict, Any, List

import requests


class NutritionAPI:
    """
    Unified wrapper for supported nutrition data sources.
    """

    def __init__(self):
        self.openfoodfacts_url = "https://world.openfoodfacts.org/api/v2/product/{}.json"
        self.fooddata_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        self.fooddata_key = os.getenv("USDA_API_KEY")
        self.edamam_url = "https://api.edamam.com/api/food-database/v2/parser"
        self.edamam_app_id = os.getenv("EDAMAM_APP_ID")
        self.edamam_app_key = os.getenv("EDAMAM_APP_KEY")
        self.edamam_vision_url = "https://api.edamam.com/api/food-database/v2/vision"  # Image analysis
        self.nutritionix_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        self.nutritionix_app_id = os.getenv("NUTRITIONIX_APP_ID")
        self.nutritionix_api_key = os.getenv("NUTRITIONIX_API_KEY")

    def _format_response(self, data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Return a normalized structure for core nutrient values."""
        return {
            "source": source,
            "calories": data.get("calories"),
            "carbs": data.get("carbohydrates"),
            "fat": data.get("fat"),
            "protein": data.get("protein"),
            "sugar": data.get("sugars"),
            "raw": data,
        }

    def fetch_from_openfoodfacts(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Fetch product data from Open Food Facts by barcode."""
        try:
            resp = requests.get(self.openfoodfacts_url.format(barcode), timeout=10)
        except Exception:
            return None
        if resp.status_code == 200:
            product = resp.json().get("product")
            if product:
                nutr = product.get("nutriments", {})
                return self._format_response(
                    {
                        "calories": nutr.get("energy-kcal_100g"),
                        "carbohydrates": nutr.get("carbohydrates_100g"),
                        "fat": nutr.get("fat_100g"),
                        "protein": nutr.get("proteins_100g"),
                        "sugars": nutr.get("sugars_100g"),
                        "product_name": product.get("product_name"),
                    },
                    source="openfoodfacts",
                )
        return None

    def fetch_from_fooddata(self, query: str) -> Optional[Dict[str, Any]]:
        """Fetch food data by name from FoodData Central."""
        if not self.fooddata_key:
            return None
        params = {"query": query, "api_key": self.fooddata_key, "pageSize": 1}
        try:
            resp = requests.get(self.fooddata_url, params=params, timeout=10)
        except Exception:
            return None
        if resp.status_code == 200:
            foods = resp.json().get("foods")
            if foods:
                nutrients = {n.get("name"): n.get("amount") for n in foods[0].get("foodNutrients", [])}
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
                )
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
                )
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
        """
        sources = preferred_sources or ["openfoodfacts", "fooddata", "edamam", "nutritionix"]
        for source in sources:
            result = None
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
                return result
        return {"source": None, "raw": None}
