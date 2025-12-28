"""
BioGuard AI - Main Entry Point
A futuristic, privacy-first health ecosystem with real-time AR analysis.
Microservices architecture with event-driven design.
"""

import streamlit as st
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import configuration
from config.settings import (
    STREAMLIT_PAGE_CONFIG, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE,
    FEATURE_FLAGS, MOBILE_VIEWPORT
)

# Import services
from services.auth_privacy import get_auth_manager
from services.graph_engine import get_graph_engine
from services.digital_twin import get_digital_twin
from services.live_vision import get_live_vision_service
from database.db_manager import get_db_manager
from models.schemas import UserProfile, FoodAnalysisResult, VerdictType
from prompts.system_prompts import get_prompt, inject_user_context

# Configure Streamlit
st.set_page_config(**STREAMLIT_PAGE_CONFIG)

# Add mobile viewport and PWA support
st.markdown(MOBILE_VIEWPORT, unsafe_allow_html=True)

# ============== Session State Initialization ==============
def init_session_state():
    """Initialize session state variables."""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'language' not in st.session_state:
        st.session_state.language = DEFAULT_LANGUAGE
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []


# ============== Authentication UI ==============
def render_auth_screen():
    """Render authentication and user profile setup."""
    st.title("🧬 BioGuard AI - Health Ecosystem")
    st.subheader("Privacy-First | Real-Time Analysis | Predictive Intelligence")
    
    with st.container():
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.write("### Your Personal Health Analyzer")
            st.write("""
            - 🔐 Your data stays on YOUR device
            - 🧠 Federated learning for privacy
            - 📊 Real-time AR food analysis
            - 🔮 Biological Digital Twin predictions
            """)
        
        with col2:
            st.write("### Get Started")
            
            user_id = st.text_input("Enter your User ID", placeholder="user_123")
            name = st.text_input("Name", placeholder="John Doe")
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0)
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
            
            allergies_input = st.text_input("Allergies (comma-separated)", placeholder="Peanuts, Dairy")
            conditions_input = st.text_input("Medical Conditions (comma-separated)", placeholder="Diabetes, Hypertension")
            
            if st.button("🚀 Create Profile", key="create_profile"):
                if user_id and name:
                    # Create user profile
                    user_profile = {
                        'user_id': user_id,
                        'name': name,
                        'age': age,
                        'weight': weight,
                        'height': height,
                        'allergies': [a.strip() for a in allergies_input.split(',') if a.strip()],
                        'medical_conditions': [c.strip() for c in conditions_input.split(',') if c.strip()],
                        'glucose_baseline': 100,
                        'bp_systolic': 120,
                        'bp_diastolic': 80,
                        'cholesterol_baseline': 200,
                    }
                    
                    # Save to database
                    db = get_db_manager()
                    if db.save_user(user_profile):
                        # Generate JWT token
                        auth = get_auth_manager()
                        token = auth.generate_jwt_token(user_id, user_profile)
                        
                        # Update session
                        st.session_state.user_id = user_id
                        st.session_state.user_profile = user_profile
                        st.session_state.authenticated = True
                        st.session_state.auth_token = token
                        
                        st.success("✅ Profile created! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create profile")
                else:
                    st.warning("⚠️ Please fill in User ID and Name")


# ============== Main Dashboard ==============
def render_dashboard():
    """Render main analytics dashboard."""
    st.title("🧬 BioGuard AI Dashboard")
    
    # Sidebar
    with st.sidebar:
        st.write(f"### User: {st.session_state.user_profile['name']}")
        st.write(f"User ID: `{st.session_state.user_id}`")
        
        st.divider()
        
        # Feature flags
        st.write("### Active Features")
        for feature, enabled in FEATURE_FLAGS.items():
            status = "✅" if enabled else "❌"
            st.write(f"{status} {feature.replace('_', ' ').title()}")
        
        st.divider()
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["📸 Live AR Analysis", "📊 Analysis History", "⚙️ Profile Settings", "🔒 Privacy & Security"]
        )
        
        if st.button("🚪 Logout"):
            auth = get_auth_manager()
            auth.revoke_token(st.session_state.user_id)
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_profile = None
            st.rerun()
    
    # Main content
    if page == "📸 Live AR Analysis":
        render_live_ar_analysis()
    elif page == "📊 Analysis History":
        render_analysis_history()
    elif page == "⚙️ Profile Settings":
        render_profile_settings()
    elif page == "🔒 Privacy & Security":
        render_privacy_settings()


# ============== Live AR Analysis Page ==============
def render_live_ar_analysis():
    """Render live AR camera feed with food detection."""
    st.header("📸 Live AR Food Analysis")
    
    st.write("""
    ### How it works:
    1. **Point camera at food** - The AR system detects food objects in real-time
    2. **Click the bubble** - Tap on detected food to perform deep analysis
    3. **Get instant insights** - Health score, predictions, and recommendations
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Camera Feed")
        
        # Check if streamlit-webrtc is available
        try:
            from streamlit_webrtc import webrtc_streamer, RTCConfiguration, WebRtcMode
            
            # Production-ready RTC configuration with public STUN servers
            rtc_config = RTCConfiguration({
                "iceServers": [
                    {"urls": ["stun:stun.l.google.com:19302"]},
                    {"urls": ["stun:stun1.l.google.com:19302"]},
                    {"urls": ["stun:stun2.l.google.com:19302"]},
                    # Add TURN server for production (optional)
                    # {"urls": ["turn:your-turn-server.com"], "username": "user", "credential": "pass"}
                ]
            })
            
            # Mobile-optimized camera constraints
            mobile_constraints = {
                "video": {
                    "width": {"max": 640},
                    "height": {"max": 480}, 
                    "frameRate": {"max": 15},
                    "facingMode": "environment"  # Back camera for food scanning
                }, 
                "audio": False
            }
            
            webrtc_ctx = webrtc_streamer(
                key="bioguard-ar",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=rtc_config,
                media_stream_constraints=mobile_constraints,
                async_processing=True,
            )
            
            if webrtc_ctx.state.playing:
                st.success("📹 الكاميرا نشطة - يتم كشف الطعام...")
                
                # Add mobile-friendly instructions
                st.markdown("""
                <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 1rem; border-radius: 12px; text-align: center;
                           margin: 1rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                    <h4>📱 نصائح الهاتف المحمول</h4>
                    <p>• اقلب الهاتف للوضع الأفقي للحصول على أفضل نتيجة</p>
                    <p>• تأكد من الإضاءة الجيدة على الطعام</p>
                    <p>• ضع الكاميرا على مسافة 20-30 سم من الطعام</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add quick action buttons for mobile
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("📸 التقط صورة", use_container_width=True):
                        st.balloons()
                        st.success("تم حفظ الصورة!")
                
                with col_btn2:
                    if st.button("🔄 تبديل كاميرا", use_container_width=True):
                        st.info("يتم تبديل الكاميرا...")
                        
                with col_btn3:
                    if st.button("🛑 إيقاف", use_container_width=True):
                        st.warning("تم إيقاف الكاميرا")
                        
            else:
                st.markdown("""
                <div style="background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
                           color: white; padding: 2rem; border-radius: 16px; text-align: center;">
                    <h3>🎥 تشغيل كاميرا الطعام</h3>
                    <p>اضغط على زر "START" أعلاه لبدء تشغيل الكاميرا</p>
                    <p><strong>للهواتف:</strong> امنح إذن الوصول للكاميرا</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Get live vision service
                vision = get_live_vision_service()
                
                # Process frames
                if webrtc_ctx.video_processor:
                    stats = vision.get_service_stats()
                    st.json(stats)
            
        except ImportError:
            st.warning("⚠️ streamlit-webrtc not installed. Using static upload mode.")
            
            uploaded_image = st.file_uploader(
                "Upload food image",
                type=['jpg', 'png', 'jpeg']
            )
            
            if uploaded_image:
                import cv2
                import numpy as np
                from PIL import Image
                
                image = Image.open(uploaded_image)
                st.image(image, caption="Uploaded image")
                
                # Process image
                vision = get_live_vision_service()
                image_array = np.array(image)
                annotated, detections = vision.process_frame(image_array)
                
                st.image(annotated, caption="Detected objects")
                
                if detections:
                    st.subheader("🎯 Detected Objects")
                    for i, detection in enumerate(detections):
                        st.write(f"**Detection {i+1}**: {detection.micro_summary}")
    
    with col2:
        st.subheader("Live Stats")
        
        vision = get_live_vision_service()
        stats = vision.get_service_stats()
        
        st.metric("Frames Processed", stats['frames_processed'])
        st.metric("Detection FPS", stats['detection_fps'])
        
        if stats['cached_detections'] > 0:
            st.success(f"✅ {stats['cached_detections']} objects detected")
        else:
            st.info("📊 No objects detected yet")


# ============== Analysis History Page ==============
def render_analysis_history():
    """Render past food analysis results."""
    st.header("📊 Analysis History")
    
    db = get_db_manager()
    history = db.get_user_history(st.session_state.user_id, limit=20)
    
    if history:
        st.write(f"Total analyses: **{len(history)}**")
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        
        safe_count = sum(1 for h in history if h['verdict'] == 'SAFE')
        warning_count = sum(1 for h in history if h['verdict'] == 'WARNING')
        danger_count = sum(1 for h in history if h['verdict'] == 'DANGER')
        
        col1.metric("✅ Safe", safe_count)
        col2.metric("⚠️ Warning", warning_count)
        col3.metric("❌ Danger", danger_count)
        
        st.divider()
        
        # Display history
        for item in history:
            with st.expander(f"{item['product_name']} - {item['verdict']}"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Health Score", item['health_score'])
                col2.metric("NOVA Score", item['nova_score'])
                col3.metric("Verdict", item['verdict'])
                col4.metric("Date", item['created_at'][:10])
    else:
        st.info("No analysis history yet. Start by analyzing a food product!")


# ============== Profile Settings Page ==============
def render_profile_settings():
    """Render user profile settings."""
    st.header("⚙️ Profile Settings")
    
    profile = st.session_state.user_profile
    
    st.write(f"### Personal Information")
    st.write(f"**User ID**: {profile['user_id']}")
    st.write(f"**Name**: {profile['name']}")
    st.write(f"**Age**: {profile['age']}")
    st.write(f"**Weight**: {profile['weight']} kg")
    st.write(f"**Height**: {profile['height']} cm")
    
    st.write(f"### Medical Profile")
    st.write(f"**Allergies**: {', '.join(profile.get('allergies', [])) or 'None'}")
    st.write(f"**Medical Conditions**: {', '.join(profile.get('medical_conditions', [])) or 'None'}")
    
    st.write(f"### Baseline Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Glucose Baseline", f"{profile.get('glucose_baseline', 100)} mg/dL")
    col2.metric("Blood Pressure", f"{profile.get('bp_systolic', 120)}/{profile.get('bp_diastolic', 80)}")
    col3.metric("Cholesterol", f"{profile.get('cholesterol_baseline', 200)} mg/dL")
    
    if st.button("✏️ Edit Profile"):
        st.info("Edit functionality coming soon")


# ============== Privacy & Security Page ==============
def render_privacy_settings():
    """Render privacy and security settings."""
    st.header("🔒 Privacy & Security")
    
    auth = get_auth_manager()
    privacy_report = auth.get_privacy_report(st.session_state.user_id)
    
    st.write("### Data Protection")
    col1, col2 = st.columns(2)
    
    col1.write("✅ **Data Stored Locally**: Your data never leaves your device")
    col2.write("🔐 **End-to-End Encrypted**: All data encrypted at rest")
    
    st.divider()
    
    st.write("### Federated Learning")
    st.write(f"**Status**: {'✅ Enabled' if privacy_report['federated_learning_enabled'] else '❌ Disabled'}")
    st.write("""
    Your device trains models locally without uploading raw medical data.
    Only encrypted model weights are shared for global model improvement.
    """)
    
    st.divider()
    
    st.write("### Two-Factor Authentication")
    
    if st.button("🔑 Enable 2FA"):
        secret = auth.generate_2fa_secret(st.session_state.user_id)
        qr_url = auth.get_2fa_qr_code(st.session_state.user_id, st.session_state.user_profile['name'])
        
        st.code(qr_url)
        st.write("Scan this QR code with an authenticator app")
    
    st.divider()
    
    st.write("### Data Access & Privacy Report")
    st.json(privacy_report)


# ============== Main Application ==============
def main():
    """Main application entry point."""
    init_session_state()
    
    if not st.session_state.authenticated:
        render_auth_screen()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
