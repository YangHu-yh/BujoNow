"""
Image Processor Module
Contains functions for analyzing images, detecting faces and emotions.
"""

import os
import sys
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import random

# Try to import face detection and emotion analysis libraries
# Provide fallbacks if they're not available
try:
    from facenet_pytorch import MTCNN
    MTCNN_AVAILABLE = True
except ImportError:
    print("Warning: facenet-pytorch not available. Face detection will be limited.")
    MTCNN_AVAILABLE = False

try:
    from fer import FER
    FER_AVAILABLE = True
except ImportError:
    print("Warning: FER not available. Emotion detection will be limited.")
    FER_AVAILABLE = False

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
    
    # Check if embedding functionality is available
    HAS_EMBEDDINGS = hasattr(genai, 'embed_content')
    if not HAS_EMBEDDINGS:
        print("Warning: google.generativeai does not have embed_content function. Some features will be disabled.")
except ImportError:
    print("Warning: google.generativeai not available. Image content analysis will be limited.")
    GENAI_AVAILABLE = False
    HAS_EMBEDDINGS = False

class ImageProcessor:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the image processor with face detection and emotion recognition
        
        Args:
            api_key: Optional Google API key for image content analysis
        """
        # Initialize face detection if available
        self.mtcnn = None
        if MTCNN_AVAILABLE:
            try:
                self.mtcnn = MTCNN(keep_all=True)
            except Exception as e:
                print(f"Error initializing MTCNN: {e}")
        
        # Initialize emotion detector if available
        self.emotion_detector = None
        if FER_AVAILABLE:
            try:
                self.emotion_detector = FER()
            except Exception as e:
                print(f"Error initializing FER: {e}")
        
        # Initialize Gemini if API key is provided and library is available
        self.gemini_client = None
        if GENAI_AVAILABLE and (api_key or os.environ.get("GOOGLE_API_KEY")):
            try:
                genai.configure(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
                self.gemini_client = genai
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
    
    def detect_faces(self, image_path: str) -> Tuple[List[np.ndarray], Optional[np.ndarray]]:
        """
        Detect faces in an image and return face regions
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (list of face regions, image tensor)
        """
        if not MTCNN_AVAILABLE or self.mtcnn is None:
            print("Face detection not available - MTCNN library missing")
            img = Image.open(image_path)
            img_tensor = np.array(img)
            return [], img_tensor
            
        try:
            img = Image.open(image_path)
            img_tensor = np.array(img)
            
            # Detect faces
            boxes, _ = self.mtcnn.detect(img)
            
            if boxes is None:
                return [], img_tensor
            
            # Extract face regions
            face_regions = []
            for box in boxes:
                x1, y1, x2, y2 = [int(b) for b in box]
                face_region = img_tensor[y1:y2, x1:x2]
                face_regions.append(face_region)
            
            return face_regions, img_tensor
        except Exception as e:
            print(f"Error in face detection: {e}")
            img = Image.open(image_path)
            img_tensor = np.array(img)
            return [], img_tensor
    
    def analyze_emotions(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze emotions in faces found in an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with emotion analysis results
        """
        if not FER_AVAILABLE or self.emotion_detector is None:
            # Return simulated emotions when library is not available
            print("Emotion detection not available - FER library missing")
            return self._generate_simulated_emotions()
            
        try:
            img = Image.open(image_path)
            img_tensor = np.array(img)
            
            # Detect emotions
            result = self.emotion_detector.detect_emotions(img_tensor)
            
            if not result:
                return {"emotions": [], "dominant_emotion": None}
            
            emotions = []
            for face in result:
                emotions.append(face["emotions"])
            
            # Calculate average emotion across all faces
            if emotions:
                avg_emotions = {}
                for emotion_dict in emotions:
                    for emotion, score in emotion_dict.items():
                        avg_emotions[emotion] = avg_emotions.get(emotion, 0) + score / len(emotions)
                
                # Find dominant emotion
                dominant_emotion = max(avg_emotions.items(), key=lambda x: x[1])
                
                return {
                    "emotions": emotions,
                    "average_emotions": avg_emotions,
                    "dominant_emotion": dominant_emotion[0],
                    "dominant_score": dominant_emotion[1]
                }
            
            return {"emotions": [], "dominant_emotion": None}
        except Exception as e:
            print(f"Error in emotion analysis: {e}")
            return self._generate_simulated_emotions()
    
    def _generate_simulated_emotions(self) -> Dict[str, Any]:
        """Generate simulated emotions when detection is not available"""
        # Define standard emotion categories
        emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
        
        # Create random but realistic-looking emotion distribution
        # Make one emotion dominant
        dominant_idx = random.randint(0, len(emotions)-1)
        emotion_scores = {}
        
        for i, emotion in enumerate(emotions):
            if i == dominant_idx:
                emotion_scores[emotion] = random.uniform(0.5, 0.8)  # Dominant emotion
            else:
                emotion_scores[emotion] = random.uniform(0.05, 0.3)  # Other emotions
        
        # Normalize to make sure sum is close to 1
        total = sum(emotion_scores.values())
        normalized_scores = {k: v/total for k, v in emotion_scores.items()}
        
        # Determine dominant emotion
        dominant_emotion = max(normalized_scores.items(), key=lambda x: x[1])
        
        return {
            "emotions": [normalized_scores],
            "average_emotions": normalized_scores,
            "dominant_emotion": dominant_emotion[0],
            "dominant_score": dominant_emotion[1],
            "simulated": True  # Flag that these are simulated results
        }
    
    def analyze_image_content(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze the content of an image using Gemini Vision
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with content analysis results
        """
        if not GENAI_AVAILABLE or self.gemini_client is None:
            print("Image content analysis not available - Gemini API not configured")
            return self._generate_simulated_content_analysis()
            
        try:
            img = Image.open(image_path)
            
            # Get Gemini model
            model = self.gemini_client.GenerativeModel('gemini-pro-vision')
            
            # Format image data for the API
            image_data = self._get_image_data(img)
            
            # Create prompt
            prompt = """
            Describe this image in detail, focusing on:
            1. The main subject or scene
            2. The mood or emotional tone
            3. Any notable elements or objects
            
            Keep your description concise but informative.
            """
            
            # Make API call
            response = model.generate_content([prompt, image_data])
            
            return {
                "description": response.text,
                "model": "gemini-pro-vision"
            }
        except Exception as e:
            print(f"Error in image content analysis: {e}")
            return self._generate_simulated_content_analysis()
    
    def _generate_simulated_content_analysis(self) -> Dict[str, Any]:
        """Generate simulated content analysis when API is not available"""
        descriptions = [
            "An image that appears to show a person in a reflective moment.",
            "A scene that conveys a sense of calm and tranquility.",
            "What looks like a nature setting with elements that create a peaceful atmosphere.",
            "An image that might represent everyday life, with a warm, inviting quality.",
            "A composition that suggests contemplation or mindfulness.",
            "A scene that could represent personal growth or self-reflection."
        ]
        
        return {
            "description": random.choice(descriptions),
            "model": "simulated",
            "simulated": True
        }
    
    def _get_image_data(self, img: Image.Image) -> Any:
        """
        Convert PIL Image to the format required by Gemini API
        
        Args:
            img: PIL Image
            
        Returns:
            Image data formatted for the API
        """
        try:
            if hasattr(self.gemini_client.types, 'Part'):
                # Use the Part class if available
                from google.generativeai.types import Part
                
                # Get image bytes
                import io
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format or 'JPEG')
                img_bytes = img_byte_arr.getvalue()
                
                # Create image part
                return Part.from_data(mime_type=f"image/{img.format.lower() if img.format else 'jpeg'}", 
                                    data=img_bytes)
            else:
                # Fallback to base64 encoding
                import base64
                import io
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format or 'JPEG')
                img_bytes = img_byte_arr.getvalue()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                return {"mime_type": f"image/{img.format.lower() if img.format else 'jpeg'}", 
                        "data": img_b64}
        except Exception as e:
            print(f"Error formatting image: {e}")
            # Return a placeholder if formatting fails
            return {"mime_type": "text/plain", "data": "Image could not be processed"}
    
    def create_emotion_visualization(self, emotion_data: Dict[str, float], save_path: str) -> str:
        """
        Create a visualization of emotions and save to file
        
        Args:
            emotion_data: Dictionary of emotions and their scores
            save_path: Path to save the visualization
            
        Returns:
            Path to the saved visualization
        """
        # Remove any empty data
        emotion_data = {k: v for k, v in emotion_data.items() if v > 0}
        
        if not emotion_data:
            return None
            
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Create bar chart
        emotions = list(emotion_data.keys())
        scores = list(emotion_data.values())
        
        # Sort by score
        sorted_indices = np.argsort(scores)[::-1]
        emotions = [emotions[i] for i in sorted_indices]
        scores = [scores[i] for i in sorted_indices]
        
        plt.bar(emotions, scores, color='skyblue')
        plt.xlabel('Emotion')
        plt.ylabel('Score')
        plt.title('Detected Emotions')
        plt.tight_layout()
        
        # Save figure
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        plt.close()
        
        return save_path 