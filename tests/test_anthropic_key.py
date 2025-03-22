#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print("Warning: No .env file found. API keys need to be set manually.")
    # Don't exit here, we'll skip tests that need API keys

# Get the Anthropic API key
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY environment variable not set.")
    pytest.skip("ANTHROPIC_API_KEY environment variable not set", allow_module_level=True)

print(f"API key found: {api_key[:10]}...{api_key[-5:]}")
print(f"API key length: {len(api_key)}")
print(f"API key format correct: {api_key.startswith('sk-ant-')}")

# List of models to try
models_to_try = [
    "claude-3-7-sonnet-latest",
    "claude-3-5-sonnet-latest",
]

# Use a direct API call with requests to test the API key
print("\nTesting API key with direct API calls to Anthropic for different models...")
headers = {
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

# Check if the API key is valid by testing it against different models
for model in models_to_try:
    print(f"\nTrying model: {model}")
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={
                "model": model,
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Say hello in one short sentence."}],
            },
            timeout=30,
        )

        print(f"API response status code: {response.status_code}")
        print(f"API response: {response.text[:200]}...")

        if response.status_code == 200:
            print(f"SUCCESS! Model {model} works with this API key.")
            break
        elif response.status_code == 401:
            print("API key is invalid or unauthorized!")
            break
        elif response.status_code == 404:
            print(f"Model {model} not found. Trying next model...")
        else:
            print(f"Unexpected response code: {response.status_code}")

    except Exception as e:
        print(f"Error during API test: {type(e).__name__}: {str(e)}")

print("\nAPI key test completed!")
