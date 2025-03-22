#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from agent.claude_agent import ClaudeAgent

# Load environment variables from .env file in parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print("Warning: No .env file found. API keys need to be set manually.")
    sys.exit(1)


async def test_claude_chat() -> bool:
    try:
        # Initialize the Claude agent with the API key from the environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key is None:
            print("Error: ANTHROPIC_API_KEY environment variable not found.")
            return False
            
        print(f"Using API key: {api_key[:10]}...{api_key[-5:]}")

        # Initialize with the new model
        agent = ClaudeAgent(api_key=api_key, model="claude-3-7-sonnet-latest")
        print(f"Agent initialized successfully with model: {agent.model}")

        # Send a simple chat message
        print("\nSending a simple chat message...")
        response = await agent.chat("What is Python?")

        print(f"\nResponse from Claude: {response[:500]}...")
        return True
    except Exception as e:
        print(f"\nError during Claude chat: {type(e).__name__}: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_claude_chat())
    if success:
        print("\nClaude chat test completed successfully!")
    else:
        print("\nClaude chat test failed!")
        sys.exit(1)
