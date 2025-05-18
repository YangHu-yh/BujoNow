"""
Fallback Analyzer Module

Ultra-minimal analyzer that requires no dependencies.
Used as a last resort when other analyzers fail to load.
"""

from typing import Dict, List, Any

class Analyzer:
    """Minimal analyzer with no external dependencies"""
    
    def __init__(self):
        """Initialize the minimal fallback analyzer"""
        print("Using minimal fallback analyzer")
    
    def analyze_journal_entry(self, text):
        """Ultra-simple journal analysis"""
        return {
            "primary_emotion": "unknown",
            "emotional_themes": ["journaling"],
            "mood_summary": "No analysis available",
            "suggested_actions": ["Continue journaling"]
        }
    
    def create_weekly_summary(self, entries):
        """Minimal weekly summary"""
        return {
            "summary": f"You made {len(entries)} journal entries.",
            "emotion_trend": "Analysis not available",
            "recommendations": ["Continue your journaling practice"]
        }
    
    def chat_response(self, user_input, chat_history=None):
        """Minimal chat response"""
        return "I'm sorry, but the chat functionality is unavailable in minimal mode. Please try again when the full analyzer is working." 