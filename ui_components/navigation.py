"""Bottom navigation bar component."""

import streamlit as st
from ui_components.theme_wheel import get_current_theme


def render_bottom_navigation():
    theme = get_current_theme()
    active_page = st.session_state.get("active_page", "home")

    css = f"""
    <style>
        /* Bottom Navigation - MUST be above everything */
        .bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 4px;
            background: rgba(255,255,255,0.98);
            backdrop-filter: blur(16px);
            padding: 8px 12px 12px 12px;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.12);
            z-index: 10000 !important;
            pointer-events: auto !important;
        }}
        
        .nav-item {{
            text-align: center;
            padding: 8px 4px;
            border-radius: 10px;
            color: #64748b;
            font-weight: 600;
            font-size: 12px;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.15s ease;
            pointer-events: auto !important;
        }}
        
        .nav-item:hover {{
            background: rgba(0,0,0,0.03);
        }}
        
        .nav-item.active {{
            color: {theme['primary']};
            border-color: {theme['primary']}33;
            background: {theme['primary']}12;
            box-shadow: 0 4px 12px {theme['primary']}22;
        }}
        
        .nav-icon {{
            display: block;
            font-size: 22px;
            line-height: 26px;
            margin-bottom: 2px;
        }}
        
        .bottom-spacer {{
            height: 80px;
        }}
        
        /* Hide the fallback buttons visually but keep them functional */
        .nav-fallback-buttons {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            background: transparent;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0;
            padding: 0;
            height: 70px;
        }}
        
        .nav-fallback-buttons button {{
            opacity: 0 !important;
            height: 70px !important;
            border-radius: 0 !important;
            border: none !important;
            background: transparent !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    nav_html = """
    <div class="bottom-nav">
        {items}
    </div>
    <div class="bottom-spacer"></div>
    """

    def item(page: str, icon: str, label: str) -> str:
        is_active = "active" if active_page == page else ""
        return f"<div class='nav-item {is_active}' onclick=\"window.parent.postMessage({{type:'set-page',page:'{page}'}},'*')\">" \
               f"<span class='nav-icon'>{icon}</span>{label}</div>"

    items_html = "".join([
        item("home", "🏡", "Home"),
        item("scan", "🎥", "Scan"),
        item("vault", "📦", "Vault"),
        item("settings", "🛠️", "Settings"),
    ])

    st.markdown(nav_html.format(items=items_html), unsafe_allow_html=True)

    # Invisible clickable buttons overlay for actual navigation
    st.markdown('<div class="nav-fallback-buttons">', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (page, label) in zip(cols, [
        ("home", "🏡"),
        ("scan", "🎥"),
        ("vault", "📦"),
        ("settings", "🛠️"),
    ]):
        with col:
            if st.button(label, key=f"nav_btn_{page}", use_container_width=True, type="secondary"):
                st.session_state.active_page = page
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def get_active_page() -> str:
    return st.session_state.get("active_page", "home")
