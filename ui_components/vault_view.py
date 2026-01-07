"""Medical Vault view with modern grid-based card design."""

from datetime import datetime

import streamlit as st

from ui_components.error_ui import safe_render
from ui_components.micro_ux import inject_skeleton_css, skeleton_card
from ui_components.theme_wheel import get_current_theme
from ui_components.ui_kit import badge, card, inject_ui_kit_css
from utils.i18n import get_lang, t
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
        log_user_action(logger, "navigate_home", {})
        st.session_state.current_page = "home"
        st.rerun()

    # Inject vault-specific CSS
    _inject_vault_css(theme)

    log_user_action(logger, "vault_view", {})

    # Page header with icon
    st.markdown("""
    <div style="
        padding: 24px 0;
        border-bottom: 2px solid #E2E8F0;
        margin-bottom: 24px;
    ">
        <h1 style="
            margin: 0;
            color: #0F172A;
            font-size: 28px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            🗄️ <span>{}</span>
        </h1>
        <p style="
            margin: 8px 0 0 0;
            color: #64748B;
            font-size: 14px;
        ">Secure Medical Document Archive</p>
    </div>
    """.format(t('vault_title')), unsafe_allow_html=True)

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
    _files_list()


def _inject_vault_css(theme: dict) -> None:
    """Inject clean medical-grade vault CSS"""
    css = f"""
    <style>
        /* Category Card - Clean Professional */
        .category-card {{
            background: {theme['card_bg']};
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            border: 2px solid {theme['secondary']};
            box-shadow: 0 2px 8px {theme['primary']}10;
            transition: all 0.2s ease;
            cursor: pointer;
            min-height: 160px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }}
        
        .category-card:hover {{
            box-shadow: 0 4px 16px {theme['primary']}20;
            border-color: {theme['primary']};
            transform: translateY(-2px);
        }}
        
        .category-icon {{
            width: 64px;
            height: 64px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            margin: 0 auto 8px;
            background: {theme['secondary']};
            transition: all 0.2s ease;
        }}
        
        .category-card:hover .category-icon {{
            background: {theme['primary']}15;
            transform: scale(1.05);
        }}
        
        .category-title {{
            font-size: 16px;
            font-weight: 700;
            color: {theme['text']};
            margin-bottom: 4px;
        }}
        
        .category-count {{
            font-size: 13px;
            color: {theme['text']};
            opacity: 0.6;
            font-weight: 500;
        }}
        
        .category-badge {{
            position: absolute;
            top: 12px;
            right: 12px;
            background: {theme['primary']};
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 700;
        }}
        
        /* Document Card - Clean */
        .doc-card {{
            background: {theme['card_bg']};
            border: 1px solid {theme['secondary']};
            border-radius: 8px;
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 16px;
            box-shadow: 0 1px 3px {theme['primary']}08;
            transition: all 0.2s ease;
            margin-bottom: 8px;
        }}
        
        .doc-card:hover {{
            box-shadow: 0 2px 8px {theme['primary']}15;
            border-color: {theme['primary']};
        }}
        
        .doc-icon-wrapper {{
            width: 56px;
            height: 56px;
            border-radius: 8px;
            background: {theme['secondary']};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            flex-shrink: 0;
        }}
        
        .doc-info {{
            flex: 1;
        }}
        
        .doc-name {{
            font-weight: 600;
            color: {theme['text']};
            font-size: 15px;
            margin-bottom: 4px;
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
    st.markdown("""
    <h3 style="
        font-size: 18px;
        font-weight: 600;
        color: #0F172A;
        margin-bottom: 16px;
    ">📂 فئات الملفات الطبية</h3>
    """, unsafe_allow_html=True)

    # Calculate counts first
    total = len(st.session_state.medical_history)
    count_tests = sum(
        1
        for doc in st.session_state.medical_history
        if "test" in doc.get("name", "").lower() or "lab" in doc.get("name", "").lower()
    )
    count_reports = sum(
        1
        for doc in st.session_state.medical_history
        if "report" in doc.get("name", "").lower()
    )
    count_prescriptions = sum(
        1
        for doc in st.session_state.medical_history
        if "prescription" in doc.get("name", "").lower()
        or "med" in doc.get("name", "").lower()
    )
    count_vaccines = sum(
        1
        for doc in st.session_state.medical_history
        if "vaccine" in doc.get("name", "").lower()
        or "vac" in doc.get("name", "").lower()
    )
    count_xrays = sum(
        1
        for doc in st.session_state.medical_history
        if "xray" in doc.get("name", "").lower()
        or "scan" in doc.get("name", "").lower()
    )
    count_other = total - (
        count_tests + count_reports + count_prescriptions + count_vaccines + count_xrays
    )

    # Define categories with icons and colors
    categories = [
        {
            "id": "tests",
            "title": "التحاليل",
            "subtitle": "Lab Tests",
            "icon": "🧪",
            "color": "#3b82f6",
            "color_light": "#60a5fa",
            "count": count_tests,
        },
        {
            "id": "reports",
            "title": "التقارير",
            "subtitle": "Medical Reports",
            "icon": "📋",
            "color": "#8b5cf6",
            "color_light": "#a78bfa",
            "count": count_reports,
        },
        {
            "id": "prescriptions",
            "title": "الوصفات",
            "subtitle": "Prescriptions",
            "icon": "💊",
            "color": "#ec4899",
            "color_light": "#f472b6",
            "count": count_prescriptions,
        },
        {
            "id": "vaccines",
            "title": "التطعيمات",
            "subtitle": "Vaccinations",
            "icon": "💉",
            "color": "#10b981",
            "color_light": "#34d399",
            "count": count_vaccines,
        },
        {
            "id": "xrays",
            "title": "الأشعة",
            "subtitle": "X-Rays & Scans",
            "icon": "🏥",
            "color": "#f59e0b",
            "color_light": "#fbbf24",
            "count": count_xrays,
        },
        {
            "id": "other",
            "title": "أخرى",
            "subtitle": "Other Documents",
            "icon": "📄",
            "color": "#64748b",
            "color_light": "#94a3b8",
            "count": count_other,
        },
    ]

    # Create 3-column grid
    cols = st.columns(3, gap="large")

    for idx, category in enumerate(categories):
        with cols[idx % 3]:
            # Store selected category in session state if clicked
            category_key = f"category_{category['id']}"

            # Use clean Streamlit button with badge
            badge = f" ({category['count']})" if category['count'] > 0 else ""
            button_label = f"{category['icon']} {category['title']}{badge}"
            
            if st.button(
                button_label,
                key=category_key,
                use_container_width=True,
                type="secondary",
                help=category['subtitle'],
            ):
                st.session_state.selected_category = category["id"]
                st.toast(f"📂 عرض فئة: {category['title']}", icon="✨")


def _upload_box(theme: dict) -> None:
    """Render professional upload box"""
    st.markdown("""
    <div style="
        background: #F8FAFC;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 32px;
        text-align: center;
        margin: 20px 0;
    ">
        <div style="font-size: 48px; margin-bottom: 12px;">🏥</div>
        <h3 style="margin: 0 0 8px 0; color: #0F172A; font-size: 18px; font-weight: 600;">اسحب الملفات هنا</h3>
        <p style="margin: 0; color: #64748B; font-size: 14px;">PDF, JPG, PNG • أشعة • تحاليل • وصفات • حتى 10MB</p>
    </div>
    """, unsafe_allow_html=True)

    file = st.file_uploader(
        "رفع مستند طبي",
        type=["pdf", "jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="vault_uploader",
        help="اختر ملف طبي للرفع",
    )

    if file:
        # Determine category and icon based on filename
        name_lower = file.name.lower()
        if "test" in name_lower or "lab" in name_lower or "تحليل" in name_lower:
            icon = "🧪"
            category = "tests"
        elif (
            "prescription" in name_lower or "med" in name_lower or "وصفة" in name_lower
        ):
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
            "size": (
                f"{file.size / 1024:.1f}KB"
                if file.size < 1024 * 1024
                else f"{file.size / (1024*1024):.1f}MB"
            ),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "icon": icon,
            "data": file.getvalue(),
        }

        # Check if not duplicate
        if not any(f["name"] == file.name for f in st.session_state.medical_history):
            st.session_state.medical_history.append(file_info)
            st.toast("✅ تمت الإضافة إلى ملفك الطبي!", icon="🏥")
            st.success(f"تم الرفع بنجاح: **{file.name}**")
            st.rerun()  # Refresh to update category counts
        else:
            st.warning(f"الملف **{file.name}** موجود بالفعل في المخزن.")


def _files_list() -> None:
    """Render documents list with clean card design"""
    st.markdown("""
    <h3 style="
        font-size: 18px;
        font-weight: 600;
        color: #0F172A;
        margin: 24px 0 16px 0;
    ">📋 مستنداتك</h3>
    """, unsafe_allow_html=True)

    if not st.session_state.medical_history:
        st.info(t("no_documents"))
        return

    # Filter by selected category if any
    selected_category = st.session_state.get("selected_category", None)

    if selected_category:
        filtered_docs = [
            doc
            for doc in st.session_state.medical_history
            if doc.get("category") == selected_category
        ]
        st.markdown(
            f"**{t('category')}: {selected_category.upper()}** ({len(filtered_docs)} files)"
        )

        if st.button(f"🔙 {t('view_all')}", type="secondary"):
            st.session_state.selected_category = None
            st.rerun()
    else:
        filtered_docs = st.session_state.medical_history
        st.markdown(f"**{len(filtered_docs)} documents**")

    # Display documents using clean native Streamlit
    for idx, doc in enumerate(filtered_docs):
        col1, col2, col3 = st.columns([5, 1, 1])

        with col1:
            # Use ui_kit card for clean display
            doc_icon = doc.get("icon", "📄")
            doc_name = doc.get("name", "Unknown")
            doc_size = doc.get("size", "N/A")
            doc_date = doc.get("date", "N/A")

            st.markdown(
                card(
                    title=f"{doc_icon} {doc_name}",
                    content=f"{doc_size} • {doc_date}",
                    style="compact",
                ),
                unsafe_allow_html=True,
            )

        with col2:
            if st.button("👁️", key=f"view_{idx}", use_container_width=True, help="View"):
                st.info(f"Viewing: {doc.get('name', 'Unknown')}")

        with col3:
            if st.button(
                "🗑️",
                key=f"del_{idx}",
                use_container_width=True,
                type="secondary",
                help="Delete",
            ):
                # Find the actual index in the original list
                actual_idx = st.session_state.medical_history.index(doc)
                st.session_state.medical_history.pop(actual_idx)
                st.toast("🗑️ تم حذف المستند", icon="✅")
                st.rerun()
