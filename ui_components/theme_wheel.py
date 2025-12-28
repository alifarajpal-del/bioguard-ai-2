"""Theme Wheel Component - interactive theme selection."""

from typing import Dict, Any
import streamlit as st
import random

THEMES: Dict[str, Dict[str, str]] = {
    "ocean": {
        "name": "Ocean",
        "primary": "#1e3a8a",
        "secondary": "#3b82f6",
        "background": "#f0f9ff",
        "text": "#0f172a",
        "accent": "#0ea5e9",
        "emoji": "🌊",
    },
    "sunset": {
        "name": "Sunset",
        "primary": "#ea580c",
        "secondary": "#fb923c",
        "background": "#fff7ed",
        "text": "#451a03",
        "accent": "#f97316",
        "emoji": "🌅",
    },
    "forest": {
        "name": "Forest",
        "primary": "#15803d",
        "secondary": "#4ade80",
        "background": "#f0fdf4",
        "text": "#052e16",
        "accent": "#22c55e",
        "emoji": "🌲",
    },
    "galaxy": {
        "name": "Galaxy",
        "primary": "#7c3aed",
        "secondary": "#a78bfa",
        "background": "#faf5ff",
        "text": "#2e1065",
        "accent": "#8b5cf6",
        "emoji": "🌌",
    },
    "midnight": {
        "name": "Midnight",
        "primary": "#111827",
        "secondary": "#1f2937",
        "background": "#0b1221",
        "text": "#f8fafc",
        "accent": "#6366f1",
        "emoji": "🌙",
    },
}


def _inject_theme_css(theme: Dict[str, str]) -> None:
    css = f"""
    <style>
        :root {{
            --primary-color: {theme['primary']};
            --background-color: {theme['background']};
            --text-color: {theme['text']};
            --secondary-background-color: {theme['secondary']};
        }}
        .stApp {{
            background: linear-gradient(135deg, {theme['background']} 0%, {theme['secondary']}22 100%);
            color: {theme['text']};
            font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .stButton > button {{
            background: linear-gradient(135deg, {theme['primary']} 0%, {theme['accent']} 100%);
            color: #fff;
            border: none;
            border-radius: 14px;
            padding: 0.75rem 1.5rem;
            font-weight: 700;
            box-shadow: 0 6px 18px {theme['primary']}35;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 10px 24px {theme['primary']}45;
        }}
        .stButton > button:active {{
            transform: translateY(0);
        }}
        .bottom-nav {{
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(10px);
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_theme_wheel() -> None:
    st.markdown("### 🎨 Theme Wheel")
    
    # Initialize spin state
    if "wheel_spinning" not in st.session_state:
        st.session_state.wheel_spinning = False
    
    # Spinning animation CSS
    spin_class = "spinning" if st.session_state.wheel_spinning else ""
    
    spin_css = """
    <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .spinning {
            animation: spin 0.5s ease-out;
        }
        .wheel-button {
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        .wheel-button:hover {
            transform: scale(1.05);
        }
        .wheel-button:active {
            transform: scale(0.95);
        }
    </style>
    """
    st.markdown(spin_css, unsafe_allow_html=True)
    
    wheel_html = f"""
    <div style="display:flex;justify-content:center;align-items:center; margin: 24px 0;">
        <div class="{spin_class}" style="position:relative;width:260px;height:260px;border-radius:50%;
                    background: conic-gradient(#3b82f6, #a78bfa, #22c55e, #f97316, #6366f1);
                    box-shadow:0 10px 30px rgba(0,0,0,0.18);">
            <div style="position:absolute;inset:32px;border-radius:50%;background: #ffffffee;
                        display:flex;align-items:center;justify-content:center;
                        font-size:42px;font-weight:700;color:#0f172a;">Spin 🎡</div>
        </div>
    </div>
    """
    st.markdown(wheel_html, unsafe_allow_html=True)

    # Interactive SPIN button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎰 SPIN THE WHEEL!", use_container_width=True, type="primary", key="spin_wheel"):
            # Select random theme
            theme_keys = list(THEMES.keys())
            current = st.session_state.get("active_theme", "ocean")
            # Ensure we get a different theme
            available = [t for t in theme_keys if t != current]
            new_theme = random.choice(available) if available else current
            
            st.session_state.active_theme = new_theme
            st.toast(f"🎨 Switched to {THEMES[new_theme]['name']} theme!", icon="✨")
            st.rerun()
    
    st.divider()
    st.markdown("**Or choose manually:**")

    cols = st.columns(3)
    for idx, (key, data) in enumerate(THEMES.items()):
        with cols[idx % 3]:
            if st.button(f"{data['emoji']} {data['name']}", key=f"theme_{key}", use_container_width=True):
                st.session_state.active_theme = key
                st.rerun()

    active = get_current_theme()
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {active['primary']} 0%, {active['accent']} 100%);
                    color:white;padding:16px;border-radius:14px;box-shadow:0 10px 30px {active['primary']}45;">
            <div style="font-weight:700;font-size:18px;">Current Theme</div>
            <div style="font-size:16px;">{active['emoji']} {active['name']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_active_theme() -> None:
    theme = get_current_theme()
    _inject_theme_css(theme)


def get_current_theme() -> Dict[str, Any]:
    key = st.session_state.get("active_theme", "ocean")
    return THEMES.get(key, THEMES["ocean"])
