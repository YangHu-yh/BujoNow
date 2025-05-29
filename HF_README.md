# BujoNow - AI-Enhanced Bullet Journal

BujoNow is an AI-powered digital bullet journal companion that helps you track your thoughts, emotions, and personal growth.

## Important: API Key Setup

This application requires a Google Gemini API key to function with full AI capabilities.

### Setting Up Your API Key

1. **Get a Google API Key**:
   - Visit [Google AI Studio](https://ai.google.dev/) to obtain a Gemini API key

2. **Add it as a Secret**:
   - Go to your Space Settings
   - Find "Repository secrets" section
   - Add a new secret with name `GOOGLE_API_KEY` and your API key as the value

The app has multiple fallback levels:
- Full analyzer with Gemini API (requires API key)
- Simplified analyzer with keyword-based emotion detection (no API required)
- Minimal fallback analyzer (ultra-basic functionality)

### Model Information

BujoNow now uses `gemini-2.0-flash` by default, which should be available in the free tier of the Google AI Gemini API. The application includes fallback logic to try other models if the default one isn't available.

## Features

### Journal Entries
- **Text Journaling**: Record your thoughts and experiences
- **AI Analysis**: Get insights about your emotions and patterns
- **Weekly Summaries**: Review your emotional trends and progress

### Interactive Chat
- **Journal Conversations**: Chat with the AI about your journal entries
- **Ask for Insights**: Get personalized reflections on your entries

## Privacy & Data

- All journal entries are stored on your Hugging Face Space
- Your API key is stored securely as a Space secret
- The application uses your API key to communicate with Google's Gemini model

## Getting Started

1. Write a journal entry in the "Journal Entry" tab
2. Save the entry to store it
3. View your entries in the "View Entries" tab
4. Generate a weekly summary to see your progress
5. Chat with your journal in the "Chat with Journal" tab

## Feedback

If you encounter any issues or have suggestions, please open a discussion in this Space.

## Credits

BujoNow was developed as an open-source project to bring AI-powered journaling to everyone.

## Extending the App

This application is open source! You can find the code on [GitHub](https://github.com/yourusername/BujoNow) and modify it to meet your needs.

## Troubleshooting

If you encounter any issues, please check:
- That you've configured the GOOGLE_API_KEY secret correctly
- The application logs for any errors

If the main analyzer doesn't work, the app will automatically fall back to simplified modes.

---

title: BujoNow
emoji: 📔
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 3.50.0
app_file: app_huggingface.py
pinned: false
license: mit
hf_oauth: true
hf_oauth_expiration_minutes: 1440
hf_oauth_scopes:
  - openid
  - profile

