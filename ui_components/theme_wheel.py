"""Theme Wheel Component - interactive theme selection."""

from typing import Dict, Any
import streamlit as st
import random

THEMES: Dict[str, Dict[str, str]] = {
    "medical": {
        "name": "Medical Pro",
        "background": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "primary": "#3B82F6",      # Professional blue
        "secondary": "#E0F2FE",    # Soft blue
        "accent": "#10B981",       # Trust green
        "success": "#10B981",      # Green
        "warning": "#F59E0B",      # Amber
        "danger": "#EF4444",       # Red
        "text": "#0F172A",
        "text_secondary": "#64748B",
        "emoji": "🩺",
    },
    "dark": {
        "name": "Dark Mode",
        "background": "#0F172A",
        "card_bg": "#1E293B",
        "primary": "#60A5FA",      # Softer blue for dark
        "secondary": "#1E3A5F",
        "accent": "#34D399",       # Bright green for contrast
        "success": "#34D399",
        "warning": "#FBBF24",
        "danger": "#F87171",
        "text": "#F1F5F9",
        "text_secondary": "#94A3B8",
        "emoji": "🌙",
    },
    "ocean": {
        "name": "Deep Ocean",
        "primary": "#0891b2",
        "secondary": "#CFFAFE",
        "background": "#F0FDFA",
        "text": "#134E4A",
        "text_secondary": "#6B7280",
        "accent": "#06B6D4",
        "success": "#14B8A6",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "card_bg": "#FFFFFF",
        "emoji": "🌊",
    },
    "sunset": {
        "name": "Peach Sunset",
        "primary": "#F97316",
        "secondary": "#FED7AA",
        "background": "#FFF7ED",
        "text": "#7C2D12",
        "text_secondary": "#92400E",
        "accent": "#FB923C",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "card_bg": "#FFFFFF",
        "emoji": "🍑",
    },
}


def get_current_theme() -> Dict[str, Any]:
    """Return the active theme with a safe fallback."""
    key = st.session_state.get("active_theme", "dark")
    return THEMES.get(key, THEMES["dark"])


def render_theme_selector():
    """Render a simple button to cycle through themes."""
    themes = list(THEMES.keys())
    current = st.session_state.get("active_theme", "dark")
    idx = themes.index(current)
    next_idx = (idx + 1) % len(themes)
    
    if st.button(f"🎨 تغيير الثيم إلى {THEMES[themes[next_idx]]['name']}", key="change_theme"):
        st.session_state.active_theme = themes[next_idx]
        st.success(f"تم تغيير الثيم إلى {themes[next_idx]}")
        st.rerun()
    
    st.markdown(f"<small>الثيم الحالي: <b>{current}</b></small>", unsafe_allow_html=True)


def apply_active_theme() -> None:
    """Inject CSS for the currently active theme."""
    theme = get_current_theme()
    _inject_theme_css(theme)



def _inject_theme_css(theme: Dict[str, str]) -> None:
    """Inject modern medical-grade theme CSS with professional color system"""
    css = f"""
    <style>
        :root {{
            /* Core color system */
            --primary: {theme['primary']};
            --secondary: {theme['secondary']};
            --accent: {theme['accent']};
            --success: {theme.get('success', theme['accent'])};
            --warning: {theme.get('warning', '#F59E0B')};
            --danger: {theme.get('danger', '#EF4444')};
            
            /* Backgrounds */
            --bg: {theme['background']};
            --card-bg: {theme['card_bg']};
            
            /* Text colors */
            --text: {theme['text']};
            --text-secondary: {theme.get('text_secondary', theme['text'])};
            
            /* Legacy aliases for compatibility */
            --primary-color: {theme['primary']};
            --background-color: {theme['background']};
            --text-color: {theme['text']};
            --secondary-background-color: {theme['secondary']};
            --accent-color: {theme['accent']};
        }}
        
        /* Main App Background - Clean and Professional */
        .stApp {{
            background: {theme['background']};
            color: {theme['text']};
            font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            min-height: 100vh;
        }}
        
        /* Typography Hierarchy */
        h1 {{
            font-size: 32px !important;
            font-weight: 700 !important;
            color: {theme['text']} !important;
            letter-spacing: -0.5px !important;
            margin-bottom: 16px !important;
        }}
        
        h2 {{
            font-size: 24px !important;
            font-weight: 600 !important;
            color: {theme['text']} !important;
            letter-spacing: -0.3px !important;
            margin-bottom: 12px !important;
        }}
        
        h3 {{
            font-size: 18px !important;
            font-weight: 600 !important;
            color: {theme['text']} !important;
            margin-bottom: 8px !important;
        }}
        
        /* Text Elements */
        .stMarkdown, .stText, p, span, label {{
            color: {theme['text']} !important;
            line-height: 1.6 !important;
        }}
        
        /* Secondary Text */
        .stMarkdown small, .text-secondary {{
            color: {theme.get('text_secondary', theme['text'])} !important;
            opacity: 0.7;
        }}
        
        /* Input Fields - Clean and Professional */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {{
            background-color: {theme['card_bg']} !important;
            color: {theme['text']} !important;
            border: 2px solid {theme['secondary']} !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            font-size: 15px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }}
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: {theme['primary']} !important;
            box-shadow: 0 0 0 3px {theme['primary']}15 !important;
            outline: none !important;
        }}
        
        /* Input Labels */
        .stTextInput > label, .stTextArea > label, .stSelectbox > label {{
            color: {theme['text']} !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            margin-bottom: 6px !important;
        }}
            letter-spacing: 0.5px !important;
        }}
        
        /* Buttons - Clean and Professional */
        .stButton > button {{
            background: {theme['primary']} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            font-size: 15px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 8px {theme['primary']}25 !important;
        }}
        
        .stButton > button:hover {{
            background: {theme['primary']}dd !important;
            box-shadow: 0 4px 12px {theme['primary']}35 !important;
            transform: translateY(-1px);
        }}
        
        .stButton > button:active {{
            transform: translateY(0);
        }}
        
        /* Card Components - Clean */
        .card {{
            background: {theme['card_bg']};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px {theme['primary']}10;
            border: 1px solid {theme['secondary']};
            transition: all 0.2s ease;
        }}
        
        .card:hover {{
            box-shadow: 0 4px 16px {theme['primary']}15;
        }}
        
        /* Bottom Navigation Bar */
        .bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: {theme['card_bg']};
            backdrop-filter: blur(20px);
            border-top: 2px solid {theme['secondary']};
            padding: 12px 0;
            box-shadow: 0 -4px 20px {theme['primary']}15;
            z-index: 1000;
        }}
        
        /* Expander Components */
        .streamlit-expanderHeader {{
            background: {theme['card_bg']} !important;
            color: {theme['text']} !important;
            border: 2px solid {theme['secondary']} !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
        }}
        
        /* Metrics and Stats */
        [data-testid="stMetricValue"] {{
            color: {theme['primary']} !important;
            font-weight: 800 !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            color: {theme['text']} !important;
            font-weight: 600 !important;
        }}
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {theme['card_bg']} 0%, {theme['secondary']} 100%) !important;
        }}
        
        /* Success/Info/Warning/Error Messages */
        .stSuccess {{
            background-color: #d1fae5 !important;
            color: #064e3b !important;
            border-left: 4px solid #10b981 !important;
        }}
        
        .stInfo {{
            background-color: #dbeafe !important;
            color: #0c4a6e !important;
            border-left: 4px solid #3b82f6 !important;
        }}
        
        .stWarning {{
            background-color: #fed7aa !important;
            color: #7c2d12 !important;
            border-left: 4px solid #f97316 !important;
        }}
        
        .stError {{
            background-color: #fecdd3 !important;
            color: #881337 !important;
            border-left: 4px solid #f43f5e !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_theme_wheel() -> None:
    """Render interactive theme wheel with smooth animations"""
    st.markdown("### 🎨 اختر الثيم المفضل")
    
    # Initialize spin state and rotation
    if "wheel_spinning" not in st.session_state:
        st.session_state.wheel_spinning = False
    if "wheel_rotation" not in st.session_state:
        st.session_state.wheel_rotation = 0
    
    current_rotation = st.session_state.wheel_rotation
    current_theme = get_current_theme()
    
    # Enhanced spinning animation CSS
    spin_css = f"""
    <style>
        @keyframes spinWheel {{
            0% {{ transform: rotate({current_rotation}deg); }}
            100% {{ transform: rotate({current_rotation + 1080}deg); }}
        }}
        
        @keyframes pulseGlow {{
            0%, 100% {{ opacity: 0.6; transform: scale(1); }}
            50% {{ opacity: 1; transform: scale(1.1); }}
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        .wheel-container {{
            perspective: 1200px;
            margin: 40px 0;
            position: relative;
        }}
        
        .spinning {{
            animation: spinWheel 2s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
        }}
        
        .wheel-wrapper {{
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            user-select: none;
            transition: all 0.3s ease;
        }}
        
        .wheel-wrapper:hover {{
            transform: scale(1.05);
        }}
        
        .wheel-glow {{
            position: absolute;
            width: 320px;
            height: 320px;
            border-radius: 50%;
            background: radial-gradient(circle, {current_theme['primary']}40 0%, transparent 70%);
            filter: blur(30px);
            animation: pulseGlow 3s infinite ease-in-out;
            pointer-events: none;
        }}
        
        .wheel-disc {{
            position: relative;
            width: 280px;
            height: 280px;
            border-radius: 50%;
            background: conic-gradient(
                #6366f1 0deg 60deg,
                #0ea5e9 60deg 120deg,
                #ec4899 120deg 180deg,
                #10b981 180deg 240deg,
                #f97316 240deg 300deg,
                #0891b2 300deg 360deg
            );
            box-shadow: 
                0 15px 50px rgba(0,0,0,0.15),
                inset 0 0 40px rgba(255,255,255,0.3),
                0 0 0 8px {current_theme['card_bg']},
                0 0 0 10px {current_theme['secondary']};
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .wheel-disc::before {{
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 50%;
            background: linear-gradient(135deg, rgba(255,255,255,0.3) 0%, transparent 50%, rgba(0,0,0,0.1) 100%);
            pointer-events: none;
        }}
        
        .wheel-disc:hover {{
            transform: scale(1.03) rotateZ(5deg);
            box-shadow: 
                0 20px 60px rgba(0,0,0,0.2),
                inset 0 0 50px rgba(255,255,255,0.4),
                0 0 0 8px {current_theme['card_bg']},
                0 0 0 12px {current_theme['primary']};
        }}
        
        .wheel-center {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 180px;
            height: 180px;
            border-radius: 50%;
            background: linear-gradient(145deg, {current_theme['card_bg']}, {current_theme['secondary']});
            box-shadow: 
                0 12px 30px rgba(0,0,0,0.15),
                inset 0 -4px 12px rgba(0,0,0,0.1),
                inset 0 4px 12px rgba(255,255,255,0.9);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 56px;
            user-select: none;
            z-index: 10;
            animation: float 3s infinite ease-in-out;
        }}
        
        .theme-name {{
            font-size: 14px;
            font-weight: 700;
            color: {current_theme['primary']};
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .wheel-pointer {{
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 15px solid transparent;
            border-right: 15px solid transparent;
            border-top: 25px solid {current_theme['primary']};
            filter: drop-shadow(0 4px 8px {current_theme['primary']}40);
            z-index: 100;
        }}
        
        .wheel-disc:active {{
            transform: scale(0.98);
        }}
        
        .spin-hint {{
            text-align: center;
            color: {current_theme['text']};
            font-size: 14px;
            margin-top: 20px;
            font-weight: 600;
            opacity: 0.7;
        }}
        
        .theme-preview {{
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .theme-dot {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: 3px solid transparent;
        }}
        
        .theme-dot:hover {{
            transform: scale(1.15);
            box-shadow: 0 6px 16px rgba(0,0,0,0.25);
        }}
        
        .theme-dot.active {{
            border-color: {current_theme['primary']};
            box-shadow: 0 0 0 4px {current_theme['primary']}30;
        }}
    </style>
    """
    st.markdown(spin_css, unsafe_allow_html=True)
    
    spin_class = "spinning" if st.session_state.wheel_spinning else ""
    
    wheel_html = f"""
    <div class="wheel-container">
        <div class="wheel-pointer"></div>
        <div class="wheel-wrapper">
            <div class="wheel-glow"></div>
            <div class="wheel-disc {spin_class}">
                <div class="wheel-center">
                    <span>{current_theme['emoji']}</span>
                    <div class="theme-name">{current_theme['name']}</div>
                </div>
            </div>
        </div>
        <div class="spin-hint">✨ اضغط العجلة أو الزر للتغيير العشوائي</div>
    </div>
    """
    st.markdown(wheel_html, unsafe_allow_html=True)

    # Interactive SPIN button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎲 تدوير العجلة!", use_container_width=True, type="primary", key="spin_wheel"):
            # Select random theme
            theme_keys = list(THEMES.keys())
            current = st.session_state.get("active_theme", "dark")
            available = [t for t in theme_keys if t != current]
            new_theme = random.choice(available) if available else current
            
            # Update rotation
            st.session_state.wheel_rotation += 1080
            st.session_state.wheel_spinning = True
            
            st.session_state.active_theme = new_theme
            st.toast(f"🎨 تم التبديل إلى ثيم {THEMES[new_theme]['name']}!", icon="✨")
            st.balloons()
            st.rerun()
    
    st.divider()
    st.markdown("**أو اختر يدوياً:**")

    # Theme selection buttons with preview colors
    cols = st.columns(3)
    for idx, (key, data) in enumerate(THEMES.items()):
        with cols[idx % 3]:
            active_indicator = "✓ " if st.session_state.get("active_theme") == key else ""
            if st.button(
                f"{active_indicator}{data['emoji']} {data['name']}", 
                key=f"theme_{key}", 
                use_container_width=True,
                type="primary" if st.session_state.get("active_theme") == key else "secondary"
            ):
                st.session_state.active_theme = key
                st.session_state.wheel_rotation += 360
                st.rerun()

    # Current theme display
    active = get_current_theme()
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {active['primary']} 0%, {active['accent']} 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 16px;
                    box-shadow: 0 12px 35px {active['primary']}45;
                    margin-top: 20px;
                    text-align: center;">
            <div style="font-weight: 800; font-size: 20px; margin-bottom: 8px;">الثيم الحالي</div>
            <div style="font-size: 32px; margin: 12px 0;">{active['emoji']}</div>
            <div style="font-size: 18px; font-weight: 600;">{active['name']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
