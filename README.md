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

### 📸 AI-Powered Food Scanner | ماسح الطعام الذكي
- Instant product analysis using GPT-4o Vision
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
OpenAI API Key
```

### Installation | التثبيت
```bash
# Clone the repository
git clone https://github.com/AliRiyadFaraj/bioguard-ai.git
cd bioguard-ai

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
OPENAI_API_KEY=your_api_key_here

# Run the application
streamlit run app.py
```

### For Streamlit Cloud | للنشر على Streamlit Cloud
Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your_api_key_here"
```

---

## 📁 Project Structure | هيكل المشروع

```
bioguard-ai/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── bioguard.db           # SQLite database (auto-created, not in repo)
└── .streamlit/
    └── secrets.toml      # Streamlit secrets (not in repo)
```

---

## 🛠️ Tech Stack | التقنيات المستخدمة

| Technology | Purpose |
|------------|---------|
| **Streamlit** | Web UI Framework |
| **OpenAI GPT-4o** | AI Vision & Chat |
| **SQLite** | Local Database |
| **PyMuPDF** | PDF Processing |
| **Plotly** | Interactive Charts |
| **Pillow** | Image Processing |

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
