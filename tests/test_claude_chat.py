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
    """Test a basic chat with Claude."""
    print("\nRunning Claude chat test...")
    try:
        # Create the agent
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY environment variable not found or empty")
        agent = ClaudeAgent(api_key=api_key, model="claude-3-5-sonnet-latest")
        assert agent is not None, "Failed to create Claude agent"
        print(f"Successfully created Claude agent with model {agent.model}")

        # Send a simple chat message
        print("\nSending a simple chat message...")
        response = await agent.chat("What is Python?")

        # Check if the response is a structured AgentResponse or a string
        if isinstance(response, dict):
            # Check the response structure
            assert "message" in response, "Structured response should have a 'message' field"
            assert "tool_calls" in response, "Structured response should have a 'tool_calls' field"
            # Extract the message for length validation
            message = response["message"]
            print(f"\nResponse from Claude: {message[:500]}...")
            assert message, "Message should not be empty"
            assert len(message) > 50, "Message should be reasonably long"
        else:
            # Backward compatibility with string responses
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
