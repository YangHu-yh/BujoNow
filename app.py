"""
BujoNow - Bullet Journal Companion

A journaling application with AI-powered analysis, voice journaling,
emotion detection, and bullet journal-style organization.
"""

import os
import json
import datetime
import gradio as gr
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

# Import local modules
from src.journal_manager import JournalManager
from src.analyzer import Analyzer
from src.image_processor import ImageProcessor
from src.audio_processor import AudioProcessor

# Constants
JOURNALS_DIR = "journals"
UPLOADS_DIR = "uploads"
VISUALIZATIONS_DIR = "visualizations"

# Ensure directories exist
for directory in [JOURNALS_DIR, UPLOADS_DIR, VISUALIZATIONS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Initialize components
journal_manager = JournalManager(JOURNALS_DIR)
analyzer = Analyzer()
image_processor = ImageProcessor()
audio_processor = AudioProcessor()

def save_text_journal(text: str, date: str = None) -> Dict[str, Any]:
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
    
    # Create entry content
    entry_content = {
        "text": text,
        "type": "text",
        "created_at": datetime.datetime.now().isoformat()
    }
    
    # Save the entry
    entry_id = journal_manager.add_entry(entry_date, entry_content)
    
    # Analyze the entry
    try:
        analysis = analyzer.analyze_journal_entry(text)
        journal_manager.add_analysis(entry_id, analysis)
    except Exception as e:
        print(f"Error analyzing entry: {e}")
    
    return {
        "success": True,
        "entry_id": entry_id,
        "date": entry_date.strftime("%Y-%m-%d")
    }

def save_audio_journal(audio_file: str, date: str = None) -> Dict[str, Any]:
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
    result = audio_processor.process_journal_audio(audio_file)
    
    if not result.get("success", False):
        return result
    
    # Use provided date or current date
    entry_date = datetime.datetime.now()
    if date:
        try:
            entry_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
    
    # Create entry content
    entry_content = {
        "text": result["text"],
        "type": "audio",
        "audio_file": result["audio_file"],
        "created_at": datetime.datetime.now().isoformat()
    }
    
    # Save the entry
    entry_id = journal_manager.add_entry(entry_date, entry_content)
    
    # Analyze the entry
    try:
        analysis = analyzer.analyze_audio(result["text"])
        journal_manager.add_analysis(entry_id, analysis)
    except Exception as e:
        print(f"Error analyzing audio entry: {e}")
    
    return {
        "success": True,
        "entry_id": entry_id,
        "date": entry_date.strftime("%Y-%m-%d"),
        "transcription": result["text"]
    }

def save_image_journal(image_file: str, notes: str = "", date: str = None) -> Dict[str, Any]:
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
    emotion_results = image_processor.analyze_emotions(image_file)
    
    # Create visualization if emotions were detected
    visualization_path = None
    if emotion_results.get("average_emotions"):
        vis_filename = f"emotions_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        visualization_path = os.path.join(VISUALIZATIONS_DIR, vis_filename)
        image_processor.create_emotion_visualization(
            emotion_results["average_emotions"], 
            visualization_path
        )
    
    # Analyze image content if available
    content_analysis = image_processor.analyze_image_content(image_file)
    
    # Create entry content
    entry_content = {
        "text": notes,
        "type": "image",
        "image_file": image_file,
        "emotions": emotion_results,
        "content_analysis": content_analysis,
        "visualization": visualization_path,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    # Save the entry
    entry_id = journal_manager.add_entry(entry_date, entry_content)
    
    return {
        "success": True,
        "entry_id": entry_id,
        "date": entry_date.strftime("%Y-%m-%d"),
        "emotions": emotion_results,
        "visualization": visualization_path
    }

def get_entries_by_date(date: str) -> List[Dict[str, Any]]:
    """
    Get journal entries for a specific date
    
    Args:
        date: Date string (format: YYYY-MM-DD)
        
    Returns:
        List of entry dictionaries
    """
    try:
        entry_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        entries = journal_manager.get_entries_by_date(entry_date)
        return entries
    except ValueError:
        return []
    except Exception as e:
        print(f"Error retrieving entries: {e}")
        return []

def get_weekly_summary(start_date: str = None) -> Dict[str, Any]:
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
    entries = journal_manager.get_entries_in_range(start, end)
    
    if not entries:
        return {
            "success": True,
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "summary": "No entries found for this week."
        }
    
    # Generate weekly summary
    try:
        summary = analyzer.create_weekly_summary(entries)
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

# Create the Gradio interface
def create_interface():
    with gr.Blocks(title="BujoNow - Bullet Journal Companion") as app:
        gr.Markdown("# BujoNow - Bullet Journal Companion")
        gr.Markdown("A smart journaling tool with AI-powered analysis, mood tracking, and organization")
        
        with gr.Tabs():
            # Text Journaling Tab
            with gr.Tab("Text Journal"):
                with gr.Row():
                    with gr.Column():
                        text_date = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                        text_input = gr.Textbox(label="Journal Entry", lines=10, placeholder="Write your thoughts here...")
                        text_submit = gr.Button("Save Entry")
                    
                    with gr.Column():
                        text_output = gr.JSON(label="Analysis Results")
                
                text_submit.click(
                    fn=save_text_journal,
                    inputs=[text_input, text_date],
                    outputs=text_output
                )
            
            # Voice Journaling Tab
            with gr.Tab("Voice Journal"):
                with gr.Row():
                    with gr.Column():
                        audio_date = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                        audio_input = gr.Audio(label="Record or Upload Audio", type="filepath")
                        audio_submit = gr.Button("Save Voice Entry")
                    
                    with gr.Column():
                        transcription = gr.Textbox(label="Transcription", lines=5)
                        audio_output = gr.JSON(label="Analysis Results")
                
                audio_submit.click(
                    fn=save_audio_journal,
                    inputs=[audio_input, audio_date],
                    outputs=audio_output
                )
            
            # Photo Journaling Tab
            with gr.Tab("Photo Journal"):
                with gr.Row():
                    with gr.Column():
                        image_date = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                        image_input = gr.Image(label="Upload Image", type="filepath")
                        image_notes = gr.Textbox(label="Notes", lines=3, placeholder="Add notes about this image...")
                        image_submit = gr.Button("Save Photo Entry")
                    
                    with gr.Column():
                        image_emotion = gr.JSON(label="Emotion Analysis")
                        image_visualization = gr.Image(label="Emotion Visualization")
                
                def process_image_output(result):
                    if result.get("success", False) and result.get("visualization"):
                        return result, result["visualization"]
                    return result, None
                
                image_submit.click(
                    fn=lambda img, notes, date: process_image_output(save_image_journal(img, notes, date)),
                    inputs=[image_input, image_notes, image_date],
                    outputs=[image_emotion, image_visualization]
                )
            
            # Journal Review Tab
            with gr.Tab("Review"):
                with gr.Row():
                    review_date = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                    review_button = gr.Button("Get Entries")
                
                entries_display = gr.JSON(label="Journal Entries")
                
                review_button.click(
                    fn=get_entries_by_date,
                    inputs=review_date,
                    outputs=entries_display
                )
            
            # Weekly Summary Tab
            with gr.Tab("Weekly Summary"):
                with gr.Row():
                    summary_date = gr.Textbox(label="Start Date (YYYY-MM-DD)", value=datetime.datetime.now().strftime("%Y-%m-%d"))
                    summary_button = gr.Button("Generate Summary")
                
                summary_display = gr.JSON(label="Weekly Summary")
                
                summary_button.click(
                    fn=get_weekly_summary,
                    inputs=summary_date,
                    outputs=summary_display
                )
    
    return app

# Launch the app
if __name__ == "__main__":
    app = create_interface()
    app.launch() 