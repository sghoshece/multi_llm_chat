# Deploy Multi-LLM Chat to Render

## Step-by-Step Deployment Guide

### Prerequisites
- GitHub account with your project pushed
- Render account (https://render.com) - free, sign up with GitHub
- API keys ready (OpenAI, Gemini, Google OAuth)
- Firebase JSON key file

---

## 1. Prepare Your Code for Production

### Update `app.py`
Change the redirect URI to be dynamic:

```python
import os

# Get redirect URI based on environment
if "RENDER" in os.environ:
    REDIRECT_URI = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8501")
else:
    REDIRECT_URI = "http://localhost:8501"

authenticator = Authenticate(
    secret_credentials_path=os.getenv("GOOGLE_CLIENT_SECRET_PATH", 
                                      'client_secret_322929524449-ok5mli1n1o8q049nqm6j7smfklq11g09.apps.googleusercontent.com.json'),
    cookie_name='multi_llm_chat_auth',
    cookie_key=os.getenv("COOKIE_KEY", 'default-key'),
    redirect_uri=REDIRECT_URI,
)
```

### Create `.streamlit/config.toml`
```toml
[client]
showErrorDetails = false

[logger]
level = "info"

[server]
runOnSave = true
enableXsrfProtection = true
headless = true

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F8F9FA"
```

---

## 2. Push to GitHub

```bash
git init
git add .
git commit -m "Prepare for Render deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

## 3. Deploy on Render

### Go to Render Dashboard
1. Visit https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Connect your GitHub repository

### Configure Web Service
- **Name**: `multi-llm-chat`
- **Environment**: `Python 3.11`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=10000 --server.address=0.0.0.0`
- **Instance Type**: Free (or Starter $7/month for always-on)

### Add Environment Variables
In Render dashboard, add these in **Environment** section:

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxx
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
COOKIE_KEY=your-secure-random-key
```

To generate a secure COOKIE_KEY:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Add Firebase Credentials
**Option 1: Upload File (Recommended)**
1. In Render, go to **Environment Files**
2. Upload file: `multi-llm-chat-487904-firebase-adminsdk-fbsvc-014c2efb00.json`
3. File will be at: `/etc/secrets/firebase-key.json`

**Option 2: Paste JSON as Env Var**
1. Copy entire JSON content
2. Create env var `FIREBASE_KEY_JSON` with full content
3. In `firebase_service.py`, add code to parse it

---

## 4. Update Google OAuth Settings

In Google Cloud Console:
1. Go to **APIs & Services** → **Credentials**
2. Edit your OAuth 2.0 Client ID
3. Add **Authorized redirect URIs**:
   - `https://your-app-name.onrender.com`
   - `https://your-app-name.onrender.com/auth/callback`
4. Save

---

## 5. Deploy

1. Click **Deploy** in Render dashboard
2. Watch the build logs
3. Once green, your app is live! 🎉

**Your app URL**: `https://your-app-name.onrender.com`

---

## Troubleshooting

**Module not found error?**
- Make sure `requirements.txt` is in root directory
- Check it has all dependencies

**Firebase credentials not found?**
- Verify file path in environment variables
- Check that file is properly uploaded to Render

**Port already in use?**
- Make sure start command has `--server.port=10000`

**OAuth redirect mismatch?**
- Get your final Render URL
- Update Google Cloud Console
- Wait 5 minutes before testing
- Restart the service

---

## Cost

- **Free tier**: App sleeps after 15 minutes of inactivity
- **Starter ($7/month)**: Always running, better for users
- **APIs**: You pay for OpenAI/Gemini usage separately

---

## Monitoring

Check logs in Render dashboard:
1. Click on your service
2. Go to **Logs** tab
3. View real-time activity

---

**Done!** Your Multi-LLM chat app is now deployed on Render! 🚀
