"""Tests for input validation and sanitization."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.validation import (
    validate_barcode,
    sanitize_barcode,
    validate_query,
    sanitize_query,
    sanitize_filename,
    validate_confidence,
    ValidationError
)


def test_validate_barcode_valid():
    """Test barcode validation with valid inputs."""
    valid, error = validate_barcode("1234567890123")
    assert valid is True
    assert error is None


def test_validate_barcode_invalid_length():
    """Test barcode validation with invalid length."""
    valid, error = validate_barcode("123")
    assert valid is False
    assert error is not None


def test_validate_barcode_non_digits():
    """Test barcode validation with non-digit characters."""
    valid, error = validate_barcode("123ABC789")
    assert valid is False
    assert "أرقام فقط" in error


def test_sanitize_barcode_valid():
    """Test barcode sanitization with valid input."""
    result = sanitize_barcode("1234567890123")
    assert result == "1234567890123"


def test_sanitize_barcode_with_whitespace():
    """Test barcode sanitization removes whitespace."""
    result = sanitize_barcode("  123456789  ")
    assert result == "123456789"


def test_validate_query_valid():
    """Test query validation with valid input."""
    valid, error = validate_query("apple juice")
    assert valid is True
    assert error is None


def test_validate_query_too_short():
    """Test query validation with too short input."""
    valid, error = validate_query("a")
    assert valid is False
    assert "قصير" in error


def test_validate_query_too_long():
    """Test query validation with too long input."""
    valid, error = validate_query("a" * 300, max_length=200)
    assert valid is False
    assert "طويل" in error


def test_validate_query_dangerous_patterns():
    """Test query validation blocks dangerous patterns."""
    dangerous_queries = [
        "<script>alert('xss')</script>",
        "javascript:void(0)",
        "DROP TABLE users",
        "DELETE FROM products",
    ]
    
    for query in dangerous_queries:
        valid, error = validate_query(query)
        assert valid is False, f"Should reject dangerous query: {query}"


def test_sanitize_query_removes_excess_whitespace():
    """Test query sanitization removes excess whitespace."""
    result = sanitize_query("apple    juice   organic")
    assert result == "apple juice organic"


def test_sanitize_filename():
    """Test filename sanitization."""
    result = sanitize_filename("my/file:name*.txt")
    assert "/" not in result
    assert ":" not in result
    assert "*" not in result


def test_validate_confidence():
    """Test confidence score validation."""
    assert validate_confidence(0.5) is True
    assert validate_confidence(0.0) is True
    assert validate_confidence(1.0) is True
    assert validate_confidence(1.5) is False
    assert validate_confidence(-0.1) is False


if __name__ == "__main__":
    # Run tests manually
    print("Running validation tests...")
    
    tests = [
        test_validate_barcode_valid,
        test_validate_barcode_invalid_length,
        test_validate_barcode_non_digits,
        test_sanitize_barcode_valid,
        test_sanitize_barcode_with_whitespace,
        test_validate_query_valid,
        test_validate_query_too_short,
        test_validate_query_too_long,
        test_validate_query_dangerous_patterns,
        test_sanitize_query_removes_excess_whitespace,
        test_sanitize_filename,
        test_validate_confidence,
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
