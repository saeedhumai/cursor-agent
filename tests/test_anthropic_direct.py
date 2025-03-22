#!/usr/bin/env python3
import os
import sys
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in parent directory
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print("Warning: No .env file found. API keys need to be set manually.")
    sys.exit(1)

# Get the Anthropic API key
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY environment variable not set.")
    sys.exit(1)

print(f"API key found: {api_key[:10]}...{api_key[-5:]}")

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
            messages=[
                {"role": "user", "content": "What is Python?"}
            ],
            max_tokens=300
        )
        
        print(f"\nResponse from Anthropic: {response.content}")
        return True
    except Exception as e:
        print(f"\nError during Anthropic API call: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_anthropic_direct())
    if success:
        print("\nDirect Anthropic API test completed successfully!")
    else:
        print("\nDirect Anthropic API test failed!")
        sys.exit(1) 