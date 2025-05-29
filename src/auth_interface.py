"""
Authentication Interface Module
Handles user authentication flow with Hugging Face OAuth.
"""

import os
import uuid
import gradio as gr
import json
from typing import Dict, Tuple, Optional, Callable, Any
import requests
from datetime import datetime
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth_interface")

from src.user_manager import UserManager

# Create global session state dictionary
SESSION_STATES = {}

def create_auth_interface(on_login_success: Optional[Callable[[str, Dict], Any]] = None):
    """Create the authentication interface components
    
    Args:
        on_login_success: Callback function called when login is successful
                         with user_id and user_data as arguments
    """
    user_manager = UserManager()
    
    # Get the OAuth configuration
    client_id = os.getenv("OAUTH_CLIENT_ID")
    openid_provider_url = os.getenv("OPENID_PROVIDER_URL")
    space_host = os.getenv("SPACE_HOST", "localhost:7860")
    
    # Define the redirect URI
    if "localhost" in space_host:
        # For local development
        redirect_uri = f"http://{space_host}/login/callback"
        is_local = True
    else:
        # For Hugging Face Spaces
        redirect_uri = f"https://{space_host}/login/callback"
        is_local = False
        
    # For deployed version override
    deployed_redirect = "https://stilllleaf-bujonow.hf.space/login/callback"
        
    # Print some debug info
    print(f"OAuth redirect URI: {redirect_uri}")
    print(f"Is local development: {is_local}")
    if is_local:
        print("WARNING: Running in local development mode. You will need to manually copy the authorization code.")
        print(f"The authorization will redirect to: {deployed_redirect}")
        print("But your local app is running at: http://localhost:7860 or http://0.0.0.0:7861")
        print("After authorizing, copy the 'code' and 'state' parameters from the URL and manually enter them in your local app.")
    
    def generate_login_url(state: str) -> str:
        """Generate the login URL with state parameter"""
        # Check if required environment variables are set
        if not user_manager.openid_provider_url:
            logger.error("Missing OPENID_PROVIDER_URL environment variable")
            user_manager.openid_provider_url = "https://huggingface.co"
            logger.info(f"Using default OPENID_PROVIDER_URL: {user_manager.openid_provider_url}")
            
        if not user_manager.client_id:
            logger.error("Missing OAUTH_CLIENT_ID environment variable - authentication will not work correctly")
            
        # For local development, always use the deployed redirect URI to match registration
        if is_local:
            login_url = user_manager.get_auth_url(deployed_redirect, state)
            logger.info(f"Using deployed redirect URL for local development: {deployed_redirect}")
        else:
            login_url = user_manager.get_auth_url(redirect_uri, state)
            
        logger.info(f"Generated login URL: {login_url}")
        return login_url
    
    def handle_login_start() -> Dict:
        """Start the login flow by creating a state and redirecting to the authorization URL"""
        # Generate a state parameter to prevent CSRF
        state = str(uuid.uuid4())
        
        # Store the state in the session
        session_id = str(uuid.uuid4())
        SESSION_STATES[session_id] = {
            "state": state,
            "created_at": datetime.now().isoformat()
        }
        
        # Generate the login URL
        login_url = generate_login_url(state)
        logger.info(f"Generated login URL: {login_url}")
        
        # Check if we have a valid login URL
        if not user_manager.client_id or "client_id=None" in login_url:
            logger.error("Cannot start authentication: Missing OAUTH_CLIENT_ID")
            return {
                "session_id": session_id,
                "error": "Authentication not configured: Missing OAUTH_CLIENT_ID environment variable",
                "login_url": ""
            }
        
        return {
            "session_id": session_id,
            "login_url": login_url
        }
    
    def handle_login_callback(session_id: str, code: Optional[str] = None, state: Optional[str] = None) -> Dict:
        """Handle the callback from the authorization server"""
        logger.info(f"Received login callback with session_id: {session_id}, state: {state}, code: {'present' if code else 'missing'}")
        
        if not code or not state or not session_id:
            logger.warning("Missing required parameters in login callback")
            return {
                "success": False,
                "error": "Missing required parameters",
                "logged_in": False
            }
        
        # Verify the state parameter
        if session_id not in SESSION_STATES:
            logger.warning(f"Invalid session ID: {session_id}")
            return {
                "success": False,
                "error": "Invalid session",
                "logged_in": False
            }
        
        session_state = SESSION_STATES[session_id]["state"]
        if state != session_state:
            logger.warning(f"State mismatch. Expected: {session_state}, Received: {state}")
            return {
                "success": False,
                "error": "Invalid state parameter",
                "logged_in": False
            }
        
        try:
            # Exchange the code for tokens
            logger.info("Exchanging code for token...")
            
            # For local development, always use the deployed redirect URI to match the authorization request
            exchange_redirect_uri = deployed_redirect if is_local else redirect_uri
            logger.info(f"Using redirect URI for token exchange: {exchange_redirect_uri}")
            
            token_data = user_manager.exchange_code_for_token(code, exchange_redirect_uri)
            
            if "error" in token_data:
                logger.error(f"Error exchanging code for token: {token_data.get('error')}: {token_data.get('error_description', '')}")
                return {
                    "success": False,
                    "error": token_data.get("error_description", token_data["error"]),
                    "logged_in": False
                }
            
            # Get the user info from the access token
            logger.info("Getting user info from access token...")
            access_token = token_data["access_token"]
            user_info = user_manager.get_user_info(access_token)
            
            if "error" in user_info:
                logger.error(f"Error getting user info: {user_info.get('error')}")
                logger.error(f"User info response details: {user_info.get('response_text', 'N/A')}")
                return {
                    "success": False,
                    "error": user_info.get("error", "Failed to get user info"),
                    "logged_in": False,
                    "details": user_info.get('response_text', 'No additional details')
                }
            
            # Store the user session
            user_id = user_info.get("preferred_username") or user_info.get("sub")
            logger.info(f"Storing session for user: {user_id}")
            user_manager.store_user_session(user_info, token_data)
            
            # Clean up the session state
            del SESSION_STATES[session_id]
            
            # Get user data
            user_data = user_manager.get_user_data(user_id)
            
            # Call the login success callback if provided
            if on_login_success and callable(on_login_success):
                logger.info(f"Calling login success callback for user: {user_id}")
                on_login_success(user_id, user_data)
            
            return {
                "success": True,
                "user_id": user_id,
                "username": user_info.get("preferred_username", ""),
                "logged_in": True
            }
        except Exception as e:
            logger.exception(f"Exception in login callback: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "logged_in": False
            }
    
    def check_login_status(user_id: Optional[str] = None) -> Dict:
        """Check if a user is logged in"""
        if not user_id:
            return {
                "logged_in": False
            }
        
        # Check if the session is valid
        is_valid = user_manager.is_session_valid(user_id)
        
        if is_valid:
            # Update the last login timestamp
            user_manager.update_last_login(user_id)
            
            # Get user data
            user_data = user_manager.get_user_data(user_id)
            
            return {
                "logged_in": True,
                "user_id": user_id,
                "username": user_data.get("username", ""),
                "name": user_data.get("name", "")
            }
        else:
            return {
                "logged_in": False
            }
    
    def logout(user_id: Optional[str] = None) -> Dict:
        """Log out a user by invalidating their session"""
        if not user_id:
            return {
                "success": True,
                "message": "No active session to log out"
            }
        
        try:
            # Get user data
            user_data = user_manager.get_user_data(user_id)
            
            if user_data and "auth" in user_data:
                # Clear auth data (we keep other user data)
                user_data["auth"] = {
                    "access_token": "",
                    "id_token": "",
                    "refresh_token": "",
                    "expires_at": datetime.now().isoformat()
                }
                
                # Save updated user data
                user_data_path = user_manager._get_user_data_path(user_id)
                with open(user_data_path, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "message": "Logged out successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # Create the login interface components
    with gr.Blocks() as auth_interface:
        user_id_state = gr.State(None)
        session_id_state = gr.State(None)
        
        with gr.Row():
            with gr.Column():
                login_button = gr.Button("Sign in with Hugging Face")
                logout_button = gr.Button("Log out")
            
            with gr.Column():
                login_status = gr.JSON({"logged_in": False})
                # Add HTML element for redirect
                html_redirect = gr.HTML("", visible=False)
        
        # Handle login flow
        def start_login():
            result = handle_login_start()
            login_url = result.get("login_url", "")
            
            # Check if there was an error
            if "error" in result:
                error_message = result["error"]
                return result["session_id"], gr.update(value={
                    "logged_in": False, 
                    "error": error_message
                }), f"""<div class="error-message">{error_message}</div>"""
            
            # Create json with login info for manual login if needed
            login_info = {
                "logged_in": False,
                "session_id": result["session_id"],
                "login_url": login_url,
                "instructions": "If automatic login doesn't work, copy and paste this URL into your browser"
            }
                
            # Create a special response that Gradio will recognize as a redirect
            return result["session_id"], gr.update(value=login_info), f"""<script>window.open("{login_url}", "_blank");</script>"""
        
        # Note: Added an HTML output for the redirect
        html_redirect = gr.HTML("")
        login_button.click(fn=start_login, outputs=[session_id_state, login_status, html_redirect])
        
        # Implement callback handling
        def process_login_callback(session_id, code, state):
            if not code or not state or not session_id:
                return None, {"logged_in": False, "error": "Invalid login attempt"}
            
            result = handle_login_callback(session_id, code, state)
            
            if result["success"]:
                return result["user_id"], result
            else:
                return None, {"logged_in": False, "error": result["error"]}
        
        # Add logout functionality
        def handle_logout(user_id):
            if not user_id:
                return None, {"logged_in": False}
            
            result = logout(user_id)
            
            if result["success"]:
                return None, {"logged_in": False, "message": "Logged out successfully"}
            else:
                return user_id, {"logged_in": True, "error": result["error"]}
        
        logout_button.click(fn=handle_logout, inputs=user_id_state, outputs=[user_id_state, login_status])
        
        # Function to check login status
        def update_login_status(user_id):
            return check_login_status(user_id)
        
    # Return the components
    return {
        "interface": auth_interface,
        "user_id_state": user_id_state,
        "session_id_state": session_id_state,
        "login_status": login_status,
        "login_button": login_button,
        "logout_button": logout_button,
        "update_login_status": update_login_status,
        "process_login_callback": process_login_callback,
        "user_manager": user_manager
    } 