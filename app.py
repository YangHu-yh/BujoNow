"""
BujoNow - Bullet Journal Companion

A journaling application with AI-powered analysis, voice journaling,
emotion detection, and bullet journal-style organization.
"""

import os
import sys
import json
import traceback
import datetime
import gradio as gr
from pathlib import Path

# Configure environment before imports
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Suppress TensorFlow warnings

print("Starting BujoNow application...")

# Check for Google API key
google_api_key = os.environ.get("GOOGLE_API_KEY")
if google_api_key:
    print("Found GOOGLE_API_KEY in environment variables")
else:
    print("Warning: GOOGLE_API_KEY not found in environment variables")
    print("Full analyzer functionality will be limited without an API key")
    print("Set it using: export GOOGLE_API_KEY=your_api_key")

# Create required directories
for directory in ["journals", "uploads", "visualizations"]:
    os.makedirs(directory, exist_ok=True)
    print(f"Ensured {directory} directory exists")

# Try to import components, with graceful fallbacks
try:
    print("Importing interface module...")
    from src.interface import create_interface
    has_interface = True
    print("Interface module imported successfully")
except Exception as e:
    print(f"Error importing interface: {e}")
    traceback.print_exc(file=sys.stdout)
    has_interface = False

# Create a simplified interface if the main one is not available
def create_simple_interface():
    """Create a simplified interface when the main one fails to load"""
    print("Creating simplified interface due to import errors")
    
    # Try to import just the essential components for basic functionality
    try:
        # Try to import simplified analyzer if available
        try:
            from src.analyzer_simplified import Analyzer
            print("Using simplified analyzer")
            has_analyzer = True
        except ImportError:
            print("Simplified analyzer not available, using minimal functions")
            has_analyzer = False
            
        # Try to import journal manager
        try:
            from src.journal_manager import JournalManager
            journal_manager = JournalManager("journals")
            print("Using journal manager")
            has_journal_manager = True
        except ImportError:
            print("Journal manager not available, using direct file operations")
            has_journal_manager = False
    except Exception as e:
        print(f"Error setting up simplified components: {e}")
        has_analyzer = False
        has_journal_manager = False
    
    with gr.Blocks(title="BujoNow - Bullet Journal Companion") as app:
        gr.Markdown("# BujoNow - Bullet Journal Companion")
        gr.Markdown("## Simplified Version (Integration Error)")
        
        error_message = "The application encountered errors during initialization."
        if not has_interface:
            error_message = "Failed to import essential modules. Please check the logs for details."
            
        gr.Markdown(f"""
        ### There was an error loading the full application
        
        {error_message}
        
        #### Troubleshooting Steps:
        
        1. Make sure you've set the `GOOGLE_API_KEY` environment variable if you need advanced features.
        2. Check the following dependencies are installed correctly:
           - google-generativeai
           - facenet-pytorch (optional for face detection)
           - fer (optional for emotion detection)
        3. Check the application logs for specific error messages.
        """)
        
        # Ensure journals directory exists
        journals_dir = "journals"
        os.makedirs(journals_dir, exist_ok=True)
        
        # Basic journal functionality
        with gr.Accordion("Basic Text Journaling", open=True):
            with gr.Row():
                with gr.Column():
                    text_date = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                    text_input = gr.Textbox(label="Journal Entry", lines=10, placeholder="Write your thoughts here...")
                    text_submit = gr.Button("Save Entry")
                
                with gr.Column():
                    text_output = gr.JSON(label="Results")
            
            def basic_journal(text, date):
                if not text:
                    return {"success": False, "error": "Journal text cannot be empty"}
                
                try:
                    # If we have the journal manager available, use it
                    if has_journal_manager and has_analyzer:
                        # Use imported components
                        try:
                            analyzer = Analyzer()
                            analysis = analyzer.analyze_journal_entry(text)
                            
                            # Convert string date to datetime
                            try:
                                entry_date = datetime.datetime.strptime(date, "%Y-%m-%d")
                            except ValueError:
                                return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
                            
                            # Create entry
                            entry = journal_manager.create_entry(
                                text=text,
                                emotion_analysis=analysis,
                                date=entry_date
                            )
                            
                            return {
                                "success": True,
                                "message": "Entry saved with analysis",
                                "date": date,
                                "entry_id": entry.get("date", date)
                            }
                            
                        except Exception as e:
                            print(f"Error using components: {e}")
                            # Fall back to direct file operations
                    
                    # Direct file operations fallback
                    # Create a minimal entry
                    entry = {
                        "date": date,
                        "text": text,
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    
                    # Save to a file
                    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                    year_month_dir = os.path.join(journals_dir, date_obj.strftime("%Y-%m"))
                    os.makedirs(year_month_dir, exist_ok=True)
                    
                    # Generate a unique ID
                    entry_id = f"{date}_{datetime.datetime.now().strftime('%H%M%S')}"
                    file_path = os.path.join(year_month_dir, f"{entry_id}.json")
                    
                    with open(file_path, 'w') as f:
                        json.dump(entry, f, indent=2)
                        
                    return {
                        "success": True,
                        "message": "Entry saved successfully in simplified mode",
                        "date": date,
                        "entry_id": entry_id,
                        "text": text[:100] + "..." if len(text) > 100 else text
                    }
                except Exception as e:
                    return {"success": False, "error": f"Error saving entry: {str(e)}"}
            
            text_submit.click(
                fn=basic_journal,
                inputs=[text_input, text_date],
                outputs=text_output
            )
        
        with gr.Accordion("System Information", open=False):
            system_info = f"""
            Python version: {sys.version}
            Platform: {sys.platform}
            Import errors occurred: {not has_interface}
            Journal manager available: {has_journal_manager if 'has_journal_manager' in locals() else False}
            Analyzer available: {has_analyzer if 'has_analyzer' in locals() else False}
            """
            gr.Markdown(system_info)
    
    return app

# Launch the app
if __name__ == "__main__":
    print("Initializing BujoNow application...")
    try:
        if has_interface:
            try:
                print("Creating main interface...")
                app = create_interface()
                print("Main interface created successfully")
            except Exception as e:
                print(f"Error creating main interface: {e}")
                traceback.print_exc(file=sys.stdout)
                app = create_simple_interface()
        else:
            app = create_simple_interface()
        
        print("Launching application...")
        app.launch(share=False, server_name="0.0.0.0", server_port=7860)
    except Exception as e:
        print(f"Critical error launching application: {e}")
        traceback.print_exc(file=sys.stdout)
        
        # Command-line fallback if GUI fails completely
        print("\n=== COMMAND LINE INTERFACE ===")
        print("BujoNow is running in command-line mode due to GUI initialization failure.")
        
        # Try to get essential components for CLI
        try:
            from src.journal_manager import JournalManager
            from src.analyzer_simplified import Analyzer
            journal_manager = JournalManager("journals")
            analyzer = Analyzer()
            
            while True:
                print("\nOptions:")
                print("1. Add journal entry")
                print("2. View entry by date")
                print("3. Exit")
                
                choice = input("\nEnter your choice (1-3): ")
                
                if choice == '1':
                    date_str = input("Enter date (YYYY-MM-DD) or press Enter for today: ")
                    if not date_str:
                        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                    text = input("Enter your journal entry (type 'done' on a new line to finish):\n")
                    lines = []
                    line = text
                    while line != "done":
                        lines.append(line)
                        line = input()
                    
                    text = "\n".join(lines)
                    
                    # Process entry
                    try:
                        entry_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                        analysis = analyzer.analyze_journal_entry(text)
                        entry = journal_manager.create_entry(
                            text=text,
                            emotion_analysis=analysis,
                            date=entry_date
                        )
                        print("\nEntry saved successfully!")
                    except Exception as e:
                        print(f"\nError saving entry: {e}")
                    
                elif choice == '2':
                    date_str = input("Enter date (YYYY-MM-DD): ")
                    try:
                        entry_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                        entry = journal_manager.get_entry(entry_date)
                        if entry:
                            print("\nEntry found:")
                            print(f"Date: {entry.get('date')}")
                            print(f"Text: {entry.get('content', {}).get('text', 'No text')}")
                            print(f"Emotion: {entry.get('emotion_analysis', {}).get('primary_emotion', 'Unknown')}")
                        else:
                            print("No entry found for that date.")
                    except Exception as e:
                        print(f"\nError retrieving entry: {e}")
                        
                elif choice == '3':
                    print("Exiting BujoNow. Goodbye!")
                    break
                
                else:
                    print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Cannot initialize command-line interface: {e}")
            print("BujoNow cannot run. Please check your installation.") 