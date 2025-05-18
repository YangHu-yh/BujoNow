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
    
    # Import journal manager first as it's most essential
    try:
        from src.journal_manager import JournalManager
        has_journal_manager = True
        print("Journal manager imported successfully")
    except Exception as e:
        print(f"Warning: Could not import journal manager: {e}")
    
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
            
            with gr.Tab("Journal Entry"):
                with gr.Row():
                    with gr.Column():
                        date_input = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                        text_input = gr.Textbox(label="Journal Entry", lines=10, placeholder="Write your thoughts here...")
                        submit_button = gr.Button("Save Entry")
                        
                    with gr.Column():
                        output = gr.JSON(label="Result")
                
                def save_entry(text, date):
                    try:
                        return app_manager.save_text_journal(text, date)
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Error saving journal: {type(e).__name__}: {e}"
                        }
                
                submit_button.click(
                    fn=save_entry,
                    inputs=[text_input, date_input],
                    outputs=output
                )
            
            # Only show these tabs if we have journal manager
            if has_journal_manager:
                with gr.Tab("View Entries"):
                    view_date = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                    view_button = gr.Button("View Entry")
                    view_output = gr.JSON(label="Entry")
                    
                    def get_entry(date):
                        try:
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
                        inputs=view_date,
                        outputs=view_output
                    )
                
                with gr.Tab("Weekly Summary"):
                    with gr.Row():
                        with gr.Column():
                            start_date = gr.Textbox(
                                label="Start Date (YYYY-MM-DD)", 
                                value=(datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
                            )
                            summary_button = gr.Button("Generate Summary")
                            
                        with gr.Column():
                            summary_output = gr.JSON(label="Weekly Summary")
                    
                    def get_summary(start):
                        try:
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
                        inputs=start_date,
                        outputs=summary_output
                    )
                
                # Add Chat interface
                with gr.Tab("Chat with Journal"):
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
                    
                    def chat_response(user_input, history):
                        if not user_input.strip():
                            return history
                        
                        try:
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
                    
                    def load_todays_chat_history():
                        try:
                            # Get today's date
                            today = datetime.datetime.now()
                            
                            # Check if app_manager and journal_manager are available
                            if not hasattr(app_manager, 'journal_manager'):
                                return [{"role": "assistant", "content": "Cannot load chat history: Journal manager not available."}]
                            
                            # Get today's entry
                            entry = app_manager.journal_manager.get_entry(today)
                            if not entry:
                                return [{"role": "assistant", "content": "No chat history found for today."}]
                            
                            # Extract chat history if it exists
                            chat_history = entry.get('content', {}).get('chat_history', [])
                            if not chat_history:
                                return [{"role": "assistant", "content": "No chat history found for today."}]
                            
                            # Convert the stored format to Gradio Chatbot format
                            gradio_history = []
                            for chat in chat_history:
                                if isinstance(chat, dict):
                                    # Chat could be in different formats depending on storage
                                    if 'user' in chat and 'assistant' in chat:
                                        # Our custom format
                                        gradio_history.append({"role": "user", "content": chat['user']})
                                        gradio_history.append({"role": "assistant", "content": chat['assistant']})
                                    elif 'role' in chat and 'content' in chat:
                                        # Already in OpenAI/Gradio format
                                        gradio_history.append(chat)
                            
                            if not gradio_history:
                                return [{"role": "assistant", "content": "Chat history found but couldn't be converted."}]
                                
                            return gradio_history
                        except Exception as e:
                            print(f"Error loading chat history: {e}")
                            return [{"role": "assistant", "content": f"Error loading chat history: {str(e)}"}]
                    
                    chat_input.submit(
                        fn=chat_response,
                        inputs=[chat_input, chatbot],
                        outputs=chatbot
                    )
                    
                    clear_button.click(
                        fn=clear_chat_history,
                        inputs=None,
                        outputs=chatbot
                    )
                    
                    load_history_button.click(
                        fn=load_todays_chat_history,
                        inputs=None,
                        outputs=chatbot
                    )
            
            with gr.Tab("System Info"):
                gr.Markdown(f"""
                ## System Information
                
                - Python version: {sys.version}
                - Platform: {sys.platform}
                - Using journal manager: {has_journal_manager}
                - Using full analyzer: {has_full_analyzer}
                - Using simplified analyzer: {has_simplified_analyzer}
                - Directory: {os.getcwd()}
                """)
            
        return interface
    except Exception as e:
        print(f"Error creating interface: {e}")
        traceback.print_exc()
        
        # Create ultra-minimal interface as last resort
        with gr.Blocks(title="BujoNow - Emergency Mode") as fallback_interface:
            gr.Markdown("# BujoNow - Emergency Mode")
            gr.Markdown("## Limited Functionality Available")
            gr.Markdown("""
            The application encountered serious errors.
            Only basic journaling is available in this emergency mode.
            """)
            
            with gr.Row():
                with gr.Column():
                    date_input = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                    text_input = gr.Textbox(label="Journal Entry", lines=10, placeholder="Write your thoughts here...")
                    submit_button = gr.Button("Save Entry")
                    
                with gr.Column():
                    output = gr.JSON(label="Result")
            
            def emergency_save(text, date):
                try:
                    # Use app_manager if available
                    if app_manager:
                        return app_manager.save_text_journal(text, date)
                    else:
                        # Last resort direct file operations
                        journals_dir = "journals"
                        os.makedirs(journals_dir, exist_ok=True)
                        
                        try:
                            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                        except ValueError:
                            return {"success": False, "error": "Invalid date format"}
                            
                        month_dir = os.path.join(journals_dir, date_obj.strftime("%Y-%m"))
                        os.makedirs(month_dir, exist_ok=True)
                        
                        entry = {
                            "date": date,
                            "content": {"text": text},
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                        
                        import json
                        file_path = os.path.join(month_dir, f"{date}.json")
                        with open(file_path, 'w') as f:
                            json.dump(entry, f, indent=2)
                        
                        return {
                            "success": True,
                            "message": "Entry saved in emergency mode",
                            "date": date
                        }
                except Exception as ex:
                    return {"success": False, "error": str(ex)}
            
            submit_button.click(
                fn=emergency_save,
                inputs=[text_input, date_input],
                outputs=output
            )
            
            gr.Markdown(f"""
            ## Error Information
            
            An error occurred: {str(e)}
            
            Please report this issue to the developers with the following information:
            - Python version: {sys.version}
            - Platform: {sys.platform}
            """)
        
        return fallback_interface 