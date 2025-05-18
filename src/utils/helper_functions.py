"""
Helper functions for the BujoNow bullet journal application.
Contains utility functions for text processing, audio processing, and image analysis.
"""

import os
import re
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pydub import AudioSegment
import speech_recognition as sr
from PIL import Image

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

import typing_extensions as typing

# Initialize face detection model if available
if MTCNN_AVAILABLE:
    mtcnn = MTCNN()
else:
    mtcnn = None

if FER_AVAILABLE:
    emotion_detector = FER()
else:
    emotion_detector = None

# RAG documents for emotional support contexts
RAG_DOCUMENTS = [
    "Practicing gratitude can significantly improve mental well-being by shifting focus from negative thoughts.",
    "CBT techniques help reframe negative thinking patterns into constructive insights.",
    "Social connection and being heard improve emotional regulation and resilience.",
    "Journaling builds self-awareness and emotional processing.",
    "Mindfulness and breathing exercises can reduce anxiety symptoms.",
    "Setting boundaries helps prevent burnout and protects well-being.",
    "Labeling emotions accurately helps regulate them.",
    "Acts of self-care can boost mood and positivity.",
    "A sense of purpose improves long-term well-being.",
    "Self-compassion reduces self-criticism and nurtures kindness.",
    "Building resilience involves embracing challenges and learning from adversity.",
    "Exercise and physical activity have a profound impact on mental health.",
    "Developing a growth mindset helps overcome obstacles and setbacks.",
    "Sleep hygiene and quality rest play a critical role in emotional health.",
    "Accepting imperfections and practicing self-forgiveness can reduce stress.",
    "Positive affirmations can improve self-esteem and mental clarity.",
    "Mindful eating and nutrition impact mental and emotional states.",
    "Visualization techniques can help manage stress and anxiety.",
    "Effective communication skills are essential for managing conflict and building connections.",
    "Grief is a complex emotional experience that requires time, patience, and support.",
    "Your mental health is just as important as your physical health.",
    "It's okay not to be okay.",
    "You are not your mental illness.",
    "Your struggles do not define you.",
    "Taking care of your mental health is an act of self-love.",
    "You are worthy of happiness and peace of mind.",
    "There is no shame in seeking help for your mental health.",
    "It's okay to take a break and prioritize your mental health.",
    "You are not alone in your struggles.",
    "It's okay to ask for support when you need it.",
    "Mental health is not a destination, it's a journey.",
    "Your mental health matters more than any external validation.",
    "You are stronger than you realize.",
    "Self-care is not selfish, it's necessary for good mental health.",
    "Small steps can lead to big progress in mental health.",
    "You are capable of overcoming your mental health challenges.",
    "Mental illness is not a personal failure, it's a medical condition.",
    "You are deserving of a life free from mental health struggles.",
    "It's okay to take medication for your mental health.",
    "You are not a burden for seeking help for your mental health.",
    "Mental health issues do not make you any less of a person.",
    "Your mental health is just as important as your career or education.",
    "You are capable of managing your mental health and living a fulfilling life.",
    "You have the power to overcome your mental health challenges.",
    "You are deserving of love and compassion, especially from yourself.",
    "Your mental health struggles do not define your future.",
    "It's okay to prioritize your mental health over other commitments.",
    "You are not alone in your journey towards better mental health.",
    "Mental health recovery is possible, and it starts with seeking help.",
    "You are worthy of a life filled with joy and happiness.",
    "It's okay to have bad days and ask for support when you need it.",
    "You have the power to change your relationship with your mental health."
]

# Pre-define emotion mapping for visualization
EMOTION_SCORES = {
    "hopeless": 1, "angry": 1.5, "anxious": 1.7, "sad": 2, "frustrated": 2.2, 
    "confused": 2.5, "neutral": 3, "okay": 3.2, "content": 3.5, 
    "hopeful": 4, "happy": 4.2, "excited": 4.5, "grateful": 5
}

# Define the response schema for journal analysis
class JournalAnalysis(typing.TypedDict):
    emotion: str
    themes: List[str]
    suggestion: str
    affirmation: str

def convert_m4a_to_wav(input_path: str) -> str:
    """
    Converts an M4A audio file to WAV format for processing.
    
    Args:
        input_path (str): Path to the input M4A audio file.
    
    Returns:
        str: Path to the converted WAV file.
    """
    output_path = input_path.rsplit(".", 1)[0] + ".wav"
    sound = AudioSegment.from_file(input_path, format="m4a")
    sound.export(output_path, format="wav")
    return output_path

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes audio to text using speech recognition.
    
    Args:
        audio_path (str): Path to the audio file.
    
    Returns:
        str: Transcribed text.
    """
    recognizer = sr.Recognizer()
    
    # Handle M4A files by converting first
    if audio_path.lower().endswith('.m4a'):
        audio_path = convert_m4a_to_wav(audio_path)
    
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Speech recognition could not understand the audio"
        except sr.RequestError:
            return "Could not request results from speech recognition service"

def detect_emotion_from_image(image_path: str) -> Dict[str, Any]:
    """
    Detects emotion from a facial image.
    
    Args:
        image_path (str): Path to the image file.
        
    Returns:
        Dict[str, Any]: Dictionary with detected emotion and confidence.
    """
    # Check if required libraries are available
    if not MTCNN_AVAILABLE or not FER_AVAILABLE:
        return {
            "emotion": "unknown", 
            "confidence": 0, 
            "message": "Face detection libraries not available",
            "all_emotions": {
                "neutral": 0.5,
                "happy": 0.2,
                "sad": 0.1,
                "angry": 0.1,
                "surprised": 0.05,
                "fearful": 0.05
            }
        }
        
    try:
        image = Image.open(image_path)
        # Use MTCNN to detect faces
        faces = mtcnn(image)
        
        if faces is None:
            return {"emotion": "unknown", "confidence": 0, "message": "No face detected"}
            
        # Use FER for emotion detection
        image_np = np.array(image)
        result = emotion_detector.detect_emotions(image_np)
        
        if not result or len(result) == 0:
            return {"emotion": "unknown", "confidence": 0, "message": "No emotions detected"}
            
        # Get the dominant emotion
        emotions = result[0]["emotions"]
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        
        return {
            "emotion": dominant_emotion[0],
            "confidence": dominant_emotion[1],
            "all_emotions": emotions
        }
    except Exception as e:
        return {"emotion": "error", "confidence": 0, "message": str(e)}

def create_word_cloud(text: str, max_words: int = 100) -> Any:
    """
    Creates a word cloud visualization from text.
    
    Args:
        text (str): Text to generate word cloud from.
        max_words (int): Maximum number of words to include.
        
    Returns:
        WordCloud: A word cloud object.
    """
    # Remove punctuation and make lowercase
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Create and return the word cloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        max_words=max_words, 
        background_color='white'
    ).generate(text)
    
    return wordcloud

def visualize_emotion_trend(entries: List[Dict]) -> plt.Figure:
    """
    Creates a visualization of emotion trends over time.
    
    Args:
        entries (List[Dict]): List of journal entries.
        
    Returns:
        plt.Figure: Matplotlib figure with the visualization.
    """
    dates = []
    emotions = []
    
    for entry in entries:
        try:
            date = datetime.strptime(entry['date'], '%Y-%m-%d')
            emotion = entry['emotion_analysis']['primary_emotion'].lower()
            
            # Convert emotion to a score (1-5 scale)
            emotion_score = EMOTION_SCORES.get(emotion, 3)  # Default to neutral if not found
            
            dates.append(date)
            emotions.append(emotion_score)
        except (KeyError, ValueError):
            # Skip entries with missing/invalid data
            continue
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, emotions, marker='o', linestyle='-')
    
    # Add labels and styling
    ax.set_xlabel('Date')
    ax.set_ylabel('Emotional State (1-5)')
    ax.set_title('Emotional Trend Over Time')
    ax.grid(True, alpha=0.3)
    
    # Add a reference line for neutral mood
    ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5)
    
    # Format the y-axis to show emotion labels
    emotion_labels = {1: 'Negative', 3: 'Neutral', 5: 'Positive'}
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels([emotion_labels.get(i, '') for i in [1, 2, 3, 4, 5]])
    
    plt.tight_layout()
    return fig

def visualize_emotion_distribution(entries: List[Dict]) -> plt.Figure:
    """
    Creates a visualization of emotion distribution across journal entries.
    
    Args:
        entries (List[Dict]): List of journal entries.
        
    Returns:
        plt.Figure: Matplotlib figure with the visualization.
    """
    emotions = []
    
    for entry in entries:
        try:
            emotion = entry['emotion_analysis']['primary_emotion'].lower()
            emotions.append(emotion)
        except KeyError:
            continue
    
    # Count emotion occurrences
    emotion_counts = Counter(emotions)
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Sort emotions by frequency
    sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_emotions) if sorted_emotions else ([], [])
    
    # Create bar chart
    bars = ax.bar(labels, values, color='skyblue')
    
    # Add labels and styling
    ax.set_xlabel('Emotions')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Emotions in Journal Entries')
    
    # Add count labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.0f}', ha='center', va='bottom')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def get_weekly_summary(entries: List[Dict]) -> str:
    """
    Generates a weekly summary of journal entries.
    
    Args:
        entries (List[Dict]): List of journal entries from the week.
        
    Returns:
        str: A summary of the week's journal entries.
    """
    if not entries:
        return "No entries found for this week."
    
    # Extract emotions and themes
    emotions = []
    all_themes = []
    
    for entry in entries:
        try:
            emotion = entry['emotion_analysis']['primary_emotion'].lower()
            emotions.append(emotion)
            
            # Extract themes if available
            if 'themes' in entry['emotion_analysis']:
                all_themes.extend(entry['emotion_analysis']['themes'])
        except KeyError:
            continue
    
    # Count occurrences
    emotion_counts = Counter(emotions)
    theme_counts = Counter(all_themes)
    
    # Find most common
    primary_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else "unknown"
    common_themes = [theme for theme, _ in theme_counts.most_common(3)]
    
    # Build summary
    summary = f"Weekly Summary:\n\n"
    summary += f"Primary emotion: {primary_emotion.capitalize()}\n\n"
    
    if common_themes:
        summary += "Common themes: " + ", ".join(common_themes) + "\n\n"
    
    summary += f"You made {len(entries)} journal entries this week.\n\n"
    
    # Add general reflection based on primary emotion
    if primary_emotion in ["happy", "excited", "grateful", "content"]:
        summary += "This week seemed positive overall. Remember to acknowledge and celebrate these positive moments.\n"
    elif primary_emotion in ["sad", "anxious", "stressed", "overwhelmed"]:
        summary += "This week seemed challenging. Remember that it's okay to have difficult periods, and practice self-care.\n"
    else:
        summary += "This week had a mix of experiences. Reflecting on both challenges and positive moments can provide valuable insights.\n"
    
    return summary

# Store RAG embeddings as a global variable to avoid recalculation
rag_embeddings = None 