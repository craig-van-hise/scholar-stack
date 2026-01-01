import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import streamlit as st

# Configuration
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/drive.file",
    "openid"
]

# Note: In production, this must be your actual deployed URL (e.g. https://your-app.com)
# For local/dev, localhost is fine.
REDIRECT_URI = "http://localhost:8501" 

def get_flow():
    """Creates the OAuth flow object."""
    if not os.path.exists(CLIENT_SECRETS_FILE):
        return None
        
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    return flow

def get_login_url():
    """Generates the Google Login URL."""
    flow = get_flow()
    if not flow:
        return None
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url

def get_token_from_code(code):
    """Exchanges the auth code for a token."""
    flow = get_flow()
    if not flow:
        return None
        
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return credentials

def get_user_info(credentials):
    """Fetches user profile info using the credentials."""
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info
    except:
        return None
