#!/usr/bin/env python3
"""
Basic usage example for Cursor Agent

This example shows how to create agents with both Claude and OpenAI
and how to interact with them for simple coding tasks.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Import the agent factory
try:
    from agent.factory import create_agent
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from agent.factory import create_agent

async def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if API keys are set
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not anthropic_key and not openai_key:
        print("Error: No API keys found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY.")
        return
    
    # Determine which agent(s) to create based on available API keys
    providers = []
    if anthropic_key:
        providers.append("claude")
    if openai_key:
        providers.append("openai")
    
    for provider in providers:
        print(f"\n{'='*20}\nUsing {provider.upper()} provider\n{'='*20}\n")
        
        # Create an agent with the current provider
        agent = create_agent(provider=provider)
        
        # Sample user query - asking for a simple code snippet
        user_query = "Create a Python function that checks if a string is a palindrome"
        print(f"User Query: {user_query}\n")
        
        # Get response from the agent
        try:
            response = await agent.chat(user_query)
            print(f"Agent Response:\n{response}\n")
        except Exception as e:
            print(f"Error with {provider} agent: {str(e)}")
        
        # Sample query with code modification
        if Path("example_code.py").exists():
            Path("example_code.py").unlink()
            
        # Create a simple file to modify
        with open("example_code.py", "w") as f:
            f.write("""def calculate_sum(numbers):
    # TODO: Implement this function to calculate the sum of a list of numbers
    pass
""")
        
        # Context information for the agent
        user_info = {
            "open_files": ["example_code.py"],
            "cursor_position": {"file": "example_code.py", "line": 2},
            "workspace_path": str(Path.cwd())
        }
        
        user_query = "Implement the calculate_sum function to add up all numbers in the list"
        print(f"User Query: {user_query}\n")
        
        # Get response from the agent with context
        try:
            response = await agent.chat(user_query, user_info=user_info)
            print(f"Agent Response:\n{response}\n")
            
            # Show the modified file
            if Path("example_code.py").exists():
                print("Modified file contents:")
                with open("example_code.py", "r") as f:
                    print(f.read())
        except Exception as e:
            print(f"Error with {provider} agent: {str(e)}")
    
    # Clean up example file
    if Path("example_code.py").exists():
        Path("example_code.py").unlink()

if __name__ == "__main__":
    asyncio.run(main()) 