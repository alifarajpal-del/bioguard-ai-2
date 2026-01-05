"""Branding helpers for BioGuard AI logo usage across screens."""

import base64
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Optional

import streamlit as st
from PIL import Image

from ui_components.theme_wheel import get_current_theme


@lru_cache(maxsize=1)
def load_logo_image() -> Optional[Image.Image]:
    """Load branding logo from assets once."""
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if not logo_path.exists():
        return None
    try:
        return Image.open(logo_path)
    except Exception:
        return None


@lru_cache(maxsize=1)
def load_logo_base64() -> Optional[str]:
    """Return base64 PNG representation of the logo for HTML embedding."""
    img = load_logo_image()
    if not img:
        return None
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def render_brand_header(subtitle: str = "") -> None:
    """Render a top-of-page brand header with logo and subtitle."""
    theme = get_current_theme()
    logo_b64 = load_logo_base64()
    subtitle_html = f'<div class="brand-subtitle">{subtitle}</div>' if subtitle else ""

    css = f"""
    <style>
        .brand-header {{
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 12px 18px;
            border-radius: 18px;
            border: 1px solid {theme['secondary']};
            background: linear-gradient(135deg, {theme['card_bg']}CC, {theme['secondary']}33);
            box-shadow: 0 10px 30px {theme['primary']}26;
            margin: 6px 0 18px 0;
        }}
        .brand-logo {{
            width: 72px;
            height: 72px;
            object-fit: contain;
            border-radius: 16px;
            background: radial-gradient(circle, {theme['card_bg']} 0%, {theme['secondary']}55 100%);
            padding: 8px;
            box-shadow: 0 8px 20px {theme['primary']}26;
            border: 1px solid {theme['secondary']};
        }}
        .brand-emoji {{
            font-size: 48px;
            display: grid;
            place-items: center;
            width: 72px;
            height: 72px;
            border-radius: 16px;
            background: {theme['card_bg']};
            border: 1px solid {theme['secondary']};
            box-shadow: 0 8px 20px {theme['primary']}26;
        }}
        .brand-copy {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 4px;
        }}
        .brand-title {{
            font-size: 24px;
            font-weight: 900;
            color: {theme['text']};
            letter-spacing: 0.5px;
        }}
        .brand-subtitle {{
            font-size: 14px;
            font-weight: 700;
            color: {theme['secondary']};
            opacity: 0.9;
        }}
    </style>
    """

    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" alt="BioGuard AI logo" class="brand-logo" />'
        if logo_b64 else
        '<div class="brand-emoji">🛡️</div>'
    )

    st.markdown(css + f"""
    <div class="brand-header">
        {logo_html}
        <div class="brand-copy">
            <div class="brand-title">BioGuard AI</div>
            {subtitle_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_brand_watermark(label: str = "BioGuard AI") -> None:
    """Render a small floating brand watermark for immersive views like camera."""
    theme = get_current_theme()
    logo_b64 = load_logo_base64()

    css = f"""
    <style>
        .brand-watermark {{
            position: fixed;
            top: 12px;
            left: 12px;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border-radius: 14px;
            background: rgba(0, 0, 0, 0.60);
            color: white;
            z-index: 150;
            backdrop-filter: blur(14px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.45);
            border: 1px solid {theme['secondary']};
        }}
        .brand-watermark img {{
            width: 42px;
            height: 42px;
            object-fit: contain;
            border-radius: 10px;
            background: rgba(255,255,255,0.06);
            padding: 6px;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.1);
        }}
        .brand-watermark .wm-emoji {{
            width: 42px;
            height: 42px;
            display: grid;
            place-items: center;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            font-size: 26px;
        }}
        .brand-watermark .wm-text {{
            display: flex;
            flex-direction: column;
            gap: 2px;
            font-weight: 800;
            letter-spacing: 0.3px;
        }}
        .brand-watermark .wm-label {{
            font-size: 13px;
            color: rgba(255,255,255,0.92);
        }}
        .brand-watermark .wm-tag {{
            font-size: 11px;
            color: {theme['secondary']};
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }}
    </style>
    """

    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" alt="BioGuard AI logo" />'
        if logo_b64 else
        '<div class="wm-emoji">🛡️</div>'
    )

    st.markdown(css + f"""
    <div class="brand-watermark">
        {logo_html}
        <div class="wm-text">
            <div class="wm-label">{label}</div>
            <div class="wm-tag">live vision</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
