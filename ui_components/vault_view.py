"""Vault view for medical documents."""

import streamlit as st
from datetime import datetime


def render_vault() -> None:
    st.markdown("## 📁 Medical Vault")
    st.markdown("Securely store and manage your medical records, X-rays, and lab results.")

    # Initialize medical history in session state
    if "medical_history" not in st.session_state:
        st.session_state.medical_history = []

    _upload_box()
    st.divider()
    _files_list()


def _upload_box() -> None:
    st.markdown(
        """
        <div style="border:2px dashed #3b82f6;border-radius:16px;padding:32px;text-align:center;background:linear-gradient(135deg,#dbeafe 0%,#eff6ff 100%);box-shadow:0 4px 12px rgba(59,130,246,0.15);">
            <div style="font-size:48px;margin-bottom:12px;">🏥</div>
            <div style="font-weight:700;color:#1e3a8a;font-size:18px;margin-bottom:8px;">Drag & Drop Medical Records</div>
            <div style="color:#3b82f6;font-size:14px;">PDF, JPG, PNG • X-Rays • Lab Results • Prescriptions</div>
            <div style="color:#64748b;font-size:12px;margin-top:8px;">Up to 10MB per file</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    file = st.file_uploader(
        "Upload Medical Document",
        type=["pdf", "jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="vault_uploader"
    )
    
    if file:
        # Save to session state
        file_info = {
            "name": file.name,
            "type": file.type,
            "size": f"{file.size / 1024:.1f}KB" if file.size < 1024*1024 else f"{file.size / (1024*1024):.1f}MB",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "icon": "🧪" if "lab" in file.name.lower() else "💊" if "prescription" in file.name.lower() or "med" in file.name.lower() else "📄",
            "data": file.getvalue()
        }
        
        # Check if not duplicate
        if not any(f["name"] == file.name for f in st.session_state.medical_history):
            st.session_state.medical_history.append(file_info)
            st.toast("✅ Added to your Medical Profile!", icon="🏥")
            st.success(f"Successfully uploaded: **{file.name}**")
        else:
            st.warning(f"File **{file.name}** already exists in your vault.")


def _files_list() -> None:
    st.markdown("### 📋 Your Medical Documents")
    
    if not st.session_state.medical_history:
        st.info("No documents uploaded yet. Start by uploading your first medical record above! 📤")
        return
    
    st.markdown(f"**{len(st.session_state.medical_history)} document(s) in your vault**")
    
    for idx, doc in enumerate(st.session_state.medical_history):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(
                f"""
                <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:16px;display:flex;gap:12px;align-items:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                    <div style="width:52px;height:52px;border-radius:12px;background:linear-gradient(135deg,#3b82f6 0%,#8b5cf6 100%);color:white;display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 4px 12px rgba(59,130,246,0.3);">{doc['icon']}</div>
                    <div style="flex:1;">
                        <div style="font-weight:700;color:#0f172a;font-size:15px;">{doc['name']}</div>
                        <div style="color:#64748b;font-size:12px;margin-top:4px;">{doc['size']} • {doc['date']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with col2:
            if st.button("👁️ View", key=f"view_{idx}", use_container_width=True):
                st.info(f"Viewing: {doc['name']}")
        
        with col3:
            if st.button("🗑️ Delete", key=f"del_{idx}", use_container_width=True, type="secondary"):
                st.session_state.medical_history.pop(idx)
                st.toast("🗑️ Document deleted", icon="✅")
                st.rerun()
            </div>
            """,
            unsafe_allow_html=True,
        )
