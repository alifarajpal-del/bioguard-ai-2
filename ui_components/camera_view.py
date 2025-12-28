"""Full-screen AR camera view with WebRTC fix and AI analysis."""

from typing import Any, Dict
from io import BytesIO

import numpy as np
import streamlit as st
from PIL import Image

try:
    from streamlit_webrtc import webrtc_streamer, RTCConfiguration, WebRtcMode
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    st.warning("⚠️ streamlit-webrtc is not installed. Camera view will use upload fallback.")

from services.engine import analyze_image_sync


def _inject_camera_css() -> None:
    css = """
    <style>
        /* Fullscreen scan stage */
        .scan-stage { position: relative; width: 100vw; height: calc(100vh - 90px); margin-left: calc(-50vw + 50%); margin-top: -1.5rem; overflow: hidden; background: #000; }
        .scan-stage [data-testid="stWebRtc"] { position: absolute; inset: 0; }
        .scan-stage video { position: absolute !important; inset: 0; width: 100% !important; height: 100% !important; object-fit: cover !important; border-radius: 0 !important; }
        .scan-overlay { position: absolute; inset: 0; pointer-events: none; background: linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.55) 100%); }
        .hud-top { position: absolute; top: 18px; left: 18px; right: 18px; display: flex; justify-content: space-between; align-items: center; gap: 10px; color: #fff; font-weight: 700; pointer-events: none; }
        .pill { padding: 10px 14px; border-radius: 999px; backdrop-filter: blur(8px); box-shadow: 0 6px 20px rgba(0,0,0,0.25); font-size: 13px; display: inline-flex; align-items: center; gap: 8px; }
        .pill.live { background: rgba(16,185,129,0.9); }
        .pill.status { background: rgba(59,130,246,0.85); }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: #fff; animation: blink 1.6s ease-in-out infinite; }
        @keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.35;} }
        .hud-bottom { position: absolute; bottom: 22px; left: 0; right: 0; display: flex; align-items: center; justify-content: center; gap: 24px; pointer-events: none; }
        .capture-btn { pointer-events: auto; width: 78px; height: 78px; border-radius: 50%; background: #fff; border: 6px solid #3b82f6; box-shadow: 0 12px 32px rgba(0,0,0,0.35); display:flex;align-items:center;justify-content:center; font-size: 28px; cursor: pointer; }
        .capture-btn:active { transform: scale(0.95); }
        .quick-action { pointer-events: auto; min-width: 82px; text-align: center; color: #e2e8f0; font-weight: 600; font-size: 13px; padding: 10px 12px; border-radius: 14px; background: rgba(0,0,0,0.55); box-shadow: 0 8px 24px rgba(0,0,0,0.3); cursor: pointer; border: 1px solid rgba(255,255,255,0.12); }
        [data-testid="stWebRtc"] button { display: none !important; }
        .scan-helper { margin-top: 0.25rem; color: #cbd5e1; text-align: center; font-size: 13px; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_camera_view() -> None:
    _inject_camera_css()

    if not WEBRTC_AVAILABLE:
        _render_upload_fallback()
        return

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
    ctx = webrtc_streamer(
        key="bioguard-ar",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_config,
        media_stream_constraints=constraints,
        desired_playing_state=True,  # auto-start without pressing the button
        video_html_attrs={"autoPlay": True, "playsInline": True, "controls": False, "muted": True},
        async_processing=True,
    )

    hud_html = """
    <div class="scan-overlay"></div>
    <div class="hud-top">
        <div class="pill live"><span class="dot"></span>LIVE</div>
        <div class="pill status">Scanning for food...</div>
    </div>
    <div class="hud-bottom">
        <div class="quick-action" onclick="console.log('flash toggle')">Flash</div>
        <div class="capture-btn" onclick="console.log('capture')">⬤</div>
        <div class="quick-action" onclick="console.log('guides')">Guides</div>
    </div>
    <div class="scan-helper">وجّه الكاميرا نحو المنتج ليتم التحليل مباشرة</div>
    </div>
    """

    analysis_box = st.empty()

    if ctx and ctx.state.playing:
        st.markdown(hud_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            if st.button("تحليل اللقطة الآن", use_container_width=True):
                if ctx.video_receiver is None:
                    st.warning("لا يمكن التقاط إطار الآن. جرب مجدداً.")
                else:
                    frame = ctx.video_receiver.get_frame(timeout=1)
                    if frame is None:
                        st.warning("لم أستطع الحصول على إطار من الكاميرا.")
                    else:
                        np_frame = frame.to_ndarray(format="rgb24")
                        image = Image.fromarray(np_frame)
                        buf = BytesIO()
                        image.save(buf, format="JPEG", quality=90)
                        provider = st.session_state.get("ai_provider", "gemini")
                        result = analyze_image_sync(buf.getvalue(), preferred_provider=provider)
                        st.session_state.analysis_history.append(result)
                        analysis_box.success(f"تم التحليل عبر {provider.title()}.")
                        analysis_box.json(result)
    else:
        st.info("اسمح للمتصفح بالوصول إلى الكاميرا ليبدأ المسح تلقائيًا.")
        st.markdown("</div>", unsafe_allow_html=True)
        with st.expander("How to scan"):
            st.markdown(
                "1) Allow camera access  •  2) Aim at food/labels  •  3) Tap the capture button for insights"
            )
        return


def _render_upload_fallback() -> None:
    st.markdown("### 📤 Upload a photo")
    file = st.file_uploader("Choose a food image", type=["png", "jpg", "jpeg", "webp"])
    if file:
        st.image(file, use_container_width=True)
        if st.button("Analyze", use_container_width=True):
            st.success("Analysis complete (mock)")
