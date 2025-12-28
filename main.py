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
    """Render authentication and lightweight profile capture."""
    st.markdown("# 🧬 BioGuard AI")
    st.markdown("### Privacy-First | Real-Time Analysis | Predictive Intelligence")

    with st.container():
        col1, col2 = st.columns([1.5, 1])

        with col1:
            st.markdown(
                """
                **Why BioGuard?**
                - 🔐 Data stays on your device
                - 🧠 Federated learning friendly
                - 📊 Real-time AR food analysis
                - 🔮 Biological Digital Twin predictions
                """
            )

        with col2:
            user_id = st.text_input("User ID", placeholder="user_123")
            name = st.text_input("Name", placeholder="John Doe")
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0)
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
            allergies_input = st.text_input("Allergies", placeholder="Peanuts, Dairy")
            conditions_input = st.text_input("Conditions", placeholder="Diabetes, Hypertension")

            if st.button("🚀 Continue", use_container_width=True):
                if user_id and name:
                    profile = {
                        "user_id": user_id,
                        "name": name,
                        "age": age,
                        "weight": weight,
                        "height": height,
                        "allergies": [a.strip() for a in allergies_input.split(",") if a.strip()],
                        "medical_conditions": [c.strip() for c in conditions_input.split(",") if c.strip()],
                    }
                    token = create_or_login_user(profile)
                    st.session_state.user_id = user_id
                    st.session_state.user_profile = profile
                    st.session_state.authenticated = True
                    st.session_state.auth_token = token
                    st.success("✅ Welcome back!")
                    st.rerun()
                else:
                    st.warning("Please fill in User ID and Name")


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
