"""
BujoNow Journal Analyzer

Analyzes journal entries using Google's Generative AI (Gemini) to provide insights.
Uses embedding-based RAG system for knowledge augmentation.
"""

import os
import time
import typing
import random
from typing import Dict, List, Any, Optional, Tuple

try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    import google.generativeai as genai
except ImportError:
    print("Warning: Some dependencies not available - analyzer will use fallback mode")

# Load RAG documents if helper_functions is available
try:
    from src.utils.helper_functions import RAG_DOCUMENTS
except ImportError:
    # Create a basic fallback for RAG
    RAG_DOCUMENTS = [
        {"title": "Self-care", "content": "Self-care is crucial for mental health. Consider daily practices like meditation, adequate sleep, and physical activity."},
        {"title": "Journaling benefits", "content": "Regular journaling helps process emotions, track patterns in your thinking, and provides an outlet for stress."},
        {"title": "Emotional regulation", "content": "Naming emotions can help regulate them. Try identifying specific feelings rather than general states like 'bad' or 'good'."},
        {"title": "Mindfulness", "content": "Mindfulness involves paying attention to the present moment without judgment. It can reduce anxiety and improve focus."},
        {"title": "Goal setting", "content": "Effective goals are specific, measurable, achievable, relevant, and time-bound (SMART)."}
    ]

# Default context to use when embeddings aren't available
DEFAULT_CONTEXT = """
Remember that journaling is a personal practice - there's no 'right way' to do it.

Setting boundaries is healthy. It's okay to say no to additional commitments when you're feeling overwhelmed.
Getting adequate sleep is crucial for emotional regulation and mental clarity.
Gratitude practices have been linked to increased happiness. Try listing 3 things you're grateful for each day.
"""

class JournalAnalysis(typing.TypedDict):
    emotion: str
    themes: List[str]
    suggestion: str
    affirmation: str

class Analyzer:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the analyzer with optional API key"""
        # Use provided API key or try to get from environment variable
        if api_key is None:
            api_key = os.environ.get("GOOGLE_API_KEY")
        
        # Store the API key directly
        self.api_key = api_key
        self.model_name = "gemini-2.0-flash"  # Default model name - using a free tier model
        
        if not api_key:
            print("Please set the GOOGLE_API_KEY environment variable or provide it as a parameter.")
            # Initialize without API functionality for now
            self.client = None
            self.rag_embeddings = None
            return

        # Configure the Google Generative AI client
        genai.configure(api_key=api_key)
        self.client = genai
        
        # Try to initialize embeddings with proper error handling
        try:
            # Check if embed_content function is available
            if hasattr(genai, 'embed_content'):
                print("Embeddings API available - initializing")
                self._initialize_embeddings()
            else:
                print("Warning: google.generativeai does not have embed_content function. Embeddings will be disabled.")
                self.rag_embeddings = None
        except Exception as e:
            print(f"Error initializing embeddings: {e}")
            self.rag_embeddings = None
    
    def _initialize_embeddings(self):
        """Initialize RAG document embeddings using embed_content"""
        try:
            # Initialize embeddings for RAG documents
            if not RAG_DOCUMENTS:
                print("No RAG documents available for embedding")
                self.rag_embeddings = None
                return
            
            print("Initializing embeddings for RAG documents")
            
            # Create embeddings for all RAG documents
            embeddings = []
            
            # First, try to see what embedding models are available
            try:
                print("Checking available embedding models...")
                embedding_model = "models/embedding-001"
                
                # Use a fixed embedding model for now since we know it's common
                print(f"Using embedding model: {embedding_model}")
                
                # Test with a simple embedding to check the response format
                test_result = genai.embed_content(
                    model=embedding_model,
                    content="Test content",
                    task_type="retrieval_document"
                )
                
                # Log the structure of the response
                print(f"Embedding result type: {type(test_result)}")
                print(f"Embedding result dir: {dir(test_result)}")
                
                # Try to extract the embedding values differently
                if hasattr(test_result, 'embedding'):
                    print("Embedding result has 'embedding' attribute")
                    print(f"Embedding type: {type(test_result.embedding)}")
                    print(f"Embedding length: {len(test_result.embedding) if hasattr(test_result.embedding, '__len__') else 'unknown'}")
                elif hasattr(test_result, 'embeddings'):
                    print("Embedding result has 'embeddings' attribute")
                    print(f"Embeddings type: {type(test_result.embeddings)}")
                    print(f"Embeddings length: {len(test_result.embeddings) if hasattr(test_result.embeddings, '__len__') else 'unknown'}")
                else:
                    print("WARNING: Embedding result doesn't have expected attributes")
                    print(f"Available attributes: {dir(test_result)}")
            except Exception as e:
                print(f"Error testing embedding model: {e}")
                self.rag_embeddings = None
                return
            
            # If we reach here, try to process all documents
            for doc in RAG_DOCUMENTS:
                try:
                    # Handle both string and dictionary formats
                    doc_content = doc
                    doc_title = ""
                    
                    # Check if doc is a dictionary with content key
                    if isinstance(doc, dict) and "content" in doc:
                        doc_content = doc["content"]
                        doc_title = doc.get("title", "")
                    
                    # Use the embed_content function from the latest library
                    result = genai.embed_content(
                        model=embedding_model,
                        content=doc_content,
                        task_type="retrieval_document"
                    )
                    
                    # Extract the embedding values - try different approaches
                    embedding = None
                    
                    if hasattr(result, 'embedding'):
                        # New API format
                        embedding = result.embedding
                    elif hasattr(result, 'embeddings') and result.embeddings:
                        # Alternative format
                        embedding = result.embeddings[0] if isinstance(result.embeddings, list) else result.embeddings
                    
                    # Only add if we successfully got an embedding
                    if embedding is not None:
                        embeddings.append({
                            "content": doc_content,
                            "title": doc_title,
                            "embedding": embedding
                        })
                    else:
                        print("Warning: Embedding result doesn't have expected structure")
                except Exception as e:
                    print(f"Error embedding document: {e}")
            
            if not embeddings:
                print("Failed to create any valid embeddings")
                self.rag_embeddings = None
                return
            
            # Store the embeddings
            self.rag_embeddings = embeddings
            print(f"Successfully initialized {len(embeddings)} document embeddings")
            
        except Exception as e:
            print(f"Error initializing embeddings: {e}")
            self.rag_embeddings = None
    
    def _get_random_contexts(self, top_k: int = 3) -> str:
        """Get random contexts when embeddings fail"""
        if not RAG_DOCUMENTS:
            return DEFAULT_CONTEXT
            
        import random
        # Select random documents
        selected_indices = random.sample(range(len(RAG_DOCUMENTS)), min(top_k, len(RAG_DOCUMENTS)))
        
        selected_docs = []
        for idx in selected_indices:
            doc = RAG_DOCUMENTS[idx]
            if isinstance(doc, dict) and "content" in doc:
                content = doc["content"]
                title = doc.get("title", "")
                if title:
                    selected_docs.append(f"{title}: {content}")
                else:
                    selected_docs.append(content)
            else:
                selected_docs.append(doc)  # Handle string format
                
        return "\n\n".join(selected_docs)
    
    def get_top_context(self, input_text: str, top_k: int = 3) -> str:
        """
        Retrieve the most relevant RAG documents based on similarity to input text
        
        Args:
            input_text: User input text to find similar documents for
            top_k: Number of top matches to return
            
        Returns:
            String with the top matching documents joined together
        """
        # Fall back to default or random contexts if no embeddings or input
        if self.rag_embeddings is None:
            print("No embeddings available, using random contexts")
            return self._get_random_contexts(top_k)
            
        if not input_text:
            return DEFAULT_CONTEXT
        
        try:
            # Get input text embedding
            result = genai.embed_content(
                model="models/embedding-001",
                content=input_text,
                task_type="retrieval_query"
            )
            
            if not hasattr(result, 'embedding'):
                print("Query embedding has unexpected structure, using random contexts")
                return self._get_random_contexts(top_k)
            
            query_embedding = result.embedding
            
            # Convert input embedding to numpy array for calculations
            query_embedding_np = np.array(query_embedding)
            
            # Calculate similarity scores
            similarities = []
            for i, doc in enumerate(self.rag_embeddings):
                doc_embedding = np.array(doc["embedding"])
                # Calculate cosine similarity
                similarity = np.dot(query_embedding_np, doc_embedding) / (
                    np.linalg.norm(query_embedding_np) * np.linalg.norm(doc_embedding)
                )
                similarities.append((i, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Get top_k documents
            top_docs = []
            for i in range(min(top_k, len(similarities))):
                doc_idx = similarities[i][0]
                doc = self.rag_embeddings[doc_idx]
                
                title = doc.get("title", "")
                content = doc["content"]
                
                if title:
                    top_docs.append(f"{title}: {content}")
                else:
                    top_docs.append(content)
            
            return "\n\n".join(top_docs)
        except Exception as e:
            print(f"Error in get_top_context: {e}")
            return self._get_random_contexts(top_k)
    
    def analyze_journal_entry(self, input_text: str) -> Dict[str, Any]:
        """
        Analyzes a journal entry using the Gemini model and returns a structured output
        with emotion, themes, suggestions, and affirmation.
        
        Args:
            input_text: The user's journal text.
        
        Returns:
            Dictionary with analysis results (emotion, themes, suggestion, affirmation)
        """
        if self.client is None:
            # Return a default response if API is not available
            return {
                "primary_emotion": "unknown",
                "emotion_intensity": 5,
                "emotional_themes": ["API not available"],
                "mood_summary": "Please set up your Google API key to enable analysis.",
                "suggested_actions": ["Your journaling practice is valuable even without AI analysis."]
            }
        
        context = self.get_top_context(input_text)
        prompt = f"""
            You are a supportive AI journaling assistant.
            Analyze the user's journal input text and return a structured JSON with the following:
            1. Primary emotion (e.g., sad, anxious, hopeful)
            2. Emotion intensity (1-10)
            3. Up to 3 emotional themes
            4. A brief mood summary
            5. Up to 3 suggested actions

            Use this context to ground your suggestions:
            {context}

            Here are a few examples:

            Journal Input Text:
            I feel hopeless. Everything I do seems to go wrong.
            Response:
            {{
              "primary_emotion": "hopeless",
              "emotion_intensity": 8,
              "emotional_themes": ["self-doubt", "negativity", "despair"],
              "mood_summary": "You're experiencing intense feelings of hopelessness and self-doubt.",
              "suggested_actions": [
                "Try writing down three things that went well each day, no matter how small.",
                "Practice self-compassion by speaking to yourself as you would to a friend.",
                "Consider reaching out to someone you trust about these feelings."
              ]
            }}

            Journal Input Text:
            I felt better today. I went for a walk and saw some friends.
            Response:
            {{
              "primary_emotion": "content",
              "emotion_intensity": 6,
              "emotional_themes": ["connection", "nature", "improvement"],
              "mood_summary": "You're experiencing a positive shift in mood through social connection and time in nature.",
              "suggested_actions": [
                "Continue spending time outdoors when possible.",
                "Maintain these social connections that bring you joy.",
                "Note what activities improve your mood for future reference."
              ]
            }}

            Now analyze the following entry:
            {input_text}
            Respond in JSON format like the examples above.
            """

        # Configure the model settings
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_name)
        
        try:
            response = model.generate_content(prompt)
            
            # Parse the JSON response
            try:
                result_text = response.text
                import json
                parsed = json.loads(result_text)
                
                # Ensure all required fields are present
                return {
                    "primary_emotion": parsed.get("primary_emotion", "unknown"),
                    "emotion_intensity": parsed.get("emotion_intensity", 5),
                    "emotional_themes": parsed.get("emotional_themes", ["general"]),
                    "mood_summary": parsed.get("mood_summary", "Continue journaling daily."),
                    "suggested_actions": parsed.get("suggested_actions", ["You're making progress by reflecting."])
                }
            except json.JSONDecodeError:
                # Fallback for non-JSON responses
                return {
                    "primary_emotion": "unknown",
                    "emotion_intensity": 5,
                    "emotional_themes": ["parsing error"],
                    "mood_summary": "Continue your journaling practice.",
                    "suggested_actions": ["Every entry brings insight, even when AI analysis fails."]
                }
        except Exception as e:
            print(f"Error generating content: {e}")
            
            # Try with a different model if available
            if "not found" in str(e) or "not supported" in str(e):
                try:
                    print("Trying with available model...")
                    self.model_name = self._get_available_model()
                    print(f"Using alternative model: {self.model_name}")
                    
                    model = genai.GenerativeModel(self.model_name)
                    response = model.generate_content(prompt)
                    
                    try:
                        result_text = response.text
                        import json
                        parsed = json.loads(result_text)
                        
                        return {
                            "primary_emotion": parsed.get("primary_emotion", "unknown"),
                            "emotion_intensity": parsed.get("emotion_intensity", 5),
                            "emotional_themes": parsed.get("emotional_themes", ["general"]),
                            "mood_summary": parsed.get("mood_summary", "Continue journaling daily."),
                            "suggested_actions": parsed.get("suggested_actions", ["You're making progress by reflecting."])
                        }
                    except Exception:
                        pass
                except Exception as alt_e:
                    print(f"Error with alternative model: {alt_e}")
            
            # Return default response if all attempts fail
            return {
                "primary_emotion": "unknown",
                "emotion_intensity": 5,
                "emotional_themes": ["error"],
                "mood_summary": f"An error occurred during analysis: {str(e)}",
                "suggested_actions": ["Technology may fail, but your journaling practice remains valuable."]
            }
    
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
        
        # Handle missing API client
        if self.client is None:
            return {
                "summary": "API key not available. Please set up your Google API key to enable summaries.",
                "emotion_trend": "Unable to analyze without API access.",
                "recommendations": ["Set up your API key to enable full functionality."]
            }
        
        # Combine all journal texts
        combined_text = " ".join([entry["content"]["text"] for entry in entries if "text" in entry.get("content", {})])
        
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

        # Configure the model settings
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_name)
        
        try:
            response = model.generate_content(prompt)
            
            # Parse the JSON response
            try:
                result_text = response.text
                import json
                parsed = json.loads(result_text)
                
                # Ensure all required fields are present
                return {
                    "summary": parsed.get("summary", "Unable to generate a summary."),
                    "emotion_trend": parsed.get("emotion_trend", "No clear emotional patterns detected."),
                    "recommendations": parsed.get("recommendations", ["Continue your regular journaling practice."])
                }
            except json.JSONDecodeError:
                # Fallback for non-JSON responses
                return {
                    "summary": "Error parsing the summary.",
                    "emotion_trend": "Unable to analyze emotional patterns.",
                    "recommendations": ["Continue your journaling practice despite AI limitations."]
                }
        except Exception as e:
            print(f"Error generating summary: {e}")
            
            # Try with a different model if available
            if "not found" in str(e) or "not supported" in str(e):
                try:
                    print("Trying weekly summary with available model...")
                    self.model_name = self._get_available_model()
                    print(f"Using alternative model: {self.model_name}")
                    
                    model = genai.GenerativeModel(self.model_name)
                    response = model.generate_content(prompt)
                    
                    try:
                        result_text = response.text
                        import json
                        parsed = json.loads(result_text)
                        
                        return {
                            "summary": parsed.get("summary", "Unable to generate a summary."),
                            "emotion_trend": parsed.get("emotion_trend", "No clear emotional patterns detected."),
                            "recommendations": parsed.get("recommendations", ["Continue your regular journaling practice."])
                        }
                    except Exception:
                        pass
                except Exception as alt_e:
                    print(f"Error with alternative model for weekly summary: {alt_e}")
            
            return {
                "summary": f"An error occurred during analysis: {str(e)}",
                "emotion_trend": "Analysis failed due to an error.",
                "recommendations": ["Try again later when the service is available."]
            }
    
    def chat_response(self, user_input: str, recent_entries=None) -> str:
        """
        Generate a response to a user's chat message about their journal entries
        
        Args:
            user_input: The user's message or question
            recent_entries: Optional list of recent journal entries to provide context
            
        Returns:
            AI assistant's response as a string
        """
        if self.client is None:
            return "I'm sorry, but I need an API connection to chat with you about your journal. Please set up your Google API key."
        
        # Extract text from recent entries if available
        recent_texts = []
        if recent_entries and isinstance(recent_entries, list):
            for entry in recent_entries:
                if isinstance(entry, dict) and "content" in entry and "text" in entry["content"]:
                    date = entry.get("date", "unknown date")
                    text = entry["content"]["text"]
                    emotion = entry.get("emotion_analysis", {}).get("primary_emotion", "unknown")
                    recent_texts.append(f"Entry from {date} (emotion: {emotion}): {text}")
        
        # Get relevant context using embeddings if available
        context = self.get_top_context(user_input)
        
        # Create the prompt for the chat response
        prompt = f"""
            You are a supportive AI journaling assistant named BujoNow.
            You help users reflect on their journaling practice and provide insights about their entries.
            
            Recent journal entries:
            {recent_texts[:3] if recent_texts else "No recent entries available."}
            
            Relevant context:
            {context}
            
            User message: {user_input}
            
            Respond in a helpful, empathetic way that encourages reflection and journaling.
            Keep your response concise (1-3 paragraphs) unless the user specifically asks for more detail.
            If you don't have enough information to answer specifically, be honest and suggest what might help.
            
            Your response:
        """
        
        # Configure the model settings
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_name)
        
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating chat response: {e}")
            
            # Try with a different model if available
            if "not found" in str(e) or "not supported" in str(e):
                try:
                    print("Trying chat with available model...")
                    self.model_name = self._get_available_model()
                    print(f"Using alternative model for chat: {self.model_name}")
                    
                    model = genai.GenerativeModel(self.model_name)
                    response = model.generate_content(prompt)
                    return response.text.strip()
                except Exception as alt_e:
                    print(f"Error with alternative model for chat: {alt_e}")
            
            return "I'm having trouble processing your question right now. Please try again later."
    
    def _get_available_model(self):
        """Try to get an available model name if the default one doesn't work"""
        try:
            # Simple fallback - try these specific model names in order
            fallback_models = [
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-1.0-pro-vision-latest",
                "gemini-1.0-pro-latest",
                "gemini-pro-latest",
                "gemini-pro"
            ]
            
            print(f"Trying fallback models in this order: {fallback_models}")
            
            # For HuggingFace Spaces, we'll just try the fallback list directly
            # This is more reliable than trying to parse the list_models result
            for model_name in fallback_models:
                if model_name == self.model_name:
                    continue  # Skip the current model that's already failing
                    
                try:
                    print(f"Testing model: {model_name}")
                    # Try a minimal request to see if the model works
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content("Hello")
                    if response and hasattr(response, 'text'):
                        print(f"Success! Model {model_name} is working")
                        return model_name
                except Exception as test_e:
                    print(f"Model {model_name} failed: {test_e}")
                    continue
            
            # If all fails, return the default
            print("All fallback models failed, keeping current model")
            return self.model_name
            
        except Exception as e:
            print(f"Error in model fallback: {e}")
            return self.model_name  # Fall back to the default 