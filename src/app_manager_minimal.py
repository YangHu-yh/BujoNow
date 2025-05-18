"""
Minimal App Manager Module

A simplified app manager with reduced functionality.
Used when the full app_manager cannot be loaded.
"""

import os
import datetime
import json
from typing import Dict, Any, List

class MinimalAppManager:
    """Minimal implementation of the app manager with basic functionality"""
    
    def __init__(self, journal_manager=None, analyzer=None):
        """
        Initialize the minimal app manager
        
        Args:
            journal_manager: Instance of JournalManager
            analyzer: Instance of an Analyzer
        """
        from src.journal_manager import JournalManager
        
        self.journal_manager = journal_manager or JournalManager()
        
        # Use provided analyzer or try to import a suitable one
        if analyzer:
            self.analyzer = analyzer
        else:
            try:
                # Try to import analyzers in order of preference
                try:
                    from src.analyzer import Analyzer
                    self.analyzer = Analyzer()
                    print("Using full analyzer in minimal app manager")
                except Exception:
                    try:
                        from src.analyzer_simplified import Analyzer
                        self.analyzer = Analyzer()
                        print("Using simplified analyzer in minimal app manager")
                    except Exception:
                        from src.analyzer_fallback import Analyzer
                        self.analyzer = Analyzer()
                        print("Using fallback analyzer in minimal app manager")
            except Exception as e:
                print(f"Error initializing analyzer in minimal app manager: {e}")
                # Create an ultra-minimal inline analyzer as last resort
                class UltraMinimalAnalyzer:
                    def analyze_journal_entry(self, text):
                        return {"primary_emotion": "unknown"}
                    def create_weekly_summary(self, entries):
                        return {"summary": f"{len(entries)} entries found."}
                    def chat_response(self, user_input, chat_history=None):
                        return "Chat functionality unavailable."
                
                self.analyzer = UltraMinimalAnalyzer()
        
        print("Created minimal app manager")
                
    def save_text_journal(self, text, date=None):
        """Save a text journal entry"""
        if not text:
            return {"success": False, "error": "Journal text cannot be empty"}
        
        # Use provided date or current date
        entry_date = datetime.datetime.now()
        if date:
            try:
                entry_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Analyze entry
        try:
            analysis = self.analyzer.analyze_journal_entry(text)
        except Exception as e:
            print(f"Error analyzing entry: {e}")
            analysis = {}  # Use empty analysis if analysis fails
        
        # Create entry
        entry = self.journal_manager.create_entry(
            text=text,
            emotion_analysis=analysis,
            date=entry_date
        )
        
        return {
            "success": True,
            "entry_id": entry.get("date", entry_date.strftime("%Y-%m-%d")),
            "date": entry_date.strftime("%Y-%m-%d")
        }
    
    def get_entries_by_date(self, date_str):
        """Get entries for a specific date"""
        try:
            entry_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            entry = self.journal_manager.get_entry(entry_date)
            return [entry] if entry else []
        except ValueError:
            return []
        except Exception as e:
            print(f"Error retrieving entries: {e}")
            return []
            
    def get_weekly_summary(self, start_date=None):
        """Generate a weekly summary of journal entries"""
        # Determine start and end dates for the week
        if start_date:
            try:
                start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                start = datetime.datetime.now() - datetime.timedelta(days=6)
        else:
            # Default to the past 7 days
            start = datetime.datetime.now() - datetime.timedelta(days=6)
        
        end = start + datetime.timedelta(days=6)
        
        # Get entries for the week
        entries = self.journal_manager.search_entries(start_date=start, end_date=end)
        
        if not entries:
            return {
                "success": True,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "summary": "No entries found for this week."
            }
        
        # Generate weekly summary
        try:
            summary = self.analyzer.create_weekly_summary(entries)
            return {
                "success": True,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "entries_count": len(entries),
                "summary": summary
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating summary: {e}",
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "entries_count": len(entries)
            }
    
    def chat_with_journal(self, user_input, chat_history=None):
        """Handle chat interactions with the journal assistant"""
        if not user_input:
            return "Please enter a message to chat with your journal assistant."
        
        try:
            # Get recent journal entries to provide context
            today = datetime.datetime.now()
            week_ago = today - datetime.timedelta(days=7)
            recent_entries = self.journal_manager.search_entries(
                start_date=week_ago, 
                end_date=today
            )
            
            # Use the analyzer to generate a response
            if hasattr(self.analyzer, 'chat_response'):
                return self.analyzer.chat_response(user_input, recent_entries)
            else:
                return "Chat functionality is not available in this mode. Please try again when full analyzer is working."
        except Exception as e:
            print(f"Error in chat: {e}")
            return f"I encountered an error while processing your message: {str(e)}" 