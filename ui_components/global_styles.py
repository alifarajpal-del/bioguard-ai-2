"""Global styles and CSS tokens for consistent theming.
WCAG 2.2 compliant color contrast ratios.
"""

import streamlit as st
from ui_components.theme_wheel import get_current_theme


def inject_global_css():
    """Inject global CSS with theme support and utility classes."""
    theme = get_current_theme()
    st.markdown(f"""
    <style>
        /* ============== CSS Tokens (Variables) ============== */
        :root {{
            /* Theme colors */
            --bg: {theme['background']};
            --card-bg: {theme['card_bg']};
            --primary: {theme['primary']};
            --secondary: {theme['secondary']};
            --accent: {theme['accent']};
            --text: {theme['text']};
            
            /* Extended palette - WCAG 2.2 AA compliant */
            --surface: #f9fafb;
            --text-muted: #6b7280;
            --border: #e5e7eb;
            --primary-hover: #2563eb;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #3b82f6;
            
            /* Spacing */
            --spacing-xs: 4px;
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
            
            /* Radius */
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-full: 9999px;
            
            /* Shadows */
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
            --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
            
            /* Typography */
            --font-size-xs: 12px;
            --font-size-sm: 13px;
            --font-size-base: 14px;
            --font-size-lg: 16px;
            --font-size-xl: 18px;
            --font-size-2xl: 24px;
        }}
        
        /* Dark theme adjustments */
        @media (prefers-color-scheme: dark) {{
            :root {{
                --surface: #1f2937;
                --text-muted: #9ca3af;
                --border: #374151;
            }}
        }}
        
        /* Body styling - minimal changes */
        body, .stApp {{
            background-color: var(--bg) !important;
            color: var(--text) !important;
        }}
        
        /* ============== Utility Classes (scoped, no layout changes) ============== */
        
        /* Card components */
        .bg-card {{
            background: var(--card-bg, var(--surface));
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: var(--spacing-md);
            box-shadow: var(--shadow-sm);
        }}
        
        .card-title {{
            font-size: var(--font-size-lg);
            font-weight: 600;
            color: var(--text);
            margin-bottom: var(--spacing-sm);
        }}
        
        .card-body {{
            font-size: var(--font-size-base);
            color: var(--text);
            line-height: 1.6;
        }}
        
        /* Spacing utilities */
        .mt-sm {{ margin-top: var(--spacing-sm); }}
        .mt-md {{ margin-top: var(--spacing-md); }}
        .mt-lg {{ margin-top: var(--spacing-lg); }}
        
        .mb-sm {{ margin-bottom: var(--spacing-sm); }}
        .mb-md {{ margin-bottom: var(--spacing-md); }}
        .mb-lg {{ margin-bottom: var(--spacing-lg); }}
        
        .p-sm {{ padding: var(--spacing-sm); }}
        .p-md {{ padding: var(--spacing-md); }}
        .p-lg {{ padding: var(--spacing-lg); }}
        
        /* Text utilities */
        .text-muted {{ color: var(--text-muted); }}
        .text-center {{ text-align: center; }}
        .text-sm {{ font-size: var(--font-size-sm); }}
        .text-lg {{ font-size: var(--font-size-lg); }}
        .font-semibold {{ font-weight: 600; }}
        .font-bold {{ font-weight: 700; }}
        
        /* Divider */
        .divider {{
            height: 1px;
            background: var(--border);
            margin: var(--spacing-md) 0;
        }}
        
        /* Focus styles for accessibility (WCAG 2.2) */
        button:focus-visible,
        input:focus-visible,
        select:focus-visible,
        textarea:focus-visible {{
            outline: 2px solid var(--primary);
            outline-offset: 2px;
        }}
        
        /* Ensure sufficient contrast for links */
        a {{
            color: var(--primary);
            text-decoration: underline;
        }}
        
        a:hover {{
            color: var(--primary-hover, var(--primary));
        }}
    </style>
    """, unsafe_allow_html=True)

