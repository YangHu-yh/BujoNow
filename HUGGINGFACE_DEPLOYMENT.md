# Deploying BujoNow on Hugging Face Spaces

This document provides instructions for deploying BujoNow on Hugging Face Spaces with user authentication enabled.

## Prerequisites

1. A Hugging Face account
2. Basic understanding of Git
3. (Optional) A Google Gemini API key for enhanced AI features

## Step 1: Fork or Clone the Repository

First, clone the BujoNow repository to your local machine or fork it on GitHub.

```bash
git clone https://github.com/yourname/BujoNow.git
cd BujoNow
```

## Step 2: Configure OAuth in README.md

The main README.md file already includes the OAuth configuration in its metadata section:

```yaml
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
hf_oauth_scopes:
  - openid
  - profile
---
```

This configuration:
- Enables OAuth authentication (`hf_oauth: true`)
- Sets token expiration to 24 hours (1440 minutes)
- Requests the openid and profile scopes, which are required for basic user info

## Step 3: Create a New Space on Hugging Face

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Select "Gradio" as the SDK
4. Give your Space a name (e.g., "bujonow")
5. Choose a license (e.g., MIT)
6. Select "Public" or "Private" visibility
7. Click "Create Space"

## Step 4: Push Your Code to the Space

Add the Hugging Face Space as a remote and push your code:

```bash
git remote add space https://huggingface.co/spaces/yourname/bujonow
git push space main
```

Or upload the files directly using the Hugging Face web interface.

## Step 5: Add API Key Secret (Optional)

If you want to use the full AI features with Google Gemini:

1. Get a Google Gemini API key from [Google AI Studio](https://ai.google.dev/)
2. Go to your Space settings
3. Find the "Repository secrets" section
4. Add a new secret with name `GOOGLE_API_KEY` and your API key as the value

## Step 6: Wait for the Build

The Space will automatically build and deploy your app. This may take a few minutes.

Once deployed, Hugging Face will automatically provide OAuth credentials for your Space based on the configuration in the README.md metadata.

## Step 7: Test the Authentication

1. Open your Space
2. Click "Sign in with Hugging Face"
3. Authorize the application
4. You should be redirected back to your app and logged in
5. Create a journal entry to test that everything is working

## Troubleshooting

If you encounter any issues with authentication:

1. Check the Space logs for error messages
2. Verify that the OAuth configuration in README.md is correct
3. Make sure your Space is properly built and running
4. Try clearing your browser cookies and cache

## How the Authentication Works

When your Space is deployed:

1. Hugging Face reads the OAuth configuration from your README.md
2. It creates OAuth credentials for your Space
3. It sets environment variables in your Space with the credentials:
   - `OAUTH_CLIENT_ID`
   - `OAUTH_CLIENT_SECRET`
   - `OAUTH_SCOPES`
   - `OPENID_PROVIDER_URL`
4. Your app uses these credentials to implement the OAuth flow

The user flow:

1. User clicks "Sign in with Hugging Face"
2. They're redirected to Hugging Face to authorize your app
3. After authorization, they're redirected back to your app
4. Your app verifies the authorization and creates a user session
5. The user can now access their personal journal data

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