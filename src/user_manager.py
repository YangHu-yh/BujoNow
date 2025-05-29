"""
User Manager Module
Handles user authentication, sessions, and user-specific data management.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from pathlib import Path
import base64
import urllib.parse

class UserManager:
    def __init__(self, users_dir: str = "users"):
        """Initialize the user manager"""
        self.users_dir = users_dir
        self._ensure_users_dir()
        self.client_id = os.getenv("OAUTH_CLIENT_ID")
        self.client_secret = os.getenv("OAUTH_CLIENT_SECRET")
        self.openid_provider_url = os.getenv("OPENID_PROVIDER_URL")

    def _ensure_users_dir(self):
        """Ensure the users directory exists"""
        Path(self.users_dir).mkdir(parents=True, exist_ok=True)

    def _get_user_dir(self, user_id: str) -> str:
        """Get the directory for a specific user's data"""
        user_dir = os.path.join(self.users_dir, user_id)
        Path(user_dir).mkdir(parents=True, exist_ok=True)
        return user_dir

    def _get_user_journal_dir(self, user_id: str) -> str:
        """Get the journal directory for a specific user"""
        return os.path.join(self._get_user_dir(user_id), "journals")

    def _get_user_data_path(self, user_id: str) -> str:
        """Get the path to the user's data file"""
        return os.path.join(self._get_user_dir(user_id), "user_data.json")

    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate the OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid",
            "state": state
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.openid_provider_url}/oauth/authorize?{query_string}"

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict:
        """Exchange authorization code for access token"""
        token_url = f"{self.openid_provider_url}/oauth/token"
        
        # Create Basic auth header using client_id and client_secret
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "redirect_uri": redirect_uri
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code != 200:
            print(f"Error exchanging code for token: {response.status_code} {response.text}")
            return {"error": "invalid_request", "error_description": f"Failed to exchange code: {response.text}"}
            
        return response.json()

    def get_user_info(self, access_token: str) -> Dict:
        """Get user information from the token"""
        userinfo_url = f"{self.openid_provider_url}/userinfo"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(userinfo_url, headers=headers)
        print(f"DEBUG: UserInfo endpoint ({userinfo_url}) response status: {response.status_code}")
        print(f"DEBUG: UserInfo endpoint response text: {response.text[:500]}...") # Log first 500 chars
        if response.status_code != 200:
            print(f"ERROR: UserInfo request failed with status {response.status_code}, content: {response.text}")
            # Return a dict with error info, as the calling code expects a dict
            return {"error": "userinfo_request_failed", "status_code": response.status_code, "response_text": response.text}
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f"ERROR: Failed to decode JSON from UserInfo endpoint. Error: {e}")
            print(f"ERROR: UserInfo raw response text: {response.text}")
            return {"error": "userinfo_json_decode_error", "response_text": response.text}

    def store_user_session(self, user_info: Dict, token_data: Dict) -> str:
        """Store user session data"""
        user_id = user_info.get("preferred_username") or user_info.get("sub")
        user_data_path = self._get_user_data_path(user_id)
        
        # Create user's journal directory
        journal_dir = self._get_user_journal_dir(user_id)
        Path(journal_dir).mkdir(parents=True, exist_ok=True)
        
        # Calculate token expiration time
        expires_in = token_data.get("expires_in", 86400)  # Default to 24 hours
        expiration_time = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
        
        user_data = {
            "user_id": user_id,
            "username": user_info.get("preferred_username", ""),
            "name": user_info.get("name", ""),
            "email": user_info.get("email", ""),
            "avatar": user_info.get("picture", ""),
            "auth": {
                "access_token": token_data.get("access_token", ""),
                "id_token": token_data.get("id_token", ""),
                "refresh_token": token_data.get("refresh_token", ""),
                "expires_at": expiration_time
            },
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat()
        }
        
        with open(user_data_path, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)
        
        return user_id

    def get_user_data(self, user_id: str) -> Optional[Dict]:
        """Get stored user data"""
        user_data_path = self._get_user_data_path(user_id)
        
        try:
            with open(user_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def update_last_login(self, user_id: str) -> None:
        """Update the last login timestamp for a user"""
        user_data = self.get_user_data(user_id)
        if user_data:
            user_data["last_login"] = datetime.now().isoformat()
            
            user_data_path = self._get_user_data_path(user_id)
            with open(user_data_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)

    def is_session_valid(self, user_id: str) -> bool:
        """Check if a user's session is still valid"""
        user_data = self.get_user_data(user_id)
        if not user_data or "auth" not in user_data:
            return False
        
        try:
            expires_at = datetime.fromisoformat(user_data["auth"]["expires_at"])
            return datetime.now() < expires_at
        except (ValueError, KeyError):
            return False

    def get_user_journal_manager_path(self, user_id: str) -> str:
        """Get the journal directory path for a specific user"""
        return self._get_user_journal_dir(user_id) 