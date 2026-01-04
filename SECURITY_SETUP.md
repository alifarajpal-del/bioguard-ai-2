# 🔒 Security & Environment Setup Guide

## Overview
BioGuard AI uses environment variables to manage sensitive information securely. **Never hardcode API keys or secrets in the codebase.**

## Quick Setup

### 1. Copy Environment Template
```bash
cp .env.example .env
```

### 2. Generate JWT Secret
```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

### 3. Fill in Your Keys
Edit `.env` and add your actual API keys:

```env
OPENAI_API_KEY=sk-your-actual-openai-key
GEMINI_API_KEY=your-actual-gemini-key
JWT_SECRET_KEY=your-generated-secret-from-step-2
```

## Required Environment Variables

### Production Requirements
These variables **MUST** be set in production:

- `JWT_SECRET_KEY` - Will raise an error if missing in production
- `OPENAI_API_KEY` or `GEMINI_API_KEY` - At least one AI provider required

### Development Mode
In development, the system will:
- Use a fallback JWT secret (with warning)
- Fall back to mock AI responses if no API keys provided
- Enable debug logging

## Environment Variables Reference

### Security
```env
JWT_SECRET_KEY=<secure-random-string>
```

### AI Providers
```env
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
```

### Feature Flags
```env
FEATURE_LIVE_AR_ENABLED=true
FEATURE_KNOWLEDGE_GRAPH_ENABLED=true
FEATURE_DIGITAL_TWIN_ENABLED=true
FEDERATED_LEARNING_ENABLED=true
```

### Performance Tuning
```env
# Rate limiting
MAX_API_CALLS_PER_MINUTE=60

# Caching
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600

# Storage
MAX_FILE_SIZE_MB=10
```

### Environment Mode
```env
ENVIRONMENT=production  # or development
LOG_LEVEL=INFO         # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Security Best Practices

### ✅ DO:
- Store all secrets in `.env` file (ignored by git)
- Use environment variables via `os.getenv()`
- Generate strong random secrets (min 32 characters)
- Rotate secrets regularly
- Use different secrets for dev/staging/production
- Set restrictive file permissions on `.env`: `chmod 600 .env`

### ❌ DON'T:
- Commit `.env` files to git
- Hardcode API keys in source code
- Share secrets via email/chat
- Use the same secret across environments
- Commit `.streamlit/secrets.toml`

## Deployment Checklist

### Before Deploying to Production:
- [ ] Set `ENVIRONMENT=production`
- [ ] Generate and set strong `JWT_SECRET_KEY`
- [ ] Configure all required API keys
- [ ] Review feature flags
- [ ] Set appropriate rate limits
- [ ] Configure logging level
- [ ] Verify `.gitignore` excludes `.env`
- [ ] Test with production credentials in staging first

## Verifying Configuration

Run this command to verify your environment (without exposing secrets):
```bash
python -c "from config.settings import *; print('✓ Configuration loaded successfully')"
```

## Getting API Keys

### OpenAI
1. Visit https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to `OPENAI_API_KEY` in `.env`

### Google Gemini
1. Visit https://ai.google.dev/
2. Get API key from Google AI Studio
3. Copy to `GEMINI_API_KEY` in `.env`

## Troubleshooting

### "JWT_SECRET_KEY environment variable must be set"
- Generate secret: `python -c 'import secrets; print(secrets.token_urlsafe(32))'`
- Add to `.env`: `JWT_SECRET_KEY=<generated-secret>`
- Restart application

### "Using mock analysis - API providers unavailable"
- Verify at least one of `OPENAI_API_KEY` or `GEMINI_API_KEY` is set
- Check API key is valid
- Ensure no extra spaces in `.env` file

### Changes not taking effect
- Restart the application after modifying `.env`
- Check for syntax errors in `.env` (no quotes needed for values)
- Verify `.env` file is in project root directory

## Support
For security concerns, please email: security@bioguard-ai.example.com
