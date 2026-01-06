"""Input validation and sanitization for security (OWASP ASVS compliance)."""

import re
from typing import Optional, Tuple


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_barcode(barcode: str) -> Tuple[bool, Optional[str]]:
    """Validate barcode input.
    
    Args:
        barcode: Barcode string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not barcode:
        return False, "الباركود فارغ"
    
    # Remove whitespace
    barcode = barcode.strip()
    
    # Check length (common barcode formats: UPC-A=12, EAN-13=13, EAN-8=8)
    if len(barcode) < 6 or len(barcode) > 14:
        return False, "طول الباركود غير صحيح (6-14 رقم)"
    
    # Check if digits only
    if not barcode.isdigit():
        return False, "الباركود يجب أن يحتوي على أرقام فقط"
    
    return True, None


def sanitize_barcode(barcode: str) -> str:
    """Sanitize and normalize barcode.
    
    Args:
        barcode: Raw barcode input
    
    Returns:
        Sanitized barcode string
    
    Raises:
        ValidationError: If barcode is invalid
    """
    barcode = barcode.strip()
    barcode = re.sub(r'\D', '', barcode)  # Remove non-digits
    
    is_valid, error = validate_barcode(barcode)
    if not is_valid:
        raise ValidationError(error)
    
    return barcode


def validate_query(query: str, max_length: int = 200) -> Tuple[bool, Optional[str]]:
    """Validate search query input.
    
    Args:
        query: Search query string
        max_length: Maximum allowed length
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query:
        return False, "الاستعلام فارغ"
    
    query = query.strip()
    
    if len(query) < 2:
        return False, "الاستعلام قصير جداً (حد أدنى 2 حرف)"
    
    if len(query) > max_length:
        return False, f"الاستعلام طويل جداً (حد أقصى {max_length} حرف)"
    
    # Check for potentially malicious patterns (basic SQLi/XSS prevention)
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
        r'DROP\s+TABLE',
        r'DELETE\s+FROM',
        r'INSERT\s+INTO',
        r'UPDATE\s+\w+\s+SET',
    ]
    
    query_lower = query.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return False, "الاستعلام يحتوي على أحرف غير مسموح بها"
    
    return True, None


def sanitize_query(query: str, max_length: int = 200) -> str:
    """Sanitize and normalize search query.
    
    Args:
        query: Raw query input
        max_length: Maximum allowed length
    
    Returns:
        Sanitized query string
    
    Raises:
        ValidationError: If query is invalid
    """
    query = query.strip()
    
    # Remove excessive whitespace
    query = re.sub(r'\s+', ' ', query)
    
    # Truncate if too long
    if len(query) > max_length:
        query = query[:max_length]
    
    is_valid, error = validate_query(query, max_length)
    if not is_valid:
        raise ValidationError(error)
    
    return query


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations.
    
    Args:
        filename: Raw filename
    
    Returns:
        Sanitized filename
    """
    # Remove path separators and dangerous characters
    filename = re.sub(r'[/\\:*?"<>|]', '', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename or 'unnamed'


def validate_confidence(value: float) -> bool:
    """Validate confidence score.
    
    Args:
        value: Confidence value to validate
    
    Returns:
        True if valid, False otherwise
    """
    return isinstance(value, (int, float)) and 0.0 <= value <= 1.0


def sanitize_url(url: str, allowed_domains: Optional[list[str]] = None) -> Optional[str]:
    """Sanitize and validate URL.
    
    Args:
        url: URL to sanitize
        allowed_domains: Optional list of allowed domains
    
    Returns:
        Sanitized URL or None if invalid
    """
    if not url:
        return None
    
    url = url.strip()
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return None
    
    # Check allowed domains if specified
    if allowed_domains:
        domain_matched = any(domain in url.lower() for domain in allowed_domains)
        if not domain_matched:
            return None
    
    return url


def rate_limit_check(
    session_state,
    key: str,
    max_calls: int = 10,
    window_seconds: int = 60
) -> Tuple[bool, Optional[str]]:
    """Simple in-memory rate limiting check.
    
    Args:
        session_state: Streamlit session state
        key: Rate limit key (e.g., 'scan_calls')
        max_calls: Maximum calls allowed in window
        window_seconds: Time window in seconds
    
    Returns:
        Tuple of (is_allowed, error_message)
    """
    import time
    
    rate_key = f'_rate_limit_{key}'
    
    if rate_key not in session_state:
        session_state[rate_key] = []
    
    current_time = time.time()
    
    # Remove old entries outside the window
    session_state[rate_key] = [
        t for t in session_state[rate_key]
        if current_time - t < window_seconds
    ]
    
    # Check if limit exceeded
    if len(session_state[rate_key]) >= max_calls:
        return False, f"تم تجاوز الحد الأقصى ({max_calls} مرات في {window_seconds} ثانية). يرجى الانتظار."
    
    # Add current call
    session_state[rate_key].append(current_time)
    
    return True, None
