"""
Authentication System Test

This file contains tests for the authentication system.
Run this manually after setting up the OAuth credentials.
"""

import os
import sys
import json
import uuid
import time
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import components
from src.user_manager import UserManager

def test_user_manager():
    """Test the UserManager class functionality"""
    print("Testing UserManager...")
    
    # Create a UserManager instance
    user_manager = UserManager()
    
    # Check directory creation
    assert os.path.exists(user_manager.users_dir), "Users directory not created"
    print("✅ Users directory exists")
    
    # Check environment variables
    if not os.environ.get("OAUTH_CLIENT_ID"):
        print("❌ OAUTH_CLIENT_ID not set - skipping OAuth tests")
        return
    
    if not os.environ.get("OAUTH_CLIENT_SECRET"):
        print("❌ OAUTH_CLIENT_SECRET not set - skipping OAuth tests")
        return
    
    if not os.environ.get("OPENID_PROVIDER_URL"):
        print("❌ OPENID_PROVIDER_URL not set - skipping OAuth tests")
        return
    
    print("✅ OAuth environment variables are set")
    
    # Test auth URL generation
    redirect_uri = "http://localhost:7860/login/callback"
    state = str(uuid.uuid4())
    auth_url = user_manager.get_auth_url(redirect_uri, state)
    
    assert "huggingface.co/oauth/authorize" in auth_url, "Auth URL doesn't contain provider URL"
    assert f"client_id={os.environ.get('OAUTH_CLIENT_ID')}" in auth_url, "Auth URL doesn't contain client ID"
    assert f"state={state}" in auth_url, "Auth URL doesn't contain state parameter"
    
    print("✅ Auth URL generation works")
    print(f"Auth URL: {auth_url}")
    
    # Test user directory functions
    test_user_id = "test_user_" + str(int(time.time()))
    user_dir = user_manager._get_user_dir(test_user_id)
    assert os.path.exists(user_dir), "User directory not created"
    print(f"✅ User directory created at {user_dir}")
    
    journal_dir = user_manager._get_user_journal_dir(test_user_id)
    assert os.path.exists(journal_dir), "User journal directory not created"
    print(f"✅ User journal directory created at {journal_dir}")
    
    # Create test user data
    test_user_data = {
        "user_id": test_user_id,
        "username": "test_user",
        "name": "Test User",
        "auth": {
            "access_token": "fake_token",
            "id_token": "fake_id_token",
            "refresh_token": "fake_refresh_token",
            "expires_at": (time.time() + 3600) # 1 hour from now
        },
        "created_at": time.time(),
        "last_login": time.time()
    }
    
    # Save test user data
    user_data_path = user_manager._get_user_data_path(test_user_id)
    with open(user_data_path, 'w', encoding='utf-8') as f:
        json.dump(test_user_data, f, indent=2)
    
    # Test getting user data
    loaded_data = user_manager.get_user_data(test_user_id)
    assert loaded_data is not None, "Failed to load user data"
    assert loaded_data["user_id"] == test_user_id, "User ID mismatch"
    print("✅ User data saved and loaded successfully")
    
    # Test session validation
    is_valid = user_manager.is_session_valid(test_user_id)
    assert is_valid, "Session should be valid"
    print("✅ Session validation works")
    
    # Clean up test data
    try:
        import shutil
        shutil.rmtree(user_dir)
        print(f"✅ Cleaned up test user directory: {user_dir}")
    except Exception as e:
        print(f"⚠️ Could not clean up test directory: {e}")
    
    print("✅ All UserManager tests passed!")

if __name__ == "__main__":
    test_user_manager() 