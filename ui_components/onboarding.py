"""Simple onboarding flow shown once per user session."""

import streamlit as st

SCREENS = [
    {
        "title": "مرحباً بك في BioGuard AI",
        "body": "مساعد صحي مدعّم بالذكاء الاصطناعي لتحليل التغذية والمنتجات في الوقت الفعلي.",
        "icon": "🛡️",
    },
    {
        "title": "الخصوصية أولاً",
        "body": "يتم حفظ بياناتك على جهازك/حسابك مع مزامنة اختيارية لملفاتك الطبية.",
        "icon": "🔒",
    },
    {
        "title": "كيف يعمل المسح",
        "body": "وجّه الكاميرا نحو المنتج، أو امسح الباركود، أو ارفع صورة لتحصل على تقييم صحي سريع.",
        "icon": "📸",
    },
]


def render_onboarding() -> None:
    if st.session_state.get("onboarding_done"):
        return

    st.markdown("## 🚀 لنبدأ")
    for screen in SCREENS:
        with st.container():
            st.markdown(f"### {screen['icon']} {screen['title']}")
            st.markdown(screen["body"])
            st.divider()

    if st.button("ابدأ الآن", type="primary", use_container_width=True):
        st.session_state.onboarding_done = True
        st.rerun()
