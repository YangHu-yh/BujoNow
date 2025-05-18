"""
Simplified Analyzer Module

Contains simplified functions for analyzing journal entries without depending on API or embeddings.
"""

import os
import json
import random
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Sample RAG documents for generating suggestions
RAG_DOCUMENTS = [
    "Journaling has been shown to reduce stress and anxiety. Try to write daily for at least 5 minutes.",
    "When feeling overwhelmed, try breaking tasks into smaller, manageable steps.",
    "Regular physical activity can improve mood and reduce symptoms of depression.",
    "Gratitude practices have been linked to increased happiness. Try listing 3 things you're grateful for each day.",
    "Mindfulness meditation can help reduce stress and improve focus. Even 5 minutes daily can make a difference.",
    "Social connections are important for mental health. Reach out to someone you care about today.",
    "Setting boundaries is healthy. It's okay to say no to additional commitments when you're feeling overwhelmed.",
    "Progressive muscle relaxation can help reduce physical tension from stress.",
    "Getting adequate sleep is crucial for emotional regulation and mental clarity.",
    "Spending time in nature has been shown to reduce stress and improve mood."
]

class Analyzer:
    """Simple analyzer for journal entries that doesn't depend on external APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the analyzer without API dependency"""
        print("Using simplified analyzer without API dependencies")
        self.rag_documents = RAG_DOCUMENTS
    
    def get_top_context(self, input_text: str, top_k: int = 3) -> str:
        """Get random documents as context"""
        selected_indices = random.sample(range(len(self.rag_documents)), min(top_k, len(self.rag_documents)))
        return "\n".join([self.rag_documents[i] for i in selected_indices])
    
    def analyze_journal_entry(self, input_text: str) -> Dict[str, Any]:
        """
        Provide a simple analysis of journal text based on keyword matching
        
        Args:
            input_text: The journal text to analyze
            
        Returns:
            Dict with simple analysis results
        """
        input_lower = input_text.lower()
        
        # Very simple emotion detection based on keywords
        emotion = "neutral"
        emotion_words = {
            "happy": ["happy", "joy", "excited", "great", "wonderful"],
            "sad": ["sad", "unhappy", "depressed", "down", "miserable"],
            "angry": ["angry", "mad", "frustrated", "annoyed", "upset"],
            "anxious": ["anxious", "worried", "nervous", "stressed", "fear"],
            "grateful": ["grateful", "thankful", "appreciate", "blessed"],
            "motivated": ["motivated", "inspired", "energized", "determined"]
        }
        
        # Count emotion words
        emotion_counts = {}
        for emotion_name, keywords in emotion_words.items():
            count = sum(1 for word in keywords if word in input_lower)
            if count > 0:
                emotion_counts[emotion_name] = count
        
        # Determine primary emotion
        if emotion_counts:
            emotion = max(emotion_counts, key=emotion_counts.get)
        
        # Extract themes based on content
        themes = []
        theme_keywords = {
            "work": ["work", "job", "career", "office", "boss", "colleague"],
            "family": ["family", "parent", "child", "mom", "dad", "brother", "sister"],
            "health": ["health", "exercise", "workout", "diet", "sleep", "sick"],
            "relationships": ["friend", "partner", "relationship", "date", "love"],
            "personal growth": ["goal", "learn", "improve", "growth", "develop", "progress"],
            "stress": ["stress", "overwhelm", "pressure", "burnout", "tired"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(word in input_lower for word in keywords):
                themes.append(theme)
        
        # Limit to top 3 themes
        themes = themes[:3] or ["general"]
        
        # Get random suggestion and affirmation based on emotion
        suggestions = {
            "happy": ["Continue activities that bring you joy.", 
                     "Share your positive energy with others who might need it.",
                     "Document what's working well so you can return to these practices."],
            "sad": ["Be gentle with yourself during difficult times.", 
                   "Try a brief activity that has lifted your mood in the past.",
                   "Consider reaching out to someone you trust about your feelings."],
            "angry": ["Take a few deep breaths before responding to situations.", 
                     "Physical activity can help release tension from anger.",
                     "Consider if there's a boundary you need to establish."],
            "anxious": ["Practice a few minutes of mindful breathing.", 
                       "Break down overwhelming tasks into smaller steps.",
                       "Try writing out your worries then challenges each one."],
            "grateful": ["Continue your gratitude practice regularly.", 
                        "Consider expressing your appreciation directly to others.",
                        "Notice how gratitude shifts your perspective on challenges."],
            "motivated": ["Capture your goals while you're feeling motivated.", 
                         "Break down your inspiration into actionable steps.",
                         "Schedule time to work on what's exciting you."],
            "neutral": ["Reflect on what would bring more meaning to your day.", 
                       "Try a new activity that interests you.",
                       "Check in with your body - are you hungry, tired, or need movement?"]
        }
        
        affirmations = {
            "happy": "Your joy is a gift - both to yourself and others around you.",
            "sad": "It's okay to not be okay. Your feelings are valid and part of being human.",
            "angry": "Your anger offers insight into what matters to you. Listen to it, then choose your response.",
            "anxious": "You've moved through difficult feelings before, and you have that same strength today.",
            "grateful": "Noticing the good in your life creates more space for positivity to grow.",
            "motivated": "Your energy and vision can create meaningful change in your life.",
            "neutral": "Each day offers new opportunities for discovery and growth."
        }
        
        emotion_suggestions = suggestions.get(emotion, suggestions["neutral"])
        suggestion = random.choice(emotion_suggestions)
        affirmation = affirmations.get(emotion, affirmations["neutral"])
        
        return {
            "primary_emotion": emotion,
            "emotion_intensity": random.randint(5, 8),  # Simple random intensity
            "emotional_themes": themes,
            "mood_summary": f"Your entry suggests you're feeling {emotion}.",
            "suggested_actions": [suggestion],
            "affirmation": affirmation
        }
    
    def analyze_audio(self, transcribed_text: str) -> Dict[str, Any]:
        """Analyze transcribed audio text"""
        return self.analyze_journal_entry(transcribed_text)
    
    def create_weekly_summary(self, entries: List[Dict]) -> Dict[str, Any]:
        """Create a simple weekly summary"""
        if not entries:
            return {
                "summary": "No entries found for this week.",
                "emotion_trend": None,
                "recommendations": []
            }
        
        # Count emotions across entries
        emotion_counts = {}
        for entry in entries:
            if "emotion_analysis" in entry and "primary_emotion" in entry["emotion_analysis"]:
                emotion = entry["emotion_analysis"]["primary_emotion"]
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Determine predominant emotion
        predominant_emotion = "mixed"
        if emotion_counts:
            predominant_emotion = max(emotion_counts, key=emotion_counts.get)
        
        # Generate simple summary
        entry_count = len(entries)
        summary = f"You made {entry_count} journal entries this week. "
        
        if predominant_emotion != "mixed":
            summary += f"You predominantly felt {predominant_emotion}. "
        else:
            summary += "You experienced a mix of emotions. "
            
        # Add random recommendations
        recommendations = random.sample([
            "Consider journaling at the same time each day to build a consistent habit.",
            "Try adding more detail about your emotions in future entries.",
            "Reflect on patterns you notice in your journaling over time.",
            "Consider adding a gratitude section to your journal practice.",
            "Look back at entries from a month ago to see how things have changed.",
            "Try using different journaling prompts to explore new perspectives."
        ], k=3)
        
        return {
            "summary": summary,
            "emotion_trend": predominant_emotion,
            "recommendations": recommendations
        }
    
    def chat_response(self, user_input: str, recent_entries=None) -> str:
        """
        Generate a response to a user's chat message about their journal entries without API
        
        Args:
            user_input: The user's message or question
            recent_entries: Optional list of recent journal entries to provide context
            
        Returns:
            AI assistant's response as a string
        """
        if not user_input or not user_input.strip():
            return "Please type a message to chat with your journal assistant."
            
        user_input_lower = user_input.lower()
        
        # Extract information from recent entries if available
        recent_emotions = []
        entry_count = 0
        
        if recent_entries and isinstance(recent_entries, list):
            entry_count = len(recent_entries)
            for entry in recent_entries:
                if isinstance(entry, dict) and "emotion_analysis" in entry and "primary_emotion" in entry["emotion_analysis"]:
                    emotion = entry["emotion_analysis"]["primary_emotion"]
                    if emotion and emotion != "unknown":
                        recent_emotions.append(emotion)
        
        # Determine predominant emotion
        predominant_emotion = "mixed"
        if recent_emotions:
            emotion_counts = {}
            for emotion in recent_emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            predominant_emotion = max(emotion_counts, key=emotion_counts.get)
        
        # Check for specific question types
        if any(word in user_input_lower for word in ["how", "what", "pattern", "trend", "notice"]) and any(word in user_input_lower for word in ["feel", "feeling", "emotion", "mood"]):
            if not recent_emotions:
                return "I don't have enough information about your recent journal entries to analyze emotional patterns. Try adding more journal entries with your feelings."
            
            if predominant_emotion != "mixed":
                return f"Based on your recent journal entries, you've been feeling predominantly {predominant_emotion}. This emotion has appeared most frequently in your {entry_count} recent entries. Remember that acknowledging your emotions is an important step in understanding yourself better."
            else:
                return f"Your recent journal entries show a mix of different emotions. This variety is normal and reflects the complexity of daily life. Consider exploring which situations tend to trigger specific emotional responses."
        
        elif any(word in user_input_lower for word in ["suggest", "recommendation", "advice", "help", "tip"]):
            # Get some suggestions based on the context
            suggestions = [
                "Try journaling at the same time each day to build a consistent habit.",
                "Consider using prompts when you're not sure what to write about.",
                "Adding a brief gratitude practice to your journaling can boost positive emotions.",
                "Reviewing past entries can help you notice patterns in your thoughts and feelings.",
                "Be honest in your journal - it's a private space for authentic reflection.",
                "Try different journaling formats: lists, narratives, or even drawings and diagrams."
            ]
            
            if predominant_emotion != "mixed" and predominant_emotion != "unknown":
                emotion_suggestions = {
                    "happy": "Continue activities that bring you joy and document what's working well.",
                    "sad": "Be gentle with yourself and consider reaching out to someone you trust.",
                    "angry": "Physical activity can help release tension from anger.",
                    "anxious": "Try breaking down overwhelming tasks into smaller steps.",
                    "grateful": "Consider expressing your appreciation directly to others.",
                    "motivated": "Capture your goals while you're feeling motivated."
                }
                
                if predominant_emotion in emotion_suggestions:
                    suggestions.append(emotion_suggestions[predominant_emotion])
            
            # Return 2-3 random suggestions
            selected_suggestions = random.sample(suggestions, min(2, len(suggestions)))
            return "Here are some suggestions for your journaling practice:\n\n" + "\n\n".join(f"- {suggestion}" for suggestion in selected_suggestions)
        
        elif any(word in user_input_lower for word in ["meaning", "purpose", "reflect", "insight"]):
            reflections = [
                "Regular journaling helps you track your emotional patterns and growth over time.",
                "Your journal is a conversation with yourself - what would your future self want to know about today?",
                "Journaling can help externalize your thoughts, making them easier to examine and understand.",
                "The act of writing itself often brings clarity to situations that feel confusing.",
                "Looking for patterns in your journal can reveal what truly matters to you."
            ]
            return random.choice(reflections)
        
        # For greetings and basic questions
        elif any(word in user_input_lower for word in ["hi", "hello", "hey", "greetings"]):
            return "Hello! I'm your journal assistant. How can I help with your journaling practice today?"
            
        elif "who are you" in user_input_lower or "what can you do" in user_input_lower:
            return "I'm your journal assistant. I can help you reflect on your journal entries, provide suggestions for your journaling practice, and answer questions about journaling. What would you like to know?"
            
        elif "thank" in user_input_lower:
            return "You're welcome! I'm here to support your journaling journey."
        
        # Direct question responses
        elif "why journal" in user_input_lower or "why should i journal" in user_input_lower:
            return "Journaling helps process emotions, gain clarity, track personal growth, improve mental health, and preserve memories. It's a powerful tool for self-reflection and understanding."
            
        elif "how often" in user_input_lower and "journal" in user_input_lower:
            return "The ideal journaling frequency is whatever works best for you - daily, weekly, or whenever you feel the need. Consistency is more important than frequency, so find a rhythm that's sustainable for your lifestyle."
            
        # Try to provide a relevant response based on the actual content of the message
        elif len(user_input) > 10:  # If it's a substantial message
            # Check for mentions of specific emotions
            emotions = ["happy", "sad", "angry", "anxious", "stressed", "grateful", "frustrated", "overwhelmed", "confused", "hopeful"]
            mentioned_emotions = [emotion for emotion in emotions if emotion in user_input_lower]
            
            if mentioned_emotions:
                emotion = mentioned_emotions[0]
                emotion_responses = {
                    "happy": "It's wonderful to experience happiness. Journaling about positive experiences can actually enhance their impact on your well-being.",
                    "sad": "When feeling sad, journaling can be a comforting way to process those emotions. Consider writing about both the feelings and any potential sources.",
                    "angry": "Anger often signals that a boundary has been crossed or a need isn't being met. Journaling can help identify the root cause.",
                    "anxious": "Writing about anxiety can help externalize your worries and see them more objectively. Consider listing what's in and outside of your control.",
                    "stressed": "Journaling can be an effective stress management tool. Try writing about your stressors and then brainstorming small steps to address them.",
                    "grateful": "Gratitude journaling has been shown to increase happiness and satisfaction. Even noting one thing you're grateful for can shift your perspective.",
                    "frustrated": "Frustration often comes from obstacles to our goals. Writing about the situation might reveal alternative paths forward.",
                    "overwhelmed": "When feeling overwhelmed, try breaking down your thoughts on paper. This can make challenges feel more manageable.",
                    "confused": "Writing through confusion can help organize thoughts and bring clarity. Try exploring different perspectives in your writing.",
                    "hopeful": "Hope is powerful. Journaling about your hopes can help clarify your values and what you want to move toward."
                }
                
                return emotion_responses.get(emotion, f"I notice you mentioned feeling {emotion}. Journaling about your emotions can help you understand them better and track patterns over time.")
            
            # If it seems like they're sharing a journal entry directly
            sharing_phrases = ["today i", "i feel", "i felt", "i am", "i'm feeling", "right now i"]
            if any(phrase in user_input_lower for phrase in sharing_phrases):
                return "Thank you for sharing your thoughts. If you'd like to save this as a journal entry, you can use the 'Text Journal' tab. What would you like to explore about what you've shared?"
        
        # Generic response with personalization if we have entry data
        if entry_count > 0:
            return f"You have {entry_count} recent journal entries. What specific aspect of your journaling practice would you like to discuss or explore?"
        else:
            return "What specific aspect of journaling would you like to explore today? I can offer suggestions, reflections, or answer questions about journaling practices." 