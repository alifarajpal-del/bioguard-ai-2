"""Bottom navigation bar component."""

import streamlit as st
from ui_components.theme_wheel import get_current_theme


def render_bottom_navigation():
    theme = get_current_theme()
    active_page = st.session_state.get("active_page", "home")

    # iOS Dock Style CSS
    css = f"""
    <style>
        /* iOS Dock Container */
        .nav-dock {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(249, 249, 249, 0.94);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border-top: 0.5px solid rgba(0, 0, 0, 0.1);
            z-index: 99999;
            padding: 8px 0 20px 0;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
        }}
        
        /* Navigation buttons - iOS style */
        .nav-dock [data-testid="column"] {{
            padding: 0 !important;
        }}
        
        .nav-dock button {{
            background: transparent !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 8px !important;
            font-size: 28px !important;
            line-height: 1 !important;
            width: 100% !important;
            color: #8e8e93 !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: none !important;
            font-weight: 400 !important;
        }}
        
        .nav-dock button:hover {{
            transform: scale(1.15) translateY(-4px) !important;
            filter: brightness(1.1) !important;
        }}
        
        .nav-dock button:active {{
            transform: scale(0.92) !important;
            transition: all 0.1s ease !important;
        }}
        
        /* Active state - iOS blue */
        .nav-dock button.active-nav {{
            color: #007AFF !important;
            background: rgba(0, 122, 255, 0.08) !important;
            transform: scale(1.08) !important;
        }}
        
        .bottom-spacer {{
            height: 75px;
        }}
        
        /* Label under icon */
        .nav-label {{
            font-size: 10px;
            color: #8e8e93;
            font-weight: 500;
            margin-top: 2px;
            letter-spacing: -0.2px;
        }}
        
        .nav-label.active {{
            color: #007AFF;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.markdown('<div class="bottom-spacer"></div>', unsafe_allow_html=True)

    # iOS Dock Navigation
    nav_container = st.container()
    with nav_container:
        st.markdown('<div class="nav-dock">', unsafe_allow_html=True)
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
                # Use plain emoji as button label - Streamlit will render it properly
                if st.button(
                    icon,
                    key=f"nav_{page}",
                    use_container_width=True,
                ):
                    st.session_state.active_page = page
                    st.rerun()
                
                # Label below icon
                label_class = "active" if is_active else ""
                st.markdown(
                    f'<div class="nav-label {label_class}" style="text-align:center;">{label}</div>',
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)


def get_active_page() -> str:
    return st.session_state.get("active_page", "home")
