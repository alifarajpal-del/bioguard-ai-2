# BioGuard AI Deployment Guide

## Quick Deploy to Streamlit Community Cloud

### Prerequisites:
1. Push your code to GitHub (already done ✅)
2. Visit https://share.streamlit.io
3. Connect your GitHub account
4. Deploy the repository: `alifarajpal-del/bioguard-ai-2`

### Environment Variables Needed:
```
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
ENVIRONMENT=production
```

### Steps:
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select repository: `alifarajpal-del/bioguard-ai-2`
4. Main file: `main.py`
5. Add secrets in Advanced settings
6. Deploy!

## Alternative Deployment Options:

### Railway (Free tier available)
- Visit railway.app
- Connect GitHub repo
- Auto-deploy from main branch

### Render (Free tier available)  
- Visit render.com
- Connect GitHub repo
- Choose Web Service

### Heroku (Paid)
- Install Heroku CLI
- Create app: `heroku create bioguard-ai-app`
- Push: `git push heroku main`

## Expected Public URL Format:
- Streamlit Cloud: `https://bioguard-ai-2-[random].streamlit.app`
- Railway: `https://bioguard-ai-2-production.up.railway.app`
- Render: `https://bioguard-ai-2.onrender.com`