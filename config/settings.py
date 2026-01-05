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

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "concise-perigee-468806-m8")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501/auth/google/callback")

# Apple OAuth Configuration
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID", "")
APPLE_TEAM_ID = os.getenv("APPLE_TEAM_ID", "")
APPLE_KEY_ID = os.getenv("APPLE_KEY_ID", "")
APPLE_PRIVATE_KEY = os.getenv("APPLE_PRIVATE_KEY", "")  # Base64 encoded .p8 file content
APPLE_REDIRECT_URI = os.getenv("APPLE_REDIRECT_URI", "http://localhost:8501/auth/apple/callback")

# JWT Secret Key - MUST be set in production
_jwt_secret = os.getenv("JWT_SECRET_KEY")
if not _jwt_secret:
    if ENVIRONMENT == "production":
        raise ValueError(
            "JWT_SECRET_KEY environment variable must be set in production. "
            "Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )
    else:
        # Development fallback
        _jwt_secret = "dev-secret-key-not-for-production"
        print("⚠️ Warning: Using development JWT secret. Set JWT_SECRET_KEY for production.")

JWT_SECRET_KEY = _jwt_secret
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

# ============== Environment-Specific Settings ==============
if ENVIRONMENT == "production":
    MAX_API_CALLS_PER_MINUTE = int(os.getenv("MAX_API_CALLS_PER_MINUTE", "60"))
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "7200"))  # 2 hours in production
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
else:
    # Development settings - more permissive
    MAX_API_CALLS_PER_MINUTE = int(os.getenv("MAX_API_CALLS_PER_MINUTE", "100"))
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "1800"))  # 30 minutes in dev
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))

# ============== Language Support ==============
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ar": "العربية",
    "fr": "Français",
    "es": "Español",
    "de": "Deutsch",
}
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

# ============== Auto-Translation ==============
AUTO_TRANSLATE_RESULTS = os.getenv("AUTO_TRANSLATE_RESULTS", "true").lower() == "true"
TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY", "")  # Google Translate API key

# ============== Logging Configuration ==============
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "./logs/bioguard.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ============== Feature Flags ==============
FEATURE_FLAGS = {
    "live_ar_enabled": os.getenv("FEATURE_LIVE_AR_ENABLED", "true").lower() == "true",
    "knowledge_graph_enabled": os.getenv("FEATURE_KNOWLEDGE_GRAPH_ENABLED", "true").lower() == "true",
    "digital_twin_enabled": os.getenv("FEATURE_DIGITAL_TWIN_ENABLED", "true").lower() == "true",
    "federated_learning_enabled": FEDERATED_LEARNING_ENABLED,
    "spectral_analysis_enabled": os.getenv("FEATURE_SPECTRAL_ANALYSIS_ENABLED", "true").lower() == "true",
}

# ============== Rate Limiting ==============
# Note: MAX_API_CALLS_PER_MINUTE is set above based on environment

# ============== Health Score Thresholds ==============
HEALTH_SCORE_THRESHOLDS = {
    "safe": (71, 100),
    "warning": (41, 70),
    "danger": (0, 40),
}

# ============== Cache Configuration ==============
# Note: CACHE_ENABLED and CACHE_TTL_SECONDS are set above based on environment

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
