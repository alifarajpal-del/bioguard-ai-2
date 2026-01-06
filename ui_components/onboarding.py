"""Simple onboarding flow shown once per user session - 2 screens only."""

import streamlit as st
from utils.translations import get_text
from ui_components.ui_kit import inject_ui_kit_css


def get_screens(lang: str) -> list:
    """Get onboarding screens in the specified language (2 screens only)."""
    return [
        {
            "title": "حماية صحتك تبدأ من هنا",
            "body": """
            **BioGuard AI** يساعدك على:
            - 📊 تحليل المنتجات الغذائية فوراً
            - ⚠️ اكتشاف المخاطر الصحية والحساسية
            - 🎯 الحصول على توصيات مخصصة
            - 📱 مسح الباركود أو التقاط الصور
            """,
            "icon": "🛡️",
        },
        {
            "title": "خصوصيتك أولويتنا",
            "body": """
            **نحن نلتزم بـ:**
            - 🔒 بياناتك محمية ومشفرة بالكامل
            - 🚫 لا نبيع معلوماتك الشخصية أبداً
            - ⚡ تحليل سريع وفوري بدون انتظار
            
            **كيف تبدأ:**
            1️⃣ وجّه الكاميرا نحو الباركود أو المنتج
            2️⃣ انتظر التحليل التلقائي
            3️⃣ راجع النتائج والتوصيات
            """,
            "icon": "🔐",
        },
    ]


def render_onboarding() -> None:
    """Render 2-screen onboarding flow with consistent styling."""
    if st.session_state.get("onboarding_done"):
        return
    
    inject_ui_kit_css()
    
    # Get current language
    lang = st.session_state.get("language", "ar")
    screens = get_screens(lang)

    # Center all onboarding content
    st.markdown("""
    <style>
        .onboarding-container {
            max-width: 650px;
            margin: 0 auto;
            padding: 20px;
        }
        .onboarding-screen {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%);
            border: 2px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 32px 24px;
            margin: 16px 0;
            text-align: center;
        }
        .onboarding-icon {
            font-size: 64px;
            margin-bottom: 16px;
        }
        .onboarding-title {
            font-size: 24px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 16px;
        }
        .onboarding-body {
            font-size: 15px;
            line-height: 1.8;
            color: #4b5563;
            text-align: right;
            direction: rtl;
        }
        .onboarding-body strong {
            color: #1f2937;
            font-weight: 600;
        }
        .welcome-title {
            text-align: center;
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1 0%, #10b981 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 32px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="onboarding-container">', unsafe_allow_html=True)
    
    st.markdown('<div class="welcome-title">مرحباً بك في BioGuard AI 🛡️</div>', unsafe_allow_html=True)
    
    for screen in screens:
        st.markdown(f'''
        <div class="onboarding-screen">
            <div class="onboarding-icon">{screen["icon"]}</div>
            <div class="onboarding-title">{screen["title"]}</div>
            <div class="onboarding-body">{screen["body"]}</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 ابدأ الآن", type="primary", use_container_width=True):
        st.session_state.onboarding_done = True
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

