"""
Emergency App Manager Module

Ultra-minimal app manager that uses direct file operations.
Used as a last resort when all other components fail.
"""

import os
import datetime
import json
from typing import Dict, Any

class UltraMinimalAppManager:
    """Emergency fallback app manager with absolute minimal functionality"""
    
    def __init__(self):
        """Initialize the emergency app manager"""
        print("Using ultra-minimal emergency app manager")
    
    def save_text_journal(self, text, date=None):
        """
        Save a journal entry using direct file operations
        
        Args:
            text: Journal text content
            date: Optional date string (YYYY-MM-DD format)
        """
        if not text:
            return {"success": False, "error": "Journal text cannot be empty"}
        
        try:
            # Use direct file operations as fallback
            if date is None:
                date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Create journals directory
            journals_dir = "journals"
            os.makedirs(journals_dir, exist_ok=True)
            
            # Parse date for directory structure
            try:
                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                month_dir = os.path.join(journals_dir, date_obj.strftime("%Y-%m"))
                os.makedirs(month_dir, exist_ok=True)
            except ValueError:
                return {"success": False, "error": "Invalid date format"}
            
            # Create entry
            entry = {
                "date": date,
                "content": {"text": text},
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Save to file
            file_path = os.path.join(month_dir, f"{date}.json")
            with open(file_path, 'w') as f:
                json.dump(entry, f, indent=2)
            
            return {
                "success": True,
                "message": "Entry saved in emergency mode",
                "date": date
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def chat_with_journal(self, user_input, chat_history=None):
        """Minimal chat implementation"""
        return "I'm sorry, but the chat functionality is not available in emergency mode."
    
    def get_entries_by_date(self, date_str):
        """Attempt to get entries for a date in emergency mode"""
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            month_dir = os.path.join("journals", date_obj.strftime("%Y-%m"))
            file_path = os.path.join(month_dir, f"{date_str}.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return [json.load(f)]
            else:
                return []
        except Exception:
            return []
    
    def get_weekly_summary(self, start_date=None):
        """Emergency weekly summary"""
        return {
            "success": False,
            "message": "Weekly summary not available in emergency mode"
        } 