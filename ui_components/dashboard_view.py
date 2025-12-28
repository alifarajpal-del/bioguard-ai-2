"""Dashboard view with charts and stats."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta


def render_dashboard() -> None:
    st.markdown("## 🏠 Home Dashboard")
    _quick_stats()
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        _health_score_trend()
    with col2:
        _safety_breakdown()
    st.divider()
    _activity_feed()


def _quick_stats() -> None:
    cols = st.columns(4)
    stats = [
        ("📊 Health Score", "85", "+4 vs last week", "#10b981"),
        ("🧪 Scans", "142", "+12 today", "#3b82f6"),
        ("⚠️ Warnings", "3", "Review needed", "#f59e0b"),
        ("✅ Safe", "128", "90% safe rate", "#22c55e"),
    ]
    for col, (title, value, delta, color) in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, {color}18 0%, {color}05 100%);
                            border-left: 4px solid {color}; padding: 14px; border-radius: 12px;">
                    <div style="color:#475569;font-weight:700;font-size:13px;">{title}</div>
                    <div style="color:{color};font-weight:800;font-size:26px;">{value}</div>
                    <div style="color:#94a3b8;font-size:12px;">{delta}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _health_score_trend() -> None:
    st.markdown("### 📈 Health Score")
    dates = pd.date_range(end=datetime.now(), periods=14, freq="D")
    scores = [72 + i % 6 + (i * 0.6) for i in range(len(dates))]
    fig = go.Figure()
    fig.add_scatter(x=dates, y=scores, mode="lines+markers", line=dict(color="#3b82f6", width=3))
    fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _safety_breakdown() -> None:
    st.markdown("### 🥧 Safety Breakdown")
    labels = ["Safe", "Warning", "Danger"]
    values = [128, 11, 3]
    colors = ["#22c55e", "#f59e0b", "#ef4444"]
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.55, marker=dict(colors=colors)))
    fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _activity_feed() -> None:
    st.markdown("### 📋 Recent Activity")
    items = [
        {"time": "2h", "item": "Organic Oats", "status": "✅ Safe", "score": 92},
        {"time": "5h", "item": "Energy Drink", "status": "⚠️ Warning", "score": 45},
        {"time": "1d", "item": "Fresh Salmon", "status": "✅ Safe", "score": 88},
    ]
    for entry in items:
        badge = f"<span style='background:#3b82f6;color:white;padding:4px 10px;border-radius:12px;font-weight:700;'>{entry['score']}</span>" if entry.get("score") else ""
        st.markdown(
            f"""
            <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-weight:700;color:#0f172a;">{entry['item']} • {entry['status']}</div>
                    <div style="font-size:12px;color:#64748b;">{entry['time']} ago</div>
                </div>
                <div>{badge}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
