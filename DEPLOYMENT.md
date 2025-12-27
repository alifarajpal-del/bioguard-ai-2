# 🚀 دليل النشر - BioGuard AI

## النشر على Streamlit Cloud (مجاني)

### الخطوات السريعة:

1. **أنشئ حساب على GitHub** (إذا لم يكن لديك)
   - اذهب إلى: https://github.com
   - سجّل حساب جديد

2. **أنشئ مستودع جديد (Repository)**
   - اضغط على "New repository"
   - اسم المستودع: `bioguard-ai` (أو أي اسم تريده)
   - اختر "Public" أو "Private"
   - لا تضع README أو .gitignore (موجود بالفعل)

3. **ارفع الكود إلى GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - BioGuard AI"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/bioguard-ai.git
   git push -u origin main
   ```

4. **النشر على Streamlit Cloud**
   - اذهب إلى: https://share.streamlit.io
   - سجّل دخول بحساب GitHub
   - اضغط "New app"
   - اختر المستودع: `bioguard-ai`
   - Main file path: `app.py`
   - اضغط "Deploy"

5. **إضافة مفتاح OpenAI API**
   - بعد النشر، اذهب إلى "Settings" → "Secrets"
   - أضف:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```
   - احفظ

6. **الرابط جاهز!**
   - سيكون الرابط: `https://YOUR_APP_NAME.streamlit.app`
   - يمكنك مشاركته مع المستثمرين

---

## النشر على Streamlit Community Cloud (الأسهل)

### طريقة بديلة أسرع:

1. **ارفع الكود إلى GitHub** (الخطوات 1-3 أعلاه)

2. **استخدم Streamlit Community Cloud**
   - اذهب إلى: https://streamlit.io/cloud
   - اضغط "Get started"
   - سجّل بحساب GitHub
   - اختر المستودع و `app.py`
   - أضف Secrets (OPENAI_API_KEY)
   - اضغط Deploy

---

## ملاحظات مهمة:

✅ **الملفات المطلوبة موجودة:**
- `app.py` ✓
- `requirements.txt` ✓
- `.streamlit/config.toml` ✓
- `.streamlit/secrets.toml.example` ✓

⚠️ **تأكد من:**
- إضافة `OPENAI_API_KEY` في Secrets بعد النشر
- أن المستودع على GitHub هو Public (أو أنك أضفت Streamlit كمساهم)
- أن `app.py` موجود في الجذر (root) للمستودع

---

## رابط سريع للنشر:

👉 **Streamlit Cloud:** https://share.streamlit.io
👉 **Streamlit Community Cloud:** https://streamlit.io/cloud

---

## بعد النشر:

1. الرابط سيكون: `https://YOUR_APP-NAME.streamlit.app`
2. شارك الرابط مع المستثمرين
3. يمكنك تخصيص الرابط في Settings

---

**ملاحظة:** التطبيق يعمل محلياً أيضاً باستخدام:
```bash
streamlit run app.py
```

