"""Bottom navigation bar component."""

import streamlit as st
from ui_components.theme_wheel import get_current_theme


def render_bottom_navigation():
    theme = get_current_theme()
    active_page = st.session_state.get("active_page", "home")

    css = f"""
    <style>
        .bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 4px;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(12px);
            padding: 10px 14px 16px 14px;
            box-shadow: 0 -6px 24px rgba(0,0,0,0.08);
            z-index: 9999;
        }}
        .nav-item {{
            text-align: center;
            padding: 10px 6px;
            border-radius: 12px;
            color: #475569;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }}
        .nav-item.active {{
            color: {theme['primary']};
            border-color: {theme['primary']}33;
            background: {theme['primary']}12;
            box-shadow: 0 6px 16px {theme['primary']}22;
        }}
        .nav-icon {{
            display:block;
            font-size: 22px;
            line-height: 24px;
        }}
        .bottom-spacer {{ height: 90px; }}
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

    # Fallback buttons for Streamlit state (since JS postMessage cannot set state directly)
    cols = st.columns(4)
    for col, (page, label) in zip(cols, [
        ("home", "🏡 Home"),
        ("scan", "🎥 Scan"),
        ("vault", "📦 Vault"),
        ("settings", "🛠️ Settings"),
    ]):
        with col:
            if st.button(label, key=f"nav_btn_{page}", use_container_width=True):
                st.session_state.active_page = page
                st.rerun()


def get_active_page() -> str:
    return st.session_state.get("active_page", "home")
