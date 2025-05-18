# Deploying to Hugging Face Spaces

This guide provides instructions for deploying the BujoNow application to Hugging Face Spaces.

## Prerequisites

- A Hugging Face account (sign up at https://huggingface.co/join)
- A Google AI API key for Gemini (get one at https://ai.google.dev/)

## Basic Deployment

1. Go to https://huggingface.co/spaces
2. Click on the "Create new Space" button
3. Enter a name for your Space (e.g., "bujonow")
4. Select "Gradio" as the SDK
5. Choose a license (if desired)
6. Click "Create Space"

## Setting Up Your Code

You can upload your code in several ways:

### Option 1: Using the Hugging Face Web Interface

1. On your Space page, click on "Files" tab
2. Use the "Add file" button to upload your files
3. Make sure to include all necessary files (all Python code and requirements.txt)

### Option 2: Using Git

1. Clone your Space repository
2. Add your application files
3. Commit and push the changes

## Setting Up API Key

The application requires a Google Gemini API key to function with full AI capabilities.

### Important: Model Compatibility

BujoNow now uses the `gemini-2.0-flash` model by default, which is available in the free tier of Google AI Studio. The application includes fallback logic to try other models if the default one isn't available.

### Setting the API Key as a Secret

1. Navigate to your Space's "Settings" tab
2. Find the "Repository Secrets" section
3. Click on "New Secret"
4. Set the name as `GOOGLE_API_KEY`
5. Enter your Gemini API key as the value
6. Click "Add new secret"

This sets up the API key securely, without exposing it in your code.

## HuggingFace README.md Setup

```
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

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
```

## Dependencies

Make sure your `requirements.txt` file includes these dependencies:

```
gradio>=5.0.0
google-generativeai>=0.4.0
numpy>=1.24.0
scikit-learn>=1.2.0
Pillow>=9.0.0
typing-extensions>=4.0.0
```

## Important Notes

1. The application will automatically check for the API key at startup
2. If no API key is found, it will fall back to simpler analysis methods
3. The application uses a progressive fallback system:
   - First tries the full analyzer with Gemini API
   - If that fails, uses the simplified analyzer with keyword-based analysis
   - If all else fails, uses an ultra-minimal analyzer

## Troubleshooting

If you encounter errors:

1. Check that your API key is correctly set in the repository secrets
2. Verify that your Space has the correct permissions to access the secret
3. Check the Space logs for any error messages
4. Make sure your dependencies are correctly installed

For more help, you can ask questions in the Hugging Face forums or consult the [Hugging Face Spaces documentation](https://huggingface.co/docs/hub/spaces-overview).

## Using Different Hardware

By default, Hugging Face Spaces run on CPU. If you need more computational power:

1. Go to your Space's settings
2. Under "Hardware", select an appropriate option (e.g., T4 GPU)
3. Note that using GPUs may incur charges unless you have free credits

## Additional Resources

- [Hugging Face Spaces documentation](https://huggingface.co/docs/hub/spaces)
- [Gradio documentation](https://www.gradio.app/docs/)
- [Google Generative AI documentation](https://ai.google.dev/docs) 