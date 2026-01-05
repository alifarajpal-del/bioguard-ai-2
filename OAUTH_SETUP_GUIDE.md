# OAuth Setup Guide - دليل إعداد OAuth

## نظرة عامة
تم إضافة نظام OAuth لتسجيل الدخول بواسطة Google و Apple إلى BioGuard AI. يتيح هذا للمستخدمين تسجيل الدخول بنقرة واحدة دون الحاجة لإنشاء حساب جديد.

## 🔐 الميزات الجديدة

### واجهة المستخدم
- ✅ أزرار Sign in with Google و Apple بتصميم رسمي
- ✅ نموذج تسجيل دخول تقليدي كخيار بديل
- ✅ تصميم متوافق مع الثيمات الجديدة (Pastel)
- ✅ رسائل خطأ واضحة بالعربية
- ✅ حماية CSRF بواسطة state parameter

### الأمان
- ✅ التحقق من ID Token باستخدام مفاتيح Google/Apple العامة
- ✅ تشفير البيانات الحساسة
- ✅ JWT tokens لإدارة الجلسات
- ✅ حماية من CSRF attacks

### قاعدة البيانات
- ✅ حقول جديدة: email, picture, provider, email_verified
- ✅ دعم المصادقة التقليدية و OAuth معاً
- ✅ ربط الحسابات بمزود المصادقة

---

## 📋 خطوات الإعداد

### 1️⃣ إعداد Google OAuth

#### الخطوة 1: إنشاء مشروع على Google Cloud Console
1. اذهب إلى [Google Cloud Console](https://console.cloud.google.com/)
2. أنشئ مشروعاً جديداً أو اختر مشروعاً موجوداً
3. انتقل إلى **APIs & Services** > **Credentials**

#### الخطوة 2: إنشاء OAuth 2.0 Client ID
1. اضغط **Create Credentials** > **OAuth client ID**
2. اختر **Web application**
3. أضف **Authorized redirect URIs**:
   ```
   http://localhost:8501/auth/google/callback  # للتطوير
   https://your-app.streamlit.app/auth/google/callback  # للإنتاج
   ```
4. احفظ **Client ID** و **Client Secret**

#### الخطوة 3: تكوين المتغيرات البيئية
أضف إلى ملف `.env`:
```env
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=https://your-app.streamlit.app/auth/google/callback
```

---

### 2️⃣ إعداد Apple Sign In

#### الخطوة 1: إنشاء App ID
1. اذهب إلى [Apple Developer](https://developer.apple.com/account/resources/identifiers/list)
2. أنشئ **App ID** جديد
3. فعّل **Sign in with Apple**

#### الخطوة 2: إنشاء Services ID
1. أنشئ **Services ID** (هذا هو Client ID)
2. فعّل **Sign in with Apple**
3. أضف **Return URLs**:
   ```
   https://your-app.streamlit.app/auth/apple/callback
   ```
4. أضف **Domain**: `your-app.streamlit.app`

#### الخطوة 3: إنشاء Private Key
1. في قسم **Keys**، أنشئ مفتاحاً جديداً
2. فعّل **Sign in with Apple**
3. حمّل ملف `.p8` (سيُستخدم مرة واحدة فقط!)
4. احفظ **Key ID**

#### الخطوة 4: تحويل Private Key إلى Base64
في Terminal:
```bash
cat AuthKey_XXXXX.p8 | base64
```

#### الخطوة 5: تكوين المتغيرات البيئية
أضف إلى ملف `.env`:
```env
APPLE_CLIENT_ID=com.yourcompany.bioguardai
APPLE_TEAM_ID=YOUR_TEAM_ID
APPLE_KEY_ID=YOUR_KEY_ID
APPLE_PRIVATE_KEY=base64_encoded_private_key
APPLE_REDIRECT_URI=https://your-app.streamlit.app/auth/apple/callback
```

---

### 3️⃣ إعداد Streamlit Cloud

#### إضافة Secrets في Streamlit
1. اذهب إلى Dashboard في Streamlit Cloud
2. افتح تطبيقك > **Settings** > **Secrets**
3. أضف جميع المتغيرات:

```toml
GOOGLE_CLIENT_ID = "your_client_id"
GOOGLE_CLIENT_SECRET = "your_client_secret"
GOOGLE_REDIRECT_URI = "https://your-app.streamlit.app/auth/google/callback"

APPLE_CLIENT_ID = "com.yourcompany.bioguardai"
APPLE_TEAM_ID = "YOUR_TEAM_ID"
APPLE_KEY_ID = "YOUR_KEY_ID"
APPLE_PRIVATE_KEY = "base64_encoded_key"
APPLE_REDIRECT_URI = "https://your-app.streamlit.app/auth/apple/callback"

JWT_SECRET_KEY = "your_jwt_secret"
```

---

## 🧪 الاختبار المحلي

### 1. تثبيت المكتبات
```bash
pip install -r requirements.txt
```

### 2. إنشاء ملف `.env`
انسخ `.env.example` إلى `.env` وأضف المفاتيح الحقيقية.

### 3. تشغيل التطبيق
```bash
streamlit run main.py
```

### 4. اختبار OAuth
1. افتح `http://localhost:8501`
2. اضغط على زر "Sign in with Google"
3. ستُعاد توجيهك إلى Google للمصادقة
4. بعد الموافقة، ستعود إلى التطبيق مصادقاً

---

## 📁 الملفات الجديدة

### `services/oauth_providers.py`
- **GoogleOAuthProvider**: معالجة OAuth 2.0 لـ Google
- **AppleOAuthProvider**: معالجة Sign in with Apple
- التحقق من ID tokens
- استخراج معلومات المستخدم

### `ui_components/oauth_login.py`
- **render_oauth_login()**: واجهة تسجيل الدخول
- **handle_oauth_callback()**: معالجة callback من OAuth
- أزرار Google و Apple رسمية
- نموذج تسجيل دخول تقليدي

### الملفات المحدثة
- ✅ `main.py`: دمج OAuth في التطبيق
- ✅ `config/settings.py`: متغيرات OAuth
- ✅ `database/db_manager.py`: حقول OAuth في جدول users
- ✅ `services/auth.py`: حفظ المستخدمين في قاعدة البيانات
- ✅ `requirements.txt`: مكتبة authlib (اختيارية)

---

## 🔄 تدفق المصادقة (OAuth Flow)

### Google Flow
```
1. المستخدم يضغط "Sign in with Google"
   ↓
2. التطبيق يُعيد التوجيه إلى صفحة Google
   ↓
3. المستخدم يوافق على الصلاحيات
   ↓
4. Google يُعيد التوجيه إلى /auth/google/callback?code=XXX
   ↓
5. التطبيق يتبادل code مع access_token و id_token
   ↓
6. التحقق من id_token باستخدام مفاتيح Google العامة
   ↓
7. استخراج البريد والاسم والصورة
   ↓
8. حفظ/تحديث المستخدم في قاعدة البيانات
   ↓
9. إنشاء JWT token للجلسة
   ↓
10. المستخدم يدخل إلى التطبيق ✅
```

### Apple Flow
مشابه لـ Google، لكن:
- يتطلب client_secret (JWT موقّع بالمفتاح الخاص)
- response_mode = form_post بدلاً من query
- البيانات محدودة (email فقط، الاسم في أول مرة)

---

## 🛡️ الأمان

### التحقق من ID Token
```python
# Google
jwt.decode(
    id_token,
    key=google_public_key,
    algorithms=["RS256"],
    audience=GOOGLE_CLIENT_ID,
    issuer="https://accounts.google.com"
)

# Apple
jwt.decode(
    id_token,
    key=apple_public_key,
    algorithms=["RS256"],
    audience=APPLE_CLIENT_ID,
    issuer="https://appleid.apple.com"
)
```

### حماية CSRF
```python
# إنشاء state عشوائي
state = secrets.token_urlsafe(32)
st.session_state.oauth_state = state

# التحقق عند callback
if state != st.session_state.oauth_state:
    raise SecurityError("Invalid state")
```

---

## 🎨 التصميم

### أزرار OAuth
- **Google**: خلفية بيضاء، أيقونة ملونة، حدود رمادية
- **Apple**: خلفية سوداء، أيقونة بيضاء
- Hover effects: ظل أقوى + حركة للأعلى

### الألوان
- تتبع الثيم النشط (Pastel themes)
- تباين WCAG AAA (12.6:1)
- رسوم متحركة ناعمة (cubic-bezier)

---

## ❗ استكشاف الأخطاء

### "Redirect URI mismatch"
✅ تأكد من أن redirect_uri في `.env` يطابق ما في Google/Apple Console

### "Invalid client"
✅ تحقق من CLIENT_ID و CLIENT_SECRET

### "Token verification failed"
✅ تأكد من اتصال الإنترنت (للحصول على public keys)
✅ تحقق من audience و issuer في token

### "State mismatch"
✅ لا تفتح callback URL مباشرة (يجب المرور عبر authorization URL أولاً)

---

## 📞 الدعم

للأسئلة أو المشاكل:
- 📧 Email: support@bioguard.ai (example)
- 📖 Documentation: [docs.bioguard.ai](https://docs.bioguard.ai) (example)
- 🐛 Issues: [GitHub Issues](https://github.com/alifarajpal-del/bioguard-ai-2/issues)

---

## 🚀 التحديثات القادمة (Roadmap)

- [ ] دعم Facebook Login
- [ ] دعم Twitter/X Login
- [ ] ربط حسابات متعددة (Link Accounts)
- [ ] تسجيل دخول بدون كلمة مرور (Passwordless)
- [ ] WebAuthn/Biometric authentication
- [ ] Two-Factor Authentication (2FA) مع OAuth

---

تم إنشاء هذا الدليل في: 5 يناير 2026
الإصدار: v2.6 - OAuth Integration
