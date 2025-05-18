"""
Test script to verify BujoNow app initialization without segmentation faults.
"""

import os
import sys
import traceback

print("Starting test script...")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Test importing key components one by one
try:
    print("\nTesting journal_manager import...")
    from src.journal_manager import JournalManager
    test_manager = JournalManager()
    print("JournalManager initialized successfully")
except Exception as e:
    print(f"Error importing journal_manager: {type(e).__name__}: {e}")
    traceback.print_exc()

try:
    print("\nTesting analyzer_simplified import...")
    from src.analyzer_simplified import Analyzer
    test_analyzer = Analyzer()
    print("Simplified analyzer initialized successfully")
except Exception as e:
    print(f"Error importing analyzer_simplified: {type(e).__name__}: {e}")
    traceback.print_exc()

try:
    print("\nTesting AppManager without processors...")
    # Create a simplified version of AppManager
    class TestAppManager:
        def __init__(self):
            from src.journal_manager import JournalManager
            from src.analyzer_simplified import Analyzer
            self.journal_manager = JournalManager()
            self.analyzer = Analyzer()
            print("TestAppManager components initialized")
    
    test_app = TestAppManager()
    print("TestAppManager initialized successfully")
except Exception as e:
    print(f"Error creating test app manager: {type(e).__name__}: {e}")
    traceback.print_exc()

# Now try adding processors one by one
try:
    print("\nTesting ImageProcessor import...")
    from src.processor.image_processor import ImageProcessor
    # Initialize with bare minimum
    test_image_processor = ImageProcessor()
    print("ImageProcessor initialized successfully")
except Exception as e:
    print(f"Error importing image_processor: {type(e).__name__}: {e}")
    traceback.print_exc()

try:
    print("\nTesting AudioProcessor import...")
    from src.processor.audio_processor import AudioProcessor
    # Initialize with bare minimum
    test_audio_processor = AudioProcessor()
    print("AudioProcessor initialized successfully")
except Exception as e:
    print(f"Error importing audio_processor: {type(e).__name__}: {e}")
    traceback.print_exc()

print("\nTest script completed") 