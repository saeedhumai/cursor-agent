#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path

import pytest
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
    # Don't exit here, we'll skip tests that need API keys

# Only print API key info if it exists
if api_key:
    print(f"API key found: {api_key[:10]}...{api_key[-5:]}")


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"),
                  reason="ANTHROPIC_API_KEY environment variable not set")
@pytest.mark.anthropic
async def test_anthropic_direct():
    try:
        # Import the Anthropic client
        from anthropic import AsyncAnthropic

        # Initialize the client with the API key
        client = AsyncAnthropic(api_key=api_key)

        # Make a simple API call
        print("\nMaking test API call to Anthropic...")
        response = await client.messages.create(
            model="claude-3-7-sonnet-latest",
            system="You are a helpful AI assistant.",
            messages=[{"role": "user", "content": "What is Python?"}],
            max_tokens=300,
        )

        print(f"\nResponse from Anthropic: {response.content}")
        return True
    except Exception as e:
        print(f"\nError during Anthropic API call: {type(e).__name__}: {str(e)}")
        return False


if __name__ == "__main__":
    # For direct script execution, we still want to exit with error code
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    success = asyncio.run(test_anthropic_direct())
    if success:
        print("\nDirect Anthropic API test completed successfully!")
    else:
        print("\nDirect Anthropic API test failed!")
        sys.exit(1)
