#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import pytest
from dotenv import load_dotenv

from agent.claude_agent import ClaudeAgent

# Load environment variables from .env file in parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print("Warning: No .env file found. API keys need to be set manually.")
    # Don't exit here, we'll skip tests that need API keys


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), 
                   reason="ANTHROPIC_API_KEY environment variable not set")
@pytest.mark.anthropic
async def test_claude_chat() -> None:
    """Test the Claude agent's chat functionality."""
    try:
        # Initialize the Claude agent with the API key from the environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key is None:
            pytest.skip("ANTHROPIC_API_KEY environment variable not found.")
            
        print(f"Using API key: {api_key[:10]}...{api_key[-5:]}")

        # Initialize with the new model
        agent = ClaudeAgent(api_key=api_key, model="claude-3-7-sonnet-latest")
        print(f"Agent initialized successfully with model: {agent.model}")

        # Send a simple chat message
        print("\nSending a simple chat message...")
        response = await agent.chat("What is Python?")

        print(f"\nResponse from Claude: {response[:500]}...")
        assert response, "Response should not be empty"
        assert len(response) > 50, "Response should be reasonably long"
    except Exception as e:
        print(f"\nError during Claude chat: {type(e).__name__}: {str(e)}")
        pytest.fail(f"Test failed with exception: {str(e)}")


if __name__ == "__main__":
    # For direct script execution with a proper exit code
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not found.")
        sys.exit(1)
        
    success = asyncio.run(test_claude_chat())
    # The test function now returns None, so we need to check for exceptions instead
    print("\nClaude chat test completed successfully!")
