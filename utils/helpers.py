"""
Utility functions for BioGuard AI.
Common helpers for data processing, validation, and async operations.
"""

import asyncio
import hashlib
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate and sanitize data inputs."""
    
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """Validate user ID format."""
        if not user_id or len(user_id) < 3:
            return False
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', user_id))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize text input."""
        if not isinstance(text, str):
            return str(text)
        return text.strip()[:1000]  # Limit to 1000 chars


class AsyncHelper:
    """Helper functions for async operations."""
    
    @staticmethod
    async def run_in_executor(func, *args):
        """Run blocking function in executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)
    
    @staticmethod
    async def gather_with_timeout(*tasks, timeout: int = 30):
        """Run multiple tasks with timeout."""
        try:
            return await asyncio.wait_for(
                asyncio.gather(*tasks),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error("⏱️ Async operation timed out")
            return [None] * len(tasks)


class TextProcessor:
    """Text processing utilities."""
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """Extract all numbers from text."""
        if not isinstance(text, str):
            return []
        return [float(n) for n in re.findall(r'[\d.]+', text)]
    
    @staticmethod
    def parse_nutrition_value(value_str: str) -> float:
        """Parse nutritional value like '15g' or '600mg'."""
        if isinstance(value_str, (int, float)):
            return float(value_str)
        
        if not isinstance(value_str, str):
            return 0.0
        
        # Extract number
        match = re.search(r'([\d.]+)', value_str)
        return float(match.group(1)) if match else 0.0
    
    @staticmethod
    def format_verdict_message(verdict: str, score: int) -> str:
        """Format verdict message with emoji."""
        emoji_map = {
            'SAFE': '✅',
            'WARNING': '⚠️',
            'DANGER': '❌',
            'UNKNOWN': '❓',
        }
        emoji = emoji_map.get(verdict, '❓')
        return f"{emoji} {verdict} (Score: {score}/100)"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text with ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."


class CacheHelper:
    """Simple in-memory caching utility."""
    
    cache = {}
    
    @staticmethod
    def set(key: str, value: Any, ttl_seconds: int = 3600):
        """Set cache value with TTL."""
        CacheHelper.cache[key] = {
            'value': value,
            'expires_at': datetime.utcnow().timestamp() + ttl_seconds
        }
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get cache value if not expired."""
        if key not in CacheHelper.cache:
            return None
        
        entry = CacheHelper.cache[key]
        if datetime.utcnow().timestamp() > entry['expires_at']:
            del CacheHelper.cache[key]
            return None
        
        return entry['value']
    
    @staticmethod
    def clear():
        """Clear all cache."""
        CacheHelper.cache.clear()


class HealthScoreCalculator:
    """Calculate health scores for food products."""
    
    INGREDIENT_PENALTIES = {
        'trans_fat': 20,
        'artificial_sweetener': 10,
        'hfcs': 15,  # High fructose corn syrup
        'msg': 8,  # Monosodium glutamate
        'preservative': 5,
        'artificial_color': 8,
    }
    
    NUTRITION_PENALTIES = {
        'sodium': lambda val: min(20, val / 50),  # -20 for 1000mg
        'sugar': lambda val: min(25, val / 4),  # -25 for 100g
        'saturated_fat': lambda val: min(15, val / 2),  # -15 for 30g
    }
    
    @staticmethod
    def calculate(
        ingredients: List[str],
        nutrition: Dict[str, float],
        nova_score: int
    ) -> int:
        """Calculate overall health score (0-100)."""
        score = 100
        
        # NOVA score penalty
        nova_penalty = (nova_score - 1) * 10  # 1=0, 2=10, 3=20, 4=30
        score -= nova_penalty
        
        # Ingredient penalties
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            for penalty_key, penalty_value in HealthScoreCalculator.INGREDIENT_PENALTIES.items():
                if penalty_key in ingredient_lower:
                    score -= penalty_value
                    break
        
        # Nutrition penalties
        for nutrient, penalty_func in HealthScoreCalculator.NUTRITION_PENALTIES.items():
            if nutrient in nutrition:
                score -= penalty_func(nutrition[nutrient])
        
        # Ensure score is in range [0, 100]
        return max(0, min(100, int(score)))


class JSONEncoder:
    """Custom JSON encoder for complex types."""
    
    @staticmethod
    def serialize(obj: Any) -> str:
        """Serialize object to JSON string."""
        try:
            def encoder(o):
                if isinstance(o, datetime):
                    return o.isoformat()
                elif hasattr(o, '__dict__'):
                    return o.__dict__
                return str(o)
            
            return json.dumps(obj, default=encoder, indent=2)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return "{}"


class HashHelper:
    """Hashing utilities for security and deduplication."""
    
    @staticmethod
    def hash_string(text: str, algorithm: str = 'sha256') -> str:
        """Hash a string."""
        if algorithm == 'sha256':
            return hashlib.sha256(text.encode()).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(text.encode()).hexdigest()
        return ""
    
    @staticmethod
    def hash_object(obj: Dict[str, Any]) -> str:
        """Hash a dictionary object."""
        json_str = json.dumps(obj, sort_keys=True)
        return HashHelper.hash_string(json_str)


def create_micro_summary(
    product_name: str,
    health_score: int,
    verdict: str,
    confidence: float
) -> str:
    """Create a brief micro-summary for AR display."""
    emoji_map = {
        'SAFE': '✅',
        'WARNING': '⚠️',
        'DANGER': '❌',
    }
    emoji = emoji_map.get(verdict, '❓')
    
    return f"{product_name} | {emoji} {verdict} | {health_score}/100 ({confidence:.0%})"


def format_time_delta(seconds: int) -> str:
    """Format time delta in human-readable format."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}min"
    else:
        return f"{seconds // 3600}h"
