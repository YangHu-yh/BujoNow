# BujoNow Tests

This directory contains tests for the BujoNow application.

## Running Tests

### Authentication Tests

The authentication test checks the functionality of the UserManager class and OAuth login flow.

```bash
python test_auth.py
```

To fully test the OAuth functionality, you'll need to set the following environment variables:

```bash
export OAUTH_CLIENT_ID="your_client_id"
export OAUTH_CLIENT_SECRET="your_client_secret"
export OPENID_PROVIDER_URL="https://huggingface.co"
```

## Understanding Test Failures

If you see `gr.open_url()` errors when running the application, run the following:

```bash
gradio --version
```

If your Gradio version is 3.x, you may need to update to Gradio 4.x or later:

```bash
pip install gradio --upgrade
```

## Troubleshooting Authentication

If you're experiencing authentication issues:

1. Check the log output for detailed error messages
2. Verify that your OAuth credentials are set correctly
3. Ensure your redirect URI is properly configured
4. Try clearing your browser cookies and cache

When running in a Hugging Face Space, the Space platform automatically provides the OAuth credentials based on the settings in your README.md metadata. 