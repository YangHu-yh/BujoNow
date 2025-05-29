#!/usr/bin/env python
"""
Test OAuth flow for BujoNow
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.append(str(Path(__file__).parent.parent))

# Set environment variables if not set
if not os.environ.get("OAUTH_CLIENT_ID"):
    # Use the actual client ID from your Hugging Face Space
    os.environ["OAUTH_CLIENT_ID"] = "5a7f13e6-56ac-4f6a-a703-b1770ec509e6"
    
if not os.environ.get("OPENID_PROVIDER_URL"):
    os.environ["OPENID_PROVIDER_URL"] = "https://huggingface.co"

# Import the user manager
from src.user_manager import UserManager

# Create a user manager
user_manager = UserManager()

# Deployed redirect URI - must match what's registered with Hugging Face
deployed_redirect = "https://stilllleaf-bujonow.hf.space/login/callback"

# Generate a state for the authorization URL
import uuid
state = str(uuid.uuid4())

# Generate the authorization URL
auth_url = user_manager.get_auth_url(deployed_redirect, state)
print("\n=== Authorization URL ===")
print(auth_url)
print("\nOpen this URL in your browser, authorize the application, and copy the code and state from the redirect URL.")

# Get the code and state from the user
print("\n=== Manual Entry ===")
code = input("Enter the 'code' parameter from the redirect URL: ")
redirect_state = input("Enter the 'state' parameter from the redirect URL: ")

# Verify the state
if state != redirect_state:
    print("\nERROR: State mismatch. This could be a security issue or you may have copied the wrong value.")
    print(f"Expected: {state}")
    print(f"Received: {redirect_state}")
    sys.exit(1)

# Exchange the code for a token
print("\n=== Exchanging Code for Token ===")
token_data = user_manager.exchange_code_for_token(code, deployed_redirect)

if "error" in token_data:
    print(f"\nERROR: Failed to exchange code for token: {token_data.get('error')}: {token_data.get('error_description', '')}")
    sys.exit(1)

# Get the user info
print("\n=== Getting User Info ===")
access_token = token_data["access_token"]
user_info = user_manager.get_user_info(access_token)

# Print the user info
print("\n=== User Info ===")
print(f"User ID: {user_info.get('preferred_username') or user_info.get('sub')}")
print(f"Name: {user_info.get('name', 'N/A')}")
print(f"Email: {user_info.get('email', 'N/A')}")

# Store the user session
user_id = user_info.get("preferred_username") or user_info.get("sub")
print("\n=== Storing User Session ===")
user_manager.store_user_session(user_info, token_data)
print(f"Session stored for user: {user_id}")

print("\n=== Success! ===")
print("OAuth flow completed successfully.")
print(f"User data saved to: {user_manager._get_user_data_path(user_id)}") 