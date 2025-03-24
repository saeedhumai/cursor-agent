#!/usr/bin/env python3
"""
Example showing how to use the cursor agent for code search/exploration.
"""

import os
import sys
import traceback
import asyncio
import platform
from pathlib import Path

from dotenv import load_dotenv

# Add the parent directory to the path so we can import the agent package
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from agent.claude_agent import ClaudeAgent
from agent.openai_agent import OpenAIAgent
from agent.tools.search_tools import codebase_search
from agent.tools.file_tools import read_file
from examples.utils import (
    Colors, print_error, print_system_message, 
    print_user_query, print_assistant_response, 
    print_info, print_separator
)

# Load environment variables from .env file
load_dotenv()

async def run_search_example():
    """Run the code search example."""
    try:
        print_system_message("Initializing agent...")
        
        # Get API keys
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        
        # Choose model based on available API keys
        if anthropic_key:
            agent = ClaudeAgent(
                api_key=anthropic_key,
                model="claude-3-5-sonnet-latest"
            )
            print_system_message("Using Claude model")
        elif openai_key:
            agent = OpenAIAgent(
                api_key=openai_key,
                model="gpt-4o"
            )
            print_system_message("Using GPT-4o model")
        else:
            print_error("No API keys found. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables.")
            return
        
        # Register the search tools with the agent
        agent.register_tool(codebase_search)
        agent.register_tool(read_file)
        
        # Create a basic user info context
        user_info = {
            "os": platform.system(),
            "workspace_path": os.getcwd(),
        }
        
        # Demo query for code search
        query = "How is the agent.chat method implemented in this codebase? Show the relevant code."
        
        print_system_message("Sending query to search the codebase...")
        print_user_query(query)
        
        # Get the response from the agent
        response = await agent.chat(query, user_info)
        
        # Process the structured response
        if isinstance(response, dict):
            # Print the agent's message
            print_assistant_response(response["message"])
            
            # Show tool usage if present
            if response.get("tool_calls"):
                print_info(f"\nAgent used {len(response['tool_calls'])} tool calls:")
                for i, call in enumerate(response["tool_calls"], 1):
                    print_info(f"\n{i}. Tool: {call['name']}")
                    if call["name"] == "codebase_search":
                        print_info(f"   Search query: {call['parameters'].get('query', 'N/A')}")
                    elif call["name"] == "read_file" and "target_file" in call["parameters"]:
                        print_info(f"   Read file: {call['parameters']['target_file']}")
            else:
                print_info("\nAgent completed the task without using any tools.")
        else:
            # Backward compatibility
            print_assistant_response(response)
            
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        traceback.print_exc()

async def main():
    """Main entry point for the code search example."""
    
    try:
        print_separator()
        print_system_message("CODE SEARCH EXAMPLE")
        print_separator()
        
        # Run the code search example
        await run_search_example()
        
        print_separator()
        print_system_message("CODE SEARCH EXAMPLE COMPLETED")
        
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        traceback.print_exc()
        
if __name__ == "__main__":
    asyncio.run(main())
