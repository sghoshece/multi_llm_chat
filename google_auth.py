"""
Simple Google OAuth2 authentication for Streamlit using authlib
Avoids PKCE issues with streamlit-google-auth
"""
import os
import json
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from urllib.parse import urlencode

class GoogleAuthenticator:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.google_auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
    
    def get_authorization_url(self):
        """Get Google OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': 'openid email profile',
            'redirect_uri': self.redirect_uri,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        return f"{self.google_auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        try:
            import requests
            data = {
                'code': code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code'
            }
            response = requests.post(self.google_token_url, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error exchanging code for token: {e}")
            return None
    
    def get_user_info(self, access_token):
        """Get user info from Google"""
        try:
            import requests
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(self.google_userinfo_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error getting user info: {e}")
            return None
    
    def authenticate(self):
        """Main authentication flow"""
        # Check if already authenticated
        if st.session_state.get('authenticated'):
            return True
        
        # Get authorization code from URL params
        query_params = st.query_params
        code = query_params.get('code')
        
        if code:
            # Exchange code for token
            token_data = self.exchange_code_for_token(code)
            if token_data and 'access_token' in token_data:
                # Get user info
                user_info = self.get_user_info(token_data['access_token'])
                if user_info:
                    # Store in session
                    st.session_state.authenticated = True
                    st.session_state.user_email = user_info.get('email')
                    st.session_state.user_id = user_info.get('sub')
                    st.session_state.display_name = user_info.get('name')
                    st.session_state.user_picture = user_info.get('picture')
                    
                    # Clear the code from URL
                    st.query_params.clear()
                    st.rerun()
                    return True
        
        return False
    
    def show_login_button(self):
        """Show Google login button"""
        auth_url = self.get_authorization_url()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                f'<a href="{auth_url}" target="_self">'
                f'<button style="width:100%; padding:10px; background-color:#4285f4; color:white; '
                f'border:none; border-radius:4px; cursor:pointer; font-size:16px;">'
                f'🔐 Sign in with Google</button></a>',
                unsafe_allow_html=True
            )
    
    def logout(self):
        """Logout user"""
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_id = None
        st.session_state.display_name = None
        st.session_state.user_picture = None
        st.query_params.clear()
        st.rerun()
