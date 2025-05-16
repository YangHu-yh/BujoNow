"""
Analyzer Module
Contains functions for analyzing journal entries using Gemini API and embeddings.
"""

import os
import json
from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import typing_extensions as typing
from google import genai
from google.genai import types

# Import RAG documents from helper functions
from utils.helper_functions import RAG_DOCUMENTS

class JournalAnalysis(typing.TypedDict):
    emotion: str
    themes: List[str]
    suggestion: str
    affirmation: str

class Analyzer:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the analyzer with a Google API key.
        
        Args:
            api_key: Optional Google API key (can be loaded from environment variable)
        """
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.environ.get("GOOGLE_API_KEY")
            
        if api_key is None:
            raise ValueError("Google API key must be provided or set as GOOGLE_API_KEY environment variable")
            
        self.client = genai.Client(api_key=api_key)
        self.rag_embeddings = None
        
        # Initialize embeddings
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize RAG document embeddings"""
        embedding_response = self.client.models.embed_content(
            model="models/text-embedding-004",
            contents=RAG_DOCUMENTS,
            config=types.EmbedContentConfig(task_type="retrieval_document")
        )
        self.rag_embeddings = [e.values for e in embedding_response.embeddings]
    
    def get_top_context(self, input_text: str, top_k: int = 3) -> str:
        """
        Retrieve top relevant documents from RAG_DOCUMENTS using embedding similarity.
        
        Args:
            input_text: The input text to find relevant contexts for
            top_k: Number of top contexts to retrieve
            
        Returns:
            String with top relevant contexts joined by newlines
        """
        query_embedding = self.client.models.embed_content(
            model="models/text-embedding-004",
            contents=input_text,
            config=types.EmbedContentConfig(task_type="retrieval_query")
        ).embeddings[0].values

        scores = cosine_similarity([query_embedding], self.rag_embeddings)[0]
        top_indices = np.argsort(scores)[::-1][:top_k]
        return "\n".join([RAG_DOCUMENTS[i] for i in top_indices])
    
    def analyze_journal_entry(self, input_text: str) -> Dict[str, Any]:
        """
        Analyzes a journal entry using the Gemini model and returns a structured output
        with emotion, themes, suggestions, and affirmation.
        
        Args:
            input_text: The user's journal text.
        
        Returns:
            Dictionary with analysis results (emotion, themes, suggestion, affirmation)
        """
        context = self.get_top_context(input_text)
        prompt = f"""
            You are a supportive AI journaling assistant.
            Analyze the user's journal input text and return a structured JSON with the following:
            1. Primary emotion (e.g., sad, anxious, hopeful)
            2. Up to 3 key themes
            3. One CBT-style reflection suggestion
            4. One daily affirmation

            Use this context to ground your suggestions:
            {context}

            Here are a few examples:

            Journal Input Text:
            I feel hopeless. Everything I do seems to go wrong.
            Response:
            {{
              "emotion": "hopeless",
              "themes": ["self-doubt", "negativity"],
              "suggestion": "Try writing down three things that went well each day, no matter how small.",
              "affirmation": "You are resilient and capable of overcoming hard days."
            }}

            Journal Input Text:
            I felt better today. I went for a walk and saw some friends.
            Response:
            {{
              "emotion": "grateful",
              "themes": ["connection", "nature"],
              "suggestion": "Continue spending time doing things that bring you joy.",
              "affirmation": "Joy is found in small, simple moments."
            }}

            Now analyze the following entry:
            {input_text}
            Respond in JSON format like:
            {{
              "emotion": "...",
              "themes": ["...", "..."],
              "suggestion": "...",
              "affirmation": "..."
            }}
            """

        config = types.GenerateContentConfig(
            temperature=0.7,
            top_k=50,
            top_p=0.9,
            response_mime_type="application/json",
            response_schema=JournalAnalysis
        )
        
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt],
            config=config
        )

        return response.parsed
    
    def analyze_audio(self, transcribed_text: str) -> Dict[str, Any]:
        """
        Analyze transcribed audio from a voice journal entry
        
        Args:
            transcribed_text: Text transcribed from audio
            
        Returns:
            Dictionary with analysis results
        """
        # Process the transcribed text the same way as a regular text entry
        return self.analyze_journal_entry(transcribed_text)
    
    def create_weekly_summary(self, entries: List[Dict]) -> Dict[str, Any]:
        """
        Generate a summary of journal entries from the past week
        
        Args:
            entries: List of journal entries
            
        Returns:
            Dictionary with summary information
        """
        if not entries:
            return {
                "summary": "No entries found for this week.",
                "emotion_trend": None,
                "recommendations": []
            }
        
        # Combine all journal texts
        combined_text = " ".join([entry["content"]["text"] for entry in entries])
        
        # Use the same approach as analyze_journal_entry but with a different prompt
        context = self.get_top_context(combined_text)
        prompt = f"""
            You are an AI assistant that helps users reflect on their journaling.
            Analyze the collection of journal entries from the past week and provide:
            1. A brief summary of the overall week
            2. Key emotional patterns observed
            3. 2-3 recommendations for the coming week based on the patterns

            Context for grounding your recommendations:
            {context}

            Journal entries from the past week:
            {combined_text}
            
            Return your analysis in JSON format like:
            {{
              "summary": "One paragraph summary of the week",
              "emotion_trend": "Description of emotional patterns",
              "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
            }}
            """
        
        config = types.GenerateContentConfig(
            temperature=0.7,
            response_mime_type="application/json"
        )
        
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt],
            config=config
        )
        
        try:
            return response.parsed
        except Exception as e:
            # Fallback if parsing fails
            text_response = response.text
            return {
                "summary": text_response,
                "emotion_trend": "Unable to analyze emotional trends",
                "recommendations": ["Consider maintaining consistent journaling practice"]
            } 