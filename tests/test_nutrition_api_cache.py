"""Test nutrition API caching logic."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_pre_confidence_scores():
    """Test pre-confidence score calculation."""
    from services.nutrition_api import get_pre_confidence
    
    assert get_pre_confidence('barcode') == 0.95
    assert get_pre_confidence('query') == 0.70
    assert get_pre_confidence('vision') == 0.55
    assert get_pre_confidence('unknown') == 0.50


def test_format_response_structure():
    """Test response formatting includes all required fields."""
    from services.nutrition_api import NutritionAPI
    
    api = NutritionAPI()
    response = api._format_response(
        data={'calories': 100, 'protein': 5},
        source='test',
        confidence=0.8
    )
    
    assert 'source' in response
    assert 'confidence' in response
    assert 'is_cached' in response
    assert 'timestamp' in response
    assert response['source'] == 'test'
    assert response['confidence'] == 0.8


def test_cache_key_generation():
    """Test cache key generation."""
    from services.nutrition_api import NutritionAPI
    
    api = NutritionAPI()
    
    # Barcode cache key
    key1 = api._cache_key(barcode="123456", query=None)
    assert key1 == "barcode::123456"
    
    # Query cache key
    key2 = api._cache_key(barcode=None, query="Apple Juice")
    assert key2 == "query::apple juice"
    
    # No cache key
    key3 = api._cache_key(barcode=None, query=None)
    assert key3 is None


if __name__ == "__main__":
    # Run tests manually
    print("Running nutrition API cache tests...")
    
    tests = [
        test_pre_confidence_scores,
        test_format_response_structure,
        test_cache_key_generation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
