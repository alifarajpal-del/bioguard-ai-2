"""Medical Vault view with modern grid-based card design."""

import streamlit as st
from datetime import datetime
from ui_components.theme_wheel import get_current_theme
from ui_components.error_ui import safe_render
from ui_components.micro_ux import skeleton_card, inject_skeleton_css
from ui_components.ui_kit import card, badge, inject_ui_kit_css
from utils.logging_setup import get_logger, log_user_action

logger = get_logger(__name__)


def render_vault() -> None:
    """Render medical vault with modern grid design"""
    safe_render(_render_vault_inner, context="vault")


def _render_vault_inner() -> None:
    # Inject CSS
    inject_skeleton_css()
    inject_ui_kit_css()
    
    theme = get_current_theme()
    
    # Back to home button
    if st.button("🔙 رجوع إلى الرئيسية", key="vault_back_home"):
        log_user_action(logger, 'navigate_home', {})
        st.session_state.current_page = "home"
        st.rerun()
    
    # Inject vault-specific CSS
    _inject_vault_css(theme)
    
    log_user_action(logger, 'vault_view', {})
    
    st.markdown("## 🗄️ المخزن الطبي")
    
    # Initialize medical history in session state
    if "medical_history" not in st.session_state:
        st.session_state.medical_history = []
    
    # Category Grid with skeleton loader
    with st.spinner(""):
        _render_category_grid(theme)
    
    st.divider()
    
    # Upload Section
    _upload_box(theme)
    
    st.divider()
    
    # Documents List
    _files_list(theme)


def _inject_vault_css(theme: dict) -> None:
    """Inject modern vault CSS with grid layout"""
    css = f"""
    <style>
        /* Category Card */
        .category-card {{
            background: {theme['card_bg']};
            border-radius: 20px;
            padding: 28px 20px;
            text-align: center;
            border: 2px solid {theme['secondary']};
            box-shadow: 0 8px 24px {theme['primary']}15;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
            min-height: 180px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }}
        
        .category-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--card-accent), var(--card-accent-light));
        }}
        
        .category-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 16px 40px {theme['primary']}25;
            border-color: {theme['primary']};
        }}
        
        .category-icon {{
            width: 72px;
            height: 72px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            margin: 0 auto 12px;
            background: linear-gradient(135deg, var(--card-accent), var(--card-accent-light));
            box-shadow: 0 8px 24px var(--card-accent)30;
            transition: all 0.3s ease;
        }}
        
        .category-card:hover .category-icon {{
            transform: scale(1.1) rotate(5deg);
            box-shadow: 0 12px 32px var(--card-accent)40;
        }}
        
        .category-title {{
            font-size: 16px;
            font-weight: 800;
            color: {theme['text']};
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .category-count {{
            font-size: 13px;
            color: {theme['text']};
            opacity: 0.7;
            font-weight: 600;
        }}
        
        .category-badge {{
            position: absolute;
            top: 12px;
            right: 12px;
            background: linear-gradient(135deg, var(--card-accent), var(--card-accent-light));
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 800;
            box-shadow: 0 4px 12px var(--card-accent)30;
        }}
        
        /* Upload Box */
        .upload-box {{
            background: linear-gradient(135deg, {theme['secondary']} 0%, {theme['background']} 100%);
            border: 3px dashed {theme['primary']};
            border-radius: 20px;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 8px 24px {theme['primary']}15;
            transition: all 0.3s ease;
        }}
        
        .upload-box:hover {{
            border-color: {theme['accent']};
            box-shadow: 0 12px 32px {theme['primary']}25;
            transform: scale(1.02);
        }}
        
        .upload-icon {{
            font-size: 64px;
            margin-bottom: 16px;
            animation: float 3s ease-in-out infinite;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        .upload-title {{
            font-weight: 800;
            color: {theme['primary']};
            font-size: 20px;
            margin-bottom: 8px;
        }}
        
        .upload-subtitle {{
            color: {theme['text']};
            font-size: 14px;
            opacity: 0.8;
            font-weight: 600;
        }}
        
        /* Document Card */
        .doc-card {{
            background: {theme['card_bg']};
            border: 2px solid {theme['secondary']};
            border-radius: 16px;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            box-shadow: 0 4px 16px {theme['primary']}10;
            transition: all 0.3s ease;
            margin-bottom: 12px;
        }}
        
        .doc-card:hover {{
            transform: translateX(4px);
            box-shadow: 0 8px 24px {theme['primary']}20;
            border-color: {theme['primary']};
        }}
        
        .doc-icon-wrapper {{
            width: 64px;
            height: 64px;
            border-radius: 16px;
            background: linear-gradient(135deg, {theme['primary']}, {theme['accent']});
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            box-shadow: 0 6px 20px {theme['primary']}30;
            flex-shrink: 0;
        }}
        
        .doc-info {{
            flex: 1;
        }}
        
        .doc-name {{
            font-weight: 700;
            color: {theme['text']};
            font-size: 16px;
            margin-bottom: 6px;
        }}
        
        .doc-meta {{
            color: {theme['text']};
            font-size: 13px;
            opacity: 0.6;
            font-weight: 500;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def _render_category_grid(theme: dict) -> None:
    """Render medical document categories in grid layout"""
    st.markdown("### 📂 فئات الملفات الطبية")
    
    # Calculate counts first
    total = len(st.session_state.medical_history)
    count_tests = sum(1 for doc in st.session_state.medical_history if "test" in doc.get("name", "").lower() or "lab" in doc.get("name", "").lower())
    count_reports = sum(1 for doc in st.session_state.medical_history if "report" in doc.get("name", "").lower())
    count_prescriptions = sum(1 for doc in st.session_state.medical_history if "prescription" in doc.get("name", "").lower() or "med" in doc.get("name", "").lower())
    count_vaccines = sum(1 for doc in st.session_state.medical_history if "vaccine" in doc.get("name", "").lower() or "vac" in doc.get("name", "").lower())
    count_xrays = sum(1 for doc in st.session_state.medical_history if "xray" in doc.get("name", "").lower() or "scan" in doc.get("name", "").lower())
    count_other = total - (count_tests + count_reports + count_prescriptions + count_vaccines + count_xrays)
    
    # Define categories with icons and colors
    categories = [
        {
            "id": "tests",
            "title": "التحاليل",
            "subtitle": "Lab Tests",
            "icon": "🧪",
            "color": "#3b82f6",
            "color_light": "#60a5fa",
            "count": count_tests
        },
        {
            "id": "reports",
            "title": "التقارير",
            "subtitle": "Medical Reports",
            "icon": "📋",
            "color": "#8b5cf6",
            "color_light": "#a78bfa",
            "count": count_reports
        },
        {
            "id": "prescriptions",
            "title": "الوصفات",
            "subtitle": "Prescriptions",
            "icon": "💊",
            "color": "#ec4899",
            "color_light": "#f472b6",
            "count": count_prescriptions
        },
        {
            "id": "vaccines",
            "title": "التطعيمات",
            "subtitle": "Vaccinations",
            "icon": "💉",
            "color": "#10b981",
            "color_light": "#34d399",
            "count": count_vaccines
        },
        {
            "id": "xrays",
            "title": "الأشعة",
            "subtitle": "X-Rays & Scans",
            "icon": "🏥",
            "color": "#f59e0b",
            "color_light": "#fbbf24",
            "count": count_xrays
        },
        {
            "id": "other",
            "title": "أخرى",
            "subtitle": "Other Documents",
            "icon": "📄",
            "color": "#64748b",
            "color_light": "#94a3b8",
            "count": count_other
        },
    ]
    
    # Create 3-column grid
    cols = st.columns(3, gap="large")
    
    for idx, category in enumerate(categories):
        with cols[idx % 3]:
            # Store selected category in session state if clicked
            category_key = f"category_{category['id']}"
            
            st.markdown(
                f"""
                <div class="category-card" style="--card-accent: {category['color']}; --card-accent-light: {category['color_light']};">
                    {f'<div class="category-badge">{category["count"]}</div>' if category["count"] > 0 else ''}
                    <div class="category-icon">{category['icon']}</div>
                    <div class="category-title">{category['title']}</div>
                    <div class="category-count">{category['subtitle']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Clickable button (invisible but functional)
            if st.button(
                f"عرض {category['title']}",
                key=category_key,
                use_container_width=True,
                type="secondary",
                help=f"عرض جميع ملفات {category['title']}"
            ):
                st.session_state.selected_category = category['id']
                st.toast(f"📂 عرض فئة: {category['title']}", icon="✨")


def _upload_box(theme: dict) -> None:
    """Render modern upload box"""
    st.markdown(
        f"""
        <div class="upload-box">
            <div class="upload-icon">🏥</div>
            <div class="upload-title">اسحب الملفات هنا</div>
            <div class="upload-subtitle">PDF, JPG, PNG • أشعة • تحاليل • وصفات</div>
            <div style="color: {theme['text']}; font-size: 12px; margin-top: 12px; opacity: 0.6;">حتى 10MB لكل ملف</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    file = st.file_uploader(
        "رفع مستند طبي",
        type=["pdf", "jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="vault_uploader",
        help="اختر ملف طبي للرفع"
    )
    
    if file:
        # Determine category and icon based on filename
        name_lower = file.name.lower()
        if "test" in name_lower or "lab" in name_lower or "تحليل" in name_lower:
            icon = "🧪"
            category = "tests"
        elif "prescription" in name_lower or "med" in name_lower or "وصفة" in name_lower:
            icon = "💊"
            category = "prescriptions"
        elif "vaccine" in name_lower or "vac" in name_lower or "تطعيم" in name_lower:
            icon = "💉"
            category = "vaccines"
        elif "xray" in name_lower or "scan" in name_lower or "أشعة" in name_lower:
            icon = "🏥"
            category = "xrays"
        elif "report" in name_lower or "تقرير" in name_lower:
            icon = "📋"
            category = "reports"
        else:
            icon = "📄"
            category = "other"
        
        # Save to session state
        file_info = {
            "name": file.name,
            "type": file.type,
            "category": category,
            "size": f"{file.size / 1024:.1f}KB" if file.size < 1024*1024 else f"{file.size / (1024*1024):.1f}MB",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "icon": icon,
            "data": file.getvalue()
        }
        
        # Check if not duplicate
        if not any(f["name"] == file.name for f in st.session_state.medical_history):
            st.session_state.medical_history.append(file_info)
            st.toast("✅ تمت الإضافة إلى ملفك الطبي!", icon="🏥")
            st.success(f"تم الرفع بنجاح: **{file.name}**")
            st.rerun()  # Refresh to update category counts
        else:
            st.warning(f"الملف **{file.name}** موجود بالفعل في المخزن.")


def _files_list(theme: dict) -> None:
    """Render documents list with modern card design"""
    st.markdown("### 📋 مستنداتك الطبية")
    
    if not st.session_state.medical_history:
        st.info("لا توجد مستندات حتى الآن. ابدأ برفع أول ملف طبي! 📤")
        return
    
    # Filter by selected category if any
    selected_category = st.session_state.get("selected_category", None)
    
    if selected_category:
        filtered_docs = [doc for doc in st.session_state.medical_history if doc.get("category") == selected_category]
        st.markdown(f"**عرض فئة: {selected_category.upper()}** ({len(filtered_docs)} ملف)")
        
        if st.button("🔙 عرض الكل", type="secondary"):
            st.session_state.selected_category = None
            st.rerun()
    else:
        filtered_docs = st.session_state.medical_history
        st.markdown(f"**{len(filtered_docs)} مستند في المخزن**")
    
    # Display documents using ui_kit cards
    for idx, doc in enumerate(filtered_docs):
        col1, col2, col3 = st.columns([5, 1, 1])
        
        with col1:
            st.markdown(card(
                title=f"{doc['icon']} {doc['name']}",
                content=f"{badge(doc['size'], 'secondary')} {badge(doc['date'], 'info')}"
            ), unsafe_allow_html=True)
        
        with col2:
            if st.button("👁️", key=f"view_{idx}", use_container_width=True, help="عرض"):
                st.info(f"عرض: {doc['name']}")
        
        with col3:
            if st.button("🗑️", key=f"del_{idx}", use_container_width=True, type="secondary", help="حذف"):
                # Find the actual index in the original list
                actual_idx = st.session_state.medical_history.index(doc)
                st.session_state.medical_history.pop(actual_idx)
                st.toast("🗑️ تم حذف المستند", icon="✅")
                st.rerun()
