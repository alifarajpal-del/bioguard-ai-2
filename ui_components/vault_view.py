"""Vault view for medical documents."""

import streamlit as st


def render_vault() -> None:
    st.markdown("## 📁 Vault")
    st.markdown("Securely store medical records and uploads.")

    _upload_box()
    st.divider()
    _files_list()


def _upload_box() -> None:
    st.markdown(
        """
        <div style="border:2px dashed #cbd5e1;border-radius:14px;padding:22px;text-align:center;background:linear-gradient(135deg,#f8fafc 0%,#e2e8f0 100%);">
            <div style="font-size:32px;">📤</div>
            <div style="font-weight:700;color:#0f172a;">Upload medical files</div>
            <div style="color:#64748b;font-size:13px;">PDF / JPG / PNG up to 10MB</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    file = st.file_uploader("Upload", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")
    if file:
        st.success(f"Uploaded: {file.name}")


def _files_list() -> None:
    st.markdown("### Your Documents")
    docs = [
        {"name": "Blood Test - Dec 2025", "type": "Lab", "size": "2.1MB", "icon": "🧪"},
        {"name": "Cholesterol Meds", "type": "Prescription", "size": "150KB", "icon": "💊"},
        {"name": "Annual Summary", "type": "Report", "size": "1.8MB", "icon": "📄"},
    ]
    for doc in docs:
        st.markdown(
            f"""
            <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:10px;display:flex;gap:12px;align-items:center;">
                <div style="width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#3b82f6 0%,#8b5cf6 100%);color:white;display:flex;align-items:center;justify-content:center;font-size:22px;">{doc['icon']}</div>
                <div style="flex:1;">
                    <div style="font-weight:700;color:#0f172a;">{doc['name']}</div>
                    <div style="color:#64748b;font-size:12px;">{doc['type']} • {doc['size']}</div>
                </div>
                <div style="display:flex;gap:8px;">
                    <button style="background:#3b82f6;color:white;border:none;padding:6px 12px;border-radius:10px;cursor:pointer;font-weight:700;">View</button>
                    <button style="background:#ef4444;color:white;border:none;padding:6px 12px;border-radius:10px;cursor:pointer;font-weight:700;">Delete</button>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
