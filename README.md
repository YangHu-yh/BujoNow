---
title: BujoNow
emoji: 📔
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.29.0
app_file: app.py
pinned: false
license: mit
short_description: A Bullet Journal Companion Powered by Gemini
hf_oauth: true
hf_oauth_expiration_minutes: 1440
---

# BujoNow - AI-Enhanced Bullet Journal

BujoNow is an AI-powered digital bullet journal companion that helps you track your thoughts, emotions, and personal growth.

## Features

- **Secure Authentication**: Sign in with your Hugging Face account to access your private journal
- **Text Journaling**: Record your thoughts and experiences
- **AI Analysis**: Get insights about your emotions and patterns (requires API key)
- **Weekly Summaries**: Review your emotional trends and progress
- **User Privacy**: All journal entries are private to your account

## Getting Started

1. Sign in with your Hugging Face account
2. Write a journal entry in the "Journal Entry" tab
3. Save the entry to store it in your personal journal
4. View your entries in the "View Entries" tab
5. Generate a weekly summary to see your progress
6. Chat with your journal in the "Chat with Journal" tab

## Authentication

BujoNow uses Hugging Face OAuth for authentication. This ensures:
- Each user has access only to their own journal entries
- Your data is securely stored in your personal user space
- Simple login with your existing Hugging Face account

## Setup

### For Users
Simply click "Sign in with Hugging Face" to authorize the app and get started.

### For Developers
To set up authentication in your own fork:
1. Add the required OAuth configuration to the README.md metadata
2. Deploy to Hugging Face Spaces
3. The Spaces platform will automatically provision OAuth credentials

#### API Key (Optional)
For enhanced AI features, add a Google Gemini API key as a Space secret:
- Get a key from [Google AI Studio](https://ai.google.dev/)
- Add it as a secret with name `GOOGLE_API_KEY`

## Troubleshooting

### Authentication Issues
If you encounter authentication problems:
1. Check the application logs for specific error messages
2. Ensure your Hugging Face Space has the correct OAuth configuration in README.md
3. Try clearing your browser cookies and cache
4. For local development, set the required environment variables:
   ```
   export OAUTH_CLIENT_ID="your_client_id"
   export OAUTH_CLIENT_SECRET="your_client_secret" 
   export OPENID_PROVIDER_URL="https://huggingface.co"
   ```

### Gradio Version Compatibility
This application requires Gradio 4.x or later. If you see errors related to missing Gradio functions:
```
pip install gradio --upgrade
```

For more detailed troubleshooting, check the [test/README.md](test/README.md) file.

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference