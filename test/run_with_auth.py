#!/usr/bin/env python
"""
Test script to run BujoNow with simulated authentication environment variables.
This is useful for testing the authentication flow locally.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Run the application with simulated authentication environment"""
    # Set environment variables for testing
    os.environ["OAUTH_CLIENT_ID"] = "test_client_id"
    os.environ["OAUTH_CLIENT_SECRET"] = "test_client_secret"
    os.environ["OPENID_PROVIDER_URL"] = "https://huggingface.co"
    
    print("=== Running BujoNow with simulated authentication environment ===")
    print("Note: Real OAuth login won't work with these test credentials")
    print("This is just to test that the app starts correctly with auth enabled")
    print("")
    print("Environment variables set:")
    print(f"OAUTH_CLIENT_ID: {os.environ.get('OAUTH_CLIENT_ID')}")
    print(f"OAUTH_CLIENT_SECRET: {os.environ.get('OAUTH_CLIENT_SECRET')}")
    print(f"OPENID_PROVIDER_URL: {os.environ.get('OPENID_PROVIDER_URL')}")
    print("")
    
    # Import and run the app
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from app import app
        app.launch()
    except Exception as e:
        print(f"Error running the app: {e}")
        
if __name__ == "__main__":
    main() 