"""Structured logging setup for enterprise-grade observability.
Includes context tracking and sanitization of sensitive data.
"""

import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import streamlit as st


class ContextFilter(logging.Filter):
    """Add context fields to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        # Add session context if available
        if hasattr(st, 'session_state'):
            record.session_id = getattr(st.session_state, 'session_id', 'unknown')
            record.user_id = getattr(st.session_state, 'user_id', 'anonymous')
            record.current_page = getattr(st.session_state, 'current_page', 'unknown')
        else:
            record.session_id = 'no-session'
            record.user_id = 'no-user'
            record.current_page = 'no-page'
        
        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()
        
        return True


class SanitizingFormatter(logging.Formatter):
    """Formatter that sanitizes sensitive data from logs."""
    
    SENSITIVE_KEYS = {'password', 'token', 'api_key', 'secret', 'authorization'}
    
    def format(self, record: logging.LogRecord) -> str:
        # Sanitize message
        if hasattr(record, 'msg'):
            record.msg = self._sanitize_string(str(record.msg))
        
        # Sanitize args
        if hasattr(record, 'args') and record.args:
            record.args = tuple(self._sanitize_value(arg) for arg in record.args)
        
        return super().format(record)
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize sensitive data from string."""
        for key in self.SENSITIVE_KEYS:
            if key in text.lower():
                # Mask the value after the key
                import re
                pattern = rf'{key}[=:\s]+["\']?([^"\'\s,}}]+)'
                text = re.sub(pattern, f'{key}=***REDACTED***', text, flags=re.IGNORECASE)
        return text
    
    def _sanitize_value(self, value: Any) -> Any:
        """Sanitize sensitive data from any value."""
        if isinstance(value, str):
            return self._sanitize_string(value)
        elif isinstance(value, dict):
            return {k: '***REDACTED***' if k.lower() in self.SENSITIVE_KEYS else v 
                    for k, v in value.items()}
        return value


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    structured: bool = True
) -> logging.Logger:
    """Setup structured logging with context tracking.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        structured: Whether to use structured (JSON-like) format
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('bioguard')
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Format: structured or standard
    if structured:
        fmt = (
            '%(timestamp)s | %(levelname)s | '
            'session=%(session_id)s user=%(user_id)s page=%(current_page)s | '
            '%(name)s:%(funcName)s:%(lineno)d | %(message)s'
        )
    else:
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = SanitizingFormatter(fmt)
    console_handler.setFormatter(formatter)
    
    # Add context filter
    context_filter = ContextFilter()
    console_handler.addFilter(context_filter)
    
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(context_filter)
        logger.addHandler(file_handler)
    
    # Don't propagate to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = 'bioguard') -> logging.Logger:
    """Get or create a logger instance.
    
    Args:
        name: Logger name (default: 'bioguard')
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # Setup if not already configured
    if not logger.handlers:
        from config.settings import LOG_LEVEL
        setup_logging(level=LOG_LEVEL)
    
    return logger


def log_api_call(
    logger: logging.Logger,
    api_name: str,
    request_type: str,
    success: bool,
    duration_ms: Optional[float] = None,
    error: Optional[str] = None
) -> None:
    """Log API call with structured data.
    
    Args:
        logger: Logger instance
        api_name: Name of the API being called
        request_type: Type of request (barcode, query, vision)
        success: Whether the call succeeded
        duration_ms: Optional duration in milliseconds
        error: Optional error message
    """
    context = {
        'api': api_name,
        'type': request_type,
        'success': success,
        'duration_ms': duration_ms,
    }
    
    msg = f"API call to {api_name} ({request_type})"
    
    if success:
        logger.info(f"{msg} succeeded", extra=context)
    else:
        logger.warning(f"{msg} failed: {error}", extra=context)


def log_user_action(
    logger: logging.Logger,
    action: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """Log user action with context.
    
    Args:
        logger: Logger instance
        action: Action name (e.g., 'scan_product', 'view_history')
        details: Optional additional details
    """
    context = {'action': action}
    if details:
        context.update(details)
    
    logger.info(f"User action: {action}", extra=context)


# Initialize default logger
default_logger = get_logger()
