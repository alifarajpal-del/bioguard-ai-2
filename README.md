# 🇵🇸 BioGuard AI - Smart Health Guardian

<div align="center">

![BioGuard AI Logo](https://img.shields.io/badge/BioGuard-AI-00bcd4?style=for-the-badge&logo=heart&logoColor=white)
![Made in Palestine](https://img.shields.io/badge/Made%20in-Palestine%20🇵🇸-007a3d?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.0.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-red?style=for-the-badge)

**نظام ذكي لتحليل المنتجات الغذائية والتقارير الطبية، صُمم بأيدي فلسطينية 🇵🇸**

*An intelligent system for food and medical analysis, built by Palestinian hands to empower community health awareness.*

[العربية](#العربية) | [English](#english) | [Français](#français)

</div>

---

## 🌟 Features | المميزات

### 🎥 LiveVision Real-Time Scanner | ماسح الرؤية الحية **NEW!**
- **Continuous Scanning**: Auto-detection and analysis (no manual capture needed)
- **Barcode Reader**: Instant product lookup via OpenFoodFacts API
- **OCR Text Extraction**: Read nutrition labels and ingredients
- **AR Overlay HUD**: Real-time detection boxes and status indicators
- **Health Conflict Detection**: Cross-reference with user profile
- **Multilingual Support**: 5 languages (Arabic, English, French, Spanish, German)
- **Auto-Translation**: AI-powered result translation

### 📸 AI-Powered Food Scanner | ماسح الطعام الذكي
- Instant product analysis using GPT-4o Vision and Gemini
- Health score calculation (0-100)
- NOVA food classification
- Personalized warnings based on medical profile
- Healthy alternatives suggestions

### 🗂️ Medical File Vault | الخزنة الطبية
- Upload and store medical documents (PDF, X-rays, Lab results)
- AI-powered document summarization
- Secure local SQLite storage
- Category organization (X-Ray, Lab, Prescription, Report)

### 📊 Health Dashboard | لوحة التحكم الصحية
- Interactive charts with Plotly
- Nutrition tracking (Carbs, Fats, Sodium)
- Product safety breakdown (Safe/Warning/Danger)
- Historical scan analysis

### 💬 Smart Health Chat | الدردشة الصحية الذكية
- Context-aware AI responses
- Considers user's medical profile
- Integrates medical vault summaries
- Multi-language support (EN, AR, FR)

### 🔒 Privacy & Security | الخصوصية والأمان
- Local SQLite database (offline-capable)
- No sensitive data sharing
- Hashed password storage
- FHIR-ready architecture

---

## 🚀 Quick Start | البدء السريع

### Prerequisites | المتطلبات
```bash
Python 3.8+
OpenAI API Key (or Google Gemini API Key)

# System Dependencies for LiveVision
# Windows:
choco install tesseract
conda install -c conda-forge zbar

# Linux:
sudo apt-get install tesseract-ocr tesseract-ocr-ara libzbar0

# macOS:
brew install tesseract tesseract-lang zbar
```

### Installation | التثبيت
```bash
# Clone the repository
git clone https://github.com/AliRiyadFaraj/bioguard-ai.git
cd bioguard-ai

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (IMPORTANT!)
cp .env.example .env
# Edit .env and add your API keys (see SECURITY_SETUP.md)

# Generate JWT secret for production
python -c 'import secrets; print(secrets.token_urlsafe(32))'
# Add the output to JWT_SECRET_KEY in .env

# Run automated setup (checks system dependencies)
python setup_livevision.py

# Run the application
streamlit run main.py
```

### LiveVision Setup | إعداد الرؤية الحية
For detailed LiveVision configuration and troubleshooting, see [LIVEVISION_INTEGRATION.md](LIVEVISION_INTEGRATION.md).

### ⚠️ Security Note | ملاحظة أمنية
**Never commit sensitive data to git!** See [SECURITY_SETUP.md](SECURITY_SETUP.md) for detailed configuration guide.

All API keys and secrets must be set via environment variables. The application will:
- Raise an error if `JWT_SECRET_KEY` is missing in production
- Show warnings when using development defaults
- Fall back to mock AI responses if API keys are not configured

### For Streamlit Cloud | للنشر على Streamlit Cloud
Add to your Streamlit Cloud secrets (Settings → Secrets):
```toml
OPENAI_API_KEY = "sk-your-actual-key"
GEMINI_API_KEY = "your-actual-key"
JWT_SECRET_KEY = "your-generated-secret"
ENVIRONMENT = "production"
```

---

## 📁 Project Structure | هيكل المشروع

```
bioguard-ai/
├── main.py                      # Main application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (not in repo)
├── .env.example                # Template for environment setup
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── SECURITY_SETUP.md           # Security configuration guide
├── LIVEVISION_INTEGRATION.md   # LiveVision documentation (NEW!)
├── setup_livevision.py         # Automated setup script (NEW!)
├── yolov8n.pt                  # YOLO object detection model
├── bioguard.db                 # SQLite database (auto-created, not in repo)
├── config/
│   ├── __init__.py
│   └── settings.py             # Environment-based configuration
├── database/
│   ├── __init__.py
│   └── db_manager.py           # Database operations (SQLite + ChromaDB + NetworkX)
├── models/
│   ├── __init__.py
│   └── schemas.py              # Pydantic data models
├── services/
│   ├── __init__.py
│   ├── auth.py                 # Authentication & JWT
│   ├── auth_privacy.py         # Privacy & FHIR integration
│   ├── engine.py               # AI vision analysis engine
│   ├── graph_engine.py         # Knowledge graph for health conflicts
│   ├── digital_twin.py         # Digital twin predictions
│   ├── live_vision.py          # Real-time vision processing
│   ├── barcode_scanner.py      # Barcode scanning & OCR (NEW!)
│   └── translation.py          # Multi-language translation (NEW!)
├── ui_components/
│   ├── __init__.py
│   ├── navigation.py           # Sidebar navigation
│   ├── dashboard_view.py       # Health dashboard
│   ├── camera_view.py          # LiveVision camera interface (UPDATED!)
│   ├── vault_view.py           # Medical vault
│   └── theme_wheel.py          # Theme customization
├── utils/
│   ├── __init__.py
│   └── helpers.py              # Utility functions
├── prompts/
│   └── system_prompts.py       # AI system prompts
├── logs/
│   └── bioguard.log            # Application logs (auto-created)
└── .streamlit/
    └── secrets.toml            # Streamlit secrets (not in repo)
```

---

## 🛠️ Tech Stack | التقنيات المستخدمة

| Technology | Purpose |
|------------|---------|
| **Streamlit** | Web UI Framework |
| **OpenAI GPT-4o** | AI Vision & Chat |
| **Google Gemini 1.5** | Alternative AI Vision Provider |
| **SQLite** | Local Relational Database |
| **ChromaDB** | Vector Database for Semantic Search |
| **NetworkX** | Knowledge Graph for Health Conflicts |
| **PyMuPDF** | PDF Processing |
| **Plotly** | Interactive Charts |
| **Pillow** | Image Processing |
| **YOLOv8** | Object Detection |
| **PyZBar** | Barcode Scanning (NEW!) |
| **Tesseract** | OCR Text Extraction (NEW!) |
| **streamlit-webrtc** | Real-time Video Streaming (NEW!) |

---

## 🇵🇸 About the Developer | عن المطور

<div align="center">

### 👨‍💻 Ali Riyad Faraj
**Location:** Palestine 🇵🇸

*"In the face of challenges, technology becomes a bridge to better health awareness for our community."*

*"في مواجهة التحديات، تصبح التكنولوجيا جسراً للوعي الصحي الأفضل لمجتمعنا."*

</div>

---

## ⚠️ Disclaimer | إخلاء المسؤولية

> **English:** This application (BioGuard AI) is a technical effort by developer Ali Riyad Faraj, intended for educational and awareness purposes only. Given the health situation specifics in Palestine, it is always advisable to consult certified Palestinian medical centers before making any medical decision based on AI analysis.

> **العربية:** هذا التطبيق (BioGuard AI) هو جهد تقني من المبرمج علي رياض فرج، وهو مخصص للأغراض التعليمية والتوعوية فقط. نظراً لخصوصية الحالة الصحية في فلسطين، يُنصح دائماً بمراجعة المراكز الطبية الفلسطينية المعتمدة قبل اتخاذ أي قرار طبي بناءً على تحليلات الذكاء الاصطناعي.

---

## 📜 License | الرخصة

```
Copyright © 2024-2025 Ali Riyad Faraj. All Rights Reserved.

This software is proprietary and confidential.
Unauthorized copying, modification, distribution, or use of this software,
via any medium, is strictly prohibited.
```

---

## 🤝 Support Palestine | ادعم فلسطين

<div align="center">

🇵🇸 **Free Palestine** 🇵🇸

*This project is dedicated to the resilient people of Palestine.*

</div>

---

<div align="center">

**Made with ❤️ in Palestine 🇵🇸**

![Palestinian Flag](https://img.shields.io/badge/🇵🇸-Free%20Palestine-black?style=flat-square&labelColor=white)

</div>
