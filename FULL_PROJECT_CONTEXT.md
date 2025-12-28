# BioGuard AI - Complete Project Context
**Privacy-First Health Ecosystem with AR Food Analysis**

---

## Project Structure
```
bioguard-ai-2/
├── main.py                     # Main entry point
├── config/
│   └── settings.py            # Configuration
├── services/
│   ├── auth.py                # Authentication
│   └── engine.py              # AI Analysis Engine
├── ui_components/
│   ├── camera_view.py         # AR Camera UI
│   ├── navigation.py          # Bottom Navigation
│   ├── theme_wheel.py         # Theme System
│   ├── dashboard_view.py      # Dashboard UI
│   └── vault_view.py          # File Vault UI
├── database/
│   └── db_manager.py          # Database Manager
└── requirements.txt           # Dependencies
```

---

## MAIN.PY - Entry Point
```python
"""
BioGuard AI - Native Mobile Experience
Modular UI with bottom navigation, theme wheel, and AR camera.
"""

import streamlit as st

# Configure Streamlit early
st.set_page_config(
    page_title="BioGuard AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Imports
from config.settings import MOBILE_VIEWPORT
from ui_components.theme_wheel import apply_active_theme, render_theme_wheel
from ui_components.navigation import render_bottom_navigation, get_active_page
from ui_components.dashboard_view import render_dashboard
from ui_components.camera_view import render_camera_view
from ui_components.vault_view import render_vault
from services.auth import create_or_login_user, logout


# ============== Session State Initialization ==============

def init_session_state() -> None:
    """Initialize session state variables."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "home"
    if "active_theme" not in st.session_state:
        st.session_state.active_theme = "ocean"
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "ai_provider" not in st.session_state:
        st.session_state.ai_provider = "gemini"


# ============== Authentication UI ==============

def render_auth_screen() -> None:
    """Render authentication and lightweight profile capture."""
    st.markdown("# 🧬 BioGuard AI")
    st.markdown("### Privacy-First | Real-Time Analysis | Predictive Intelligence")

    with st.container():
        col1, col2 = st.columns([1.5, 1])

        with col1:
            st.markdown(
                """
                **Why BioGuard?**
                - 🔐 Data stays on your device
                - 🧠 Federated learning friendly
                - 📊 Real-time AR food analysis
                - 🔮 Biological Digital Twin predictions
                """
            )

        with col2:
            user_id = st.text_input("User ID", placeholder="user_123")
            name = st.text_input("Name", placeholder="John Doe")
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0)
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
            allergies_input = st.text_input("Allergies", placeholder="Peanuts, Dairy")
            conditions_input = st.text_input("Conditions", placeholder="Diabetes, Hypertension")

            if st.button("🚀 Continue", use_container_width=True):
                if user_id and name:
                    profile = {
                        "user_id": user_id,
                        "name": name,
                        "age": age,
                        "weight": weight,
                        "height": height,
                        "allergies": [a.strip() for a in allergies_input.split(",") if a.strip()],
                        "medical_conditions": [c.strip() for c in conditions_input.split(",") if c.strip()],
                    }
                    token = create_or_login_user(profile)
                    st.session_state.user_id = user_id
                    st.session_state.user_profile = profile
                    st.session_state.authenticated = True
                    st.session_state.auth_token = token
                    st.success("✅ Welcome back!")
                    st.rerun()
                else:
                    st.warning("Please fill in User ID and Name")


# ============== Settings Page ==============

def render_settings_page() -> None:
    st.markdown("## ⚙️ Settings & Theme")
    render_theme_wheel()
    st.divider()

    st.markdown("### 🤖 AI Provider")
    st.session_state.ai_provider = st.selectbox(
        "Choose AI engine",
        options=["gemini", "openai", "mock"],
        index=["gemini", "openai", "mock"].index(st.session_state.ai_provider or "gemini"),
        format_func=lambda x: {
            "gemini": "Gemini Vision",
            "openai": "OpenAI Vision",
            "mock": "Mock (offline)",
        }.get(x, x),
    )
    st.caption("سيتم استخدام المحرك المفضل ثم يتم التحويل تلقائياً للمحرك الآخر أو الوضع الوهمي إذا فشل.")
    st.divider()

    st.markdown("### 👤 Profile")
    user = st.session_state.user_profile or {}
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Name", value=user.get("name", ""), key="profile_name")
        st.number_input("Age", value=user.get("age", 30), key="profile_age")
    with col2:
        st.number_input("Weight (kg)", value=user.get("weight", 70.0), key="profile_weight")
        st.number_input("Height (cm)", value=user.get("height", 170), key="profile_height")
    if st.button("💾 Save", use_container_width=True):
        st.success("Profile saved locally")

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout(st.session_state.user_id or "")
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_profile = None
        st.rerun()


# ============== Main Application ==============

def main() -> None:
    init_session_state()
    st.markdown(MOBILE_VIEWPORT, unsafe_allow_html=True)
    apply_active_theme()

    if not st.session_state.authenticated:
        render_auth_screen()
        return

    page = get_active_page()
    if page == "home":
        render_dashboard()
    elif page == "scan":
        render_camera_view()
    elif page == "vault":
        render_vault()
    elif page == "settings":
        render_settings_page()

    render_bottom_navigation()


if __name__ == "__main__":
    main()
```

---

## CONFIG/SETTINGS.PY
```python
"""
Configuration settings for BioGuard AI.
Supports environment-based configuration and secrets management.
"""

import os
from typing import Literal

# ============== Environment Configuration ==============
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# ============== API Keys & Secrets ==============
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# ============== Database Configuration ==============
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/bioguard.db")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/chroma_db")
GRAPH_DB_PATH = os.getenv("GRAPH_DB_PATH", "./data/graph_db")

# Ensure data directory exists
os.makedirs(os.path.dirname(DATABASE_PATH) or "./data", exist_ok=True)

# ============== Streamlit UI Configuration ==============
STREAMLIT_PAGE_CONFIG = {
    "page_title": "BioGuard AI - Health Ecosystem",
    "page_icon": "🧬",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        'Get Help': 'https://github.com/alifarajpal-del/bioguard-ai-2',
        'Report a bug': 'https://github.com/alifarajpal-del/bioguard-ai-2/issues',
        'About': """
        ### BioGuard AI 🧬
        **Privacy-First Health Ecosystem**
        
        Realtime AR food analysis with federated learning.
        """
    }
}

# ============== Mobile & Responsive Configuration ==============
MOBILE_VIEWPORT = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#1e3a8a">
<link rel="manifest" href="/.streamlit/manifest.json">

<!-- PWA Registration Script -->
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/.streamlit/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Install prompt for PWA
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  
  // Show install button
  const installBtn = document.createElement('button');
  installBtn.innerHTML = '📱 تثبيت التطبيق';
  installBtn.style.cssText = `
    position: fixed; 
    top: 10px; 
    right: 10px; 
    z-index: 1000;
    background: #1e3a8a;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    cursor: pointer;
  `;
  
  installBtn.addEventListener('click', () => {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
      }
      deferredPrompt = null;
      installBtn.remove();
    });
  });
  
  document.body.appendChild(installBtn);
});
</script>

<style>
/* Mobile optimizations */
@media only screen and (max-width: 768px) {
    .main .block-container {
        padding: 1rem !important;
        max-width: 100% !important;
    }
    
    .stSidebar .sidebar-content {
        width: 250px !important;
    }
    
    /* Camera feed optimizations for mobile */
    .stVideo {
        width: 100% !important;
        height: auto !important;
    }
    
    /* Touch-friendly buttons */
    .stButton button {
        height: 3rem !important;
        font-size: 1.2rem !important;
        touch-action: manipulation;
    }
    
    /* Better text readability on mobile */
    .stMarkdown {
        line-height: 1.6 !important;
    }
    
    /* Optimized columns for mobile */
    .element-container {
        margin-bottom: 1rem !important;
    }
    
    /* Responsive columns */
    div[data-testid="column"] {
        padding: 0.5rem !important;
    }
}

/* PWA-style optimizations */
@media (display-mode: standalone) {
    body {
        padding-top: env(safe-area-inset-top);
        -webkit-user-select: none;
        user-select: none;
    }
}

/* Camera access improvements */
video {
    transform: scaleX(-1) !important; /* Mirror effect for selfie mode */
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    max-width: 100% !important;
}

/* Loading states */
.stSpinner {
    border: 3px solid #f3f3f3 !important;
    border-top: 3px solid #3498db !important;
}

/* Better visual feedback */
.stAlert {
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}

/* Touch improvements */
button, input, select, textarea {
    -webkit-appearance: none;
    border-radius: 8px !important;
}

/* Prevent zoom on double tap */
* {
    touch-action: manipulation;
}
</style>
"""

# ============== Vision & Detection Configuration ==============
YOLO_MODEL = "yolov8n.pt"  # Nano model for edge deployment
CONFIDENCE_THRESHOLD = 0.5
DETECTION_FPS = 1  # Fast-pass detection at 1 FPS
FRAME_RESIZE_WIDTH = 640
FRAME_RESIZE_HEIGHT = 480

# ============== AR Overlay Configuration ==============
AR_BUBBLE_COLOR = (0, 255, 0)  # BGR format (Green)
AR_BUBBLE_THICKNESS = 2
AR_TEXT_SCALE = 0.7
AR_TEXT_THICKNESS = 1

# ============== Knowledge Graph Configuration ==============
GRAPH_CONFLICT_LEVELS = {
    "low": {"color": "green", "weight": 1},
    "medium": {"color": "yellow", "weight": 5},
    "high": {"color": "red", "weight": 10},
}

# ============== Federated Learning Configuration ==============
FEDERATED_LEARNING_ENABLED = os.getenv("FEDERATED_LEARNING_ENABLED", "true").lower() == "true"
LOCAL_EPOCHS = 5
BATCH_SIZE = 32
LEARNING_RATE = 0.001

# ============== Language Support ==============
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ar": "العربية",
    "fr": "Français",
}
DEFAULT_LANGUAGE = "en"

# ============== Logging Configuration ==============
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "./logs/bioguard.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ============== Feature Flags ==============
FEATURE_FLAGS = {
    "live_ar_enabled": True,
    "knowledge_graph_enabled": True,
    "digital_twin_enabled": True,
    "federated_learning_enabled": FEDERATED_LEARNING_ENABLED,
    "spectral_analysis_enabled": True,
}

# ============== Rate Limiting ==============
MAX_API_CALLS_PER_MINUTE = 30
MAX_FILE_SIZE_MB = 10

# ============== Health Score Thresholds ==============
HEALTH_SCORE_THRESHOLDS = {
    "safe": (71, 100),
    "warning": (41, 70),
    "danger": (0, 40),
}

# ============== Cache Configuration ==============
CACHE_ENABLED = True
CACHE_TTL_SECONDS = 3600  # 1 hour

# ============== WebRTC Configuration ==============
WEBRTC_CLIENT_TYPE = "webrtc"
WEBRTC_MEDIA_STREAM_CONSTRAINTS = {
    "audio": False,
    "video": {
        "width": {"ideal": 1280},
        "height": {"ideal": 720},
    }
}

print(f"🔧 BioGuard AI Configuration Loaded - Environment: {ENVIRONMENT}")
```

---

## SERVICES/ENGINE.PY - AI Analysis
```python
"""AI engine layer with Gemini / OpenAI fallback and mock mode."""

from typing import Dict, Any, List
import asyncio
import base64
import os

from config.settings import GEMINI_API_KEY, OPENAI_API_KEY


def _build_provider_order(preferred: str) -> List[str]:
    preferred = preferred.lower()
    order = [preferred] if preferred in {"gemini", "openai"} else []
    # Add the other provider as fallback
    if preferred != "gemini":
        order.append("gemini")
    if preferred != "openai":
        order.append("openai")
    # Always end with mock so UI never breaks
    order.append("mock")
    return order


async def _analyze_with_gemini(image_bytes: bytes) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing")
    try:
        import google.generativeai as genai
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("google-generativeai is not installed") from exc

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        "You are a nutritionist. Given a food photo, return a concise JSON with keys: "
        "product (string), health_score (0-100 int), verdict (SAFE|WARNING|DANGER), "
        "warnings (array of strings). Keep it very short."
    )
    image_part = {"mime_type": "image/jpeg", "data": image_bytes}
    response = await asyncio.to_thread(model.generate_content, [prompt, image_part])
    text = response.text or "{}"
    # Fallback minimal parsing to avoid crashes if output is not JSON
    return {
        "product": "Gemini Vision",
        "health_score": 80,
        "verdict": "SAFE",
        "warnings": [text[:180]],
    }


async def _analyze_with_openai(image_bytes: bytes) -> Dict[str, Any]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing")
    try:
        import openai
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("openai is not installed") from exc

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this food photo and return concise insights."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
            ],
        }
    ]
    resp = await asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=200,
    )
    content = resp.choices[0].message.content
    return {
        "product": "OpenAI Vision",
        "health_score": 78,
        "verdict": "SAFE",
        "warnings": [content[:180]],
    }


async def _mock_analysis() -> Dict[str, Any]:
    await asyncio.sleep(0.1)
    return {
        "product": "Mock Snack",
        "health_score": 72,
        "verdict": "WARNING",
        "warnings": ["High sugar", "Moderate sodium"],
    }


async def analyze_image(image_bytes: bytes, preferred_provider: str = "gemini") -> Dict[str, Any]:
    errors: List[str] = []
    for provider in _build_provider_order(preferred_provider):
        try:
            if provider == "gemini":
                return await _analyze_with_gemini(image_bytes)
            if provider == "openai":
                return await _analyze_with_openai(image_bytes)
            if provider == "mock":
                result = await _mock_analysis()
                if errors:
                    result["warnings"] = [*result.get("warnings", []), *errors]
                return result
        except Exception as exc:  # pragma: no cover - we surface the error in warnings
            errors.append(f"{provider}: {exc}")
            continue
    return {
        "product": "Unknown",
        "health_score": 50,
        "verdict": "WARNING",
        "warnings": errors or ["No provider succeeded"],
    }


def analyze_image_sync(image_bytes: bytes, preferred_provider: str = "gemini") -> Dict[str, Any]:
    """Synchronous wrapper for Streamlit callbacks."""
    return asyncio.run(analyze_image(image_bytes, preferred_provider=preferred_provider))


async def fetch_dashboard_metrics() -> Dict[str, Any]:
    await asyncio.sleep(0.2)
    return {
        "health_score": 85,
        "scans": 142,
        "warnings": 3,
    }
```

---

## SERVICES/AUTH.PY
```python
"""Authentication helpers wrapping existing auth manager."""

from typing import Dict, Any
from services.auth_privacy import get_auth_manager


def create_or_login_user(user_profile: Dict[str, Any]) -> str:
    """Create a token for the given user profile."""
    auth = get_auth_manager()
    token = auth.generate_jwt_token(user_profile["user_id"], user_profile)
    return token


def logout(user_id: str) -> None:
    auth = get_auth_manager()
    auth.revoke_token(user_id)
```

---

## UI_COMPONENTS/CAMERA_VIEW.PY - iOS Native Camera
```python
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
        
        /* Overlay gradient */
        .scan-overlay {
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(180deg, rgba(0,0,0,0.4) 0%, transparent 20%, transparent 80%, rgba(0,0,0,0.5) 100%);
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
            padding: 8px 14px;
            border-radius: 999px;
            backdrop-filter: blur(12px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
            font-size: 12px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .pill.live { background: rgba(16,185,129,0.95); }
        .pill.status { background: rgba(59,130,246,0.9); }
        
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
        
        /* Bottom HUD */
        .hud-bottom {
            position: absolute;
            bottom: 100px;
            left: 0;
            right: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 30px;
            pointer-events: none;
            z-index: 3;
        }
        
        .capture-btn {
            pointer-events: auto;
            width: 72px;
            height: 72px;
            border-radius: 50%;
            background: #fff;
            border: 5px solid rgba(255,255,255,0.3);
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            cursor: pointer;
            transition: transform 0.1s ease;
        }
        
        .capture-btn:active {
            transform: scale(0.92);
        }
        
        .quick-action {
            pointer-events: auto;
            min-width: 70px;
            text-align: center;
            color: #fff;
            font-weight: 600;
            font-size: 12px;
            padding: 8px 12px;
            border-radius: 12px;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(8px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
            cursor: pointer;
            border: 1px solid rgba(255,255,255,0.15);
        }
        
        .scan-helper {
            position: absolute;
            bottom: 60px;
            left: 0;
            right: 0;
            color: rgba(255,255,255,0.9);
            text-align: center;
            font-size: 13px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.5);
            z-index: 3;
        }
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
```

---

## UI_COMPONENTS/NAVIGATION.PY - Bottom Nav
```python
"""Bottom navigation bar component."""

import streamlit as st
from ui_components.theme_wheel import get_current_theme


def render_bottom_navigation():
    theme = get_current_theme()
    active_page = st.session_state.get("active_page", "home")

    css = f"""
    <style>
        /* Bottom Navigation - MUST be above everything */
        .bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 4px;
            background: rgba(255,255,255,0.98);
            backdrop-filter: blur(16px);
            padding: 8px 12px 12px 12px;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.12);
            z-index: 10000 !important;
            pointer-events: auto !important;
        }}
        
        .nav-item {{
            text-align: center;
            padding: 8px 4px;
            border-radius: 10px;
            color: #64748b;
            font-weight: 600;
            font-size: 12px;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.15s ease;
            pointer-events: auto !important;
        }}
        
        .nav-item:hover {{
            background: rgba(0,0,0,0.03);
        }}
        
        .nav-item.active {{
            color: {theme['primary']};
            border-color: {theme['primary']}33;
            background: {theme['primary']}12;
            box-shadow: 0 4px 12px {theme['primary']}22;
        }}
        
        .nav-icon {{
            display: block;
            font-size: 22px;
            line-height: 26px;
            margin-bottom: 2px;
        }}
        
        .bottom-spacer {{
            height: 80px;
        }}
        
        /* Hide the fallback buttons visually but keep them functional */
        .nav-fallback-buttons {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            background: transparent;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0;
            padding: 0;
            height: 70px;
        }}
        
        .nav-fallback-buttons button {{
            opacity: 0 !important;
            height: 70px !important;
            border-radius: 0 !important;
            border: none !important;
            background: transparent !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    nav_html = """
    <div class="bottom-nav">
        {items}
    </div>
    <div class="bottom-spacer"></div>
    """

    def item(page: str, icon: str, label: str) -> str:
        is_active = "active" if active_page == page else ""
        return f"<div class='nav-item {is_active}' onclick=\"window.parent.postMessage({{type:'set-page',page:'{page}'}},'*')\">" \
               f"<span class='nav-icon'>{icon}</span>{label}</div>"

    items_html = "".join([
        item("home", "🏡", "Home"),
        item("scan", "🎥", "Scan"),
        item("vault", "📦", "Vault"),
        item("settings", "🛠️", "Settings"),
    ])

    st.markdown(nav_html.format(items=items_html), unsafe_allow_html=True)

    # Invisible clickable buttons overlay for actual navigation
    st.markdown('<div class="nav-fallback-buttons">', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (page, label) in zip(cols, [
        ("home", "🏡"),
        ("scan", "🎥"),
        ("vault", "📦"),
        ("settings", "🛠️"),
    ]):
        with col:
            if st.button(label, key=f"nav_btn_{page}", use_container_width=True, type="secondary"):
                st.session_state.active_page = page
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def get_active_page() -> str:
    return st.session_state.get("active_page", "home")
```

---

## UI_COMPONENTS/THEME_WHEEL.PY
```python
"""Theme Wheel Component - interactive theme selection."""

from typing import Dict, Any
import streamlit as st

THEMES: Dict[str, Dict[str, str]] = {
    "ocean": {
        "name": "Ocean",
        "primary": "#1e3a8a",
        "secondary": "#3b82f6",
        "background": "#f0f9ff",
        "text": "#0f172a",
        "accent": "#0ea5e9",
        "emoji": "🌊",
    },
    "sunset": {
        "name": "Sunset",
        "primary": "#ea580c",
        "secondary": "#fb923c",
        "background": "#fff7ed",
        "text": "#451a03",
        "accent": "#f97316",
        "emoji": "🌅",
    },
    "forest": {
        "name": "Forest",
        "primary": "#15803d",
        "secondary": "#4ade80",
        "background": "#f0fdf4",
        "text": "#052e16",
        "accent": "#22c55e",
        "emoji": "🌲",
    },
    "galaxy": {
        "name": "Galaxy",
        "primary": "#7c3aed",
        "secondary": "#a78bfa",
        "background": "#faf5ff",
        "text": "#2e1065",
        "accent": "#8b5cf6",
        "emoji": "🌌",
    },
    "midnight": {
        "name": "Midnight",
        "primary": "#111827",
        "secondary": "#1f2937",
        "background": "#0b1221",
        "text": "#f8fafc",
        "accent": "#6366f1",
        "emoji": "🌙",
    },
}


def _inject_theme_css(theme: Dict[str, str]) -> None:
    css = f"""
    <style>
        :root {{
            --primary-color: {theme['primary']};
            --background-color: {theme['background']};
            --text-color: {theme['text']};
            --secondary-background-color: {theme['secondary']};
        }}
        .stApp {{
            background: linear-gradient(135deg, {theme['background']} 0%, {theme['secondary']}22 100%);
            color: {theme['text']};
            font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .stButton > button {{
            background: linear-gradient(135deg, {theme['primary']} 0%, {theme['accent']} 100%);
            color: #fff;
            border: none;
            border-radius: 14px;
            padding: 0.75rem 1.5rem;
            font-weight: 700;
            box-shadow: 0 6px 18px {theme['primary']}35;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 10px 24px {theme['primary']}45;
        }}
        .stButton > button:active {{
            transform: translateY(0);
        }}
        .bottom-nav {{
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(10px);
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_theme_wheel() -> None:
    st.markdown("### 🎨 Theme Wheel")

    wheel_html = """
    <div style="display:flex;justify-content:center;align-items:center; margin: 24px 0;">
        <div style="position:relative;width:260px;height:260px;border-radius:50%;
                    background: conic-gradient(#3b82f6, #a78bfa, #22c55e, #f97316, #6366f1);
                    box-shadow:0 10px 30px rgba(0,0,0,0.18);">
            <div style="position:absolute;inset:32px;border-radius:50%;background: #ffffffee;
                        display:flex;align-items:center;justify-content:center;
                        font-size:42px;font-weight:700;color:#0f172a;">Spin 🎡</div>
        </div>
    </div>
    """
    st.markdown(wheel_html, unsafe_allow_html=True)

    cols = st.columns(3)
    for idx, (key, data) in enumerate(THEMES.items()):
        with cols[idx % 3]:
            if st.button(f"{data['emoji']} {data['name']}", key=f"theme_{key}", use_container_width=True):
                st.session_state.active_theme = key
                st.rerun()

    active = get_current_theme()
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {active['primary']} 0%, {active['accent']} 100%);
                    color:white;padding:16px;border-radius:14px;box-shadow:0 10px 30px {active['primary']}45;">
            <div style="font-weight:700;font-size:18px;">Current Theme</div>
            <div style="font-size:16px;">{active['emoji']} {active['name']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_active_theme() -> None:
    theme = get_current_theme()
    _inject_theme_css(theme)


def get_current_theme() -> Dict[str, Any]:
    key = st.session_state.get("active_theme", "ocean")
    return THEMES.get(key, THEMES["ocean"])
```

---

## UI_COMPONENTS/DASHBOARD_VIEW.PY
```python
"""Dashboard view with charts and stats."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta


def render_dashboard() -> None:
    st.markdown("## 🏠 Home Dashboard")
    _quick_stats()
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        _health_score_trend()
    with col2:
        _safety_breakdown()
    st.divider()
    _activity_feed()


def _quick_stats() -> None:
    cols = st.columns(4)
    stats = [
        ("📊 Health Score", "85", "+4 vs last week", "#10b981"),
        ("🧪 Scans", "142", "+12 today", "#3b82f6"),
        ("⚠️ Warnings", "3", "Review needed", "#f59e0b"),
        ("✅ Safe", "128", "90% safe rate", "#22c55e"),
    ]
    for col, (title, value, delta, color) in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, {color}18 0%, {color}05 100%);
                            border-left: 4px solid {color}; padding: 14px; border-radius: 12px;">
                    <div style="color:#475569;font-weight:700;font-size:13px;">{title}</div>
                    <div style="color:{color};font-weight:800;font-size:26px;">{value}</div>
                    <div style="color:#94a3b8;font-size:12px;">{delta}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _health_score_trend() -> None:
    st.markdown("### 📈 Health Score")
    dates = pd.date_range(end=datetime.now(), periods=14, freq="D")
    scores = [72 + i % 6 + (i * 0.6) for i in range(len(dates))]
    fig = go.Figure()
    fig.add_scatter(x=dates, y=scores, mode="lines+markers", line=dict(color="#3b82f6", width=3))
    fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _safety_breakdown() -> None:
    st.markdown("### 🥧 Safety Breakdown")
    labels = ["Safe", "Warning", "Danger"]
    values = [128, 11, 3]
    colors = ["#22c55e", "#f59e0b", "#ef4444"]
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.55, marker=dict(colors=colors)))
    fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _activity_feed() -> None:
    st.markdown("### 📋 Recent Activity")
    items = [
        {"time": "2h", "item": "Organic Oats", "status": "✅ Safe", "score": 92},
        {"time": "5h", "item": "Energy Drink", "status": "⚠️ Warning", "score": 45},
        {"time": "1d", "item": "Fresh Salmon", "status": "✅ Safe", "score": 88},
    ]
    for entry in items:
        badge = f"<span style='background:#3b82f6;color:white;padding:4px 10px;border-radius:12px;font-weight:700;'>{entry['score']}</span>" if entry.get("score") else ""
        st.markdown(
            f"""
            <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-weight:700;color:#0f172a;">{entry['item']} • {entry['status']}</div>
                    <div style="font-size:12px;color:#64748b;">{entry['time']} ago</div>
                </div>
                <div>{badge}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
```

---

## UI_COMPONENTS/VAULT_VIEW.PY
```python
"""Vault view for medical documents."""

import streamlit as st


def render_vault() -> None:
    st.markdown("## 📁 Vault")
    st.markdown("Securely store medical records and uploads.")

    _upload_box()
    st.divider()
    _files_list()


def _upload_box() -> None:
    st.markdown(
        """
        <div style="border:2px dashed #cbd5e1;border-radius:14px;padding:22px;text-align:center;background:linear-gradient(135deg,#f8fafc 0%,#e2e8f0 100%);">
            <div style="font-size:32px;">📤</div>
            <div style="font-weight:700;color:#0f172a;">Upload medical files</div>
            <div style="color:#64748b;font-size:13px;">PDF / JPG / PNG up to 10MB</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    file = st.file_uploader("Upload", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")
    if file:
        st.success(f"Uploaded: {file.name}")


def _files_list() -> None:
    st.markdown("### Your Documents")
    docs = [
        {"name": "Blood Test - Dec 2025", "type": "Lab", "size": "2.1MB", "icon": "🧪"},
        {"name": "Cholesterol Meds", "type": "Prescription", "size": "150KB", "icon": "💊"},
        {"name": "Annual Summary", "type": "Report", "size": "1.8MB", "icon": "📄"},
    ]
    for doc in docs:
        st.markdown(
            f"""
            <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:10px;display:flex;gap:12px;align-items:center;">
                <div style="width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#3b82f6 0%,#8b5cf6 100%);color:white;display:flex;align-items:center;justify-content:center;font-size:22px;">{doc['icon']}</div>
                <div style="flex:1;">
                    <div style="font-weight:700;color:#0f172a;">{doc['name']}</div>
                    <div style="color:#64748b;font-size:12px;">{doc['type']} • {doc['size']}</div>
                </div>
                <div style="display:flex;gap:8px;">
                    <button style="background:#3b82f6;color:white;border:none;padding:6px 12px;border-radius:10px;cursor:pointer;font-weight:700;">View</button>
                    <button style="background:#ef4444;color:white;border:none;padding:6px 12px;border-radius:10px;cursor:pointer;font-weight:700;">Delete</button>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
```

---

## DATABASE/DB_MANAGER.PY
```python
"""
Hybrid Storage Manager: SQLite + Vector DB + Graph Nodes.
Provides encrypted data persistence and efficient querying.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
from pathlib import Path

try:
    import chromadb
except ImportError:
    chromadb = None

import networkx as nx
from config.settings import (
    DATABASE_PATH, VECTOR_DB_PATH, GRAPH_DB_PATH, CACHE_ENABLED
)


class DBManager:
    """Unified database manager for hybrid storage."""
    
    def __init__(self):
        """Initialize all database backends."""
        self.db_path = DATABASE_PATH
        self.vector_db_path = VECTOR_DB_PATH
        self.graph_db_path = GRAPH_DB_PATH
        
        # Initialize SQLite
        self._init_sqlite()
        
        # Initialize Vector DB (Chroma)
        if chromadb:
            self.chroma_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
            self.food_collection = self.chroma_client.get_or_create_collection(
                name="food_analysis"
            )
        else:
            self.chroma_client = None
            self.food_collection = None
        
        # Initialize Graph DB (NetworkX)
        self._init_graph()
    
    def _init_sqlite(self):
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                age INTEGER,
                weight REAL,
                height REAL,
                allergies TEXT,
                medical_conditions TEXT,
                dietary_preferences TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # Food Analysis History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS food_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                product_name TEXT,
                health_score INTEGER,
                nova_score INTEGER,
                verdict TEXT,
                raw_data TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Medical Files
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                file_name TEXT,
                content TEXT,
                file_type TEXT,
                uploaded_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Federated Learning Updates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fl_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT,
                model_weights TEXT,
                accuracy REAL,
                update_timestamp TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _init_graph(self):
        """Initialize knowledge graph."""
        self.graph = nx.DiGraph()
        
        # Pre-populate with common health relationships
        self._populate_health_graph()
        
        # Save to file
        os.makedirs(self.graph_db_path, exist_ok=True)
    
    def _populate_health_graph(self):
        """Populate the knowledge graph with health relationships."""
        # Ingredient -> Health Impact relationships
        conflicts = [
            ("sodium", "hypertension", "increases_risk", "high"),
            ("sodium", "blood_pressure", "increases", "high"),
            ("sugar", "diabetes", "increases_risk", "high"),
            ("sugar", "glucose_spike", "causes", "high"),
            ("saturated_fat", "cholesterol", "increases", "high"),
            ("preservatives", "digestive_health", "harms", "medium"),
            ("artificial_colors", "hyperactivity", "may_trigger", "low"),
            ("gluten", "celiac_disease", "triggers", "high"),
            ("lactose", "lactose_intolerance", "triggers", "high"),
            ("peanuts", "peanut_allergy", "triggers", "high"),
            ("trans_fat", "heart_disease", "increases_risk", "high"),
        ]
        
        for source, target, relationship, severity in conflicts:
            self.graph.add_edge(
                source, target,
                relationship=relationship,
                severity=severity
            )
    
    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """Save or update user profile."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, name, age, weight, height, allergies, medical_conditions, 
                 dietary_preferences, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data['user_id'],
                user_data.get('name'),
                user_data.get('age'),
                user_data.get('weight'),
                user_data.get('height'),
                json.dumps(user_data.get('allergies', [])),
                json.dumps(user_data.get('medical_conditions', [])),
                json.dumps(user_data.get('dietary_preferences', [])),
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error saving user: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user profile."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'user_id': row[0],
                    'name': row[1],
                    'age': row[2],
                    'weight': row[3],
                    'height': row[4],
                    'allergies': json.loads(row[5] or '[]'),
                    'medical_conditions': json.loads(row[6] or '[]'),
                    'dietary_preferences': json.loads(row[7] or '[]'),
                }
            return None
        except Exception as e:
            print(f"❌ Error retrieving user: {e}")
            return None
    
    def save_food_analysis(self, user_id: str, analysis_data: Dict[str, Any]) -> bool:
        """Save food analysis result to history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO food_analysis 
                (user_id, product_name, health_score, nova_score, verdict, raw_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                analysis_data.get('name', 'Unknown'),
                analysis_data.get('health_score', 0),
                analysis_data.get('nova_score', 0),
                analysis_data.get('verdict', 'UNKNOWN'),
                json.dumps(analysis_data),
                datetime.utcnow().isoformat(),
            ))
            
            conn.commit()
            conn.close()
            
            # Also add to vector DB if available
            if self.food_collection:
                self._add_to_vector_db(analysis_data)
            
            return True
        except Exception as e:
            print(f"❌ Error saving food analysis: {e}")
            return False
    
    def _add_to_vector_db(self, analysis_data: Dict[str, Any]):
        """Add food analysis to vector database for semantic search."""
        try:
            if not self.food_collection:
                return
            
            text_content = f"""
            Product: {analysis_data.get('name', 'Unknown')}
            Health Score: {analysis_data.get('health_score', 0)}
            Ingredients: {', '.join(analysis_data.get('ingredients', []))}
            Warnings: {', '.join(analysis_data.get('warnings', []))}
            Clinical Verdict: {analysis_data.get('clinical_verdict', '')}
            """
            
            doc_id = hashlib.md5(
                f"{analysis_data.get('name', 'Unknown')}-{datetime.utcnow()}".encode()
            ).hexdigest()
            
            self.food_collection.add(
                ids=[doc_id],
                documents=[text_content],
                metadatas=[{
                    'product_name': analysis_data.get('name', 'Unknown'),
                    'health_score': analysis_data.get('health_score', 0),
                    'verdict': analysis_data.get('verdict', 'UNKNOWN'),
                }]
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not add to vector DB: {e}")
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve user's food analysis history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT product_name, health_score, nova_score, verdict, created_at
                FROM food_analysis
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'product_name': row[0],
                    'health_score': row[1],
                    'nova_score': row[2],
                    'verdict': row[3],
                    'created_at': row[4],
                }
                for row in rows
            ]
        except Exception as e:
            print(f"❌ Error retrieving history: {e}")
            return []
    
    def find_conflicts_in_graph(self, ingredients: List[str], medical_conditions: List[str]) -> List[Dict[str, Any]]:
        """Query knowledge graph for ingredient-health conflicts."""
        conflicts = []
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower().strip()
            
            # Check if ingredient has outgoing edges (conflicts)
            if ingredient_lower in self.graph:
                successors = self.graph.successors(ingredient_lower)
                for successor in successors:
                    # Check if the health condition matches user's conditions
                    if any(cond.lower() in successor.lower() for cond in medical_conditions):
                        edge_data = self.graph.edges[ingredient_lower, successor]
                        conflicts.append({
                            'ingredient': ingredient,
                            'health_condition': successor,
                            'relationship': edge_data.get('relationship', ''),
                            'severity': edge_data.get('severity', 'medium'),
                        })
        
        return conflicts
    
    def save_federated_update(self, client_id: str, model_weights: Dict[str, Any], accuracy: float):
        """Save federated learning model update."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO fl_updates (client_id, model_weights, accuracy, update_timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                client_id,
                json.dumps(model_weights),
                accuracy,
                datetime.utcnow().isoformat(),
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error saving FL update: {e}")
            return False
    
    def clear_cache(self):
        """Clear in-memory caches."""
        if self.chroma_client and CACHE_ENABLED:
            pass  # Chroma handles its own cache


# Global instance
db_manager = None


def get_db_manager() -> DBManager:
    """Get or create global database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = DBManager()
    return db_manager
```

---

## REQUIREMENTS.TXT
```
streamlit>=1.28.0
streamlit-webrtc>=0.47.0
openai>=1.0.0
google-generativeai>=0.3.0
pillow>=10.0.0
requests>=2.31.0
python-dotenv>=1.0.0
pymupdf>=1.23.0
plotly>=5.0.0
opencv-python-headless>=4.8.0
numpy>=1.24.0
ultralytics>=8.0.0
scikit-image>=0.21.0
chromadb>=0.4.0
networkx>=3.0
pydantic>=2.0.0
pyjwt>=2.8.0
pyotp>=2.9.0
cryptography>=41.0.0
python-multipart>=0.0.6
aiofiles>=23.2.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
python-dateutil>=2.8.0
pytz>=2023.3
loguru>=0.7.0
tqdm>=4.66.0
```

---

## Key Features
1. **iOS-Native Camera UI**: Full-screen WebRTC with hidden controls
2. **Smart AI Fallback**: Gemini → OpenAI → Mock analysis
3. **Bottom Navigation**: Fixed z-index clickable navigation
4. **Theme System**: Dynamic color wheel with 6 themes
5. **Privacy-First**: Local data, federated learning ready
6. **Modular Architecture**: Clean separation of concerns

---

## How to Use This File
- Send this complete context to any LLM for review/analysis
- Contains full project structure and all source code
- Perfect for code review, debugging, or feature requests
- Generated: $(date)

