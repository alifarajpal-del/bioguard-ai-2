"""
Dashboard view with modern card-based design.
Displays health metrics with rounded cards, soft shadows, and circular icons.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb
import pandas as pd
from datetime import datetime, timedelta
from ui_components.theme_wheel import get_current_theme


def render_dashboard() -> None:
    """Render modern dashboard with card-based design."""
    theme = get_current_theme()
    
    # Inject dashboard-specific CSS
    _inject_dashboard_css(theme)
    
    st.markdown("## 🏠 لوحة التحكم")
    _modern_stats_cards(theme)
    st.divider()
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        _health_score_trend(theme)
    with col2:
        _safety_breakdown(theme)
    
    st.divider()
    _activity_feed(theme)


def _inject_dashboard_css(theme: dict) -> None:
    """Inject modern card-based CSS for dashboard"""
    css = f"""
    <style>
        .stat-card {{
            background: var(--card-bg);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 8px 24px var(--primary)15;
            border: 2px solid var(--secondary);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--card-color) 0%, var(--card-color-light) 100%);
        }}
        
        .stat-card:hover {{
            transform: translateY(-6px);
            box-shadow: 0 16px 40px var(--primary)25;
            border-color: var(--primary);
        }}
        
        .icon-circle {{
            width: 64px;
            height: 64px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            margin-bottom: 16px;
            box-shadow: 0 8px 20px var(--card-color)30;
            background: linear-gradient(135deg, var(--card-color) 0%, var(--card-color-light) 100%);
        }}
        
        .stat-label {{
            color: var(--text);
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            opacity: 0.8;
        }}
        
        .stat-value {{
            color: var(--text);
            font-weight: 900;
            font-size: 36px;
            line-height: 1;
            margin-bottom: 8px;
        }}
        
        .stat-delta {{
            color: var(--text);
            font-size: 13px;
            font-weight: 600;
            opacity: 0.6;
        }}
        
        .activity-card {{
            background: var(--card-bg);
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 12px;
            border: 2px solid var(--secondary);
            box-shadow: 0 4px 12px var(--primary)10;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        
        .activity-card:hover {{
            transform: translateX(4px);
            box-shadow: 0 6px 20px var(--primary)20;
            border-color: var(--primary);
        }}
        
        .activity-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
        }}
        
        .chart-container {{
            background: var(--card-bg);
            border-radius: 20px;
            padding: 24px;
            border: 2px solid var(--secondary);
            box-shadow: 0 8px 24px var(--primary)15;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def _modern_stats_cards(theme: dict) -> None:
    """Display modern statistics cards with circular icons."""
    cols = st.columns(4, gap="medium")
    
    stats = [
        {
            "icon": "💚",
            "label": "Health Score",
            "value": "85",
            "delta": "+4 من الأسبوع الماضي",
            "color": "#10b981",
            "color_light": "#34d399"
        },
        {
            "icon": "🔬",
            "label": "Total Scans",
            "value": "142",
            "delta": "+12 اليوم",
            "color": "#3b82f6",
            "color_light": "#60a5fa"
        },
        {
            "icon": "⚠️",
            "label": "Warnings",
            "value": "3",
            "delta": "بحاجة للمراجعة",
            "color": "#f59e0b",
            "color_light": "#fbbf24"
        },
        {
            "icon": "✅",
            "label": "Safe Items",
            "value": "128",
            "delta": "90% معدل الأمان",
            "color": "#22c55e",
            "color_light": "#4ade80"
        },
    ]
    
    for col, stat in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div class="stat-card" style="--card-color: {stat['color']}; --card-color-light: {stat['color_light']};">
                    <div class="icon-circle">{stat['icon']}</div>
                    <div class="stat-label">{stat['label']}</div>
                    <div class="stat-value">{stat['value']}</div>
                    <div class="stat-delta">{stat['delta']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _health_score_trend(theme: dict) -> None:
    """Display health score trend chart with modern styling."""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📈 مؤشر الصحة")
    
    dates = pd.date_range(end=datetime.now(), periods=14, freq="D")
    scores = [72 + i % 6 + (i * 0.6) for i in range(len(dates))]
    
    # Convert hex color to RGBA with transparency
    rgb = hex_to_rgb(theme['primary'])
    fillcolor = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.2)"
    
    fig = go.Figure()
    fig.add_scatter(
        x=dates, 
        y=scores, 
        mode="lines+markers",
        line=dict(color=theme['primary'], width=4, shape='spline'),
        marker=dict(size=8, color=theme['accent'], line=dict(width=2, color='white')),
        fill='tozeroy',
        fillcolor=fillcolor
    )
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, color=theme['text']),
        yaxis=dict(showgrid=True, gridcolor=theme['secondary'], color=theme['text'])
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _safety_breakdown(theme: dict) -> None:
    """Display pie chart with modern styling."""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 🥧 توزيع الأمان")
    
    labels = ["آمن", "تحذير", "خطر"]
    values = [128, 11, 3]
    colors = ["#22c55e", "#f59e0b", "#ef4444"]
    
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color='white', width=3)),
        textfont=dict(size=14, color='white', family='Arial Black'),
        hovertemplate='<b>%{label}</b><br>%{value} عنصر<br>%{percent}<extra></extra>'
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=True,
        legend=dict(orientation="v", x=1, y=0.5),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _activity_feed(theme: dict) -> None:
    """Display recent activity with modern card design."""
    st.markdown("### 📋 النشاط الأخير")
    
    items = [
        {
            "time": "منذ ساعتين",
            "item": "شوفان عضوي",
            "status": "آمن",
            "score": 92,
            "icon": "✅",
            "color": "#22c55e"
        },
        {
            "time": "منذ 5 ساعات",
            "item": "مشروب طاقة",
            "status": "تحذير",
            "score": 45,
            "icon": "⚠️",
            "color": "#f59e0b"
        },
        {
            "time": "منذ يوم",
            "item": "سمك السلمون الطازج",
            "status": "آمن",
            "score": 88,
            "icon": "✅",
            "color": "#22c55e"
        },
        {
            "time": "منذ يومين",
            "item": "شوكولاتة داكنة",
            "status": "آمن",
            "score": 78,
            "icon": "✅",
            "color": "#10b981"
        },
    ]
    
    for entry in items:
        st.markdown(
            f"""
            <div class="activity-card">
                <div class="activity-icon" style="background: {entry['color']}20; color: {entry['color']};">
                    {entry['icon']}
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: 700; color: {theme['text']}; font-size: 16px; margin-bottom: 4px;">
                        {entry['item']}
                    </div>
                    <div style="font-size: 13px; color: {theme['text']}; opacity: 0.6;">
                        {entry['time']} • {entry['status']}
                    </div>
                </div>
                <div style="background: linear-gradient(135deg, {theme['primary']}, {theme['accent']});
                            color: white;
                            padding: 8px 16px;
                            border-radius: 12px;
                            font-weight: 800;
                            font-size: 18px;
                            box-shadow: 0 4px 12px {theme['primary']}30;">
                    {entry['score']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
