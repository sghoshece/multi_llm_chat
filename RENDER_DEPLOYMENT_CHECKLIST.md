# 🚀 Render Deployment Checklist & Instructions

## ✅ Pre-Deployment Checklist

- [x] GitHub repository created and code pushed
- [x] `.gitignore` file created (excludes `.json` credentials, `.env`)
- [x] `requirements.txt` with all dependencies
- [x] `.streamlit/config.toml` for production config
- [x] `render.yaml` with deployment configuration
- [x] Firebase credentials secured (NOT in repo)
- [x] API keys ready (OpenAI, Gemini, Google OAuth)

---

## 🎯 Render Deployment Steps

### Step 1: Log in to Render
1. Go to https://render.com
2. Click **Sign up** → Choose **GitHub** authentication
3. Authorize Render to access your GitHub account

### Step 2: Create a New Web Service
1. Dashboard → Click **New +** → Select **Web Service**
2. Connect your GitHub account (if not already done)
3. Select the repository: `multi_llm_chat`
4. Click **Connect**

### Step 3: Configure the Web Service

**Name:** `multi-llm-chat` (or any name you prefer)

**Environment:** `Python 3`

**Build Command:** Leave as default or use:
```
pip install -r requirements.txt
```

**Start Command:**
```
streamlit run app.py
```

**Instance Type:** Choose based on usage:
- **Free** (~0.50 CPU, 0.5 GB RAM) - Works for light usage, sleeps after 15 min of inactivity
- **Paid** ($7/month) - Always-on, recommended for production

### Step 4: Add Environment Variables

Click **Add Environment Variable** for each of these:

| Variable Name | Value | Source |
|--------------|-------|--------|
| `OPENAI_API_KEY` | Your OpenAI API key | https://platform.openai.com/api-keys |
| `GOOGLE_API_KEY` | Your Google Gemini API key | https://ai.google.dev/tutorials/setup |
| `GOOGLE_CLIENT_ID` | Your Google OAuth Client ID | Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Your Google OAuth Client Secret | Google Cloud Console |
| `COOKIE_KEY` | Any random secret string | Generate: `openssl rand -hex 32` |
| `FIREBASE_CONFIG` | Your Firebase JSON (see note below) | Firebase Console |

**Important: Firebase JSON handling**

Since you can't commit the Firebase JSON directly, you need to pass it as an environment variable:

Option A (Recommended): Paste entire JSON as base64
```bash
# On your local machine:
base64 -i multi-llm-chat-487904-firebase-adminsdk-fbsvc-014c2efb00.json
```
Then set `FIREBASE_CONFIG_BASE64` env var with the output.

Update your `firebase_service.py`:
```python
import base64
import json
import os

firebase_json_b64 = os.getenv('FIREBASE_CONFIG_BASE64')
if firebase_json_b64:
    firebase_json = json.loads(base64.b64decode(firebase_json_b64))
    firebase_admin.initialize_app(cred=firebase_admin.credentials.Certificate(firebase_json))
```

### Step 5: Deploy

1. Scroll down and click **Create Web Service**
2. Render will automatically:
   - Build your application
   - Install dependencies from `requirements.txt`
   - Start your Streamlit app

3. Check the **Logs** tab for any errors
4. Once build is complete, your app URL will appear at the top

---

## 🔑 Getting Your API Keys (Quick Reference)

### OpenAI API Key
- Go to https://platform.openai.com/api-keys
- Create new secret key
- Copy and paste in Render env vars

### Google Gemini API Key
- Go to https://ai.google.dev
- Click **Get API Key**
- Create key for "default project"
- Copy and paste in Render env vars

### Google OAuth (Client ID & Secret)
- Go to https://console.cloud.google.com
- Create/select a project
- Enable "Google+ API"
- Go to **Credentials** > **Create OAuth 2.0 Client ID**
- Add authorized redirect URI: `https://your-render-url.onrender.com`
- Copy Client ID and Secret to Render env vars

### Cookie Key (Random Secret)
- Run in terminal:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- Use the output as `COOKIE_KEY`

---

## 🧪 Testing After Deployment

1. Click your deployment URL
2. The Streamlit app should load
3. Test Google OAuth login
4. Try a chat message to verify LLMs work
5. Check Firebase integration with saved messages

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Build fails** | Check logs, ensure Python 3.9+ |
| **App won't start** | Verify `app.py` exists and is readable |
| **Auth errors** | Check `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| **API errors** | Verify API keys are correct and have quotas |
| **Firebase errors** | Ensure `FIREBASE_CONFIG_BASE64` is valid |
| **Cold start takes long** | Free tier sleeps after 15 min - normal behavior |

---

## 📊 Monitoring

- **Logs:** View in Render dashboard under **Logs** tab
- **Metrics:** View CPU, memory, disk usage in **Metrics** tab
- **Alerts:** Set up notifications for failures in **Settings**

---

## 💡 Advanced Configuration

### Custom Domain
1. In Render dashboard: **Settings** → **Custom Domain**
2. Add your domain
3. Follow DNS instructions

### Environment-Specific Config
Update `app.py` to detect Render environment:
```python
import os

if "RENDER" in os.environ:
    # Production Render config
    DEBUG = False
else:
    # Local development
    DEBUG = True
```

---

## ✨ Next Steps After Deployment

1. Test all features in production
2. Set up GitHub integrations (auto-deploy on push)
3. Monitor logs and performance
4. Consider upgrading to paid tier if needed
5. Set up custom domain

---

**Need help?** Check Render docs: https://docs.render.com
