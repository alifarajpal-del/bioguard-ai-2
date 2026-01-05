"""User-friendly error UI wrappers to avoid raw tracebacks."""

import logging
from typing import Callable
import streamlit as st

logger = logging.getLogger(__name__)


def safe_render(fn: Callable, context: str = "") -> None:
    """Run a render function safely, showing friendly error UI on failure."""
    try:
        fn()
    except Exception as exc:  # pragma: no cover
        logger.exception("Render failed: %s", context)
        st.error("حدث خطأ غير متوقع. الرجاء المحاولة مرة أخرى.")
        if st.button("إعادة المحاولة", key=f"retry_{context}"):
            st.rerun()
