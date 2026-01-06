"""Simple onboarding flow shown once per user session."""

import streamlit as st
from utils.translations import get_text


def get_screens(lang: str) -> list:
    """Get onboarding screens in the specified language."""
    return [
        {
            "title": get_text("onboarding_title_1", lang),
            "body": get_text("onboarding_body_1", lang),
            "icon": "🛡️",
        },
        {
            "title": get_text("onboarding_title_2", lang),
            "body": get_text("onboarding_body_2", lang),
            "icon": "🔒",
        },
        {
            "title": get_text("onboarding_title_3", lang),
            "body": get_text("onboarding_body_3", lang),
            "icon": "📸",
        },
    ]


def render_onboarding() -> None:
    if st.session_state.get("onboarding_done"):
        return
    
    # Get current language
    lang = st.session_state.get("language", "en")
    screens = get_screens(lang)

    # Center all onboarding content
    st.markdown("""
    <style>
        .onboarding-container {
            max-width: 600px;
            margin: 0 auto;
            text-align: center;
        }
        .onboarding-container h2,
        .onboarding-container h3,
        .onboarding-container p,
        .onboarding-container .stMarkdown {
            text-align: center !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="onboarding-container">', unsafe_allow_html=True)
    
    st.markdown(f"## 🚀 {get_text('lets_start', lang)}")
    for screen in screens:
        with st.container():
            st.markdown(f"### {screen['icon']} {screen['title']}")
            st.markdown(screen["body"])
            st.divider()

    if st.button(get_text("start_now", lang), type="primary", use_container_width=True):
        st.session_state.onboarding_done = True
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
