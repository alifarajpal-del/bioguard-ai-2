"""
OAuth Login UI Component.
Beautiful login screen with Google and Apple Sign-In buttons.
"""

import streamlit as st
from typing import Optional
import secrets

from services.oauth_providers import get_oauth_provider
from services.auth import create_or_login_user
from ui_components.theme_wheel import get_current_theme
from database.db_manager import get_db_manager


def _inject_oauth_css() -> None:
    """Inject CSS for OAuth login screen."""
    theme = get_current_theme()
    
    css = f"""
    <style>
        /* OAuth Login Container */
        .oauth-login-container {{
            max-width: 480px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        /* Logo & Title */
        .oauth-header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        .oauth-logo {{
            font-size: 72px;
            margin-bottom: 16px;
            animation: float 3s ease-in-out infinite;
        }}
        
        .oauth-title {{
            font-size: 32px;
            font-weight: 700;
            color: {theme['text']};
            margin-bottom: 8px;
        }}
        
        .oauth-subtitle {{
            font-size: 16px;
            color: {theme['secondary']};
            line-height: 1.5;
        }}
        
        /* OAuth Buttons Container */
        .oauth-buttons {{
            display: flex;
            flex-direction: column;
            gap: 16px;
            margin-bottom: 32px;
        }}
        
        /* Google Button */
        .oauth-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 14px 24px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-decoration: none;
            border: 2px solid transparent;
        }}
        
        .oauth-btn-google {{
            background: white;
            color: #1f1f1f;
            border: 2px solid #dadce0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
        }}
        
        .oauth-btn-google:hover {{
            background: #f8f9fa;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }}
        
        /* Apple Button */
        .oauth-btn-apple {{
            background: #000000;
            color: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }}
        
        .oauth-btn-apple:hover {{
            background: #1f1f1f;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
            transform: translateY(-2px);
        }}
        
        /* Button Icons */
        .oauth-icon {{
            font-size: 20px;
            line-height: 1;
        }}
        
        /* Divider */
        .oauth-divider {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin: 32px 0;
            color: {theme['secondary']};
            font-size: 14px;
        }}
        
        .oauth-divider::before,
        .oauth-divider::after {{
            content: '';
            flex: 1;
            height: 1px;
            background: {theme['secondary']}40;
        }}
        
        /* Traditional Form */
        .oauth-traditional-form {{
            background: {theme['card_bg']};
            padding: 24px;
            border-radius: 16px;
            border: 2px solid {theme['primary']}20;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }}
        
        .oauth-form-title {{
            font-size: 18px;
            font-weight: 600;
            color: {theme['text']};
            margin-bottom: 16px;
            text-align: center;
        }}
        
        /* Features List */
        .oauth-features {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin: 40px 0;
            padding: 24px;
            background: {theme['card_bg']};
            border-radius: 12px;
        }}
        
        .oauth-feature {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: {theme['text']};
        }}
        
        .oauth-feature-icon {{
            font-size: 20px;
        }}
        
        /* Privacy Notice */
        .oauth-privacy {{
            text-align: center;
            font-size: 12px;
            color: {theme['secondary']};
            line-height: 1.6;
            margin-top: 24px;
        }}
        
        .oauth-privacy a {{
            color: {theme['primary']};
            text-decoration: none;
            font-weight: 600;
        }}
        
        /* Animations */
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        /* Error/Success Messages */
        .oauth-message {{
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 16px;
            font-size: 14px;
            text-align: center;
        }}
        
        .oauth-message-error {{
            background: #fee;
            color: #c33;
            border: 1px solid #fcc;
        }}
        
        .oauth-message-success {{
            background: #efe;
            color: #3c3;
            border: 1px solid #cfc;
        }}
        
        /* Responsive */
        @media (max-width: 600px) {{
            .oauth-features {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def render_oauth_login() -> None:
    """Render OAuth login screen with Google and Apple Sign-In."""
    _inject_oauth_css()
    
    # Initialize session state
    if "oauth_state" not in st.session_state:
        st.session_state.oauth_state = secrets.token_urlsafe(32)
    if "oauth_error" not in st.session_state:
        st.session_state.oauth_error = None
    
    # Container
    st.markdown('<div class="oauth-login-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('''
        <div class="oauth-header">
            <div class="oauth-logo">🧬</div>
            <div class="oauth-title">BioGuard AI</div>
            <div class="oauth-subtitle">
                مساعدك الذكي للصحة والتغذية<br>
                Privacy-First | Real-Time Analysis | Predictive Intelligence
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Error message
    if st.session_state.oauth_error:
        st.markdown(
            f'<div class="oauth-message oauth-message-error">{st.session_state.oauth_error}</div>',
            unsafe_allow_html=True
        )
        st.session_state.oauth_error = None
    
    # OAuth Buttons
    st.markdown('<div class="oauth-buttons">', unsafe_allow_html=True)
    
    # Google Sign-In Button
    google_provider = get_oauth_provider("google")
    if google_provider:
        google_url = google_provider.get_authorization_url(st.session_state.oauth_state)
        st.markdown(f'''
            <a href="{google_url}" class="oauth-btn oauth-btn-google" target="_self">
                <svg class="oauth-icon" viewBox="0 0 24 24" width="20" height="20">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span>Sign in with Google</span>
            </a>
        ''', unsafe_allow_html=True)
    
    # Apple Sign-In Button
    apple_provider = get_oauth_provider("apple")
    if apple_provider:
        apple_url = apple_provider.get_authorization_url(st.session_state.oauth_state)
        st.markdown(f'''
            <a href="{apple_url}" class="oauth-btn oauth-btn-apple" target="_self">
                <svg class="oauth-icon" viewBox="0 0 24 24" width="20" height="20" fill="white">
                    <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                </svg>
                <span>Sign in with Apple</span>
            </a>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Divider
    st.markdown('<div class="oauth-divider">أو</div>', unsafe_allow_html=True)
    
    # Traditional Login Form
    st.markdown('<div class="oauth-traditional-form">', unsafe_allow_html=True)
    st.markdown('<div class="oauth-form-title">تسجيل الدخول التقليدي</div>', unsafe_allow_html=True)
    
    with st.form("traditional_login"):
        user_id = st.text_input("🆔 User ID", placeholder="user_123", help="معرف فريد لحسابك")
        name = st.text_input("👤 الاسم", placeholder="أحمد محمد")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("🎂 العمر", min_value=1, max_value=120, value=30)
            weight = st.number_input("⚖️ الوزن (كجم)", min_value=20.0, max_value=300.0, value=70.0)
        with col2:
            height = st.number_input("📏 الطول (سم)", min_value=100, max_value=250, value=170)
        
        allergies = st.text_input("🚫 الحساسية", placeholder="الفول السوداني، اللاكتوز")
        conditions = st.text_input("🏥 الحالات الصحية", placeholder="السكري، ضغط الدم")
        
        submit = st.form_submit_button("🚀 متابعة", use_container_width=True)
        
        if submit:
            if user_id and name:
                profile = {
                    "user_id": user_id,
                    "name": name,
                    "age": age,
                    "weight": weight,
                    "height": height,
                    "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
                    "medical_conditions": [c.strip() for c in conditions.split(",") if c.strip()],
                    "provider": "traditional",
                }
                
                try:
                    token = create_or_login_user(profile)
                    st.session_state.user_id = user_id
                    st.session_state.user_profile = profile
                    st.session_state.authenticated = True
                    st.session_state.auth_token = token
                    st.success("✅ مرحباً بك!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ حدث خطأ: {e}")
            else:
                st.warning("⚠️ يرجى إدخال User ID والاسم")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Features
    st.markdown('''
        <div class="oauth-features">
            <div class="oauth-feature">
                <span class="oauth-feature-icon">🔐</span>
                <span>خصوصية تامة</span>
            </div>
            <div class="oauth-feature">
                <span class="oauth-feature-icon">🧠</span>
                <span>ذكاء اصطناعي</span>
            </div>
            <div class="oauth-feature">
                <span class="oauth-feature-icon">📊</span>
                <span>تحليل فوري</span>
            </div>
            <div class="oauth-feature">
                <span class="oauth-feature-icon">🔮</span>
                <span>توقعات صحية</span>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Privacy Notice
    st.markdown('''
        <div class="oauth-privacy">
            بتسجيل الدخول، أنت توافق على <a href="#">شروط الخدمة</a> و<a href="#">سياسة الخصوصية</a>.<br>
            بياناتك الصحية مشفرة ومحمية بالكامل.
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def handle_oauth_callback(provider: str, code: str, state: str) -> bool:
    """
    Handle OAuth callback from provider.
    
    Args:
        provider: "google" or "apple"
        code: Authorization code from provider
        state: State parameter for CSRF verification
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Verify state (CSRF protection)
        if state != st.session_state.get("oauth_state"):
            st.session_state.oauth_error = "⚠️ Invalid state parameter. Please try again."
            return False
        
        # Get OAuth provider
        oauth_provider = get_oauth_provider(provider)
        if not oauth_provider:
            st.session_state.oauth_error = f"❌ Provider {provider} not available."
            return False
        
        # Exchange code for token
        token_data = oauth_provider.exchange_code_for_token(code)
        if not token_data:
            st.session_state.oauth_error = "❌ فشل الحصول على رمز المصادقة."
            return False
        
        # Get user info
        user_info = oauth_provider.get_user_info(token_data)
        if not user_info:
            st.session_state.oauth_error = "❌ فشل الحصول على معلومات المستخدم."
            return False
        
        # Create/update user in database
        db = get_db_manager()
        user_profile = {
            "user_id": f"{provider}_{user_info['user_id']}",
            "name": user_info.get("name", user_info.get("email", "").split("@")[0]),
            "email": user_info.get("email"),
            "picture": user_info.get("picture"),
            "provider": provider,
            "email_verified": user_info.get("email_verified", False),
        }
        
        # Generate JWT token
        token = create_or_login_user(user_profile)
        
        # Set session state
        st.session_state.user_id = user_profile["user_id"]
        st.session_state.user_profile = user_profile
        st.session_state.authenticated = True
        st.session_state.auth_token = token
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth callback error: {e}")
        st.session_state.oauth_error = f"❌ حدث خطأ: {str(e)}"
        return False
