#!/usr/bin/env python3

"""
Test script to verify backward-compatible imports work in practice.
This simulates the pattern that would be used in existing code.
"""

import asyncio
import os
import sys

# Test backward-compatible imports
from cursor_agent_tools.agent import create_agent
from cursor_agent_tools.agent import BaseAgent
from cursor_agent_tools.agent import run_agent_interactive
from cursor_agent_tools.agent.tools.file_tools import read_file, edit_file
from cursor_agent_tools.agent.tools.search_tools import grep_search 

print("Imports successful!")

async def test_create_agent():
    """Test that create_agent works through the compatibility layer."""
    try:
        # Create an agent with dummy API key and minimal configuration
        agent = create_agent(
            model="gpt-4o",
            api_key="sk-dummy-key-for-testing",
            temperature=0.0
        )
        print(f"Created agent: {type(agent).__name__}")
        
        # Test the agent has core attributes
        assert hasattr(agent, "available_tools")
        assert hasattr(agent, "api_key")
        
        print("Agent creation successful!")
        return True
    except Exception as e:
        print(f"Error creating agent: {e}")
        return False

async def test_file_tools():
    """Test that file tools work through the compatibility layer."""
    try:
        # Create a test file
        test_file_path = "test_backward_compat.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test file for backward compatibility.")
        
        # Read the file using the tools
        result = read_file(test_file_path, should_read_entire_file=True)
        
        # Verify the result
        assert "content" in result
        assert "This is a test file" in result["content"]
        
        # Clean up
        os.unlink(test_file_path)
        
        print("File tools work correctly!")
        return True
    except Exception as e:
        print(f"Error testing file tools: {e}")
        return False

async def main():
    """Run all tests."""
    print("\n=== Testing Agent Creation ===")
    await test_create_agent()
    
    print("\n=== Testing File Tools ===")
    await test_file_tools()
    
    print("\n=== All Tests Complete ===")

if __name__ == "__main__":
    asyncio.run(main()) 