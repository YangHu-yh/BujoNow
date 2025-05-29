"""
Interface Module

Creates the web interface for the BujoNow application with graceful fallbacks
for missing dependencies.
"""

import os
import sys
import datetime
import traceback
import gradio as gr
from typing import Dict, Any, List

# First try to import core components that should always work
try:
    # Basic imports
    print("Initializing interface module with safe imports...")
    
    # Set up variables to track available features
    has_journal_manager = False
    has_full_analyzer = False
    has_simplified_analyzer = False
    has_app_manager = False
    has_auth_interface = False
    
    # Import authentication components
    try:
        from src.auth_interface import create_auth_interface
        has_auth_interface = True
        print("Authentication interface imported successfully")
    except Exception as e:
        print(f"Warning: Could not import authentication interface: {e}")
    
    # Import journal manager first as it's most essential
    try:
        from src.journal_manager import JournalManager
        has_journal_manager = True
        print("Journal manager imported successfully")
    except Exception as e:
        print(f"Warning: Could not import journal manager: {e}")
    
    # Import user manager
    try:
        from src.user_manager import UserManager
        has_user_manager = True
        print("User manager imported successfully")
    except Exception as e:
        print(f"Warning: Could not import user manager: {e}")
    
    # Try to import analyzers with fallbacks
    try:
        try:
            from src.analyzer import Analyzer
            has_full_analyzer = True
            print("Using full analyzer with embeddings support")
        except Exception as e:
            print(f"Warning: Could not import full analyzer: {e}")
            try:
                from src.analyzer_simplified import Analyzer
                has_simplified_analyzer = True
                print("Using simplified analyzer without embeddings")
            except Exception as e:
                print(f"Warning: Could not import simplified analyzer: {e}")
                
        # Use fallback analyzer if others failed
        if not has_full_analyzer and not has_simplified_analyzer:
            print("Creating minimal analyzer as fallback")
            try:
                from src.analyzer_fallback import Analyzer
                has_simplified_analyzer = True
                print("Using fallback analyzer")
            except Exception as e:
                print(f"Could not import fallback analyzer: {e}")
                # We'll handle this case below in safety check
    except Exception as e:
        print(f"Error setting up analyzer: {e}")
    
    # Try to import app_manager
    try:
        from src.app_manager import AppManager, app_manager
        has_app_manager = True
        print("App manager imported successfully")
    except Exception as e:
        print(f"Warning: Could not import app manager: {e}")
    
    # Create components if needed
    if has_journal_manager and not has_app_manager:
        # Create a minimal app manager
        try:
            from src.app_manager_minimal import MinimalAppManager
            app_manager = MinimalAppManager()
            print("Created minimal app manager")
        except Exception as e:
            print(f"Error creating minimal app manager: {e}")
            app_manager = None
    
    # Safety check
    if not has_journal_manager or not 'app_manager' in locals() or app_manager is None:
        raise ImportError("Critical components unavailable")
        
except Exception as e:
    # Critical error fallback - avoid any imports from other modules
    print(f"CRITICAL ERROR in interface.py: {e}")
    traceback.print_exc()
    has_journal_manager = False
    has_full_analyzer = False
    has_simplified_analyzer = False
    has_app_manager = False
    has_auth_interface = False
    
    # Use emergency app manager
    try:
        from src.app_manager_emergency import UltraMinimalAppManager
        app_manager = UltraMinimalAppManager()
        print("Created ultra-minimal app manager due to critical errors")
    except Exception as e:
        print(f"Error creating emergency app manager: {e}")
        app_manager = None

def create_interface():
    """
    Create the main application interface with graceful fallbacks for errors
    
    Returns:
        Gradio Blocks interface
    """
    try:
        # Current active user ID
        current_user_id = None
        
        def on_login_success(user_id, user_data):
            """Handle successful login"""
            nonlocal current_user_id
            current_user_id = user_id
            
            # Update the app manager with the new user
            if has_app_manager and hasattr(app_manager, 'set_user_id'):
                app_manager.set_user_id(user_id)
            
            print(f"User {user_id} logged in successfully")
        
        # Create the main interface
        with gr.Blocks(title="BujoNow - Bullet Journal Companion") as interface:
            gr.Markdown("# BujoNow - Bullet Journal Companion")
            
            # Show a message if using the simplified version
            if not has_app_manager or not has_full_analyzer:
                mode = "Safe Mode" if has_journal_manager else "Ultra-Minimal Mode"
                gr.Markdown(f"## {mode}")
                gr.Markdown("""
                Running with limited functionality due to missing components.
                Some advanced features may not be available.
                """)
            
            # User state storage
            user_id_state = gr.State(None)
            
            # Create authentication interface if available
            if has_auth_interface:
                auth_components = create_auth_interface(on_login_success=on_login_success)
                auth_interface = auth_components["interface"]
                user_id_state = auth_components["user_id_state"]
                login_status = auth_components["login_status"]
                session_id_state = auth_components["session_id_state"]
                process_login_callback = auth_components["process_login_callback"]
                user_manager = auth_components["user_manager"]
                
                # Add login status indicator
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("## Login Status")
                    with gr.Column(scale=1):
                        login_info = gr.JSON(label="Account Info", value={"logged_in": False})
                
                # Function to update UI based on login status
                def update_login_display(user_id):
                    if not user_id:
                        return {"logged_in": False}
                    
                    user_data = user_manager.get_user_data(user_id)
                    if user_data:
                        return {
                            "logged_in": True,
                            "username": user_data.get("username", ""),
                            "name": user_data.get("name", ""),
                        }
                    return {"logged_in": False}
                
                # Update login info when user_id changes
                user_id_state.change(
                    fn=update_login_display,
                    inputs=user_id_state,
                    outputs=login_info
                )
                
                # Add a manual check button
                check_login_button = gr.Button("Check Login Status")
                
                def check_login_status_manually():
                    try:
                        print("DEBUG - Manual login status check")
                        
                        # Try to see if there's a successful login in URL params
                        import os
                        query = os.environ.get("QUERY_STRING", "")
                        if "login_success=true" in query:
                            print("DEBUG - Login success detected in URL")
                            # Get all session IDs from SESSION_STATES
                            from src.auth_interface import SESSION_STATES
                            sessions = list(SESSION_STATES.keys())
                            print(f"DEBUG - Active sessions: {sessions}")
                            
                            # TODO: This is incomplete, would need to get user_id somehow
                            return {"logged_in": True, "message": "Login successful!"}
                        
                        # Check if there's a login error
                        if "auth_error=true" in query:
                            return {"logged_in": False, "error": "Login failed, please try again"}
                            
                        return {"logged_in": False, "message": "No active login detected"}
                    except Exception as e:
                        print(f"Error checking login status: {e}")
                        return {"logged_in": False, "error": str(e)}
                
                check_login_button.click(
                    fn=check_login_status_manually,
                    inputs=[],
                    outputs=[login_info]
                )
                
                # Add clear instructions for the redirect
                gr.Markdown("""
                ## Important: Callback Instructions
                
                After authorizing with Hugging Face, you'll be redirected to a callback URL.
                If the redirection doesn't happen automatically, please:
                
                1. Copy the URL from your browser after you authorize
                2. Go back to this app and modify the URL to include the code and state parameters
                3. The URL should look like: `[app-url]/?code=...&state=...`
                """)
                
                # Add manual authorization code entry for local development
                with gr.Accordion("Manual Authorization (for local testing)", open=True):
                    gr.Markdown("""
                    ### Manual Authorization Code Entry
                    
                    When testing locally, the OAuth redirect won't work properly. Follow these steps:
                    
                    1. Click "Sign in with Hugging Face" and authorize in the new window
                    2. After authorizing, you'll be redirected to a URL that shows "Not Found"
                    3. Copy the `code` and `state` parameters from that URL (look in your browser's address bar)
                    4. Enter them below and click "Process Authorization"
                    """)
                    
                    with gr.Row():
                        with gr.Column():
                            manual_code = gr.Textbox(label="Authorization Code", placeholder="Enter 'code' parameter from URL")
                            manual_state = gr.Textbox(label="State", placeholder="Enter 'state' parameter from URL")
                            manual_session_id = gr.Textbox(label="Session ID", value="")
                            manual_submit = gr.Button("Process Authorization")
                            
                        with gr.Column():
                            manual_result = gr.JSON(label="Authorization Result")
                    
                    def process_manual_auth(code, state, session_id):
                        try:
                            print(f"DEBUG - Processing manual authorization: code={code}, state={state}, session_id={session_id}")
                            
                            if not code or not state:
                                return {"success": False, "error": "Both code and state are required"}
                                
                            # If session_id is not provided, try to find it
                            if not session_id:
                                # Find matching session by state
                                from src.auth_interface import SESSION_STATES
                                for sid, data in SESSION_STATES.items():
                                    if data.get("state") == state:
                                        session_id = sid
                                        print(f"DEBUG - Found matching session ID: {session_id}")
                                        break
                                        
                            if not session_id:
                                return {"success": False, "error": "No matching session found for this state. Try clicking 'Sign in' again."}
                                
                            # Process the authentication
                            result = process_login_callback(session_id, code, state)
                            
                            if result and result[0]:  # If login succeeded
                                user_id = result[0]
                                print(f"DEBUG - Manual login succeeded for user: {user_id}")
                                return {"success": True, "user_id": user_id, "message": "Login successful!"}
                            else:
                                return {"success": False, "error": "Login processing failed"}
                                
                        except Exception as e:
                            print(f"Error in manual authorization: {e}")
                            import traceback
                            traceback.print_exc()
                            return {"success": False, "error": str(e)}
                    
                    # Update session ID when starting login
                    def update_session_id(session_id):
                        return session_id
                        
                    # Connect the session ID to the manual form
                    session_id_state.change(fn=update_session_id, inputs=[session_id_state], outputs=[manual_session_id])
                    
                    # Process manual authorization
                    manual_submit.click(
                        fn=process_manual_auth,
                        inputs=[manual_code, manual_state, manual_session_id],
                        outputs=[manual_result]
                    )
                
            # Only show journal tabs if user is logged in
            with gr.Tabs() as tabs:
                with gr.TabItem("Journal Entry", id="journal_entry"):
                    with gr.Row():
                        with gr.Column():
                            date_input = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                            text_input = gr.Textbox(label="Journal Entry", lines=10, placeholder="Write your thoughts here...")
                            submit_button = gr.Button("Save Entry")
                            
                        with gr.Column():
                            output = gr.JSON(label="Result")
                    
                    def save_entry(text, date, user_id):
                        try:
                            if not user_id:
                                return {
                                    "success": False,
                                    "error": "You must be logged in to save entries"
                                }
                            
                            # Update app manager to use the current user's journal directory
                            if has_app_manager and hasattr(app_manager, 'set_user_id'):
                                app_manager.set_user_id(user_id)
                            
                            return app_manager.save_text_journal(text, date)
                        except Exception as e:
                            return {
                                "success": False,
                                "error": f"Error saving journal: {type(e).__name__}: {e}"
                            }
                    
                    submit_button.click(
                        fn=save_entry,
                        inputs=[text_input, date_input, user_id_state],
                        outputs=output
                    )
                
                # Only show these tabs if we have journal manager
                if has_journal_manager:
                    with gr.TabItem("View Entries", id="view_entries"):
                        view_date = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                        view_button = gr.Button("View Entry")
                        view_output = gr.JSON(label="Entry")
                        
                        def get_entry(date, user_id):
                            try:
                                if not user_id:
                                    return {
                                        "success": False,
                                        "error": "You must be logged in to view entries"
                                    }
                                
                                # Update app manager to use the current user's journal directory
                                if has_app_manager and hasattr(app_manager, 'set_user_id'):
                                    app_manager.set_user_id(user_id)
                                
                                if hasattr(app_manager, 'get_entries_by_date'):
                                    entries = app_manager.get_entries_by_date(date)
                                    if entries and len(entries) > 0:
                                        return entries[0]
                                    return {"error": "No entry found for this date"}
                                else:
                                    return {"error": "View functionality is not available in this mode"}
                            except Exception as e:
                                return {
                                    "error": f"Error retrieving entry: {type(e).__name__}: {e}"
                                }
                        
                        view_button.click(
                            fn=get_entry,
                            inputs=[view_date, user_id_state],
                            outputs=view_output
                        )
                    
                    with gr.TabItem("Weekly Summary", id="weekly_summary"):
                        with gr.Row():
                            with gr.Column():
                                start_date = gr.Textbox(
                                    label="Start Date (YYYY-MM-DD)", 
                                    value=(datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
                                )
                                summary_button = gr.Button("Generate Summary")
                                
                            with gr.Column():
                                summary_output = gr.JSON(label="Weekly Summary")
                        
                        def get_summary(start, user_id):
                            try:
                                if not user_id:
                                    return {
                                        "success": False,
                                        "error": "You must be logged in to view summaries"
                                    }
                                
                                # Update app manager to use the current user's journal directory
                                if has_app_manager and hasattr(app_manager, 'set_user_id'):
                                    app_manager.set_user_id(user_id)
                                
                                if hasattr(app_manager, 'get_weekly_summary'):
                                    return app_manager.get_weekly_summary(start_date=start)
                                else:
                                    return {"error": "Weekly summary not available in this mode"}
                            except Exception as e:
                                return {
                                    "error": f"Error generating summary: {type(e).__name__}: {e}"
                                }
                        
                        summary_button.click(
                            fn=get_summary,
                            inputs=[start_date, user_id_state],
                            outputs=summary_output
                        )
                    
                    # Add Chat interface
                    with gr.TabItem("Chat with Journal", id="chat_journal"):
                        gr.Markdown("""
                        # Journal Assistant
                        
                        Chat with an AI assistant that can help you reflect on your journal entries.
                        Ask questions about your patterns, emotions, or for suggestions.
                        """)
                        
                        chatbot = gr.Chatbot(label="Journal Chat", type="messages")
                        chat_input = gr.Textbox(
                            placeholder="Ask a question about your journal entries...",
                            label="Your message",
                            lines=2
                        )
                        clear_button = gr.Button("Clear Chat")
                        load_history_button = gr.Button("Load Today's Chat History")
                        
                        def chat_response(user_input, history, user_id):
                            if not user_id:
                                return history + [
                                    {"role": "user", "content": user_input},
                                    {"role": "assistant", "content": "Please log in to use the chat functionality."}
                                ]
                            
                            if not user_input.strip():
                                return history
                            
                            try:
                                # Update app manager to use the current user's journal directory
                                if has_app_manager and hasattr(app_manager, 'set_user_id'):
                                    app_manager.set_user_id(user_id)
                                
                                # Get response from app manager
                                if hasattr(app_manager, 'chat_with_journal'):
                                    response = app_manager.chat_with_journal(user_input, history)
                                else:
                                    response = "Chat functionality is not available in the current mode."
                                
                                # Add to history and return - convert to message format
                                history.append({"role": "user", "content": user_input})
                                history.append({"role": "assistant", "content": response})
                                return history
                            except Exception as e:
                                print(f"Error in chat: {e}")
                                history.append({"role": "user", "content": user_input})
                                history.append({"role": "assistant", "content": f"Error: {str(e)}"})
                                return history
                        
                        def clear_chat_history():
                            return []
                        
                        def load_todays_chat_history(user_id):
                            if not user_id:
                                return []
                            
                            try:
                                # Update app manager to use the current user's journal directory
                                if has_app_manager and hasattr(app_manager, 'set_user_id'):
                                    app_manager.set_user_id(user_id)
                                
                                # Get today's date
                                today = datetime.datetime.now()
                                
                                # Try to get today's entry
                                if hasattr(app_manager, 'get_entries_by_date'):
                                    entries = app_manager.get_entries_by_date(today.strftime("%Y-%m-%d"))
                                    if entries and len(entries) > 0:
                                        entry = entries[0]
                                        # Check if entry has chat history
                                        if "content" in entry and "chat_history" in entry["content"]:
                                            return entry["content"]["chat_history"]
                                return []
                            except Exception as e:
                                print(f"Error loading chat history: {e}")
                                return []
                        
                        chat_input.submit(
                            fn=chat_response,
                            inputs=[chat_input, chatbot, user_id_state],
                            outputs=chatbot
                        )
                        
                        clear_button.click(
                            fn=clear_chat_history,
                            inputs=[],
                            outputs=chatbot
                        )
                        
                        load_history_button.click(
                            fn=load_todays_chat_history,
                            inputs=[user_id_state],
                            outputs=chatbot
                        )
                
                # User Profile Tab
                if has_auth_interface:
                    with gr.TabItem("User Profile", id="user_profile"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("## User Profile")
                                user_profile_info = gr.JSON(label="User Information")
                        
                        def get_user_profile(user_id):
                            if not user_id:
                                return {
                                    "logged_in": False,
                                    "message": "You must be logged in to view your profile"
                                }
                            
                            user_data = user_manager.get_user_data(user_id)
                            if user_data:
                                # Don't include auth data in the profile
                                profile_data = {k: v for k, v in user_data.items() if k != "auth"}
                                return profile_data
                            return {"logged_in": False, "message": "User data not found"}
                        
                        # Refresh button
                        refresh_profile_button = gr.Button("Refresh Profile")
                        refresh_profile_button.click(
                            fn=get_user_profile,
                            inputs=[user_id_state],
                            outputs=user_profile_info
                        )
                        
                        # Update profile on tab load
                        gr.on(
                            triggers=[tabs.select],
                            fn=lambda tab_id, user_id: get_user_profile(user_id) if tab_id == "user_profile" else None,
                            inputs=[tabs, user_id_state],
                            outputs=user_profile_info
                        )
            
            # Emergency fallback UI if no proper components are available
            if not has_journal_manager:
                with gr.Accordion("Emergency Journal", open=True):
                    with gr.Row():
                        with gr.Column():
                            emergency_date = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                            emergency_text = gr.Textbox(label="Emergency Journal Entry", lines=5, placeholder="Write your thoughts here...")
                            emergency_button = gr.Button("Save Emergency Entry")
                            
                        with gr.Column():
                            emergency_output = gr.JSON(label="Emergency Result")
                    
                    def emergency_save(text, date, user_id):
                        """Ultra simple journal save for emergency mode"""
                        try:
                            if not user_id:
                                return {
                                    "success": False,
                                    "error": "You must be logged in to save entries"
                                }
                            
                            # Create a basic journal directory structure
                            if has_user_manager:
                                user_journal_dir = user_manager.get_user_journal_manager_path(user_id)
                            else:
                                user_journal_dir = os.path.join("users", user_id, "journals")
                            
                            os.makedirs(user_journal_dir, exist_ok=True)
                            
                            # Parse the date
                            try:
                                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                                year_month = date_obj.strftime("%Y-%m")
                            except ValueError:
                                return {"success": False, "error": "Invalid date format"}
                            
                            # Create year-month directory
                            year_month_dir = os.path.join(user_journal_dir, year_month)
                            os.makedirs(year_month_dir, exist_ok=True)
                            
                            # Create emergency journal entry
                            entry = {
                                "date": date,
                                "timestamp": datetime.datetime.now().isoformat(),
                                "content": {
                                    "text": text,
                                    "tasks": [],
                                    "goals": [],
                                    "tags": [],
                                    "chat_history": []
                                },
                                "emotion_analysis": {
                                    "primary_emotion": "unknown",
                                    "emotion_intensity": 5,
                                    "emotional_themes": [],
                                    "mood_summary": "No analysis available in emergency mode",
                                    "suggested_actions": []
                                },
                                "metadata": {
                                    "last_modified": datetime.datetime.now().isoformat(),
                                    "word_count": len(text.split()),
                                    "has_tasks": False,
                                    "has_goals": False,
                                    "has_chat_history": False,
                                    "has_ai_summary": False,
                                    "emergency_mode": True
                                }
                            }
                            
                            # Save the file
                            file_path = os.path.join(year_month_dir, f"{date}.json")
                            with open(file_path, 'w') as f:
                                import json
                                json.dump(entry, f, indent=2)
                                
                            return {
                                "success": True,
                                "message": "Entry saved in emergency mode",
                                "date": date
                            }
                        except Exception as e:
                            return {"success": False, "error": f"Emergency save failed: {str(e)}"}
                    
                    emergency_button.click(
                        fn=emergency_save,
                        inputs=[emergency_text, emergency_date, user_id_state],
                        outputs=emergency_output
                    )
            
            # Add a processing page for OAuth callback
            with gr.Row(visible=False) as processing_page:
                gr.Markdown("# Processing Login")
                processing_status = gr.Markdown("Please wait while we complete your login...")
            
            # Add callback to check for URL parameters at load
            @interface.load(outputs=[processing_page, processing_status, user_id_state, login_info])
            def check_parameters_on_load():
                try:
                    import os
                    import urllib.parse
                    
                    # Check if there are URL parameters
                    query_string = os.environ.get("QUERY_STRING", "")
                    if not query_string:
                        return gr.update(visible=False), "", None, {"logged_in": False}
                        
                    print(f"DEBUG - Found query string on load: {query_string}")
                    params = dict(urllib.parse.parse_qsl(query_string))
                    
                    # Check for login callback
                    code = params.get("code")
                    state = params.get("state")
                    
                    if code and state:
                        print(f"DEBUG - Found OAuth callback parameters: code={code}, state={state}")
                        
                        # Find a matching session with this state
                        from src.auth_interface import SESSION_STATES
                        matching_session = None
                        for session_id, session_data in SESSION_STATES.items():
                            if session_data.get("state") == state:
                                matching_session = session_id
                                break
                                
                        if matching_session:
                            # Process the callback
                            result = process_login_callback(matching_session, code, state)
                            if result and result[0]:  # If login succeeded
                                user_id = result[0]
                                print(f"DEBUG - Login succeeded for user: {user_id}")
                                return gr.update(visible=True), "Login successful! Redirecting...", user_id, {
                                    "logged_in": True, 
                                    "user_id": user_id,
                                    "message": "Login successful!"
                                }
                                
                        return gr.update(visible=True), "Login failed. Please try again.", None, {"logged_in": False, "error": "Login processing failed"}
                        
                    # Check for success parameter
                    if "login_success" in params:
                        return gr.update(visible=False), "", None, {"logged_in": True, "message": "Login successful!"}
                        
                    return gr.update(visible=False), "", None, {"logged_in": False}
                except Exception as e:
                    print(f"Error checking parameters on load: {e}")
                    return gr.update(visible=False), "", None, {"logged_in": False, "error": str(e)}
            
            return interface
        
    except Exception as e:
        print(f"Error creating interface: {e}")
        traceback.print_exc()
        
        # Create an ultra-minimal interface
        with gr.Blocks(title="BujoNow - Critical Error Mode") as minimal_interface:
            gr.Markdown("# BujoNow - CRITICAL ERROR")
            gr.Markdown(f"""
            ## The application encountered critical errors during startup
            
            Error details: {type(e).__name__}: {str(e)}
            
            Please check the logs for more information.
            """)
            
            # Minimal text input in case of critical errors
            with gr.Accordion("Emergency Text Input", open=True):
                text = gr.Textbox(label="Emergency Journal Entry", lines=5)
                save_button = gr.Button("Save Emergency Entry")
                output = gr.Textbox(label="Result")
                
                def critical_save(text):
                    try:
                        # Save to a simple text file as last resort
                        filename = f"emergency_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        with open(os.path.join("journals", filename), 'w') as f:
                            f.write(text)
                        return f"Saved emergency entry to {filename}"
                    except Exception as e:
                        return f"Failed to save: {str(e)}"
                
                save_button.click(fn=critical_save, inputs=text, outputs=output)
                
        return minimal_interface 