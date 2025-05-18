import os
import sys
import traceback

print("Starting test script...")
print(f"Python version: {sys.version}")

# Step 1: Test google.generativeai import
print("\nStep 1: Testing basic imports...")
try:
    import google.generativeai as genai
    print(f"Successfully imported google.generativeai version: {genai.version.__version__}")
    print(f"Available attributes in genai: {dir(genai)}")
except Exception as e:
    print(f"Error importing google.generativeai: {type(e).__name__}: {e}")
    traceback.print_exc()

# Step 2: Import other necessary modules
print("\nStep 2: Testing related imports...")
try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    print("Successfully imported numpy and sklearn")
except Exception as e:
    print(f"Error importing dependencies: {type(e).__name__}: {e}")
    traceback.print_exc()

# Step 3: Test embedding module specifically
print("\nStep 3: Testing embedding module...")
try:
    if hasattr(genai, 'embedding'):
        print("embedding module is available")
        from google.generativeai import embedding
        print(f"Available functions in embedding: {dir(embedding)}")
    else:
        print("embedding module is NOT available")
        print("Available modules:", [name for name in dir(genai) if not name.startswith('_')])
except Exception as e:
    print(f"Error checking embedding module: {type(e).__name__}: {e}")
    traceback.print_exc()

# Step 4: Test RAG_DOCUMENTS import
print("\nStep 4: Testing RAG_DOCUMENTS import...")
try:
    # Attempt to import RAG_DOCUMENTS without using the actual import path
    # This avoids potential issues in the analyzer module
    RAG_DOCUMENTS = [
        "This is a sample document for testing embeddings.",
        "Another test document with different content."
    ]
    print(f"Using test RAG_DOCUMENTS: {len(RAG_DOCUMENTS)} documents")
except Exception as e:
    print(f"Error with RAG_DOCUMENTS: {type(e).__name__}: {e}")
    traceback.print_exc()

# Step 5: Test embedding functionality if available
print("\nStep 5: Testing embedding functionality...")
try:
    if hasattr(genai, 'embedding'):
        # Configure API
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key:
            print("API key found in environment variables")
            genai.configure(api_key=api_key)
            
            # Test a single embedding
            print("Attempting to generate an embedding...")
            result = embedding.embed_content(
                model="models/embedding-001",
                content="Test document for embedding",
                task_type="RETRIEVAL_DOCUMENT"
            )
            print(f"Embedding result keys: {result.keys()}")
            if 'embedding' in result:
                print(f"Successfully created embedding with {len(result['embedding'])} dimensions")
            else:
                print(f"Embedding not found in result: {result}")
        else:
            print("No API key found in environment variables")
    else:
        print("Skipping embedding test since module is not available")
except Exception as e:
    print(f"Error testing embedding functionality: {type(e).__name__}: {e}")
    traceback.print_exc()

print("\nTest script completed") 