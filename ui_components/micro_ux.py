"""Micro-UX components: skeletons, progress indicators, loading states.
Focused on immediate user feedback and perceived performance.
"""

import streamlit as st
from typing import List, Optional
from contextlib import contextmanager


def inject_skeleton_css() -> None:
    """Inject CSS for skeleton loading animations (scoped to skeleton classes only)."""
    css = """
    <style>
        /* Skeleton loading animation */
        @keyframes skeleton-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        
        .skeleton {
            background: linear-gradient(
                90deg,
                rgba(200, 200, 200, 0.2) 25%,
                rgba(200, 200, 200, 0.3) 50%,
                rgba(200, 200, 200, 0.2) 75%
            );
            background-size: 200% 100%;
            animation: skeleton-pulse 1.5s ease-in-out infinite;
            border-radius: 12px;
        }
        
        .skeleton-card {
            width: 100%;
            margin: 8px 0;
        }
        
        .skeleton-line {
            height: 16px;
            margin: 8px 0;
            border-radius: 4px;
        }
        
        .skeleton-circle {
            border-radius: 50%;
        }
        
        /* Step progress indicator */
        .step-progress {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 16px 0;
            direction: rtl;
        }
        
        .step {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .step-dot {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .step-dot.active {
            background: #10b981;
            color: white;
            box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
        }
        
        .step-dot.pending {
            background: #e5e7eb;
            color: #9ca3af;
        }
        
        .step-dot.completed {
            background: #3b82f6;
            color: white;
        }
        
        .step-label {
            font-size: 13px;
            color: #6b7280;
        }
        
        .step-label.active {
            color: #10b981;
            font-weight: 600;
        }
        
        .step-connector {
            width: 40px;
            height: 2px;
            background: #e5e7eb;
        }
        
        .step-connector.completed {
            background: #3b82f6;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def skeleton_card(height_px: int = 120, radius: int = 16) -> None:
    """Render a skeleton loading placeholder card.
    
    Args:
        height_px: Height of the skeleton card in pixels
        radius: Border radius in pixels
    """
    st.markdown(
        f'<div class="skeleton skeleton-card" style="height: {height_px}px; border-radius: {radius}px;"></div>',
        unsafe_allow_html=True
    )


def skeleton_lines(count: int = 3, widths: Optional[List[str]] = None) -> None:
    """Render skeleton text lines.
    
    Args:
        count: Number of skeleton lines to render
        widths: Optional list of width percentages (e.g., ["100%", "80%", "60%"])
    """
    if widths is None:
        widths = ["100%", "90%", "80%"][:count]
    
    for i in range(count):
        width = widths[i] if i < len(widths) else "100%"
        st.markdown(
            f'<div class="skeleton skeleton-line" style="width: {width};"></div>',
            unsafe_allow_html=True
        )


def step_progress(steps: List[str], active_index: int) -> None:
    """Render a step progress indicator.
    
    Args:
        steps: List of step labels (in order)
        active_index: Index of the currently active step (0-based)
    """
    html_parts = ['<div class="step-progress">']
    
    for i, label in enumerate(steps):
        # Determine step state
        if i < active_index:
            dot_class = "completed"
            label_class = ""
            icon = "✓"
        elif i == active_index:
            dot_class = "active"
            label_class = "active"
            icon = str(i + 1)
        else:
            dot_class = "pending"
            label_class = ""
            icon = str(i + 1)
        
        # Render step
        html_parts.append(f'''
            <div class="step">
                <div class="step-dot {dot_class}">{icon}</div>
                <span class="step-label {label_class}">{label}</span>
            </div>
        ''')
        
        # Add connector (except after last step)
        if i < len(steps) - 1:
            connector_class = "completed" if i < active_index else ""
            html_parts.append(f'<div class="step-connector {connector_class}"></div>')
    
    html_parts.append('</div>')
    st.markdown(''.join(html_parts), unsafe_allow_html=True)


@contextmanager
def with_loading(label: str = "جاري التحميل..."):
    """Context manager for loading states with spinner.
    
    Args:
        label: Loading message to display
    
    Usage:
        with with_loading("جاري تحليل الصورة..."):
            result = expensive_operation()
    """
    placeholder = st.empty()
    
    with placeholder.container():
        with st.spinner(label):
            yield placeholder
    
    placeholder.empty()


def show_processing_status(
    status: str,
    steps: Optional[List[str]] = None,
    active_step: int = 0,
    show_spinner: bool = True
) -> None:
    """Show a complete processing status with steps and message.
    
    Args:
        status: Current status message
        steps: Optional list of step names
        active_step: Currently active step index
        show_spinner: Whether to show a spinner
    """
    inject_skeleton_css()
    
    if steps:
        step_progress(steps, active_step)
    
    if show_spinner:
        st.markdown(f"""
        <div style="text-align: center; padding: 16px; color: #6b7280;">
            <div style="font-size: 15px; font-weight: 500;">{status}</div>
        </div>
        """, unsafe_allow_html=True)


def skeleton_grid(columns: int = 3, rows: int = 2, card_height: int = 120) -> None:
    """Render a grid of skeleton cards.
    
    Args:
        columns: Number of columns in the grid
        rows: Number of rows in the grid
        card_height: Height of each card in pixels
    """
    inject_skeleton_css()
    
    for _ in range(rows):
        cols = st.columns(columns)
        for col in cols:
            with col:
                skeleton_card(height_px=card_height)
