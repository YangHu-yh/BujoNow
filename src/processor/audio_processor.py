"""
Audio Processor Module
Contains functions for processing audio recordings for voice journaling.
"""

import os
import json
from typing import Dict, Any, Optional
import speech_recognition as sr
from pydub import AudioSegment
import tempfile

class AudioProcessor:
    def __init__(self):
        """Initialize the audio processor for voice journal entries"""
        self.recognizer = sr.Recognizer()
    
    def convert_audio(self, file_path: str, output_format: str = 'wav') -> str:
        """
        Convert audio file to the desired format
        
        Args:
            file_path: Path to the audio file
            output_format: Desired output format (default: wav)
            
        Returns:
            Path to the converted file
        """
        try:
            # Get the directory and filename without extension
            dir_name = os.path.dirname(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Create output path
            output_path = os.path.join(dir_name, f"{base_name}.{output_format}")
            
            # Load audio
            audio = AudioSegment.from_file(file_path)
            
            # Export to new format
            audio.export(output_path, format=output_format)
            
            return output_path
        except Exception as e:
            print(f"Error converting audio: {e}")
            return file_path
    
    def transcribe_audio(self, file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with transcription results
        """
        # Ensure we have a WAV file for speech recognition
        wav_path = file_path
        if not file_path.lower().endswith('.wav'):
            wav_path = self.convert_audio(file_path)
        
        try:
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise and record the audio
                self.recognizer.adjust_for_ambient_noise(source)
                audio_data = self.recognizer.record(source)
                
                # Use Google Speech Recognition API
                text = self.recognizer.recognize_google(audio_data)
                
                return {
                    "success": True,
                    "text": text
                }
        except sr.UnknownValueError:
            return {
                "success": False,
                "error": "Speech Recognition could not understand the audio"
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "error": f"Could not request results from Speech Recognition service; {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error transcribing audio: {e}"
            }
    
    def process_journal_audio(self, file_path: str) -> Dict[str, Any]:
        """
        Process an audio journal entry: convert and transcribe
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with processed results including transcription
        """
        # Convert if needed
        if not file_path.lower().endswith('.wav'):
            file_path = self.convert_audio(file_path)
        
        # Transcribe
        transcription_result = self.transcribe_audio(file_path)
        
        if not transcription_result.get("success", False):
            return transcription_result
        
        # Return the processed result
        return {
            "success": True,
            "audio_file": file_path,
            "text": transcription_result["text"]
        }
        
    def save_audio_journal(self, file_path: str, journal_dir: str) -> Dict[str, Any]:
        """
        Process and save an audio journal entry
        
        Args:
            file_path: Path to the audio file
            journal_dir: Directory to save processed journal entries
            
        Returns:
            Dictionary with results including file paths and transcription
        """
        # Make sure journal directory exists
        os.makedirs(journal_dir, exist_ok=True)
        
        # Process the audio
        result = self.process_journal_audio(file_path)
        
        if not result.get("success", False):
            return result
        
        # Create a unique filename based on timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save the WAV file
        wav_path = os.path.join(journal_dir, f"audio_journal_{timestamp}.wav")
        
        if file_path != wav_path:
            import shutil
            shutil.copy2(file_path, wav_path)
        
        # Save the transcription
        text_path = os.path.join(journal_dir, f"audio_journal_{timestamp}.txt")
        with open(text_path, 'w') as f:
            f.write(result["text"])
        
        # Return the complete result
        return {
            "success": True,
            "audio_file": wav_path,
            "text_file": text_path,
            "text": result["text"]
        } 