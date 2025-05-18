---
title: BujoNow
emoji: ⚡
colorFrom: green
colorTo: green
sdk: gradio
sdk_version: 5.29.0
app_file: app.py
pinned: false
license: mit
short_description: A Bullet Journal Companion Powered by Gemini
---

# BujoNow - Bullet Journal Companion

BujoNow is a digital bullet journal application with AI-powered features for journal analysis, emotion tracking, and personal growth insights.

## Features

- Text-based journaling with emotion analysis
- Weekly summaries and insights
- Graceful degradation when optional dependencies are unavailable
- Multiple fallback mechanisms to ensure the app works in various environments

## Running the Application

To run the application with full features:

```bash
python app.py
```

The app will automatically detect available dependencies and use appropriate fallbacks if some are missing.

## Dependencies

- Required:
  - gradio
  - python 3.7+
  
- Optional (for enhanced features):
  - google-generativeai (for AI analysis)
  - facenet-pytorch (for face detection)
  - fer (for emotion recognition)

## Project Structure

- `app.py`: Main entry point with fallback mechanisms
- `src/`: Core application code
  - `journal_manager.py`: Handles journal entry creation and storage
  - `analyzer.py`: Provides AI-powered analysis (requires google-generativeai)
  - `analyzer_simplified.py`: Simplified analysis without API dependencies
  - `interface.py`: Creates the Gradio web interface
  - `processor/`: Image and audio processing utilities

## Fallback Mechanisms

BujoNow implements several fallback mechanisms:

1. If the full analyzer with Google AI isn't available, it uses a simplified analyzer
2. If the web interface fails, it provides a command-line interface
3. If components fail to import, it gracefully degrades functionality

This ensures that users can still journal even if some dependencies are missing or API access is unavailable.

## License

MIT License

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference