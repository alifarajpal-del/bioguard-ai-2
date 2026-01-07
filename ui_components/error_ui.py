"""User-friendly error UI wrappers to avoid raw tracebacks.
Enterprise-grade error handling with logging and recovery options.
"""

import logging
from typing import Callable, Optional
import streamlit as st
from utils.logging_setup import get_logger
from utils.i18n import t

logger = get_logger(__name__)


def safe_render(fn: Callable, context: str = "", show_details: bool = False) -> None:
    """Run a render function safely, showing friendly error UI on failure.
    
    Args:
        fn: Function to execute safely
        context: Context string for logging (e.g., 'dashboard', 'camera')
        show_details: Whether to show error details (dev mode only)
    """
    try:
        fn()
    except Exception as exc:
        # Log the full exception with context
        logger.exception(
            f"Render failed in context: {context}",
            extra={'context': context, 'error_type': type(exc).__name__}
        )
        
        # Show user-friendly error card
        st.markdown(f"""
        <div style="
            padding: 20px;
            border-radius: 12px;
            background: rgba(239, 68, 68, 0.1);
            border-left: 4px solid #ef4444;
            margin: 16px 0;
        ">
            <div style="font-size: 16px; font-weight: 600; color: #ef4444; margin-bottom: 8px;">
                ⚠️ {t('unexpected_error')}
            </div>
            <div style="font-size: 14px; color: #6b7280; line-height: 1.6;">
                {t('error_apology')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show error details in development mode
        if show_details and hasattr(st, 'secrets') and st.secrets.get('ENVIRONMENT') == 'development':
            with st.expander("تفاصيل الخطأ (وضع التطوير)"):
                st.code(str(exc))
        
        # Offer recovery options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"🔄 {t('retry')}", key=f"retry_{context}", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button(f"🏠 {t('go_home')}", key=f"home_{context}", use_container_width=True):
                from ui_components.router import go_to
                go_to("dashboard")
                st.rerun()
        
        with col3:
            if st.button(f"📝 {t('report_issue')}", key=f"report_{context}", use_container_width=True):
                st.info(t('contact_support'))


def show_api_error(
    message: str = "تعذر الاتصال بالخدمة",
    suggestion: Optional[str] = None,
    cached_data: Optional[dict] = None
) -> None:
    """Show a user-friendly API error with suggestions and cached data fallback.
    
    Args:
        message: Error message to display
        suggestion: Optional suggestion for the user
        cached_data: Optional cached data to display as fallback
    """
    st.markdown(f"""
    <div style="
        padding: 16px;
        border-radius: 12px;
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        margin: 16px 0;
    ">
        <div style="font-size: 15px; font-weight: 600; color: #f59e0b; margin-bottom: 6px;">
            ⚠️ {message}
        </div>
        {f'<div style="font-size: 13px; color: #6b7280;">{suggestion}</div>' if suggestion else ''}
    </div>
    """, unsafe_allow_html=True)
    
    if cached_data:
        st.info("📦 عرض البيانات المخزنة مؤقتاً")


def show_validation_error(message: str) -> None:
    """Show a validation error message.
    
    Args:
        message: Validation error message
    """
    st.markdown(f"""
    <div style="
        padding: 12px 16px;
        border-radius: 8px;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        margin: 8px 0;
    ">
        <div style="font-size: 14px; color: #ef4444;">
            ❌ {message}
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_rate_limit_error(message: str) -> None:
    """Show a rate limit error message.
    
    Args:
        message: Rate limit error message
    """
    st.markdown(f"""
    <div style="
        padding: 16px;
        border-radius: 12px;
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        margin: 16px 0;
    ">
        <div style="font-size: 15px; font-weight: 600; color: #f59e0b; margin-bottom: 6px;">
            ⏱️ حد الاستخدام
        </div>
        <div style="font-size: 13px; color: #6b7280;">{message}</div>
    </div>
    """, unsafe_allow_html=True)

