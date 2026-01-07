"""
Simplified Camera View with Separated Processing Logic
Modern, clean UI focused on core scanning functionality.
"""

from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Optional

import numpy as np
import streamlit as st
from PIL import Image

import os

try:
    from streamlit_webrtc import RTCConfiguration, WebRtcMode, webrtc_streamer

    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False


def _is_streamlit_cloud() -> bool:
    """Detect if running on Streamlit Cloud."""
    # Check common Streamlit Cloud indicators
    if os.path.exists("/mount/src"):
        return True
    if os.environ.get("STREAMLIT_RUNTIME"):
        return True
    return False


# Disable WebRTC on Cloud by default (unstable)
WEBRTC_ENABLED = WEBRTC_AVAILABLE and not _is_streamlit_cloud()

from app_config.settings import SUPPORTED_LANGUAGES
from database.db_manager import get_db_manager
from services.engine import analyze_image_sync
from services.video_processor import BioGuardVideoProcessor, get_video_processor_factory
from utils.i18n import get_lang, t


def render_camera_view() -> None:
    """
    Render simplified camera view with clear separation of concerns.
    """
    # Initialize session state
    _init_session_state()

    # Get UI messages
    lang = st.session_state.get("language", "en")
    messages = _get_messages(lang)

    # Inject minimal CSS
    _inject_minimal_css()

    # Main layout
    st.title(messages["title"])

    if not WEBRTC_ENABLED:
        st.info(messages["webrtc_unavailable"])
        _render_upload_interface(messages)
        return

    # Camera controls
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        scan_enabled = st.toggle(
            messages["enable_scanning"],
            value=st.session_state.scan_enabled,
            key="scan_toggle",
        )
        st.session_state.scan_enabled = scan_enabled

    with col3:
        if st.button(messages["capture"], width="stretch", type="primary"):
            st.session_state.manual_capture = True

    # WebRTC configuration
    rtc_config = RTCConfiguration(
        {
            "iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]},
            ]
        }
    )

    # Video constraints
    constraints = {
        "video": {
            "width": {"ideal": 1280},
            "height": {"ideal": 720},
            "frameRate": {"ideal": 15},
            "facingMode": "environment",
        },
        "audio": False,
    }

    # Status indicator
    status_placeholder = st.empty()
    _update_status(status_placeholder, st.session_state.scan_status, messages)

    # WebRTC streamer with video processor - wrapped in try/except for Cloud stability
    ctx = None
    try:
        ctx = webrtc_streamer(
            key="bioguard-camera",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc_config,
            media_stream_constraints=constraints,
            video_processor_factory=get_video_processor_factory(),
            desired_playing_state=True,
            async_processing=True,
        )
    except AttributeError as e:
        # Handle 'NoneType' object has no attribute 'is_alive' error on Cloud
        st.warning("📷 WebRTC unavailable. Please use the file upload option below.")
        ctx = None
    except Exception as e:
        st.error(f"Camera error: {str(e)[:50]}...")
        ctx = None

    # Process results if camera is active
    if ctx and ctx.state.playing and ctx.video_processor:
        processor: BioGuardVideoProcessor = ctx.video_processor

        # Update processor settings
        processor.toggle_scanning(st.session_state.scan_enabled)

        # Handle manual capture
        if st.session_state.manual_capture:
            st.session_state.manual_capture = False
            _handle_capture(processor, messages)

        # Check for detections
        detection_result = processor.get_detection_result(timeout=0.01)
        if detection_result:
            _display_detection_info(detection_result, messages)

        # Check for barcodes
        barcode_result = processor.get_barcode_result(timeout=0.01)
        if barcode_result:
            _display_barcode_info(barcode_result, messages)

        # Display stats in sidebar
        if st.sidebar.checkbox(messages["show_stats"], value=False):
            stats = processor.get_stats()
            st.sidebar.json(stats)

    elif ctx and not ctx.state.playing:
        st.info(messages["camera_permission"])

    # Display analysis history
    _display_history(messages)

    # Upload fallback
    with st.expander(messages["upload_option"], expanded=False):
        _render_upload_interface(messages)


def _init_session_state() -> None:
    """Initialize session state variables."""
    if "scan_status" not in st.session_state:
        st.session_state.scan_status = "idle"  # idle, detecting, analyzing, complete
    if "scan_enabled" not in st.session_state:
        st.session_state.scan_enabled = True
    if "manual_capture" not in st.session_state:
        st.session_state.manual_capture = False
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "last_barcode" not in st.session_state:
        st.session_state.last_barcode = None


def _inject_minimal_css() -> None:
    """Inject minimal, clean CSS for camera view."""
    st.markdown(
        """
    <style>
        /* Video container */
        [data-testid="stWebRtc"] video {
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            width: 100% !important;
            max-height: 60vh;
            object-fit: cover;
        }
        
        /* Status badge */
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
            margin: 10px 0;
        }
        
        .status-idle {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .status-detecting {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        .status-analyzing {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .status-complete {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: white;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        /* Detection card */
        .detection-card {
            background: var(--background-color);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            margin: 10px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
        
        /* Result container */
        .result-container {
            background: var(--background-color);
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            border: 2px solid var(--primary-color);
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def _update_status(placeholder, status: str, messages: Dict[str, str]) -> None:
    """Update status indicator."""
    status_class = f"status-{status}"
    status_text = messages.get(f"status_{status}", status.upper())
    status_icon = {
        "idle": "🔍",
        "detecting": "👁️",
        "analyzing": "🧠",
        "complete": "✅",
    }.get(status, "🔍")

    placeholder.markdown(
        f'<div class="status-badge {status_class}">{status_icon} {status_text}</div>',
        unsafe_allow_html=True,
    )


def _handle_capture(
    processor: BioGuardVideoProcessor, messages: Dict[str, str]
) -> None:
    """Handle manual capture and analysis."""
    st.session_state.scan_status = "analyzing"

    with st.spinner(messages["analyzing"]):
        # Capture frame
        captured_frame = processor.capture_frame()

        if captured_frame is None:
            st.warning(messages["no_detection"])
            st.session_state.scan_status = "idle"
            return

        # Convert to PIL Image
        frame_rgb = captured_frame
        if len(frame_rgb.shape) == 3 and frame_rgb.shape[2] == 3:
            # BGR to RGB
            frame_rgb = frame_rgb[:, :, ::-1]

        pil_image = Image.fromarray(frame_rgb)

        # Ensure RGB mode for JPEG (handle RGBA/P/LA modes)
        if pil_image.mode in ("RGBA", "LA") or (pil_image.mode == "P" and "transparency" in pil_image.info):
            pil_image = pil_image.convert("RGBA").convert("RGB")
        elif pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Convert to bytes
        img_byte_arr = BytesIO()
        pil_image.save(img_byte_arr, format="JPEG")
        image_bytes = img_byte_arr.getvalue()

        # Analyze with AI
        try:
            analysis_result = analyze_image_sync(image_bytes)

            # Save to history
            st.session_state.analysis_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "result": analysis_result,
                    "image": pil_image,
                }
            )

            # Save to database if authenticated
            if st.session_state.get("authenticated"):
                db = get_db_manager()
                db.save_analysis(
                    user_id=st.session_state.get("user_profile", {}).get(
                        "email", "guest"
                    ),
                    analysis_data=analysis_result,
                    image_bytes=image_bytes,
                )

            st.session_state.scan_status = "complete"

            # Display result
            _display_analysis_result(analysis_result, pil_image, messages)

        except Exception as e:
            st.error(f"{messages['analysis_error']}: {str(e)}")
            st.session_state.scan_status = "idle"


def _display_detection_info(result: Dict[str, Any], messages: Dict[str, str]) -> None:
    """Display detection information."""
    detections = result.get("detections", [])

    if detections:
        st.session_state.scan_status = "detecting"

        with st.expander(
            f"{messages['detections_found']}: {len(detections)}", expanded=False
        ):
            for i, detection in enumerate(detections[:3]):  # Show top 3
                st.markdown(
                    f"""
                <div class="detection-card">
                    <strong>{i+1}.</strong> {detection.object_type} 
                    <span style="color: var(--primary-color);">
                        ({detection.confidence:.0%})
                    </span>
                </div>
                """,
                    unsafe_allow_html=True,
                )
    else:
        st.session_state.scan_status = "idle"


def _display_barcode_info(result: Dict[str, Any], messages: Dict[str, str]) -> None:
    """Display barcode scan result."""
    barcode = result.get("barcode", "")

    if barcode and barcode != st.session_state.last_barcode:
        st.session_state.last_barcode = barcode

        with st.expander(
            f"📊 {messages['barcode_detected']}: {barcode}", expanded=True
        ):
            product_info = result.get("product_info")

            if product_info:
                col1, col2 = st.columns([1, 2])

                with col1:
                    if product_info.get("image_url"):
                        st.image(product_info["image_url"], width=150)

                with col2:
                    st.markdown(
                        f"**{messages['product_name']}:** {product_info.get('name', 'N/A')}"
                    )
                    st.markdown(
                        f"**{messages['brand']}:** {product_info.get('brands', 'N/A')}"
                    )

                    grade = product_info.get("nutrition_grade", "unknown").upper()
                    st.markdown(f"**{messages['nutrition_grade']}:** {grade}")


def _display_analysis_result(
    analysis: Dict[str, Any], image: Image.Image, messages: Dict[str, str]
) -> None:
    """Display comprehensive analysis result with full nutrition cards."""
    st.markdown('<div class="result-container">', unsafe_allow_html=True)

    st.success(f"✅ {messages['analysis_complete']}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(image, caption=messages["captured_image"], width="stretch")

    with col2:
        # Health score with visual indicator
        health_score = analysis.get("health_score", "N/A")
        verdict = analysis.get("verdict", "UNKNOWN")
        
        # Color code the verdict
        verdict_color = {"SAFE": "🟢", "WARNING": "🟡", "DANGER": "🔴"}.get(verdict, "⚪")
        st.metric(messages["health_score"], f"{health_score} {verdict_color}")

        # Product name if available
        product = analysis.get("product", "")
        if product and product not in ["Gemini Vision", "OpenAI Vision", "Mock Snack"]:
            st.markdown(f"**{t('product_name')}:** {product}")

    # Summary card
    if "summary" in analysis:
        with st.expander(f"📋 {t('analysis_complete')}", expanded=True):
            st.info(analysis["summary"])

    # Nutrition Facts card
    nutrients = analysis.get("nutrients", {})
    if nutrients:
        with st.expander(f"🍎 {t('nutrition_facts')}", expanded=True):
            nut_cols = st.columns(3)
            nutrient_display = [
                ("calories", "🔥", "kcal"),
                ("carbohydrates", "🍞", "g"),
                ("fat", "🧈", "g"),
                ("protein", "🥩", "g"),
                ("sugars", "🍬", "g"),
                ("sodium", "🧂", "mg"),
            ]
            for i, (key, icon, unit) in enumerate(nutrient_display):
                val = nutrients.get(key, "N/A")
                if val != "N/A":
                    with nut_cols[i % 3]:
                        st.metric(f"{icon} {key.title()}", f"{val}{unit}")

    # Why this score
    why_score = analysis.get("why_score", "")
    if why_score:
        with st.expander(f"❓ {t('why_score')}", expanded=False):
            st.write(why_score)
    elif analysis.get("warnings"):
        # Generate why from warnings
        with st.expander(f"❓ {t('why_score')}", expanded=False):
            warnings_list = analysis.get("warnings", [])
            if isinstance(warnings_list, list) and warnings_list:
                st.write("Score based on: " + ", ".join(str(w)[:50] for w in warnings_list[:3]))

    # Warnings
    warnings = analysis.get("warnings", [])
    if warnings and isinstance(warnings, list):
        with st.expander(f"⚠️ {t('warnings')}", expanded=True):
            for w in warnings:
                if isinstance(w, str) and w.strip():
                    st.warning(w[:200])

    # Ingredients
    if "ingredients" in analysis:
        with st.expander(f"📜 {messages['ingredients']}", expanded=False):
            st.write(analysis["ingredients"])

    # Recommendations
    if "recommendations" in analysis:
        with st.expander(f"💡 {t('recommendations')}", expanded=False):
            recs = analysis["recommendations"]
            if isinstance(recs, list):
                for rec in recs:
                    st.markdown(f"• {rec}")
            else:
                st.write(recs)

    st.markdown("</div>", unsafe_allow_html=True)


def _display_history(messages: Dict[str, str]) -> None:
    """Display analysis history."""
    if st.session_state.analysis_history:
        with st.expander(
            f"📜 {messages['history']} ({len(st.session_state.analysis_history)})",
            expanded=False,
        ):
            for idx, item in enumerate(
                reversed(st.session_state.analysis_history[-5:])
            ):
                result = item.get("result", {})
                timestamp = item.get("timestamp", "")

                col1, col2 = st.columns([1, 3])

                with col1:
                    if "image" in item:
                        st.image(item["image"], width=100)

                with col2:
                    st.markdown(f"**{idx+1}.** {timestamp[:19]}")
                    st.markdown(f"Score: {result.get('health_score', 'N/A')}")


def _render_upload_interface(messages: Dict[str, str]) -> None:
    """Render image upload fallback interface."""
    st.markdown(f"### {messages['upload_title']}")
    st.caption(messages["upload_caption"])

    uploaded_file = st.file_uploader(
        messages["choose_file"],
        type=["jpg", "jpeg", "png"],
        help=messages["upload_help"],
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption=messages["uploaded_image"], width="stretch")

        if st.button(
            messages["analyze_button"], type="primary", width="stretch"
        ):
            with st.spinner(messages["analyzing"]):
                try:
                    # Ensure RGB mode for JPEG (handle RGBA/P/LA modes)
                    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                        image = image.convert("RGBA").convert("RGB")
                    elif image.mode != "RGB":
                        image = image.convert("RGB")

                    # Convert to bytes
                    img_byte_arr = BytesIO()
                    image.save(img_byte_arr, format="JPEG")
                    image_bytes = img_byte_arr.getvalue()

                    # Analyze
                    analysis_result = analyze_image_sync(image_bytes)

                    # Save to history
                    st.session_state.analysis_history.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "result": analysis_result,
                            "image": image,
                        }
                    )

                    # Display result
                    _display_analysis_result(analysis_result, image, messages)

                    st.success(messages["upload_success"])

                except Exception as e:
                    st.error(f"{messages['analysis_error']}: {str(e)}")


def _get_messages(language: str = "en") -> Dict[str, str]:
    """Get UI messages in specified language."""

    messages_en = {
        "title": "📸 Smart Camera",
        "webrtc_unavailable": "Camera module not available. Please use upload option below.",
        "enable_scanning": "Enable Auto-Scan",
        "capture": "📸 Capture & Analyze",
        "camera_permission": "Please allow camera access to start scanning.",
        "show_stats": "Show Statistics",
        "status_idle": "Ready to Scan",
        "status_detecting": "Detecting...",
        "status_analyzing": "Analyzing...",
        "status_complete": "Complete",
        "analyzing": "Analyzing image...",
        "no_detection": "No product detected. Please point camera at a product.",
        "analysis_error": "Analysis error",
        "detections_found": "Objects Detected",
        "barcode_detected": "Barcode",
        "product_name": "Product",
        "brand": "Brand",
        "nutrition_grade": "Grade",
        "analysis_complete": "Analysis Complete",
        "captured_image": "Captured Image",
        "health_score": "Health Score",
        "summary": "Summary",
        "ingredients": "Ingredients",
        "recommendations": "Recommendations",
        "history": "Recent Scans",
        "upload_option": "📤 Or Upload Image",
        "upload_title": "Upload Image",
        "upload_caption": "Upload a photo of the product for analysis",
        "choose_file": "Choose an image",
        "upload_help": "Supports JPG, JPEG, PNG",
        "uploaded_image": "Your Image",
        "analyze_button": "Analyze Image",
        "upload_success": "Image analyzed successfully!",
    }

    messages_ar = {
        "title": "📸 كاميرا ذكية",
        "webrtc_unavailable": "وحدة الكاميرا غير متوفرة. يرجى استخدام خيار الرفع أدناه.",
        "enable_scanning": "تفعيل المسح التلقائي",
        "capture": "📸 التقاط وتحليل",
        "camera_permission": "يرجى السماح بالوصول للكاميرا لبدء المسح.",
        "show_stats": "عرض الإحصائيات",
        "status_idle": "جاهز للمسح",
        "status_detecting": "جارٍ الكشف...",
        "status_analyzing": "جارٍ التحليل...",
        "status_complete": "اكتمل",
        "analyzing": "جارٍ تحليل الصورة...",
        "no_detection": "لم يتم اكتشاف منتج. يرجى توجيه الكاميرا نحو منتج.",
        "analysis_error": "خطأ في التحليل",
        "detections_found": "كائنات مكتشفة",
        "barcode_detected": "باركود",
        "product_name": "المنتج",
        "brand": "العلامة التجارية",
        "nutrition_grade": "الدرجة",
        "analysis_complete": "اكتمل التحليل",
        "captured_image": "الصورة الملتقطة",
        "health_score": "النتيجة الصحية",
        "summary": "الملخص",
        "ingredients": "المكونات",
        "recommendations": "التوصيات",
        "history": "المسوحات الأخيرة",
        "upload_option": "📤 أو رفع صورة",
        "upload_title": "رفع صورة",
        "upload_caption": "ارفع صورة المنتج للتحليل",
        "choose_file": "اختر صورة",
        "upload_help": "يدعم JPG, JPEG, PNG",
        "uploaded_image": "صورتك",
        "analyze_button": "تحليل الصورة",
        "upload_success": "تم تحليل الصورة بنجاح!",
    }

    return messages_ar if language == "ar" else messages_en
