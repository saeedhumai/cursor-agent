#!/usr/bin/env python3
"""
Simple test script to verify that imports work as expected.
"""

# Test importing directly from cursor_agent.agent
print("Testing import from cursor_agent.agent...")
try:
    from cursor_agent.agent import create_agent, BaseAgent, ClaudeAgent, OpenAIAgent
    print("✅ Successfully imported create_agent from cursor_agent.agent")
    print("✅ Successfully imported BaseAgent from cursor_agent.agent")
    print("✅ Successfully imported ClaudeAgent from cursor_agent.agent")
    print("✅ Successfully imported OpenAIAgent from cursor_agent.agent")
    
    # Don't try to create agent - just test imports
    print("✅ All imports successful!")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")

# Test that example code from README.md would work (without executing)
print("\nTesting example code structure from README.md...")
print("Example from Quick Start section:")
print("""
import asyncio
from cursor_agent.agent import create_agent

async def main():
    # Create a Claude agent instance
    agent = create_agent(model='claude-3-5-sonnet-latest')
    
    # Chat with the agent
    response = await agent.chat("Create a Python function to calculate Fibonacci numbers")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
""")

# Verify that we can parse and define the example function (without executing it)
import asyncio
from cursor_agent.agent import create_agent

async def example_main():
    # This function is just defined to verify the syntax is valid - we don't actually run it
    print("Note: This function is not actually executed during testing")
    agent = create_agent(model='claude-3-5-sonnet-latest')
    # We don't actually call agent.chat to avoid API calls during testing
    
print("✅ Successfully defined example function with cursor_agent.agent imports")
print("\nDone!") 