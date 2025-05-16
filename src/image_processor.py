"""
Image Processor Module
Contains functions for analyzing images, detecting faces and emotions.
"""

import os
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
from fer import FER
import matplotlib.pyplot as plt
from google import genai
from google.genai import types

class ImageProcessor:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the image processor with face detection and emotion recognition
        
        Args:
            api_key: Optional Google API key for image content analysis
        """
        # Initialize face detection
        self.mtcnn = MTCNN(keep_all=True)
        
        # Initialize emotion detector
        self.emotion_detector = FER()
        
        # Initialize Gemini if API key is provided
        self.gemini_client = None
        if api_key or os.environ.get("GOOGLE_API_KEY"):
            self.gemini_client = genai.Client(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
    
    def detect_faces(self, image_path: str) -> Tuple[List[np.ndarray], Optional[np.ndarray]]:
        """
        Detect faces in an image and return face regions
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (list of face regions, image tensor)
        """
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
    
    def analyze_emotions(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze emotions in faces found in an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with emotion analysis results
        """
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
    
    def analyze_image_content(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze the content of an image using Gemini Vision
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with image content analysis
        """
        if not self.gemini_client:
            return {"error": "Gemini API key not provided for image content analysis"}
        
        try:
            img = Image.open(image_path)
            
            prompt = """
            Analyze this image and provide:
            1. A brief description of the scene (1-2 sentences)
            2. Key objects or elements present
            3. The overall mood/atmosphere conveyed
            
            Return your analysis in JSON format like:
            {
              "description": "...",
              "key_elements": ["...", "..."],
              "mood": "..."
            }
            """
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash-vision",
                contents=[prompt, {"mime_type": "image/jpeg", "data": self._get_image_bytes(img)}],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            
            return response.parsed
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_image_bytes(self, img: Image.Image) -> bytes:
        """Convert PIL Image to bytes for Gemini API"""
        import io
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    
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