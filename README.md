# BujoNow - Bullet Journal Companion

BujoNow is an AI-powered bullet journal companion app that helps you maintain a digital journal with advanced analysis features.

## Features

- **Text Journaling**: Write your thoughts with AI-powered analysis of emotions, themes, and suggestions
- **Voice Journaling**: Record audio journals that get transcribed automatically
- **Photo Journaling**: Add images to your journal with automatic facial emotion detection
- **Weekly Summaries**: Generate insights from your week's journaling activity
- **Entry Organization**: Keep your journal entries organized by date

## Project Structure

```
├── app.py                 # Main application with Gradio interface
├── requirements.txt       # Python dependencies
├── src/
│   ├── journal_manager.py # Manages saving and retrieving journal entries
│   ├── analyzer.py        # AI analysis using Google's Gemini API
│   ├── image_processor.py # Image and emotion analysis
│   └── audio_processor.py # Audio processing and transcription
├── utils/
│   └── helper_functions.py # Utility functions for various operations
└── data/
    └── sample_input.txt    # Sample journal entry
```

## Setup and Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Google API key for Gemini:
   ```
   export GOOGLE_API_KEY="your_api_key_here"
   ```
4. Run the application:
   ```
   python app.py
   ```

## API Key Setup

This application uses Google's Gemini API for text analysis. You will need to:

1. Create a Google Cloud account if you don't have one
2. Enable the Gemini API
3. Get an API key from the Google Cloud Console
4. Set the API key as an environment variable or provide it directly in the application

## Dependencies

- google-generativeai: For AI-powered text analysis
- gradio: For the web interface
- pydub & speechrecognition: For audio processing
- facenet-pytorch & fer: For facial emotion detection
- matplotlib & wordcloud: For data visualizations

## Usage

After running the app, you'll see a web interface with tabs for different journaling modes:

1. **Text Journal**: Type your thoughts and receive analysis
2. **Voice Journal**: Record or upload audio for transcription and analysis
3. **Photo Journal**: Upload images for emotion detection and analysis
4. **Review**: View past entries by date
5. **Weekly Summary**: Generate summaries of your journaling activity

## Data Storage

Journal entries are stored locally in the `journals` directory, organized by year and month. Images and audio files are saved in the `uploads` directory, while visualizations are stored in the `visualizations` directory.

## Privacy

All data is stored locally on your machine. No data is sent to external servers except for:
- Text sent to Google's Gemini API for analysis
- Audio sent to Google's Speech Recognition API for transcription
- Images processed by Google's Gemini Vision API (if enabled)

## License

This project is open source and available under the MIT License. 