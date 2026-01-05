import streamlit as st
from ui_components.theme_wheel import get_current_theme

def inject_global_css():
    theme = get_current_theme()
    st.markdown(f"""
    <style>
        :root {{
            --bg: {theme['background']};
            --card-bg: {theme['card_bg']};
            --primary: {theme['primary']};
            --secondary: {theme['secondary']};
            --accent: {theme['accent']};
            --text: {theme['text']};
        }}
        body, .stApp {{
            background-color: var(--bg) !important;
            color: var(--text) !important;
        }}
    </style>
    """, unsafe_allow_html=True)
