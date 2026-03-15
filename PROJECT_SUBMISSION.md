# Multi-LLM Chat Application — Project Documentation

## Project Overview

A **Multi-LLM Chat Application** built with **Streamlit** that allows users to interact with both **OpenAI (GPT-4o-mini)** and **Google Gemini** models simultaneously. The app features **Google OAuth** authentication, **Firebase Firestore** for chat history persistence, and is deployed on **Render**.

**Live URL:** https://multi-llm-chat-k91n.onrender.com

---

## Architecture

```
User (Browser)
    │
    ▼
Streamlit (app.py)  ──►  Google OAuth (google_auth.py)
    │
    ├──►  OpenAI API (GPT-4o-mini)    ┐
    │                                   ├──  Parallel responses via threading
    ├──►  Gemini API (gemini-3-flash)  ┘
    │
    └──►  Firebase Firestore (firebase_service.py)  ──►  Chat history & user data
```

---

## Key Features

1. **Multi-LLM Parallel Responses** — Queries both OpenAI and Gemini in parallel using Python threading, displaying responses side-by-side for easy comparison.
2. **Google OAuth 2.0 Authentication** — Secure sign-in via Google accounts using a custom authlib-based OAuth flow.
3. **Firebase Firestore Integration** — Persistent chat history and user profiles stored in Firestore.
4. **Model Selection** — Users can choose to get responses from OpenAI only, Gemini only, or both simultaneously.
5. **Cloud Deployment** — Deployed on Render with environment-variable-based configuration for all secrets.

---

## Files to Submit

### Core Application Files (Required)

| # | File | Description |
|---|------|-------------|
| 1 | `app.py` | Main Streamlit application — UI, routing, chat interface, parallel LLM response handling |
| 2 | `llm_functions.py` | LLM integration — OpenAI and Gemini API calls with lazy initialization and error handling |
| 3 | `google_auth.py` | Google OAuth 2.0 authenticator using authlib — login, token exchange, user info retrieval |
| 4 | `firebase_service.py` | Firebase/Firestore operations — user management, chat history save/load/clear |

### Configuration & Deployment Files (Required)

| # | File | Description |
|---|------|-------------|
| 5 | `requirements.txt` | Python dependencies (streamlit, openai, google-generativeai, firebase-admin, authlib, etc.) |
| 6 | `render.yaml` | Render deployment blueprint — service config, build/start commands, environment variables |
| 7 | `.streamlit/config.toml` | Streamlit production configuration — theme, server settings, XSRF protection |
| 8 | `.python-version` | Python runtime version (3.11.0) enforced on Render |
| 9 | `.gitignore` | Git ignore rules — excludes .env, credentials JSON, __pycache__, venv |

### Documentation Files (Optional)

| # | File | Description |
|---|------|-------------|
| 10 | `PROJECT_SUBMISSION.md` | This document — project overview, architecture, and submission guide |
| 11 | `firebase_setup.md` | Step-by-step Firebase setup instructions |
| 12 | `RENDER_DEPLOY_GUIDE.md` | Detailed Render deployment guide |
| 13 | `planning.txt` | Project planning notes and task tracking |

---

## Files NOT to Submit (Sensitive / Auto-generated)

| File | Reason |
|------|--------|
| `.env` | Contains API keys (OPENAI_API_KEY, GEMINI_API_KEY) — **never share** |
| `*.json` (credentials files) | Firebase service account key and Google OAuth client secret — **never share** |
| `__pycache__/` | Python bytecode cache — auto-generated |
| `.venv/` | Virtual environment — auto-generated |
| `get_firebase_credentials.py` | Helper utility for extracting Firebase credentials |
| `update_redirect_uri.py` | Helper utility for updating OAuth redirect URIs |
| `test_*.py`, `create_test_doc.py` | Test/utility scripts not part of the core application |

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | Streamlit | 1.32.0 |
| LLM 1 | OpenAI GPT-4o-mini | via openai >= 1.60.0 |
| LLM 2 | Google Gemini 3 Flash | via google-generativeai >= 0.3.0 |
| Authentication | Google OAuth 2.0 | via authlib 1.3.0 |
| Database | Firebase Firestore | via firebase-admin 6.2.0 |
| Deployment | Render | Python 3.11 |

---

## Environment Variables (Required on Render)

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini |
| `GEMINI_API_KEY` | Google Gemini API key |
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 Client Secret |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Firebase service account JSON (entire file content) |
| `RENDER_EXTERNAL_URL` | Auto-set by Render — used for OAuth redirect URI |

---

## How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/sghoshece/multi_llm_chat.git
cd multi_llm_chat

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your API keys
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=AI...
# GOOGLE_CLIENT_ID=...
# GOOGLE_CLIENT_SECRET=...

# 5. Place Firebase service account JSON in project root

# 6. Run the app
streamlit run app.py
```

---

## Application Flow

1. **User visits the app** → Sees Google Sign-In page
2. **User clicks "Sign in with Google"** → Redirected to Google OAuth consent
3. **Google authenticates user** → Redirected back with auth code
4. **App exchanges code for token** → Retrieves user email, name, and picture
5. **User registered in Firestore** → Profile created/updated
6. **Chat history loaded** → Previous conversations restored from Firestore
7. **User sends a message** → App queries selected LLM(s) in parallel via threading
8. **Responses displayed side-by-side** → OpenAI and Gemini columns (when "Both" selected)
9. **Chat saved to Firestore** → Messages persisted for future sessions
