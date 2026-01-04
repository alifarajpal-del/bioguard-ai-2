"""
Health Product Recommendations Service.
Suggests healthier alternatives based on category, nutritional profile, and health score.
"""

import logging
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime, timedelta

from database.db_manager import get_db_manager

logger = logging.getLogger(__name__)


class HealthRecommendationsService:
    """Recommend healthier product alternatives."""
    
    def __init__(self):
        """Initialize recommendations service."""
        self.logger = logging.getLogger(__name__)
        self.db_manager = get_db_manager()
        self.cache = {}  # Cache for API results
        self.cache_ttl = timedelta(hours=6)
    
    def get_healthier_alternatives(
        self,
        product_name: str,
        current_health_score: int,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find healthier alternatives for a given product.
        
        Args:
            product_name: Current product name
            current_health_score: Current product's health score (0-100)
            category: Product category (optional, improves matching)
            limit: Maximum number of alternatives to return
            
        Returns:
            List of alternative products with higher health scores
        """
        alternatives = []
        
        # Strategy 1: Check local database for similar products
        local_alternatives = self._get_local_alternatives(
            product_name, 
            current_health_score, 
            category
        )
        alternatives.extend(local_alternatives)
        
        # Strategy 2: Query OpenFoodFacts for similar products
        if len(alternatives) < limit:
            api_alternatives = self._get_openfoodfacts_alternatives(
                product_name,
                current_health_score,
                category,
                limit - len(alternatives)
            )
            alternatives.extend(api_alternatives)
        
        # Sort by health score (highest first)
        alternatives.sort(key=lambda x: x.get('health_score', 0), reverse=True)
        
        # Limit results
        return alternatives[:limit]
    
    def _get_local_alternatives(
        self,
        product_name: str,
        current_health_score: int,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search local database for healthier alternatives.
        
        Args:
            product_name: Product name to find alternatives for
            current_health_score: Minimum health score threshold
            category: Product category filter
            
        Returns:
            List of alternative products from local database
        """
        try:
            conn = self.db_manager._get_connection()
            cursor = conn.cursor()
            
            # Build query based on available filters
            query = """
                SELECT DISTINCT product, health_score, verdict, warnings
                FROM food_analysis
                WHERE health_score > ?
                AND product != ?
            """
            params = [current_health_score, product_name]
            
            # Add category filter if available (search in product name)
            if category:
                query += " AND LOWER(product) LIKE ?"
                params.append(f"%{category.lower()}%")
            
            query += " ORDER BY health_score DESC LIMIT 10"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            alternatives = []
            for row in rows:
                alternatives.append({
                    'product': row[0],
                    'health_score': row[1],
                    'verdict': row[2],
                    'source': 'local_database',
                    'reason': f"Better health score: {row[1]} vs {current_health_score}"
                })
            
            self.logger.info(f"Found {len(alternatives)} local alternatives for {product_name}")
            return alternatives
            
        except Exception as e:
            self.logger.error(f"Error searching local alternatives: {e}")
            return []
    
    def _get_openfoodfacts_alternatives(
        self,
        product_name: str,
        current_health_score: int,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query OpenFoodFacts API for healthier alternatives.
        
        Args:
            product_name: Product to find alternatives for
            current_health_score: Current health score
            category: Product category
            limit: Max results to return
            
        Returns:
            List of alternative products from OpenFoodFacts
        """
        # Check cache first
        cache_key = f"{product_name}_{category}_{current_health_score}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                self.logger.info(f"Using cached alternatives for {product_name}")
                return cached_data
        
        alternatives = []
        
        try:
            # Extract category from product name if not provided
            search_category = category or self._extract_category(product_name)
            
            # Search OpenFoodFacts
            search_url = "https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                'search_terms': search_category,
                'search_simple': 1,
                'action': 'process',
                'json': 1,
                'page_size': 20
            }
            
            response = requests.get(search_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                for product in products:
                    # Skip if same product
                    if product.get('product_name', '').lower() == product_name.lower():
                        continue
                    
                    # Calculate health score from OpenFoodFacts data
                    nutriscore = product.get('nutriscore_grade', '')
                    nova_group = product.get('nova_group', 0)
                    
                    estimated_score = self._estimate_health_score(nutriscore, nova_group)
                    
                    # Only include if healthier than current product
                    if estimated_score > current_health_score:
                        alternatives.append({
                            'product': product.get('product_name', 'Unknown'),
                            'brand': product.get('brands', ''),
                            'health_score': estimated_score,
                            'nutriscore': nutriscore.upper() if nutriscore else 'N/A',
                            'nova_score': nova_group,
                            'source': 'openfoodfacts',
                            'reason': self._generate_recommendation_reason(
                                nutriscore, 
                                nova_group,
                                current_health_score
                            )
                        })
                
                self.logger.info(f"Found {len(alternatives)} API alternatives for {product_name}")
            
            # Cache results
            self.cache[cache_key] = (alternatives[:limit], datetime.now())
            
            return alternatives[:limit]
            
        except Exception as e:
            self.logger.error(f"Error fetching OpenFoodFacts alternatives: {e}")
            return []
    
    def _extract_category(self, product_name: str) -> str:
        """
        Extract product category from name.
        
        Args:
            product_name: Product name
            
        Returns:
            Extracted category
        """
        # Common food categories
        categories = {
            'chips': ['chips', 'crisps', 'snack'],
            'chocolate': ['chocolate', 'cocoa'],
            'biscuit': ['biscuit', 'cookie', 'cracker'],
            'cereal': ['cereal', 'granola', 'muesli'],
            'yogurt': ['yogurt', 'yoghurt'],
            'juice': ['juice', 'drink', 'beverage'],
            'bread': ['bread', 'toast'],
            'cheese': ['cheese'],
            'milk': ['milk', 'dairy'],
        }
        
        product_lower = product_name.lower()
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in product_lower:
                    return category
        
        # Default: use first word of product name
        return product_name.split()[0] if product_name else 'food'
    
    def _estimate_health_score(self, nutriscore: str, nova_group: int) -> int:
        """
        Estimate health score from Nutri-Score and NOVA group.
        
        Args:
            nutriscore: Nutri-Score grade (a-e)
            nova_group: NOVA classification (1-4)
            
        Returns:
            Estimated health score (0-100)
        """
        # Nutri-Score mapping (a=best, e=worst)
        nutriscore_map = {
            'a': 95,
            'b': 80,
            'c': 65,
            'd': 45,
            'e': 25
        }
        
        # NOVA group penalty (1=unprocessed, 4=ultra-processed)
        nova_penalty = {
            1: 0,
            2: -5,
            3: -15,
            4: -25
        }
        
        # Calculate base score from Nutri-Score
        base_score = nutriscore_map.get(nutriscore.lower(), 50)
        
        # Apply NOVA penalty
        penalty = nova_penalty.get(nova_group, 0)
        
        # Final score (clamped to 0-100)
        final_score = max(0, min(100, base_score + penalty))
        
        return final_score
    
    def _generate_recommendation_reason(
        self,
        nutriscore: str,
        nova_group: int,
        current_score: int
    ) -> str:
        """
        Generate human-readable recommendation reason.
        
        Args:
            nutriscore: Nutri-Score grade
            nova_group: NOVA classification
            current_score: Current product's health score
            
        Returns:
            Recommendation reason text
        """
        reasons = []
        
        # Nutri-Score reason
        if nutriscore:
            grade = nutriscore.upper()
            if grade in ['A', 'B']:
                reasons.append(f"Excellent Nutri-Score ({grade})")
            elif grade == 'C':
                reasons.append(f"Good Nutri-Score ({grade})")
        
        # NOVA reason
        if nova_group in [1, 2]:
            reasons.append("Minimally processed")
        elif nova_group == 3:
            reasons.append("Moderately processed")
        
        # Score difference
        estimated = self._estimate_health_score(nutriscore, nova_group)
        if estimated > current_score:
            diff = estimated - current_score
            reasons.append(f"+{diff} health points")
        
        return " • ".join(reasons) if reasons else "Better nutritional profile"
    
    def get_personalized_alternatives(
        self,
        product_name: str,
        current_health_score: int,
        user_profile: Dict[str, Any],
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get personalized alternatives based on user health profile.
        
        Args:
            product_name: Current product name
            current_health_score: Current health score
            user_profile: User's health profile (allergies, conditions, etc.)
            category: Product category
            limit: Max alternatives to return
            
        Returns:
            List of personalized alternatives
        """
        # Get general alternatives
        alternatives = self.get_healthier_alternatives(
            product_name,
            current_health_score,
            category,
            limit * 2  # Get more to filter
        )
        
        # Filter based on user profile
        filtered_alternatives = []
        
        user_allergies = user_profile.get('allergies', [])
        user_conditions = user_profile.get('health_conditions', [])
        
        for alt in alternatives:
            # Skip if conflicts with user allergies
            product_lower = alt['product'].lower()
            
            has_conflict = False
            for allergy in user_allergies:
                if allergy.lower() in product_lower:
                    has_conflict = True
                    break
            
            if has_conflict:
                continue
            
            # Add personalization note
            if 'diabetes' in user_conditions and 'sugar' in product_lower:
                alt['personalized_note'] = "⚠️ Contains sugar - review if diabetic"
            elif 'hypertension' in user_conditions and 'salt' in product_lower:
                alt['personalized_note'] = "⚠️ May contain sodium - review blood pressure"
            else:
                alt['personalized_note'] = "✅ Matches your health profile"
            
            filtered_alternatives.append(alt)
        
        return filtered_alternatives[:limit]


# Global instance
_recommendations_service = None


def get_recommendations_service() -> HealthRecommendationsService:
    """Get or create global recommendations service instance."""
    global _recommendations_service
    if _recommendations_service is None:
        _recommendations_service = HealthRecommendationsService()
    return _recommendations_service
