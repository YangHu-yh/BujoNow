"""
BujoNow Application Manager

Handles core application logic and manages interactions between components.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Union, Optional
from pathlib import Path

from src.journal_manager import JournalManager
# Try to import analyzers in prioritized order
try:
    # First try to import the main analyzer
    from src.analyzer import Analyzer
    has_main_analyzer = True
    print("Main analyzer imported successfully")
except Exception as e:
    print(f"Main analyzer not available: {e}")
    has_main_analyzer = False
    try:
        # If main analyzer fails, try the simplified analyzer
        from src.analyzer_simplified import Analyzer as SimplifiedAnalyzer
        has_simplified_analyzer = True
        print("Simplified analyzer imported successfully")
    except Exception as e:
        print(f"Simplified analyzer not available: {e}")
        has_simplified_analyzer = False
        try:
            # If both fail, try the fallback analyzer
            from src.analyzer_fallback import Analyzer as FallbackAnalyzer
            has_fallback_analyzer = True
            print("Fallback analyzer imported successfully")
        except Exception as e:
            print(f"Fallback analyzer not available: {e}")
            has_fallback_analyzer = False

from src.processor.image_processor import ImageProcessor
from src.processor.audio_processor import AudioProcessor

# Constants
JOURNALS_DIR = "journals"
UPLOADS_DIR = "uploads"
VISUALIZATIONS_DIR = "visualizations"

class AppManager:
    """Manages the BujoNow application components and operations"""
    
    def __init__(self, initialize_dirs: bool = True):
        """
        Initialize the application manager
        
        Args:
            initialize_dirs: Whether to create required directories
        """
        self.journals_dir = JOURNALS_DIR
        self.uploads_dir = UPLOADS_DIR
        self.visualizations_dir = VISUALIZATIONS_DIR
        
        # Create required directories
        if initialize_dirs:
            self._initialize_directories()
        
        # Initialize components
        self.journal_manager = JournalManager(self.journals_dir)
        
        # Initialize analyzer in priority order
        print("Initializing analyzer component...")
        try:
            if has_main_analyzer:
                # Try the main analyzer first
                self.analyzer = Analyzer()
                print("Using main analyzer with full functionality")
            elif has_simplified_analyzer:
                # Try simplified analyzer if main fails
                self.analyzer = SimplifiedAnalyzer()
                print("Using simplified analyzer (main analyzer not available)")
            elif has_fallback_analyzer:
                # Use fallback if both main and simplified fail
                self.analyzer = FallbackAnalyzer()
                print("Using fallback analyzer (main and simplified not available)")
            else:
                # If all analyzers fail, raise an exception
                raise Exception("No analyzer components available")
        except Exception as e:
            print(f"Error initializing analyzer component: {e}")
            raise Exception("Failed to initialize analyzer component")
            
        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
    
    def _initialize_directories(self):
        """Ensure all required directories exist"""
        for directory in [self.journals_dir, self.uploads_dir, self.visualizations_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def save_text_journal(self, text: str, date: str = None) -> Dict[str, Any]:
        """
        Save a text journal entry
        
        Args:
            text: The journal text content
            date: Optional date string (format: YYYY-MM-DD)
            
        Returns:
            Result dictionary with status and entry ID
        """
        if not text:
            return {"success": False, "error": "Journal text cannot be empty"}
        
        # Use provided date or current date
        entry_date = datetime.datetime.now()
        if date:
            try:
                entry_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Analyze the entry
        try:
            analysis = self.analyzer.analyze_journal_entry(text)
        except Exception as e:
            print(f"Error analyzing entry: {e}")
            analysis = {}  # Use empty analysis if analysis fails
        
        # Create entry with the analysis
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

    def save_audio_journal(self, audio_file: str, date: str = None) -> Dict[str, Any]:
        """
        Save an audio journal entry
        
        Args:
            audio_file: Path to the uploaded audio file
            date: Optional date string (format: YYYY-MM-DD)
            
        Returns:
            Result dictionary with status and entry information
        """
        if not audio_file:
            return {"success": False, "error": "No audio file provided"}
        
        # Process the audio file
        result = self.audio_processor.process_journal_audio(audio_file)
        
        if not result.get("success", False):
            return result
        
        # Use provided date or current date
        entry_date = datetime.datetime.now()
        if date:
            try:
                entry_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Analyze the entry
        try:
            analysis = self.analyzer.analyze_audio(result["text"])
        except Exception as e:
            print(f"Error analyzing audio entry: {e}")
            analysis = {}  # Use empty analysis if analysis fails
        
        # Create entry with analysis
        entry = self.journal_manager.create_entry(
            text=result["text"],
            emotion_analysis=analysis,
            date=entry_date,
            tags=["audio"]
        )
        
        return {
            "success": True,
            "entry_id": entry.get("date", entry_date.strftime("%Y-%m-%d")),
            "date": entry_date.strftime("%Y-%m-%d"),
            "transcription": result["text"]
        }

    def save_image_journal(self, image_file: str, notes: str = "", date: str = None) -> Dict[str, Any]:
        """
        Save an image journal entry with emotion analysis
        
        Args:
            image_file: Path to the uploaded image file
            notes: Optional notes to accompany the image
            date: Optional date string (format: YYYY-MM-DD)
            
        Returns:
            Result dictionary with status and entry information
        """
        if not image_file:
            return {"success": False, "error": "No image file provided"}
        
        # Use provided date or current date
        entry_date = datetime.datetime.now()
        if date:
            try:
                entry_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Analyze emotions in the image
        emotion_results = self.image_processor.analyze_emotions(image_file)
        
        # Create visualization if emotions were detected
        visualization_path = None
        if emotion_results.get("average_emotions"):
            vis_filename = f"emotions_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            visualization_path = os.path.join(self.visualizations_dir, vis_filename)
            self.image_processor.create_emotion_visualization(
                emotion_results["average_emotions"], 
                visualization_path
            )
        
        # Analyze image content if available
        content_analysis = self.image_processor.analyze_image_content(image_file)
        
        # Create simplified emotion analysis for the journal entry
        emotion_analysis = {
            "primary_emotion": emotion_results.get("primary_emotion", "unknown"),
            "emotion_intensity": emotion_results.get("intensity", 5),
            "emotional_themes": emotion_results.get("detected_emotions", []),
            "mood_summary": f"Image analysis: {content_analysis.get('description', '')}" if content_analysis else "No content analysis available",
            "suggested_actions": []
        }
        
        # Create entry
        entry = self.journal_manager.create_entry(
            text=notes,
            emotion_analysis=emotion_analysis,
            date=entry_date,
            tags=["image"]
        )
        
        return {
            "success": True,
            "entry_id": entry.get("date", entry_date.strftime("%Y-%m-%d")),
            "date": entry_date.strftime("%Y-%m-%d"),
            "emotions": emotion_results,
            "visualization": visualization_path
        }

    def get_entries_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        Get journal entries for a specific date
        
        Args:
            date: Date string (format: YYYY-MM-DD)
            
        Returns:
            List of entry dictionaries
        """
        try:
            entry_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            entry = self.journal_manager.get_entry(entry_date)
            return [entry] if entry else []
        except ValueError:
            return []
        except Exception as e:
            print(f"Error retrieving entries: {e}")
            return []

    def get_weekly_summary(self, start_date: str = None) -> Dict[str, Any]:
        """
        Get a summary of the week's journal entries
        
        Args:
            start_date: Optional starting date (format: YYYY-MM-DD)
            
        Returns:
            Summary dictionary
        """
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

    def chat_with_journal(self, user_input: str, chat_history=None) -> str:
        """
        Handle chat interactions with the journal assistant
        
        Args:
            user_input: The user's message
            chat_history: Previous chat history
            
        Returns:
            AI assistant's response as a string
        """
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
                response = self.analyzer.chat_response(user_input, recent_entries)
            else:
                response = "Chat functionality is not available with the current analyzer."
                
            # Store the chat in today's journal entry
            try:
                # Format chat messages
                current_chat_message = {
                    "user": user_input,
                    "assistant": response,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                # Get today's entry if it exists
                today_entry = self.journal_manager.get_entry(today)
                
                if today_entry:
                    # Update existing entry with new chat message
                    existing_chat = today_entry['content'].get('chat_history', [])
                    existing_chat.append(current_chat_message)
                    
                    # Update the entry with the new chat history
                    self.journal_manager.update_entry(
                        date=today,
                        chat_history=existing_chat
                    )
                    print(f"Added chat to existing journal entry for {today.strftime('%Y-%m-%d')}")
                else:
                    # Create a minimal entry for today if none exists
                    empty_analysis = {
                        "primary_emotion": "neutral",
                        "emotion_intensity": 5,
                        "emotional_themes": ["chat"],
                        "mood_summary": "Chat interaction with journal assistant",
                        "suggested_actions": ["Consider writing a journal entry for today"]
                    }
                    
                    self.journal_manager.create_entry(
                        text="",  # Empty text since this is just for the chat
                        emotion_analysis=empty_analysis,
                        date=today,
                        tags=["chat"],
                        category="chat",
                        chat_history=[current_chat_message]
                    )
                    print(f"Created new chat-only journal entry for {today.strftime('%Y-%m-%d')}")
            except Exception as chat_save_error:
                print(f"Error saving chat to journal: {chat_save_error}")
                # Continue even if saving fails
                
            return response
        except Exception as e:
            print(f"Error in chat: {e}")
            return f"I encountered an error while processing your message: {str(e)}"

# Create a singleton instance
app_manager = AppManager() 