"""
BioGuard AI - Native Mobile Experience
Modular UI with bottom navigation, theme wheel, and AR camera.
"""

import os

import streamlit as st
from PIL import Image

# Configure Streamlit early


def _get_page_icon():
    """Load app icon from branding assets if available."""
    logo_path = os.path.join("ui_components", "assets", "logo.png")
    if os.path.exists(logo_path):
        try:
            return Image.open(logo_path)
        except Exception:
            return "🧬"
    return "🧬"


st.set_page_config(
    page_title="BioGuard AI",
    page_icon=_get_page_icon(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Imports
from config.settings import MOBILE_VIEWPORT
from ui_components.theme_wheel import render_theme_wheel
from ui_components.navigation import render_bottom_navigation, get_active_page
from ui_components.dashboard_view import render_dashboard
from ui_components.vault_view import render_vault
from ui_components.oauth_login import render_oauth_login, handle_oauth_callback
from ui_components.global_styles import inject_global_css
from ui_components.branding import render_brand_header
from ui_components.onboarding import render_onboarding
from ui_components.router import ensure_nav_state, go_to, go_back, next_page, prev_page
from ui_components.error_ui import safe_render
from services.auth import create_or_login_user, logout
from utils.i18n import get_lang, set_lang, t

# Camera view - choose version
try:
    from ui_components.camera_view_refactored import render_camera_view as render_camera_new
    REFACTORED_CAMERA_AVAILABLE = True
except ImportError:
    REFACTORED_CAMERA_AVAILABLE = False
    render_camera_new = None

from ui_components.camera_view import render_camera_view as render_camera_legacy

PAGE_SUBTITLES = {
    "dashboard": "Health Dashboard",
    "scan": "Smart Camera",
    "vault": "Medical Vault",
    "settings": "Settings & Theme & Sync",
}


# ============== Session State Initialization ==============

def init_session_state() -> None:
    """Initialize session state variables."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    if "active_theme" not in st.session_state:
        st.session_state.active_theme = "dark"
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "ai_provider" not in st.session_state:
        st.session_state.ai_provider = "gemini"
    if "use_refactored_camera" not in st.session_state:
        st.session_state.use_refactored_camera = REFACTORED_CAMERA_AVAILABLE
    # Initialize language with default English
    get_lang()  # This will set to "en" if not already set
    ensure_nav_state()
    if "onboarding_done" not in st.session_state:
        st.session_state.onboarding_done = False


# ============== Authentication UI ==============

def render_auth_screen() -> None:
    """Render OAuth authentication screen with Google/Apple Sign-In."""
    # Check if this is an OAuth callback
    query_params = st.query_params
    
    # Handle Google OAuth callback
    if "code" in query_params and "state" in query_params:
        # Determine provider from URL path or session state
        provider = st.session_state.get("oauth_provider", "google")
        
        code = query_params["code"]
        state = query_params["state"]
        
        if handle_oauth_callback(provider, code, state):
            # Clear query params and redirect to dashboard
            st.query_params.clear()
            st.session_state.current_page = "dashboard"
            st.success("✅ تم تسجيل الدخول بنجاح!")
            st.rerun()
        else:
            st.query_params.clear()
            st.rerun()
    
    # Render OAuth login screen
    render_oauth_login()


# ============== Settings Page ==============

def render_settings_page() -> None:
    """Render settings page with safe error handling."""
    safe_render(_render_settings_inner, context="settings")


def _render_settings_inner() -> None:
    # Back button
    if st.button(f"⬅️ {t('go_home')}", key="settings_back_home"):
        go_back()
    
    st.markdown(f"## ⚙️ {t('settings_title')}")
    
    # Language selector
    st.markdown("### 🌍 Language / اللغة")
    current_lang = get_lang()
    lang_choice = st.selectbox(
        "Choose your language",
        options=["English", "العربية"],
        index=0 if current_lang == "en" else 1,
        key="language_selector"
    )
    new_lang = "en" if lang_choice == "English" else "ar"
    if new_lang != current_lang:
        set_lang(new_lang)
        st.rerun()
    st.divider()
    
    render_theme_wheel()
    st.divider()

    st.markdown("### 🤖 AI Provider")
    st.session_state.ai_provider = st.selectbox(
        "Choose AI engine",
        options=["gemini", "openai", "mock"],
        index=["gemini", "openai", "mock"].index(st.session_state.ai_provider or "gemini"),
        format_func=lambda x: {
            "gemini": "Gemini Vision",
            "openai": "OpenAI Vision",
            "mock": "Mock (offline)",
        }.get(x, x),
    )
    st.caption("Will use preferred engine, then fallback to others or mock mode if failed.")
    st.divider()
    
    # Camera view selector
    if REFACTORED_CAMERA_AVAILABLE:
        st.markdown("### 📸 Camera Version")
        use_new = st.checkbox(
            "Use Refactored Camera (Recommended)",
            value=st.session_state.use_refactored_camera,
            help="New modular camera with better performance and cleaner UI"
        )
        st.session_state.use_refactored_camera = use_new
        st.divider()

    st.markdown("### 👤 Profile")
    user = st.session_state.user_profile or {}
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Name", value=user.get("name", ""), key="profile_name")
        st.number_input("Age", value=user.get("age", 30), key="profile_age")
    with col2:
        st.number_input("Weight (kg)", value=user.get("weight", 70.0), key="profile_weight")
        st.number_input("Height (cm)", value=user.get("height", 170), key="profile_height")
    if st.button("💾 Save", use_container_width=True):
        st.success("Profile saved locally")

    st.divider()
    
    st.markdown("### 🩺 Diagnostics")
    with st.expander("System Info", expanded=False):
        st.write({
            "current_page": st.session_state.get("current_page", "N/A"),
            "nav_stack_depth": len(st.session_state.get("nav_stack", [])),
            "authenticated": st.session_state.get("authenticated", False),
            "onboarding_done": st.session_state.get("onboarding_done", False),
            "ai_provider": st.session_state.get("ai_provider", "N/A"),
            "active_theme": st.session_state.get("active_theme", "N/A"),
        })
    
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout(st.session_state.user_id or "")
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_profile = None
        st.rerun()


# ============== Main Application ==============

def main() -> None:
    init_session_state()
    st.markdown(MOBILE_VIEWPORT, unsafe_allow_html=True)
    inject_global_css()

    if not st.session_state.authenticated:
        render_auth_screen()
        return

    if not st.session_state.onboarding_done:
        render_onboarding()
        return

    def _handle_swipe_navigation() -> None:
        """Update current_page based on swipe gestures."""
        if st.session_state.get("swipe_next"):
            st.session_state.swipe_next = False
            go_to(next_page())

        if st.session_state.get("swipe_prev"):
            st.session_state.swipe_prev = False
            go_to(prev_page())

    _handle_swipe_navigation()

    page = get_active_page()

    if page != "scan":
        render_brand_header(subtitle=PAGE_SUBTITLES.get(page, "BioGuard AI"))
        if page != "dashboard" and st.session_state.get("nav_stack"):
            if st.button("⬅️ رجوع", key="back_btn_top"):
                go_back()

    if page == "dashboard":
        render_dashboard()
    elif page == "scan":
        # Choose camera version based on settings
        if st.session_state.use_refactored_camera and REFACTORED_CAMERA_AVAILABLE:
            render_camera_new()
        else:
            render_camera_legacy()
    elif page == "vault":
        render_vault()
    elif page == "settings":
        render_settings_page()

    render_bottom_navigation()


if __name__ == "__main__":
    main()
