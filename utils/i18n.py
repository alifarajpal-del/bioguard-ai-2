# utils/i18n.py
"""Simple i18n layer for multi-language support."""
import streamlit as st

_STRINGS = {
    "en": {
        "app_name": "BioGuard AI",
        "dashboard_title": "Dashboard",
        "scan_title": "Scan",
        "vault_title": "Vault",
        "settings_title": "Settings",

        "unexpected_error": "An unexpected error occurred.",
        "retry": "Retry",
        "go_home": "Home",
        "report_issue": "Report issue",

        "recent_scans": "Recent Scans",
        "analysis_complete": "Analysis Complete",
        "health_score": "Health Score",
        "nutrition_facts": "Nutrition Facts",
        "why_score": "Why this score?",
        "warnings": "Warnings",
        "recommendations": "Recommendations",
        "save_to_vault": "Save to Vault",
        "source": "Source",
        "confidence": "Confidence",
        "cached": "Cached",
        "total_scans": "Total Scans",
        "safe_items": "Safe Items",
        "medical_vault": "Medical Vault",
        "your_documents": "Your Medical Documents",
        "no_documents": "No documents yet. Start by uploading your first medical file! 📤",
        "upload": "Upload",
        "upload_file": "Upload a file",
        "view_all": "View All",
        "category": "Category",
        "prescriptions": "Prescriptions",
        "lab_reports": "Lab Reports",
        "vaccinations": "Vaccinations",
        "xrays": "X-Rays & Scans",
        "other": "Other Documents",
    },
    "ar": {
        "app_name": "BioGuard AI",
        "dashboard_title": "لوحة التحكم",
        "scan_title": "الكاميرا",
        "vault_title": "المخزن",
        "settings_title": "الإعدادات",

        "unexpected_error": "حدث خطأ غير متوقع.",
        "retry": "إعادة المحاولة",
        "go_home": "الصفحة الرئيسية",
        "report_issue": "تقرير المشكلة",

        "recent_scans": "آخر عمليات الفحص",
        "analysis_complete": "اكتمل التحليل",
        "health_score": "مؤشر الصحة",
        "nutrition_facts": "القيم الغذائية",
        "why_score": "لماذا هذه النتيجة؟",
        "warnings": "تحذيرات",
        "recommendations": "توصيات",
        "save_to_vault": "حفظ في المخزن",
        "source": "المصدر",
        "confidence": "الثقة",
        "cached": "من الذاكرة",
        "total_scans": "إجمالي الفحوصات",
        "safe_items": "عناصر آمنة",
        "medical_vault": "المخزن الطبي",
        "your_documents": "مستنداتك الطبية",
        "no_documents": "لا توجد مستندات حتى الآن. ابدأ برفع أول ملف طبي! 📤",
        "upload": "رفع",
        "upload_file": "رفع ملف",
        "view_all": "عرض الكل",
        "category": "الفئة",
        "prescriptions": "الروشتات",
        "lab_reports": "التحاليل الطبية",
        "vaccinations": "التطعيمات",
        "xrays": "الأشعة",
        "other": "أخرى",
    },
}


def get_lang() -> str:
    """Get current language, default to English."""
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    return st.session_state.lang


def set_lang(lang: str) -> None:
    """Set language to 'en' or 'ar'."""
    st.session_state.lang = "ar" if lang == "ar" else "en"


def t(key: str) -> str:
    """Translate key to current language."""
    lang = get_lang()
    return _STRINGS.get(lang, _STRINGS["en"]).get(key, _STRINGS["en"].get(key, key))
