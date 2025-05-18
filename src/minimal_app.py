"""
BujoNow - Bullet Journal Companion (Minimal Version)

A minimal version of the BujoNow application that doesn't rely on complex dependencies.
"""

import os
import datetime
import json
import gradio as gr
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ensure needed directories exist
JOURNALS_DIR = "journals"
os.makedirs(JOURNALS_DIR, exist_ok=True)

class MinimalJournalManager:
    """A simple journal manager with basic functionality"""
    
    def __init__(self, journal_dir: str = "journals"):
        self.journal_dir = journal_dir
        Path(self.journal_dir).mkdir(parents=True, exist_ok=True)
    
    def save_entry(self, text: str, date: str = None) -> Dict[str, Any]:
        """Save a basic journal entry"""
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            
        entry = {
            "date": date,
            "text": text,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # Create year-month directory
        try:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            year_month_dir = os.path.join(self.journal_dir, date_obj.strftime("%Y-%m"))
            os.makedirs(year_month_dir, exist_ok=True)
            
            # Generate a unique ID for the entry
            entry_id = f"{date}_{datetime.datetime.now().strftime('%H%M%S')}"
            
            # Save the entry to a JSON file
            file_path = os.path.join(year_month_dir, f"{entry_id}.json")
            with open(file_path, 'w') as f:
                json.dump(entry, f, indent=2)
                
            return {
                "success": True,
                "entry_id": entry_id,
                "date": date,
                "file_path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_entries_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get entries for a specific date"""
        try:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            year_month_dir = os.path.join(self.journal_dir, date_obj.strftime("%Y-%m"))
            
            if not os.path.exists(year_month_dir):
                return []
                
            entries = []
            for file_name in os.listdir(year_month_dir):
                if file_name.startswith(date) and file_name.endswith(".json"):
                    file_path = os.path.join(year_month_dir, file_name)
                    with open(file_path, 'r') as f:
                        entry = json.load(f)
                        entries.append(entry)
                        
            return entries
        except Exception as e:
            print(f"Error getting entries: {e}")
            return []

# Initialize the journal manager
journal_manager = MinimalJournalManager()

def create_minimal_interface():
    """Create a simple Gradio interface for journaling"""
    with gr.Blocks(title="BujoNow - Minimal Journal") as app:
        gr.Markdown("# BujoNow - Minimal Journal")
        gr.Markdown("A simple bullet journal app with basic journaling capabilities.")
        
        with gr.Tab("Journal"):
            with gr.Row():
                with gr.Column():
                    date_input = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                    text_input = gr.Textbox(label="Journal Entry", lines=10, placeholder="Write your thoughts here...")
                    save_button = gr.Button("Save Entry")
                
                with gr.Column():
                    result_output = gr.JSON(label="Result")
            
            def save_journal_entry(text, date):
                """Save a journal entry"""
                if not text:
                    return {"success": False, "error": "Journal text cannot be empty"}
                
                # Simple sentiment detection
                positive_words = ["happy", "good", "great", "excellent", "wonderful", "joy", "grateful"]
                negative_words = ["sad", "bad", "terrible", "awful", "unhappy", "angry", "frustrated"]
                
                text_lower = text.lower()
                sentiment = "neutral"
                
                if any(word in text_lower for word in positive_words):
                    sentiment = "positive"
                elif any(word in text_lower for word in negative_words):
                    sentiment = "negative"
                
                # Save the entry
                result = journal_manager.save_entry(text, date)
                
                if result["success"]:
                    result["sentiment"] = sentiment
                
                return result
            
            save_button.click(
                fn=save_journal_entry,
                inputs=[text_input, date_input],
                outputs=result_output
            )
        
        with gr.Tab("Review"):
            with gr.Row():
                review_date = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                review_button = gr.Button("Get Entries")
            
            entries_display = gr.JSON(label="Journal Entries")
            
            review_button.click(
                fn=journal_manager.get_entries_by_date,
                inputs=review_date,
                outputs=entries_display
            )
    
    return app

if __name__ == "__main__":
    print("Starting BujoNow Minimal Journal...")
    app = create_minimal_interface()
    app.launch(share=False, server_name="0.0.0.0", server_port=7860) 