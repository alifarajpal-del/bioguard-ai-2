# 🔐 إعداد OAuth على Streamlit Cloud

## المشكلة
عند محاولة تسجيل الدخول بواسطة Google أو Apple، لا تعمل الأزرار لأن متغيرات البيئة غير محددة.

## ✅ الحل السريع (5 دقائق)

### الخطوة 1: احصل على مفاتيح Google
1. اذهب إلى [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. أنشئ مشروعاً جديداً (أو استخدم موجود)
3. اضغط **Create Credentials** > **OAuth client ID**
4. اختر **Web application**
5. في **Authorized redirect URIs** أضف:
   ```
   https://your-app-name.streamlit.app/auth/google/callback
   ```
   (غيّر `your-app-name` باسم تطبيقك الفعلي)
6. احفظ **Client ID** و **Client Secret**

### الخطوة 2: أضف Secrets في Streamlit Cloud
1. افتح [Streamlit Cloud Dashboard](https://share.streamlit.io/)
2. اختر تطبيقك > **Settings** (⚙️)
3. اذهب إلى **Secrets**
4. أضف التالي:

```toml
# JWT Secret (مطلوب)
JWT_SECRET_KEY = "your_jwt_secret_key_here"

# Google OAuth
GOOGLE_CLIENT_ID = "your_client_id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your_client_secret"
GOOGLE_REDIRECT_URI = "https://your-app-name.streamlit.app/auth/google/callback"

# اختياري: Apple OAuth (يحتاج حساب Developer بـ $99/سنة)
# APPLE_CLIENT_ID = "com.yourcompany.bioguardai"
# APPLE_TEAM_ID = "YOUR_TEAM_ID"
# APPLE_KEY_ID = "YOUR_KEY_ID"
# APPLE_PRIVATE_KEY = "base64_encoded_key"
# APPLE_REDIRECT_URI = "https://your-app-name.streamlit.app/auth/apple/callback"
```

5. اضغط **Save**
6. أعد تشغيل التطبيق (سيُعاد تلقائياً)

### الخطوة 3: جرّب تسجيل الدخول
1. افتح التطبيق
2. اضغط **Sign in with Google**
3. سيُعاد توجيهك لصفحة Google
4. بعد الموافقة، ستعود للتطبيق مسجّلاً ✅

---

## 🔒 توليد JWT Secret

إذا لم يكن لديك JWT secret بعد:

### في Windows PowerShell:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### في Linux/Mac:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

انسخ الناتج واستخدمه كـ `JWT_SECRET_KEY`

---

## ⚠️ ملاحظات مهمة

### Redirect URI
يجب أن يطابق **تماماً** ما في Google Console:
- ❌ خطأ: `http://localhost:8501/...` (في Production)
- ✅ صحيح: `https://your-app.streamlit.app/auth/google/callback`

### HTTPS مطلوب
- Streamlit Cloud يوفر HTTPS تلقائياً ✅
- لا يمكن استخدام `http://` في Production

### التطبيق بدون OAuth
التطبيق يعمل بدون OAuth! استخدم نموذج "تسجيل الدخول التقليدي" كبديل.

---

## 🐛 حل المشاكل

### "Redirect URI mismatch"
✅ **الحل**: تأكد أن الـ URI في Secrets = URI في Google Console

### الأزرار لا تظهر
✅ **الحل**: تحقق من أن `GOOGLE_CLIENT_ID` موجود في Secrets

### "Invalid client"
✅ **الحل**: تأكد من نسخ Client ID و Secret بشكل صحيح (بدون مسافات)

### التطبيق لا يعمل بعد إضافة Secrets
✅ **الحل**: أعد تشغيل التطبيق من Dashboard (⋮ > Reboot app)

---

## 📖 مزيد من المعلومات

- [دليل الإعداد الكامل](OAUTH_SETUP_GUIDE.md)
- [دليل البدء السريع](QUICK_START_OAUTH.md)
- [Google OAuth Docs](https://developers.google.com/identity/protocols/oauth2)

---

## 💡 نصائح

1. **للاختبار المحلي**: استخدم `http://localhost:8501` في redirect URI
2. **للإنتاج**: استخدم `https://your-app.streamlit.app`
3. **احتفظ بنسخة احتياطية** من Client Secret (لا يمكن استرجاعه)
4. **لا تنشر** Secrets على GitHub أبداً!

---

✅ بعد إضافة المفاتيح، سيعمل تسجيل الدخول بواسطة Google فوراً!
