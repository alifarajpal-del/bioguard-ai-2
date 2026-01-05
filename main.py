"""
BioGuard AI - Native Mobile Experience
Modular UI with bottom navigation, theme wheel, and AR camera.
"""

import streamlit as st

# Configure Streamlit early
st.set_page_config(
    page_title="BioGuard AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Imports
from config.settings import MOBILE_VIEWPORT
from ui_components.theme_wheel import apply_active_theme, render_theme_wheel
from ui_components.navigation import render_bottom_navigation, get_active_page
from ui_components.dashboard_view import render_dashboard
from ui_components.camera_view import render_camera_view
from ui_components.vault_view import render_vault
from ui_components.oauth_login import render_oauth_login, handle_oauth_callback
from services.auth import create_or_login_user, logout


# ============== Session State Initialization ==============

def init_session_state() -> None:
    """Initialize session state variables."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "home"
    if "active_theme" not in st.session_state:
        st.session_state.active_theme = "ocean"
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "ai_provider" not in st.session_state:
        st.session_state.ai_provider = "gemini"


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
            # Clear query params
            st.query_params.clear()
            st.success("✅ تم تسجيل الدخول بنجاح!")
            st.rerun()
        else:
            st.query_params.clear()
            st.rerun()
    
    # Render OAuth login screen
    render_oauth_login()


# ============== Settings Page ==============

def render_settings_page() -> None:
    st.markdown("## ⚙️ Settings & Theme")
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
    st.caption("سيتم استخدام المحرك المفضل ثم يتم التحويل تلقائياً للمحرك الآخر أو الوضع الوهمي إذا فشل.")
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
    apply_active_theme()

    if not st.session_state.authenticated:
        render_auth_screen()
        return

    page = get_active_page()
    if page == "home":
        render_dashboard()
    elif page == "scan":
        render_camera_view()
    elif page == "vault":
        render_vault()
    elif page == "settings":
        render_settings_page()

    render_bottom_navigation()


if __name__ == "__main__":
    main()
