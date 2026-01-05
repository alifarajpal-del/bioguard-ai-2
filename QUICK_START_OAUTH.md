# 🚀 Quick Start - OAuth Setup

## للتشغيل السريع محلياً (بدون OAuth)

التطبيق يعمل بدون OAuth! فقط استخدم نموذج "تسجيل الدخول التقليدي":

```bash
streamlit run main.py
```

---

## لتفعيل Google Sign-In فقط

### 1. احصل على مفاتيح Google (5 دقائق)
1. اذهب إلى: https://console.cloud.google.com/apis/credentials
2. **Create Credentials** > **OAuth client ID**
3. Application type: **Web application**
4. Authorized redirect URIs: `http://localhost:8501/auth/google/callback`
5. احفظ **Client ID** و **Client Secret**

### 2. أضف المفاتيح
في Terminal:
```bash
# Windows PowerShell
$env:GOOGLE_CLIENT_ID="your_client_id"
$env:GOOGLE_CLIENT_SECRET="your_client_secret"
$env:GOOGLE_REDIRECT_URI="http://localhost:8501/auth/google/callback"

# أو أنشئ ملف .env
echo GOOGLE_CLIENT_ID=your_id >> .env
echo GOOGLE_CLIENT_SECRET=your_secret >> .env
```

### 3. شغّل التطبيق
```bash
streamlit run main.py
```

---

## لتفعيل Apple Sign-In (متقدم)

Apple أصعب قليلاً لأنه يحتاج:
- حساب Apple Developer ($99/سنة)
- Private key (.p8 file)
- Domain verification

### خطوات سريعة:
1. https://developer.apple.com/account/resources
2. أنشئ **Services ID**
3. أنشئ **Private Key** (حمّل `.p8`)
4. حوّل المفتاح لـ Base64: `cat AuthKey_XXX.p8 | base64`
5. أضف المتغيرات:

```bash
$env:APPLE_CLIENT_ID="com.yourcompany.bioguardai"
$env:APPLE_TEAM_ID="YOUR_TEAM_ID"
$env:APPLE_KEY_ID="YOUR_KEY_ID"
$env:APPLE_PRIVATE_KEY="base64_encoded_key"
```

---

## ⚠️ نصائح مهمة

### للتطوير المحلي
- يكفي Google OAuth (Apple يحتاج domain verification)
- استخدم `http://localhost:8501` في redirect URIs
- التطبيق يعمل بدون OAuth (استخدم التسجيل التقليدي)

### للنشر على Streamlit Cloud
1. اذهب إلى Dashboard > Settings > Secrets
2. أضف جميع المتغيرات بصيغة TOML:
```toml
GOOGLE_CLIENT_ID = "your_id"
GOOGLE_CLIENT_SECRET = "your_secret"
GOOGLE_REDIRECT_URI = "https://your-app.streamlit.app/auth/google/callback"
```
3. **مهم**: غيّر redirect URI إلى URL الحقيقي للتطبيق
4. أضف نفس الـ URL في Google Console > Authorized redirect URIs

### التحديثات التلقائية
Streamlit Cloud يعيد النشر تلقائياً عند كل push لـ GitHub! ✅

---

## 🐛 حل المشاكل السريع

### "Redirect URI mismatch"
✅ تأكد أن redirect_uri في `.env` = URI في Google Console

### "Module not found: jwt"
✅ نفذ: `pip install -r requirements.txt`

### الأزرار لا تظهر
✅ تحقق أن المتغيرات موجودة: `echo $env:GOOGLE_CLIENT_ID`

### التطبيق لا يعمل
✅ التطبيق يعمل بدون OAuth! استخدم التسجيل التقليدي

---

## 📖 دليل كامل

للتعليمات التفصيلية، انظر: [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md)

---

## 💡 أسئلة شائعة

**Q: هل OAuth إلزامي؟**
A: لا! التطبيق يعمل بالتسجيل التقليدي بدون OAuth.

**Q: أيهما أسهل، Google أم Apple؟**
A: Google أسهل بكثير (لا يحتاج domain verification).

**Q: هل أحتاج لـ HTTPS؟**
A: محلياً لا (http://localhost يعمل). للنشر نعم (Streamlit Cloud يوفرها تلقائياً).

**Q: كم يستغرق الإعداد؟**
A: Google: 5-10 دقائق | Apple: 20-30 دقيقة

**Q: هل يمكن استخدام OAuth و التقليدي معاً؟**
A: نعم! المستخدم يختار الطريقة المفضلة.

---

تم! 🎉
