"""
Multi-LLM Chat Application
Streamlit app with Google Sign-In (Firebase) and Firestore chat history.

Setup:
  1. Go to Google Cloud Console > APIs & Credentials > Create OAuth 2.0 Client ID
  2. Set Authorized redirect URIs to: http://localhost:8501
  3. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to your .env file
  4. Run with: streamlit run app.py
"""
import streamlit as st
from streamlit_google_auth import Authenticate
from firebase_service import (
    get_or_create_google_user,
    save_chat_message,
    get_chat_history, clear_chat_history
)
from llm_functions import get_gemini_response, get_response_from_openai
import os
from dotenv import load_dotenv
import threading
from queue import Queue
import json
import tempfile

load_dotenv()

# ==================== Setup Google Credentials ====================
# For production (Render), create credentials file from env variable
credentials_file = 'client_secret_322929524449-ok5mli1n1o8q049nqm6j7smfklq11g09.apps.googleusercontent.com.json'

def ensure_credentials_file():
    """Ensure credentials file exists, either locally or from environment."""
    if not os.path.exists(credentials_file):
        creds_json = os.getenv('GOOGLE_CLIENT_SECRET_JSON')
        if creds_json:
            try:
                with open(credentials_file, 'w') as f:
                    f.write(creds_json)
                print(f"✓ Credentials file created from environment variable")
                return True
            except Exception as e:
                print(f"✗ Error creating credentials file from env: {e}")
                return False
        else:
            print(f"✗ WARNING: Credentials file not found and GOOGLE_CLIENT_SECRET_JSON not set")
            return False
    else:
        print(f"✓ Credentials file exists locally")
        return True

# Try to ensure credentials are available
credentials_available = ensure_credentials_file()


# ==================== Page Config ====================
st.set_page_config(
    page_title="Multi-LLM Chat",
    page_icon="🤖",
    layout="wide"
)

# ==================== Session State Initialization ====================
defaults = {
    'connected': False,
    'user_id': None,
    'user_email': None,
    'display_name': None,
    'openai_chat_history': [],
    'gemini_chat_history': [],
    'model_choice': 'Both',
    'chat_loaded': False
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================== Google Authentication ====================

if not credentials_available:
    st.error("❌ **Missing Google Credentials**\n\n" +
             "Please set the `GOOGLE_CLIENT_SECRET_JSON` environment variable on Render.\n\n" +
             "Steps:\n" +
             "1. Copy your Google Client Secret JSON file content\n" +
             "2. Go to Render Dashboard → Environment Variables\n" +
             "3. Add: `GOOGLE_CLIENT_SECRET_JSON` = (paste entire JSON content)\n" +
             "4. Redeploy")
    st.stop()

authenticator = Authenticate(
    secret_credentials_path=credentials_file,
    cookie_name='multi_llm_chat_auth',
    cookie_key='multi_llm_chat_secret_key',
    redirect_uri=os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8501"),
)

authenticator.check_authentification()


# ==================== Chat Interface ====================

def load_chat_history():
    """Load chat history from Firestore into session state."""
    if not st.session_state.chat_loaded and st.session_state.user_id:
        history = get_chat_history(st.session_state.user_id)
        st.session_state.openai_chat_history = []
        st.session_state.gemini_chat_history = []

        # Rebuild LLM chat histories for context
        for msg in history:
            if msg['role'] == 'user':
                st.session_state.openai_chat_history.append({
                    "role": "user", "content": msg['content']
                })
                st.session_state.gemini_chat_history.append({
                    "role": "user", "content": msg['content']
                })
            elif msg['role'] == 'assistant':
                if msg.get('model') == 'openai':
                    st.session_state.openai_chat_history.append({
                        "role": "assistant", "content": msg['content']
                    })
                elif msg.get('model') == 'gemini':
                    st.session_state.gemini_chat_history.append({
                        "role": "assistant", "content": msg['content']
                    })

        st.session_state.chat_loaded = True


def fetch_openai_response(user_query, chat_history, response_queue):
    """Fetch OpenAI response in a separate thread."""
    try:
        response = get_response_from_openai(user_query, chat_history)
        response_queue.put(("openai", response))
    except Exception as e:
        response_queue.put(("openai", f"Error: {str(e)}"))


def fetch_gemini_response(user_query, chat_history, response_queue):
    """Fetch Gemini response in a separate thread."""
    try:
        response = get_gemini_response(user_query, chat_history)
        response_queue.put(("gemini", response))
    except Exception as e:
        response_queue.put(("gemini", f"Error: {str(e)}"))



def show_login_page():
    """Display the Google Sign-In login page."""
    st.markdown("<h1 style='text-align: center;'>🤖 Multi-LLM Chat</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Welcome! Sign in to continue</h3>", unsafe_allow_html=True)
    st.markdown("")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        authenticator.login()
        st.markdown("---")
        st.caption("Sign in with your Google account to access the Multi-LLM Chat application.")


def show_chat_page():
    """Display the main chat interface."""

    # Register user in Firestore on first login
    if not st.session_state.user_id:
        user_info = get_or_create_google_user(
            email=st.session_state.user_email,
            display_name=st.session_state.display_name or ''
        )
        st.session_state.user_id = st.session_state.user_email

    # ---- Sidebar ----
    with st.sidebar:
        if st.session_state.get('user_info', {}).get('picture'):
            st.image(st.session_state['user_info']['picture'], width=80)
        st.markdown(f"### 👤 {st.session_state.display_name or st.session_state.user_email}")
        st.caption(st.session_state.user_email)
        st.markdown("---")

        # Model selection
        st.subheader("🔧 Model Selection")
        model_choice = st.radio(
            "Choose AI Model:",
            ["OpenAI", "Gemini", "Both"],
            index=["OpenAI", "Gemini", "Both"].index(st.session_state.model_choice),
            key="model_radio"
        )
        st.session_state.model_choice = model_choice

        st.markdown("---")

        # Clear chat
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            with st.spinner("Clearing..."):
                clear_chat_history(st.session_state.user_id)
            st.session_state.openai_chat_history = []
            st.session_state.gemini_chat_history = []
            st.session_state.chat_loaded = False
            st.rerun()

        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            authenticator.logout()

    # ---- Main Chat Area ----
    st.title("🤖 Multi-LLM Chat")

    # Load existing chat history from Firestore
    load_chat_history()

    # Display chat history from Firestore
    history = get_chat_history(st.session_state.user_id) if st.session_state.user_id else []
    for msg in history:
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.write(msg['content'])
        elif msg['role'] == 'assistant':
            model_label = msg.get('model', 'AI').upper()
            with st.chat_message("assistant"):
                st.caption(f"🤖 {model_label}")
                st.write(msg['content'])

    # ---- Chat Input ----
    if user_query := st.chat_input("Type your message..."):
        # Display user message
        with st.chat_message("user"):
            st.write(user_query)

        # Save user message to Firestore
        save_chat_message(st.session_state.user_id, 'user', user_query)

        # Get AI responses based on model choice
        if st.session_state.model_choice == "Both":
            # Fetch both responses in parallel
            response_queue = Queue()
            threads = []

            # Start both threads
            openai_thread = threading.Thread(
                target=fetch_openai_response,
                args=(user_query, st.session_state.openai_chat_history, response_queue)
            )
            gemini_thread = threading.Thread(
                target=fetch_gemini_response,
                args=(user_query, st.session_state.gemini_chat_history, response_queue)
            )

            threads.append(openai_thread)
            threads.append(gemini_thread)

            # Show spinners for both models
            col1, col2 = st.columns(2)
            with col1:
                st.write("🤖 **OpenAI**")
                spinner_placeholder_openai = st.empty()
            with col2:
                st.write("🤖 **Gemini**")
                spinner_placeholder_gemini = st.empty()

            # Start threads
            openai_thread.start()
            gemini_thread.start()

            # Show spinners while waiting
            with spinner_placeholder_openai:
                with st.spinner("OpenAI is thinking..."):
                    pass
            with spinner_placeholder_gemini:
                with st.spinner("Gemini is thinking..."):
                    pass

            # Wait for both threads to complete
            openai_thread.join()
            gemini_thread.join()

            # Collect responses from queue
            responses = {}
            while not response_queue.empty():
                model, response = response_queue.get()
                responses[model] = response

            # Display responses side by side
            col1, col2 = st.columns(2)

            with col1:
                with st.chat_message("assistant"):
                    st.caption("🤖 OPENAI")
                    openai_response = responses.get("openai", "Error: No response received")
                    st.write(openai_response)

            with col2:
                with st.chat_message("assistant"):
                    st.caption("🤖 GEMINI")
                    gemini_response = responses.get("gemini", "Error: No response received")
                    st.write(gemini_response)

            # Update chat histories and save to Firestore
            st.session_state.openai_chat_history.append({"role": "user", "content": user_query})
            st.session_state.openai_chat_history.append({"role": "assistant", "content": openai_response})
            save_chat_message(st.session_state.user_id, 'assistant', openai_response, model='openai')

            st.session_state.gemini_chat_history.append({"role": "user", "content": user_query})
            st.session_state.gemini_chat_history.append({"role": "assistant", "content": gemini_response})
            save_chat_message(st.session_state.user_id, 'assistant', gemini_response, model='gemini')

        elif st.session_state.model_choice == "OpenAI":
            with st.chat_message("assistant"):
                st.caption("🤖 OPENAI")
                with st.spinner("OpenAI is thinking..."):
                    openai_response = get_response_from_openai(
                        user_query,
                        st.session_state.openai_chat_history
                    )
                st.write(openai_response)

            # Update OpenAI chat history for context
            st.session_state.openai_chat_history.append({"role": "user", "content": user_query})
            st.session_state.openai_chat_history.append({"role": "assistant", "content": openai_response})

            # Save to Firestore
            save_chat_message(st.session_state.user_id, 'assistant', openai_response, model='openai')

        elif st.session_state.model_choice == "Gemini":
            with st.chat_message("assistant"):
                st.caption("🤖 GEMINI")
                with st.spinner("Gemini is thinking..."):
                    gemini_response = get_gemini_response(
                        user_query,
                        st.session_state.gemini_chat_history
                    )
                st.write(gemini_response)

            # Update Gemini chat history for context
            st.session_state.gemini_chat_history.append({"role": "user", "content": user_query})
            st.session_state.gemini_chat_history.append({"role": "assistant", "content": gemini_response})

            # Save to Firestore
            save_chat_message(st.session_state.user_id, 'assistant', gemini_response, model='gemini')


# ==================== Main App Router ====================

if st.session_state.get('connected'):
    # User is authenticated via Google
    st.session_state.user_email = st.session_state.get('user_info', {}).get('email', '')
    st.session_state.display_name = st.session_state.get('user_info', {}).get('name', '')
    show_chat_page()
else:
    show_login_page()
