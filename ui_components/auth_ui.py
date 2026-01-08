"""Login and Register UI components."""
import streamlit as st
from utils.i18n import get_lang, set_lang, t
from services.auth import login_user, register_user
from ui_components.branding import load_logo_base64


def render_login_register():
    """Render login/register page."""
    # Language selector
    cols = st.columns([1, 10, 1])
    with cols[2]:
        current_lang = get_lang()
        new_lang = st.selectbox(
            "Language / اللغة",
            ["English", "العربية"],
            index=0 if current_lang == "en" else 1,
            key="lang_selector"
        )
        # Only rerun if language actually changed
        selected_lang = "ar" if new_lang == "العربية" else "en"
        if selected_lang != current_lang:
            set_lang(selected_lang)
            st.rerun()
    
    # Centered login/register form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Show logo
    with col2:
        logo_b64 = load_logo_base64()
        if logo_b64:
            st.markdown(
                f'''
                <div style="text-align: center; margin-bottom: 20px;">
                    <img src="data:image/png;base64,{logo_b64}" 
                         style="width: 120px; height: 120px; border-radius: 20px; 
                                box-shadow: 0 10px 30px rgba(0, 188, 212, 0.3);" />
                </div>
                ''',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="text-align: center; font-size: 80px; margin-bottom: 20px;">🧬</div>',
                unsafe_allow_html=True
            )
    
    with col2:
        st.markdown("### " + t("login_title"))
        st.caption(t("login_subtitle"))
        
        # Tab selection
        tab1, tab2 = st.tabs([t("login"), t("register")])
        
        with tab1:
            st.markdown(f"#### {t('login')}")
            email = st.text_input(t("email"), key="login_email")
            password = st.text_input(t("password"), type="password", key="login_pwd")
            
            if st.button(t("login_button"), width="stretch", key="login_btn"):
                if email and password:
                    result = login_user(email, password)
                    if result["success"]:
                        st.session_state.user_id = result["user_id"]
                        st.session_state.is_admin = result["is_admin"]
                        st.session_state.authenticated = True
                        st.success(t("login_success") if "login_success" in dir() else "Login successful!")
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.warning("Please enter email and password")
            
            st.caption(t("no_account"))
        
        with tab2:
            st.markdown(f"#### {t('register')}")
            reg_email = st.text_input(t("email"), key="reg_email")
            reg_password = st.text_input(t("password"), type="password", key="reg_pwd")
            reg_confirm = st.text_input(t("password_confirm"), type="password", key="reg_confirm")
            
            if st.button(t("register_button"), width="stretch", key="reg_btn"):
                if not reg_email or not reg_password or not reg_confirm:
                    st.warning("Please fill all fields")
                elif reg_password != reg_confirm:
                    st.error(t("password_mismatch"))
                else:
                    result = register_user(reg_email, reg_password, is_admin=False)
                    if result["success"]:
                        st.success(t("register_success"))
                        st.info("Now you can login with your credentials")
                    else:
                        st.error(result["message"])
            
            st.caption(t("already_have_account"))


def check_authentication():
    """Check if user is authenticated, return True/False."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    return st.session_state.authenticated


def require_login():
    """Decorator-like check. If not authenticated, show login and stop."""
    if not check_authentication():
        render_login_register()
        st.stop()
