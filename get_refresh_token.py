#!/usr/bin/env python3
"""
Google Calendar Refresh Token Extractor

This script helps you get the refresh token needed for Coolify deployment.
Run this locally to complete the OAuth flow and extract the refresh token.
"""

import os
import json
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("refresh_token_extractor")

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

def extract_from_existing_token():
    """Extract refresh token from existing token file"""
    token_file = "google_calendar_token.json"
    
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            refresh_token = token_data.get('refresh_token')
            if refresh_token:
                print("\n" + "="*60)
                print("🎉 REFRESH TOKEN FOUND!")
                print("="*60)
                print(f"GOOGLE_REFRESH_TOKEN={refresh_token}")
                print("="*60)
                print("\n📋 Copy the above line to your Coolify environment variables!")
                return True
            else:
                print("❌ No refresh token found in existing token file")
                return False
                
        except Exception as e:
            print(f"❌ Error reading token file: {e}")
            return False
    else:
        print("ℹ️ No existing token file found")
        return False

def run_oauth_flow():
    """Run OAuth flow to get refresh token"""
    credentials_file = "gcp-oauth.keys.json"
    
    if not os.path.exists(credentials_file):
        print(f"❌ OAuth credentials file not found: {credentials_file}")
        print("💡 Make sure you have downloaded your OAuth credentials from Google Cloud Console")
        print("💡 and renamed the file to 'gcp-oauth.keys.json'")
        return False
    
    try:
        # Create OAuth flow
        flow = Flow.from_client_secrets_file(
            credentials_file, 
            SCOPES,
            redirect_uri='http://localhost:3500/oauth2callback'
        )
        
        # Get authorization URL
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline'  # This ensures we get a refresh token
        )
        
        print("\n" + "="*60)
        print("🔐 GOOGLE OAUTH AUTHORIZATION")
        print("="*60)
        print("1. Open this URL in your browser:")
        print(f"   {auth_url}")
        print("\n2. Complete the authorization process")
        print("3. You'll be redirected to a localhost URL that won't load")
        print("4. Copy the ENTIRE redirect URL from your browser's address bar")
        print("5. Paste it below")
        print("="*60)
        
        # Get authorization code from user
        redirect_url = input("\nPaste the redirect URL here: ").strip()
        
        if 'code=' not in redirect_url:
            print("❌ Invalid redirect URL. Make sure it contains 'code=' parameter")
            return False
        
        # Extract authorization code
        code = redirect_url.split('code=')[1].split('&')[0]
        
        # Exchange code for tokens
        flow.fetch_token(code=code)
        
        # Save credentials
        credentials = flow.credentials
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        with open('google_calendar_token.json', 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print("\n" + "="*60)
        print("🎉 SUCCESS! TOKENS OBTAINED")
        print("="*60)
        print(f"GOOGLE_REFRESH_TOKEN={credentials.refresh_token}")
        print("="*60)
        print("\n📋 Copy the above line to your Coolify environment variables!")
        print("💾 Tokens saved to: google_calendar_token.json")
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth flow failed: {e}")
        return False

def extract_credentials_info():
    """Extract client ID, secret, and project ID from credentials file"""
    credentials_file = "gcp-oauth.keys.json"
    
    if not os.path.exists(credentials_file):
        print(f"❌ Credentials file not found: {credentials_file}")
        return False
    
    try:
        with open(credentials_file, 'r') as f:
            creds_data = json.load(f)
        
        # Handle both "installed" and "web" credential types
        creds_info = creds_data.get('installed') or creds_data.get('web')
        
        if not creds_info:
            print("❌ Invalid credentials file format")
            return False
        
        client_id = creds_info.get('client_id')
        client_secret = creds_info.get('client_secret')
        project_id = creds_info.get('project_id')
        
        print("\n" + "="*60)
        print("📋 GOOGLE OAUTH CREDENTIALS")
        print("="*60)
        print(f"GOOGLE_CLIENT_ID={client_id}")
        print(f"GOOGLE_CLIENT_SECRET={client_secret}")
        print(f"GOOGLE_PROJECT_ID={project_id}")
        print("="*60)
        print("\n📋 Copy the above lines to your Coolify environment variables!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False

def main():
    print("🔑 Google Calendar Refresh Token Extractor")
    print("=" * 50)
    
    # First, show the credentials info
    print("\n1️⃣ Extracting OAuth credentials info...")
    extract_credentials_info()
    
    # Try to extract from existing token file first
    print("\n2️⃣ Checking for existing refresh token...")
    if extract_from_existing_token():
        print("\n✅ All done! You have everything needed for Coolify deployment.")
        return
    
    # If no existing token, run OAuth flow
    print("\n3️⃣ Running OAuth flow to get refresh token...")
    if run_oauth_flow():
        print("\n✅ All done! You now have everything needed for Coolify deployment.")
    else:
        print("\n❌ Failed to get refresh token. Please check the errors above.")

if __name__ == "__main__":
    main()