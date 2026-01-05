"""Full-screen AR camera view with WebRTC fix and AI analysis."""

from typing import Any, Dict, Optional, List
from io import BytesIO
import time
import asyncio
from datetime import datetime, timedelta

import numpy as np
import streamlit as st
from PIL import Image

try:
    from streamlit_webrtc import webrtc_streamer, RTCConfiguration, WebRtcMode, VideoProcessorBase
    import av
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    st.warning("⚠️ streamlit-webrtc is not installed. Camera view will use upload fallback.")

from services.engine import analyze_image_sync
from services.live_vision import get_live_vision_service
from services.barcode_scanner import get_barcode_scanner
from services.recommendations import get_recommendations_service
from database.db_manager import get_db_manager
from services.health_sync import get_health_sync_service
from config.settings import (
    DETECTION_FPS,
    SUPPORTED_LANGUAGES,
    DEFAULT_REGION,
    DEFAULT_PREFERRED_SOURCES,
    REGIONAL_SOURCE_DEFAULTS,
    HEALTH_SYNC_DEFAULT,
)
from services.nutrition_api import NutritionAPI


def _inject_camera_css() -> None:
    """Inject iOS-style camera CSS with grid overlay and modern controls"""
    css = """
    <style>
        /* iOS Native Camera - Full Screen */
        .scan-stage {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: calc(100vh - 80px);
            z-index: 100;
            background: #000;
            overflow: hidden;
        }
        
        /* Force WebRTC container to fill */
        .scan-stage [data-testid="stWebRtc"] {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            z-index: 1;
        }
        
        /* Video element - cover entire screen */
        .scan-stage video {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
            border-radius: 0 !important;
            transform: scaleX(-1); /* mirror for selfie */
        }

        /* Force embedded WebRTC video to fill and sit behind HUD */
        .streamlit-webrtc video {
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
        }
        .streamlit-webrtc {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -1; /* background layer */
        }
        .streamlit-webrtc .stVideo {
            display: none;
        }
        
        /* CRITICAL: Hide ALL default WebRTC controls */
        [data-testid="stWebRtc"] button,
        [data-testid="stWebRtc"] select,
        .scan-stage button[kind],
        .scan-stage button[type],
        div[data-testid="stVerticalBlock"] > div > button {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        
        /* iOS Grid Overlay - Rule of Thirds */
        .camera-grid {
            position: absolute;
            inset: 0;
            pointer-events: none;
            z-index: 2;
            opacity: 0.3;
        }
        
        .camera-grid::before,
        .camera-grid::after {
            content: '';
            position: absolute;
            background: rgba(255, 255, 255, 0.5);
        }
        
        /* Vertical Lines */
        .camera-grid::before {
            left: 33.33%;
            top: 0;
            bottom: 0;
            width: 1px;
            box-shadow: 100vw 0 0 rgba(255, 255, 255, 0.5);
        }
        
        /* Horizontal Lines */
        .camera-grid::after {
            top: 33.33%;
            left: 0;
            right: 0;
            height: 1px;
            box-shadow: 0 33.34vh 0 rgba(255, 255, 255, 0.5);
        }
        
        /* Overlay gradient */
        .scan-overlay {
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, transparent 15%, transparent 85%, rgba(0,0,0,0.6) 100%);
            z-index: 2;
        }
        
        /* HUD Elements */
        .hud-top {
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #fff;
            font-weight: 700;
            pointer-events: none;
            z-index: 3;
        }
        
        .pill {
            padding: 10px 16px;
            border-radius: 999px;
            backdrop-filter: blur(20px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            font-size: 13px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .pill.live { background: rgba(16,185,129,0.95); }
        .pill.status { background: rgba(59,130,246,0.92); }
        
        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #fff;
            animation: blink 1.5s ease-in-out infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        /* iOS Style Bottom Controls */
        .hud-bottom {
            position: absolute;
            bottom: 110px;
            left: 0;
            right: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 40px;
            pointer-events: none;
            z-index: 3;
        }
        
        /* Main Capture Button - iOS Style */
        .capture-btn {
            pointer-events: auto;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: #fff;
            border: 6px solid rgba(255,255,255,0.4);
            box-shadow: 
                0 10px 30px rgba(0,0,0,0.5),
                inset 0 -2px 8px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            cursor: pointer;
            transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        .capture-btn::before {
            content: '';
            position: absolute;
            inset: -12px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        }
        
        .capture-btn:active {
            transform: scale(0.90);
            box-shadow: 0 5px 15px rgba(0,0,0,0.4);
        }
        
        /* Side Control Buttons */
        .side-control {
            pointer-events: auto;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(20px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 24px;
        }
        
        .side-control:hover {
            transform: scale(1.1);
            background: rgba(0, 0, 0, 0.7);
            border-color: rgba(255, 255, 255, 0.5);
        }
        
        .side-control:active {
            transform: scale(0.95);
        }
        
        /* Quick Action Pills */
        .quick-action {
            pointer-events: auto;
            min-width: 80px;
            text-align: center;
            color: #fff;
            font-weight: 700;
            font-size: 13px;
            padding: 10px 16px;
            border-radius: 16px;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(20px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            cursor: pointer;
            border: 2px solid rgba(255,255,255,0.2);
            transition: all 0.2s ease;
        }
        
        .quick-action:hover {
            background: rgba(0,0,0,0.75);
            border-color: rgba(255,255,255,0.4);
            transform: translateY(-2px);
        }
        
        /* Helper Text at Bottom */
        .scan-helper {
            position: absolute;
            bottom: 40px;
            left: 0;
            right: 0;
            color: rgba(255,255,255,0.95);
            text-align: center;
            font-size: 14px;
            font-weight: 600;
            text-shadow: 0 2px 12px rgba(0,0,0,0.7);
            z-index: 3;
            padding: 12px 20px;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            max-width: 320px;
            margin: 0 auto;
        }
        
        /* Progress Ring */
        .progress-ring {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 4;
        }
        
        .progress-ring circle {
            fill: transparent;
            stroke: #10b981;
            stroke-width: 4;
            stroke-dasharray: 251.2;
            stroke-dashoffset: 251.2;
            animation: progress 2s ease-in-out forwards;
        }
        
        @keyframes progress {
            to { stroke-dashoffset: 0; }
        }
        
        /* Detection Box */
        .detection-box {
            position: absolute;
            border: 3px solid #10b981;
            border-radius: 8px;
            background: rgba(16, 185, 129, 0.1);
            backdrop-filter: blur(4px);
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.8; transform: scale(1.02); }
        }
        
        /* Status Messages */
        .status-message {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 20px 40px;
            border-radius: 16px;
            font-size: 18px;
            font-weight: 600;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            z-index: 5;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
            to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def _get_nutrition_client() -> NutritionAPI:
    """Singleton nutrition client stored in session state."""
    if 'nutrition_client' not in st.session_state:
        st.session_state.nutrition_client = NutritionAPI()
    return st.session_state.nutrition_client


def _get_preferred_sources(region: Optional[str] = None) -> List[str]:
    """Resolve preferred nutrition sources with regional defaults."""
    if st.session_state.get('preferred_sources'):
        return st.session_state.preferred_sources
    region_key = (region or st.session_state.get('region') or DEFAULT_REGION).lower()
    return REGIONAL_SOURCE_DEFAULTS.get(region_key, DEFAULT_PREFERRED_SOURCES)


class LiveVisionProcessor(VideoProcessorBase):
    """Process video frames with LiveVision service."""
    
    def __init__(self):
        self.vision = get_live_vision_service()
        self.barcode_scanner = get_barcode_scanner()
        self.last_analysis_time = None
        self.analysis_cooldown = 3.0  # seconds
        self.current_detections = []
        self.barcode_data = None
        
    def recv(self, frame):
        """Process incoming frame."""
        img = frame.to_ndarray(format="bgr24")
        
        # Process with LiveVision
        annotated_frame, detections = self.vision.process_frame(img)
        self.current_detections = detections
        
        # Try barcode scanning periodically
        if self.vision.frame_count % 30 == 0:  # Every 30 frames
            self.barcode_data = self.barcode_scanner.scan_barcode(img)
        
        # Auto-trigger analysis if detection found and cooldown passed
        if detections and len(detections) > 0:
            now = time.time()
            if (self.last_analysis_time is None or 
                now - self.last_analysis_time > self.analysis_cooldown):
                
                # Capture high-quality frame for analysis
                hq_frame = self.vision.capture_high_quality_frame(
                    img, 
                    detections[0].bounding_box
                )
                
                # Store in session state for analysis
                if 'pending_analysis_frame' not in st.session_state:
                    st.session_state.pending_analysis_frame = hq_frame
                    st.session_state.pending_analysis_bbox = detections[0].bounding_box
                    self.last_analysis_time = now
        
        return av.VideoFrame.from_ndarray(annotated_frame, format="bgr24")


def render_camera_view() -> None:
    """Render live camera view with AR overlays and continuous scanning."""
    # Back to home button
    if st.button("🔙 رجوع إلى الرئيسية", key="camera_back_home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    _inject_camera_css()
    
    # Initialize session state
    if 'scan_status' not in st.session_state:
        st.session_state.scan_status = 'searching'  # searching, detected, analyzing, complete
    if 'last_barcode' not in st.session_state:
        st.session_state.last_barcode = None
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'preferred_sources' not in st.session_state:
        st.session_state.preferred_sources = _get_preferred_sources()
    if 'region' not in st.session_state:
        st.session_state.region = DEFAULT_REGION
    if 'health_sync_enabled' not in st.session_state:
        st.session_state.health_sync_enabled = HEALTH_SYNC_DEFAULT
    if 'last_nutrition_snapshot' not in st.session_state:
        st.session_state.last_nutrition_snapshot = None

    if not WEBRTC_AVAILABLE:
        _render_upload_fallback()
        return

    # Get messages based on language
    messages = _get_ui_messages(st.session_state.language)
    
    # Status indicators
    status_text = {
        'searching': messages['searching'],
        'detected': messages['detected'],
        'analyzing': messages['analyzing'],
        'complete': messages['complete']
    }.get(st.session_state.scan_status, messages['searching'])

    region_options = list(REGIONAL_SOURCE_DEFAULTS.keys())
    region_index = region_options.index(st.session_state.region) if st.session_state.region in region_options else region_options.index(DEFAULT_REGION)

    with st.expander("Nutrition sources & sync", expanded=False):
        selected_region = st.selectbox("Region defaults", region_options, index=region_index)
        preferred_sources = st.multiselect(
            "Preferred sources (first wins)",
            DEFAULT_PREFERRED_SOURCES,
            default=_get_preferred_sources(selected_region),
            help="Order determines lookup priority",
        )
        sync_enabled = st.checkbox(
            "Sync with Health apps",
            value=st.session_state.health_sync_enabled,
            help="Enable HealthKit / Health Connect sync for nutrition entries",
        )

        if (
            selected_region != st.session_state.region
            or preferred_sources != st.session_state.preferred_sources
            or sync_enabled != st.session_state.health_sync_enabled
        ):
            st.session_state.region = selected_region
            st.session_state.preferred_sources = preferred_sources or _get_preferred_sources(selected_region)
            st.session_state.health_sync_enabled = sync_enabled

            user_id = st.session_state.get('user_id')
            if user_id:
                db = get_db_manager()
                db.update_user_settings(
                    user_id,
                    health_sync_enabled=sync_enabled,
                    region=selected_region,
                    preferred_sources=st.session_state.preferred_sources,
                )

    rtc_config = RTCConfiguration({
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]},
        ]
    })

    constraints: Dict[str, Any] = {
        "video": {
            "width": {"max": 1280, "ideal": 720},
            "height": {"max": 720, "ideal": 480},
            "frameRate": {"max": 30, "ideal": 15},
            "facingMode": "environment",
        },
        "audio": False,
    }

    st.markdown('<div class="scan-stage">', unsafe_allow_html=True)
    
    # Start WebRTC with custom processor
    ctx = webrtc_streamer(
        key="bioguard-ar-live",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_config,
        media_stream_constraints=constraints,
        video_processor_factory=LiveVisionProcessor,
        desired_playing_state=True,
        video_html_attrs={"autoPlay": True, "playsInline": True, "controls": False, "muted": True},
        async_processing=True,
    )

    # Dynamic HUD with iOS grid overlay
    hud_html = f"""
    <div class="camera-grid"></div>
    <div class="scan-overlay"></div>
    <div class="hud-top">
        <div class="pill live"><span class="dot"></span>{messages['live']}</div>
        <div class="pill status">{status_text}</div>
    </div>
    """
    
    # Show progress ring when analyzing
    if st.session_state.scan_status == 'analyzing':
        hud_html += """
        <div class="progress-ring">
            <svg width="80" height="80">
                <circle cx="40" cy="40" r="36"></circle>
            </svg>
        </div>
        """
    
    hud_html += f"""
    <div class="hud-bottom">
        <div class="side-control" onclick="alert('{messages['flash_tip']}')" title="Flash">💡</div>
        <div class="capture-btn" onclick="console.log('manual capture')" title="Capture">⬤</div>
        <div class="side-control" onclick="alert('Switch Camera')" title="Switch">🔄</div>
    </div>
    <div class="scan-helper">
        📸 {messages.get('camera_guide', 'وجّه الكاميرا نحو المنتج للمسح التلقائي')}
    </div>
    </div>
    """

    if ctx and ctx.state.playing:
        st.markdown(hud_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Check for pending analysis
        if 'pending_analysis_frame' in st.session_state:
            st.session_state.scan_status = 'analyzing'
            
            # Convert frame to bytes
            frame = st.session_state.pending_analysis_frame
            image = Image.fromarray(frame)
            buf = BytesIO()
            image.save(buf, format="JPEG", quality=95)
            
            # Perform analysis
            provider = st.session_state.get("ai_provider", "gemini")
            
            with st.spinner(messages['analyzing'] + "..."):
                result = analyze_image_sync(buf.getvalue(), preferred_provider=provider)
                
                # Check for health conflicts
                user_id = st.session_state.get('user_id', 'anonymous')
                db = get_db_manager()
                user_profile = db.get_user(user_id)
                
                if user_profile and result.get('product'):
                    # Check against knowledge graph
                    from services.graph_engine import GraphEngine
                    graph_engine = GraphEngine()
                    
                    ingredients = result.get('ingredients', [])
                    conflicts = graph_engine.find_hidden_conflicts(
                        ingredients,
                        user_profile.get('medical_conditions', []),
                        user_profile.get('allergies', [])
                    )
                    
                    if conflicts:
                        result['health_conflicts'] = conflicts
                        result['warnings'] = result.get('warnings', []) + [
                            f"⚠️ {c['ingredient']} may affect {c['health_condition']}" 
                            for c in conflicts[:3]
                        ]

                if not st.session_state.last_nutrition_snapshot and result.get('product'):
                    nutrition_client = _get_nutrition_client()
                    snapshot = nutrition_client.get_nutrition(
                        query=result.get('product'),
                        preferred_sources=_get_preferred_sources(st.session_state.region),
                    )
                    if snapshot.get('source'):
                        st.session_state.last_nutrition_snapshot = snapshot

                if st.session_state.last_barcode and isinstance(st.session_state.last_barcode, dict):
                    result['barcode'] = st.session_state.last_barcode.get('barcode')

                if st.session_state.last_nutrition_snapshot:
                    snapshot = st.session_state.last_nutrition_snapshot
                    result['data_source'] = snapshot.get('source')
                    result['nutrients'] = snapshot.get('raw') or snapshot
                    if not result.get('product') and isinstance(snapshot.get('raw'), dict):
                        label = snapshot['raw'].get('product_name')
                        if label:
                            result['product'] = label
                
                # Save to history
                st.session_state.analysis_history.append(result)
                db.save_food_analysis(user_id, result)

                if st.session_state.health_sync_enabled and result.get('nutrients'):
                    health_sync = get_health_sync_service()
                    health_sync.sync_nutrition_entry(
                        user_id=user_id,
                        product=result.get('product', 'Unknown'),
                        nutrients=result.get('nutrients', {}),
                        source=result.get('data_source'),
                        timestamp=datetime.utcnow().isoformat(),
                    )
                
                st.session_state.scan_status = 'complete'
                
                # Show results
                st.success(f"✅ {messages['analysis_complete']}")
                
                # Display result
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader(result.get('product', 'Unknown Product'))
                    
                    # Health score with color
                    score = result.get('health_score', 50)
                    color = '#10b981' if score > 70 else ('#f59e0b' if score > 40 else '#ef4444')
                    st.markdown(f"""
                    <div style="font-size: 48px; font-weight: 800; color: {color};">
                        {score}/100
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Warnings
                    if result.get('warnings'):
                        st.warning("⚠️ " + " • ".join(result.get('warnings', [])[:3]))
                    
                    # Ingredients
                    if result.get('ingredients'):
                        with st.expander(messages['ingredients']):
                            st.write(", ".join(result.get('ingredients', [])))

                    nutrients = result.get('nutrients') or {}
                    if nutrients:
                        with st.expander(messages.get('nutrition_details', 'Nutrition breakdown')):
                            st.write({
                                'calories': nutrients.get('calories'),
                                'carbs': nutrients.get('carbohydrates') or nutrients.get('carbs'),
                                'fat': nutrients.get('fat'),
                                'protein': nutrients.get('protein'),
                                'sugar': nutrients.get('sugars') or nutrients.get('sugar'),
                            })
                            if result.get('data_source'):
                                st.caption(f"Source: {result['data_source']}")
                
                with col2:
                    st.image(image, use_container_width=True, caption=messages['scanned_image'])
                
                # Suggest alternatives if score is low
                if score < 70:
                    with st.expander(messages['alternatives']):
                        # Get healthier alternatives
                        try:
                            recommendations_service = get_recommendations_service()
                            product_name = result.get('product', 'Unknown')
                            category = result.get('category')
                            
                            # Get user profile for personalized recommendations
                            username = st.session_state.get('username')
                            user_profile = {}
                            if username:
                                db = get_db_manager()
                                user_data = db.get_user_profile(username)
                                if user_data:
                                    user_profile = {
                                        'allergies': user_data.get('allergies', []),
                                        'health_conditions': user_data.get('health_conditions', [])
                                    }
                            
                            # Get alternatives
                            if user_profile:
                                alternatives = recommendations_service.get_personalized_alternatives(
                                    product_name,
                                    score,
                                    user_profile,
                                    category,
                                    limit=5
                                )
                            else:
                                alternatives = recommendations_service.get_healthier_alternatives(
                                    product_name,
                                    score,
                                    category,
                                    limit=5
                                )
                            
                            if alternatives:
                                st.success(f"✨ {messages.get('found_alternatives', 'Found')} {len(alternatives)} {messages.get('healthier_options', 'healthier options')}:")
                                
                                for i, alt in enumerate(alternatives, 1):
                                    with st.container():
                                        col_alt1, col_alt2 = st.columns([3, 1])
                                        
                                        with col_alt1:
                                            st.markdown(f"**{i}. {alt['product']}**")
                                            if alt.get('brand'):
                                                st.caption(f"🏷️ {alt['brand']}")
                                            
                                            # Show reason
                                            if alt.get('reason'):
                                                st.caption(f"📊 {alt['reason']}")
                                            
                                            # Show personalized note
                                            if alt.get('personalized_note'):
                                                st.caption(alt['personalized_note'])
                                        
                                        with col_alt2:
                                            # Health score badge
                                            alt_score = alt.get('health_score', 0)
                                            if alt_score >= 80:
                                                st.success(f"**{alt_score}**")
                                            elif alt_score >= 60:
                                                st.info(f"**{alt_score}**")
                                            else:
                                                st.warning(f"**{alt_score}**")
                                        
                                        st.divider()
                            else:
                                st.info(messages['alternatives_message'])
                        
                        except Exception as e:
                            st.error(f"Error fetching alternatives: {str(e)}")
                            st.info(messages['alternatives_message'])
                
            # Clear pending frame
            del st.session_state.pending_analysis_frame
            if 'pending_analysis_bbox' in st.session_state:
                del st.session_state.pending_analysis_bbox
            
            # Reset status after delay
            time.sleep(2)
            st.session_state.scan_status = 'searching'
            st.session_state.last_nutrition_snapshot = None
            st.rerun()
        
        # Manual capture button
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            if st.button(messages['manual_capture'], use_container_width=True, key="manual_capture_btn"):
                if ctx.video_processor:
                    processor = ctx.video_processor
                    if hasattr(processor, 'current_detections') and processor.current_detections:
                        st.session_state.scan_status = 'detected'
                        st.success(f"✅ {messages['product_detected']}")
                    else:
                        st.warning(messages['no_detection'])
                else:
                    st.warning(messages['camera_not_ready'])
        
        # Show barcode if detected
        if ctx.video_processor and hasattr(ctx.video_processor, 'barcode_data'):
            barcode_data = ctx.video_processor.barcode_data
            if barcode_data and barcode_data != st.session_state.last_barcode:
                st.session_state.last_barcode = barcode_data
                product_info = barcode_data.get('product_info')

                nutrition_client = _get_nutrition_client()
                nutrition_snapshot = nutrition_client.get_nutrition(
                    barcode=barcode_data.get('barcode'),
                    query=product_info.get('name') if product_info else None,
                    preferred_sources=_get_preferred_sources(st.session_state.region),
                )
                if nutrition_snapshot.get('source'):
                    st.session_state.last_nutrition_snapshot = nutrition_snapshot
                
                if product_info:
                    with st.expander(f"📊 {messages['barcode_detected']}: {barcode_data['barcode']}", expanded=True):
                        st.write(f"**{messages['product_name']}:** {product_info['name']}")
                        st.write(f"**{messages['brand']}:** {product_info['brands']}")
                        st.write(f"**{messages['nutrition_grade']}:** {product_info['nutrition_grade'].upper()}")
                        
                        if product_info.get('image_url'):
                            st.image(product_info['image_url'], width=200)

                        if nutrition_snapshot.get('source'):
                            st.info(
                                {
                                    'calories': nutrition_snapshot['raw'].get('calories') if nutrition_snapshot.get('raw') else None,
                                    'carbs': nutrition_snapshot['raw'].get('carbohydrates') if nutrition_snapshot.get('raw') else None,
                                    'fat': nutrition_snapshot['raw'].get('fat') if nutrition_snapshot.get('raw') else None,
                                    'protein': nutrition_snapshot['raw'].get('protein') if nutrition_snapshot.get('raw') else None,
                                    'sugar': nutrition_snapshot['raw'].get('sugars') if nutrition_snapshot.get('raw') else None,
                                    'source': nutrition_snapshot.get('source'),
                                }
                            )
                
        # Show analysis history
        if st.session_state.analysis_history:
            with st.expander(f"📜 {messages['history']} ({len(st.session_state.analysis_history)})", expanded=False):
                for idx, analysis in enumerate(reversed(st.session_state.analysis_history[-5:])):
                    st.markdown(f"**{idx+1}.** {analysis.get('product', 'Unknown')} - Score: {analysis.get('health_score', 'N/A')}")
                    
    else:
        st.info(messages.get('allow_camera', 'Allow camera access and refresh, or upload a photo below.'))
        st.markdown("</div>", unsafe_allow_html=True)
        with st.expander(messages.get('how_to_scan', 'How to scan')):
            st.markdown(messages.get('scan_instructions', '1) Allow camera • 2) Point to product • 3) Wait or upload below'))
        _render_upload_fallback()
        return


def _get_ui_messages(language: str = 'en') -> Dict[str, str]:
    """
    Get UI messages in specified language.
    
    Args:
        language: Language code (ar, en, fr)
        
    Returns:
        Dictionary of UI messages
    """
    messages = {
        'ar': {
            'live': 'مباشر',
            'searching': 'جارٍ البحث عن منتج...',
            'detected': 'منتج مُكتشف ✓',
            'analyzing': 'جارٍ التحليل...',
            'complete': 'اكتمل التحليل ✓',
            'flash': 'فلاش',
            'guides': 'إرشادات',
            'flash_tip': 'استخدم الفلاش في الإضاءة المنخفضة',
            'guide_tip': 'وجّه الكاميرا نحو ملصق المنتج للحصول على أفضل النتائج',
            'helper_text': 'وجّه الكاميرا نحو المنتج ليتم التحليل مباشرة',
            'analysis_complete': 'اكتمل التحليل',
            'ingredients': 'المكونات',
            'scanned_image': 'الصورة الممسوحة',
            'alternatives': 'بدائل صحية',
            'alternatives_message': 'نوصي بالبحث عن منتجات ذات درجة صحية أعلى من نفس الفئة',
            'found_alternatives': 'وجدنا',
            'healthier_options': 'خيارات أصح',
            'manual_capture': 'التقاط يدوي',
            'product_detected': 'تم اكتشاف منتج',
            'no_detection': 'لم يتم اكتشاف منتج. حاول توجيه الكاميرا بشكل أفضل',
            'camera_not_ready': 'الكاميرا غير جاهزة',
            'barcode_detected': 'باركود مكتشف',
            'product_name': 'اسم المنتج',
            'brand': 'العلامة التجارية',
            'nutrition_grade': 'الدرجة الغذائية',
            'history': 'السجل',
            'allow_camera': 'اسمح للمتصفح بالوصول إلى الكاميرا ليبدأ المسح تلقائيًا',
            'how_to_scan': 'كيفية المسح',
            'scan_instructions': '1) اسمح بالوصول للكاميرا  •  2) وجّه نحو المنتج  •  3) انتظر التحليل التلقائي أو اضغط زر الالتقاط',
            'nutrition_details': 'الحقائق الغذائية',
        },
        'en': {
            'live': 'LIVE',
            'searching': 'Searching for product...',
            'detected': 'Product Detected ✓',
            'analyzing': 'Analyzing...',
            'complete': 'Analysis Complete ✓',
            'flash': 'Flash',
            'guides': 'Guides',
            'flash_tip': 'Use flash in low light conditions',
            'guide_tip': 'Point camera at product label for best results',
            'helper_text': 'Point camera at product for automatic analysis',
            'analysis_complete': 'Analysis Complete',
            'ingredients': 'Ingredients',
            'scanned_image': 'Scanned Image',
            'alternatives': 'Healthy Alternatives',
            'alternatives_message': 'We recommend looking for products with higher health scores in the same category',
            'found_alternatives': 'Found',
            'healthier_options': 'healthier options',
            'manual_capture': 'Manual Capture',
            'product_detected': 'Product detected',
            'no_detection': 'No product detected. Try repositioning camera',
            'camera_not_ready': 'Camera not ready',
            'barcode_detected': 'Barcode Detected',
            'product_name': 'Product Name',
            'brand': 'Brand',
            'nutrition_grade': 'Nutrition Grade',
            'history': 'History',
            'allow_camera': 'Allow browser to access camera to start scanning',
            'how_to_scan': 'How to Scan',
            'scan_instructions': '1) Allow camera access  •  2) Point at product  •  3) Wait for auto-analysis or tap capture',
            'nutrition_details': 'Nutrition facts',
        },
        'fr': {
            'live': 'EN DIRECT',
            'searching': 'Recherche de produit...',
            'detected': 'Produit Détecté ✓',
            'analyzing': 'Analyse en cours...',
            'complete': 'Analyse Terminée ✓',
            'flash': 'Flash',
            'guides': 'Guides',
            'flash_tip': 'Utilisez le flash en cas de faible luminosité',
            'guide_tip': 'Pointez la caméra sur l\'étiquette du produit pour de meilleurs résultats',
            'helper_text': 'Pointez la caméra vers le produit pour une analyse automatique',
            'analysis_complete': 'Analyse Terminée',
            'ingredients': 'Ingrédients',
            'scanned_image': 'Image Scannée',
            'alternatives': 'Alternatives Saines',
            'alternatives_message': 'Nous recommandons de chercher des produits avec de meilleurs scores santé dans la même catégorie',            'found_alternatives': 'Trouvé',
            'healthier_options': 'options plus saines',            'manual_capture': 'Capture Manuelle',
            'product_detected': 'Produit détecté',
            'no_detection': 'Aucun produit détecté. Essayez de repositionner la caméra',
            'camera_not_ready': 'Caméra pas prête',
            'barcode_detected': 'Code-barres Détecté',
            'product_name': 'Nom du Produit',
            'brand': 'Marque',
            'nutrition_grade': 'Note Nutritionnelle',
            'history': 'Historique',
            'allow_camera': 'Autorisez le navigateur à accéder à la caméra pour commencer',
            'how_to_scan': 'Comment Scanner',
            'scan_instructions': '1) Autorisez l\'accès caméra  •  2) Pointez vers le produit  •  3) Attendez l\'analyse auto ou appuyez',
            'nutrition_details': 'Infos nutritionnelles',
        }
    }
    
    return messages.get(language, messages['en'])


def _render_upload_fallback() -> None:
    """Render file upload fallback when WebRTC not available."""
    messages = _get_ui_messages(st.session_state.get('language', 'ar'))
    
    st.markdown(f"### 📤 {messages.get('manual_capture', 'Upload Photo')}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        file = st.file_uploader(
            messages.get('helper_text', 'Choose a food image'), 
            type=["png", "jpg", "jpeg", "webp"]
        )
        
        if file:
            image = Image.open(file)
            st.image(image, use_container_width=True)
            
            if st.button(messages.get('analyzing', 'Analyze'), use_container_width=True):
                # Convert to bytes
                buf = BytesIO()
                image.save(buf, format="JPEG", quality=95)
                
                # Analyze
                provider = st.session_state.get("ai_provider", "gemini")
                
                with st.spinner(messages.get('analyzing', 'Analyzing') + "..."):
                    result = analyze_image_sync(buf.getvalue(), preferred_provider=provider)
                    
                    # Try barcode and OCR
                    barcode_scanner = get_barcode_scanner()
                    img_array = np.array(image)
                    
                    # Try barcode
                    barcode_data = barcode_scanner.scan_barcode(img_array)
                    if barcode_data:
                        st.success(f"📊 {messages.get('barcode_detected', 'Barcode')}: {barcode_data['barcode']}")
                        if barcode_data.get('product_info'):
                            result['barcode_info'] = barcode_data['product_info']

                        nutrition_client = _get_nutrition_client()
                        nutrition_snapshot = nutrition_client.get_nutrition(
                            barcode=barcode_data.get('barcode'),
                            query=barcode_data.get('product_info', {}).get('name') if barcode_data.get('product_info') else None,
                            preferred_sources=_get_preferred_sources(st.session_state.region),
                        )
                        if nutrition_snapshot.get('source'):
                            st.session_state.last_nutrition_snapshot = nutrition_snapshot
                            result['data_source'] = nutrition_snapshot.get('source')
                            result['nutrients'] = nutrition_snapshot.get('raw') or nutrition_snapshot
                    
                    # Try OCR
                    ocr_text = barcode_scanner.extract_text_ocr(img_array)
                    if ocr_text:
                        st.info(f"📝 OCR: {ocr_text[:200]}...")
                        
                        # Parse nutrition
                        nutrition = barcode_scanner.parse_nutrition_label(ocr_text)
                        if any(nutrition.values()):
                            result['ocr_nutrition'] = nutrition
                        
                        # Extract ingredients
                        ingredients = barcode_scanner.extract_ingredients_list(ocr_text)
                        if ingredients:
                            result['ocr_ingredients'] = ingredients

                    if not st.session_state.last_nutrition_snapshot and result.get('product'):
                        nutrition_client = _get_nutrition_client()
                        snapshot = nutrition_client.get_nutrition(
                            query=result.get('product'),
                            preferred_sources=_get_preferred_sources(st.session_state.region),
                        )
                        if snapshot.get('source'):
                            st.session_state.last_nutrition_snapshot = snapshot
                            result['data_source'] = snapshot.get('source')
                            result['nutrients'] = snapshot.get('raw') or snapshot
                    
                    # Save to history
                    st.session_state.analysis_history.append(result)

                    if st.session_state.health_sync_enabled and result.get('nutrients'):
                        health_sync = get_health_sync_service()
                        health_sync.sync_nutrition_entry(
                            user_id=st.session_state.get('user_id', 'anonymous'),
                            product=result.get('product', 'Unknown'),
                            nutrients=result.get('nutrients', {}),
                            source=result.get('data_source'),
                        )
                    
                    # Display results
                    st.success(f"✅ {messages.get('analysis_complete', 'Complete')}")
                    
                    st.subheader(result.get('product', 'Unknown Product'))
                    
                    # Health score
                    score = result.get('health_score', 50)
                    color = '#10b981' if score > 70 else ('#f59e0b' if score > 40 else '#ef4444')
                    st.markdown(f"""
                    <div style="font-size: 48px; font-weight: 800; color: {color};">
                        {score}/100
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show all data
                    with st.expander("📊 Full Analysis"):
                        st.json(result)
    
    with col2:
        st.info("""
        **Tips for better results:**
        - Good lighting
        - Clear label view
        - Steady camera
        - Close enough to read text
        """)
        
        if st.session_state.get('analysis_history'):
            st.markdown(f"**{messages.get('history', 'History')}:** {len(st.session_state.analysis_history)} scans")

