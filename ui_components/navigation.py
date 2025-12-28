"""Bottom navigation bar component."""

import streamlit as st
from ui_components.theme_wheel import get_current_theme


def render_bottom_navigation():
    theme = get_current_theme()
    active_page = st.session_state.get("active_page", "home")

    # Global CSS with haptic feedback
    css = f"""
    <style>
        /* Haptic feedback for all buttons */
        button:active {{
            transform: scale(0.95) !important;
            box-shadow: inset 0 3px 5px rgba(0,0,0,0.2) !important;
            transition: all 0.1s ease !important;
        }}
        
        /* Fixed navigation container */
        .fixed-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(255,255,255,0.98);
            backdrop-filter: blur(16px);
            box-shadow: 0 -4px 20px rgba(0,0,0,0.12);
            z-index: 99999 !important;
            padding: 8px 12px 16px 12px;
        }}
        
        /* Navigation button styling */
        .fixed-nav [data-testid="column"] {{
            padding: 0 4px !important;
        }}
        
        .fixed-nav button {{
            width: 100% !important;
            padding: 12px 8px !important;
            border-radius: 12px !important;
            border: 2px solid transparent !important;
            background: transparent !important;
            color: #64748b !important;
            font-weight: 600 !important;
            font-size: 11px !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            gap: 4px !important;
        }}
        
        .fixed-nav button:hover {{
            background: rgba(0,0,0,0.04) !important;
            transform: translateY(-2px) !important;
        }}
        
        /* Active state styling */
        .fixed-nav button[data-active="true"] {{
            color: {theme['primary']} !important;
            background: {theme['primary']}12 !important;
            border-color: {theme['primary']}33 !important;
            box-shadow: 0 4px 12px {theme['primary']}25 !important;
        }}
        
        .nav-icon {{
            font-size: 24px;
            line-height: 1;
        }}
        
        .bottom-spacer {{
            height: 85px;
        }}
        
        /* Ensure nav is always on top */
        [data-testid="stVerticalBlock"] > div:has(div.fixed-nav) {{
            z-index: 99999 !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.markdown('<div class="bottom-spacer"></div>', unsafe_allow_html=True)

    # Create functional navigation with real Streamlit buttons
    st.markdown('<div class="fixed-nav">', unsafe_allow_html=True)
    cols = st.columns(4)
    
    nav_items = [
        ("home", "🏡", "Home"),
        ("scan", "🎥", "Scan"),
        ("vault", "📦", "Vault"),
        ("settings", "🛠️", "Settings"),
    ]
    
    for col, (page, icon, label) in zip(cols, nav_items):
        with col:
            is_active = page == active_page
            button_html = f'<div class="nav-icon">{icon}</div><div>{label}</div>'
            if st.button(
                button_html,
                key=f"nav_{page}",
                use_container_width=True,
                type="secondary" if not is_active else "primary",
            ):
                st.session_state.active_page = page
                st.rerun()
            
            # Mark active button with custom attribute via JS
            if is_active:
                st.markdown(
                    f'<script>document.querySelector("[data-testid=\\"baseButton-secondary\\"][key=\\"nav_{page}\\"]").setAttribute("data-active", "true");</script>',
                    unsafe_allow_html=True
                )
    
    st.markdown('</div>', unsafe_allow_html=True)


def get_active_page() -> str:
    return st.session_state.get("active_page", "home")
