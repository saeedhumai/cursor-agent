#!/usr/bin/env python3
"""
Test script that actually uses the chat feature to demonstrate full functionality.
"""
import asyncio
import os
from dotenv import load_dotenv
from cursor_agent.agent import create_agent

# Load environment variables from .env file
load_dotenv()

async def test_chat_feature():
    """
    Create an agent and test the chat functionality with a simple question.
    Uses a very minimal prompt to reduce token usage and API costs.
    """
    print("Creating agent...")
    # Use OpenAI model by default to avoid Anthropic version issues
    model = os.getenv("TEST_MODEL", "gpt-4o")
    agent = create_agent(model=model)
    
    print(f"Using model: {model}")
    print("Sending chat request...")
    
    # Very minimal prompt to minimize token usage
    prompt = "Respond with a single sentence about Python."
    
    response = await agent.chat(prompt)
    
    print("\nResponse from agent:")
    print("-" * 40)
    print(response)
    print("-" * 40)
    
    # Simple validation
    if response and len(response) > 0:
        print("✅ Successfully received response from chat API")
    else:
        print("❌ Failed to get meaningful response")
    
    return response

if __name__ == "__main__":
    print("Running chat feature test with cursor_agent.agent...")
    
    # Check if API keys are set
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        print("⚠️ No OpenAI API key found in environment variables.")
        print("This test now uses OpenAI's GPT-4o model by default.")
        print("Set OPENAI_API_KEY to run this test.")
        print("You can also set TEST_MODEL to specify which model to use.")
        exit(1)
    
    print("API keys found, proceeding with test...")
    asyncio.run(test_chat_feature()) 