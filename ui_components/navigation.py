"""Modern bottom navigation bar with iOS-style design."""

import streamlit as st
from ui_components.theme_wheel import get_current_theme
from ui_components.router import ensure_nav_state, go_to


def render_bottom_navigation():
    """Render modern bottom navigation with circular buttons and labels"""
    ensure_nav_state()
    theme = get_current_theme()
    active_page = st.session_state.get("current_page", "home")

    # Modern Bottom Navigation CSS with theme colors
    css = f"""
    <style>
        /* Modern Bottom Navigation Container */
        .nav-dock {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: {theme['card_bg']};
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border-top: 2px solid {theme['secondary']};
            z-index: 99999;
            padding: 12px 0 16px 0;
            box-shadow: 0 -8px 24px {theme['primary']}15;
        }}
        
        /* Navigation Container */
        .nav-items-container {{
            display: flex;
            justify-content: space-around;
            align-items: center;
            max-width: 600px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        /* Navigation Item */
        .nav-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 8px 16px;
            border-radius: 16px;
            position: relative;
        }}
        
        .nav-item:hover {{
            transform: translateY(-4px);
            background: {theme['secondary']};
        }}
        
        .nav-item.active {{
            background: linear-gradient(135deg, {theme['primary']}15, {theme['accent']}15);
        }}
        
        /* Circular Icon Button */
        .nav-icon {{
            width: 52px;
            height: 52px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            background: {theme['secondary']};
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px {theme['primary']}10;
        }}
        
        .nav-item:hover .nav-icon {{
            transform: scale(1.1);
            box-shadow: 0 6px 20px {theme['primary']}25;
            border-color: {theme['primary']}40;
        }}
        
        .nav-item.active .nav-icon {{
            background: linear-gradient(135deg, {theme['primary']}, {theme['accent']});
            box-shadow: 0 8px 24px {theme['primary']}40;
            transform: scale(1.05);
            border-color: {theme['primary']};
        }}
        
        /* Navigation Label */
        .nav-label {{
            font-size: 11px;
            font-weight: 700;
            color: {theme['text']};
            opacity: 0.6;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
        }}
        
        .nav-item.active .nav-label {{
            opacity: 1;
            color: {theme['primary']};
            font-weight: 800;
        }}
        
        /* Active Indicator Dot */
        .nav-indicator {{
            position: absolute;
            top: 4px;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: {theme['primary']};
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .nav-item.active .nav-indicator {{
            opacity: 1;
        }}
        
        /* Bottom Spacer */
        .bottom-spacer {{
            height: 90px;
        }}
        
        /* Hide default Streamlit button styling in nav */
        .nav-dock .stButton > button {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            width: 100% !important;
            height: auto !important;
        }}
        
        .nav-dock .stButton > button:hover {{
            background: transparent !important;
            border: none !important;
            transform: none !important;
        }}

        /* Swipe handle hint */
        .swipe-handle {{
            position: fixed;
            bottom: 90px;
            left: 0;
            right: 0;
            height: 50px;
            background: rgba(0,0,0,0.1);
            border-top: 1px solid rgba(255,255,255,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: {theme['text']};
            z-index: 99998;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.markdown('<div class="bottom-spacer"></div>', unsafe_allow_html=True)

    st.markdown('<div class="swipe-handle">اسحب لليسار للتالي • اسحب لليمين للرجوع</div>', unsafe_allow_html=True)

    # Bottom Navigation Bar
    nav_container = st.container()
    with nav_container:
        st.markdown('<div class="nav-dock">', unsafe_allow_html=True)
        
        nav_items = [
            ("dashboard", "🏠", "الرئيسية"),
            ("scan", "📸", "الكاميرا"),
            ("vault", "🗄️", "المخزن"),
            ("settings", "⚙️", "الإعدادات"),
        ]
        
        # Create navigation using streamlit buttons
        cols = st.columns(4)
        for col, (page, icon, label) in zip(cols, nav_items):
            with col:
                is_active = page == active_page
                button_type = "primary" if is_active else "secondary"
                
                if st.button(
                    f"{icon}\n{label}",
                    key=f"nav_{page}",
                    use_container_width=True,
                    type=button_type,
                    help=f"انتقل إلى {label}"
                ):
                    go_to(page)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Touch swipe listener injected once per render (left/right)
        swipe_placeholder = st.empty()
        try:
            swipe_placeholder.components.v1.html(
                """
                <script>
                    let startX = null;
                    let startY = null;
                    document.addEventListener('touchstart', function(e) {
                        startX = e.touches[0].clientX;
                        startY = e.touches[0].clientY;
                    });
                    document.addEventListener('touchend', function(e) {
                        if (startX === null || startY === null) return;
                        const endX = e.changedTouches[0].clientX;
                        const endY = e.changedTouches[0].clientY;
                        const deltaX = endX - startX;
                        const deltaY = endY - startY;
                        if (Math.abs(deltaX) > 60 && Math.abs(deltaY) < 50) {
                            if (deltaX < 0) {
                                window.parent.postMessage({type: 'streamlit:setComponentValue', key: 'swipe_next', value: true}, '*');
                            } else {
                                window.parent.postMessage({type: 'streamlit:setComponentValue', key: 'swipe_prev', value: true}, '*');
                            }
                        }
                        startX = null;
                        startY = null;
                    });
                </script>
                """,
                height=0,
            )
        except Exception:
            st.warning("Swipe navigation unavailable right now.")


def get_active_page() -> str:
    """Get the currently active page"""
    return st.session_state.get("current_page", "dashboard")
