"""Navigation helpers with stack-based routing and swipe flags."""

import streamlit as st

PAGES = ["dashboard", "scan", "vault", "settings"]


def ensure_nav_state() -> None:
    """Initialize navigation-related session state keys."""
    if "current_page" not in st.session_state or st.session_state.get("current_page") not in PAGES:
        st.session_state.current_page = "dashboard"
    if "nav_stack" not in st.session_state:
        st.session_state.nav_stack = []
    if "swipe_next" not in st.session_state:
        st.session_state.swipe_next = False
    if "swipe_prev" not in st.session_state:
        st.session_state.swipe_prev = False


def go_to(page: str) -> None:
    """Navigate to a page and push the previous page to the stack."""
    ensure_nav_state()
    if page not in PAGES:
        return
    current = st.session_state.get("current_page", "dashboard")
    if current != page:
        st.session_state.nav_stack.append(current)
    st.session_state.current_page = page
    st.session_state.swipe_next = False
    st.session_state.swipe_prev = False
    st.rerun()


def go_back() -> None:
    """Pop the nav stack and return to the previous page."""
    ensure_nav_state()
    if st.session_state.nav_stack:
        st.session_state.current_page = st.session_state.nav_stack.pop()
    else:
        st.session_state.current_page = "dashboard"
    st.session_state.swipe_next = False
    st.session_state.swipe_prev = False
    st.rerun()


def next_page() -> str:
    """Get the next page in sequence for swipe navigation."""
    ensure_nav_state()
    current = st.session_state.get("current_page", "dashboard")
    idx = PAGES.index(current) if current in PAGES else 0
    return PAGES[(idx + 1) % len(PAGES)]


def prev_page() -> str:
    """Get the previous page in sequence for swipe navigation."""
    ensure_nav_state()
    current = st.session_state.get("current_page", "dashboard")
    idx = PAGES.index(current) if current in PAGES else 0
    return PAGES[(idx - 1) % len(PAGES)]
