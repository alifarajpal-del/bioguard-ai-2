"""UI Kit: Consistent cards, badges, metrics, and component system.
Enterprise-grade design system for BioGuard AI.
"""

import streamlit as st
from typing import Optional, Literal
from contextlib import contextmanager


BadgeKind = Literal["info", "success", "warning", "danger", "muted", "primary"]


def inject_ui_kit_css() -> None:
    """Inject UI Kit CSS (scoped to component classes only)."""
    css = """
    <style>
        /* Badge components */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            line-height: 1.4;
        }
        
        .badge-info {
            background: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }
        
        .badge-success {
            background: rgba(16, 185, 129, 0.1);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        
        .badge-warning {
            background: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
        
        .badge-danger {
            background: rgba(239, 68, 68, 0.1);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }
        
        .badge-muted {
            background: rgba(107, 114, 128, 0.1);
            color: #6b7280;
            border: 1px solid rgba(107, 114, 128, 0.2);
        }
        
        .badge-primary {
            background: rgba(99, 102, 241, 0.1);
            color: #6366f1;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }
        
        /* Metric card */
        .metric-card {
            text-align: center;
            padding: 16px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric-label {
            font-size: 13px;
            color: #9ca3af;
            margin-bottom: 4px;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #1f2937;
            line-height: 1.2;
        }
        
        .metric-unit {
            font-size: 14px;
            color: #6b7280;
            margin-left: 4px;
        }
        
        /* Section title */
        .section-title {
            font-size: 18px;
            font-weight: 700;
            color: #1f2937;
            margin: 24px 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #e5e7eb;
        }
        
        /* Pills row */
        .pills-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 12px 0;
        }
        
        .pill {
            padding: 6px 14px;
            background: rgba(229, 231, 235, 0.5);
            color: #4b5563;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 500;
            border: 1px solid rgba(209, 213, 219, 0.5);
        }
        
        /* Info card */
        .info-card {
            padding: 16px;
            border-radius: 12px;
            border-left: 4px solid;
            margin: 12px 0;
        }
        
        .info-card.info {
            background: rgba(59, 130, 246, 0.05);
            border-color: #3b82f6;
        }
        
        .info-card.success {
            background: rgba(16, 185, 129, 0.05);
            border-color: #10b981;
        }
        
        .info-card.warning {
            background: rgba(245, 158, 11, 0.05);
            border-color: #f59e0b;
        }
        
        .info-card.danger {
            background: rgba(239, 68, 68, 0.05);
            border-color: #ef4444;
        }
        
        .info-card-title {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .info-card-body {
            font-size: 13px;
            line-height: 1.6;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def badge(text: str, kind: BadgeKind = "info", icon: Optional[str] = None) -> str:
    """Generate a badge HTML.
    
    Args:
        text: Badge text
        kind: Badge style variant
        icon: Optional emoji/icon to show before text
    
    Returns:
        HTML string for the badge
    """
    inject_ui_kit_css()
    icon_html = f'<span>{icon}</span>' if icon else ''
    return f'<span class="badge badge-{kind}">{icon_html}{text}</span>'


def metric(label: str, value: str, unit: str = "", delta: Optional[str] = None) -> None:
    """Display a metric card.
    
    Args:
        label: Metric label
        value: Metric value
        unit: Optional unit (e.g., "g", "%", "kcal")
        delta: Optional delta/change indicator
    """
    inject_ui_kit_css()
    
    unit_html = f'<span class="metric-unit">{unit}</span>' if unit else ''
    delta_html = f'<div style="font-size: 12px; color: #10b981; margin-top: 4px;">{delta}</div>' if delta else ''
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}{unit_html}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_title(text: str, icon: Optional[str] = None) -> None:
    """Display a section title with optional icon.
    
    Args:
        text: Section title text
        icon: Optional emoji/icon
    """
    inject_ui_kit_css()
    icon_html = f'{icon} ' if icon else ''
    st.markdown(f'<div class="section-title">{icon_html}{text}</div>', unsafe_allow_html=True)


def pills_row(items: list[str], interactive: bool = False) -> None:
    """Display a row of pill badges.
    
    Args:
        items: List of pill text items
        interactive: Whether pills should appear clickable (visual only)
    """
    inject_ui_kit_css()
    
    style_extra = 'cursor: pointer;' if interactive else ''
    pills_html = ''.join([
        f'<span class="pill" style="{style_extra}">{item}</span>'
        for item in items
    ])
    
    st.markdown(f'<div class="pills-row">{pills_html}</div>', unsafe_allow_html=True)


@contextmanager
def card(title: Optional[str] = None, icon: Optional[str] = None):
    """Context manager for a consistent card layout.
    
    Args:
        title: Optional card title
        icon: Optional icon/emoji for title
    
    Usage:
        with card(title="نتائج التحليل", icon="🔬"):
            st.write("Card content here")
    """
    inject_ui_kit_css()
    
    container = st.container()
    with container:
        if title:
            title_html = f'{icon} {title}' if icon else title
            st.markdown(f'<div style="font-size: 16px; font-weight: 600; margin-bottom: 12px; color: #1f2937;">{title_html}</div>', unsafe_allow_html=True)
        
        yield container


def info_card(
    title: str,
    body: str,
    kind: Literal["info", "success", "warning", "danger"] = "info",
    icon: Optional[str] = None
) -> None:
    """Display an information card with colored border.
    
    Args:
        title: Card title
        body: Card body text
        kind: Card style variant
        icon: Optional icon/emoji
    """
    inject_ui_kit_css()
    
    icon_html = f'{icon} ' if icon else ''
    
    st.markdown(f"""
    <div class="info-card {kind}">
        <div class="info-card-title">{icon_html}{title}</div>
        <div class="info-card-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def confidence_badge(confidence: float, label: str = "الثقة") -> str:
    """Generate a confidence badge with appropriate styling.
    
    Args:
        confidence: Confidence score (0.0 to 1.0)
        label: Label text
    
    Returns:
        HTML string for the badge
    """
    if confidence >= 0.85:
        kind = "success"
        icon = "✓"
    elif confidence >= 0.65:
        kind = "warning"
        icon = "⚠"
    else:
        kind = "danger"
        icon = "⚠"
    
    percentage = int(confidence * 100)
    return badge(f"{label}: {percentage}%", kind=kind, icon=icon)


def source_badge(source: str, cached: bool = False) -> str:
    """Generate a source badge.
    
    Args:
        source: Data source name
        cached: Whether the data is from cache
    
    Returns:
        HTML string for the badge
    """
    source_names = {
        "fooddata": "USDA",
        "openfoodfacts": "Open Food Facts",
        "edamam": "Edamam",
        "nutritionix": "Nutritionix",
    }
    
    display_name = source_names.get(source, source)
    icon = "📦" if cached else "🌐"
    
    return badge(f"{icon} {display_name}", kind="info" if not cached else "muted")
