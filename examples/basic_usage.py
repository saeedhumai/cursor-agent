#!/usr/bin/env python3
"""
Basic Usage Demo for Cursor Agent

This script demonstrates the basic usage of the cursor agent with different models.
It shows how to create agents and get responses to simple coding queries.
"""

import asyncio
import os
import sys
import traceback
from pathlib import Path
import json
import platform

from dotenv import load_dotenv

# Add the parent directory to the path so we can import the agent package
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from agent.claude_agent import ClaudeAgent
from agent.openai_agent import OpenAIAgent
from examples.utils import (
    Colors,
    clear_screen,
    print_error,
    print_separator,
    print_system_message,
    print_assistant_response,
    print_info
)

# Load environment variables
load_dotenv()


async def run_claude_example():
    """Run an example query with Claude agent."""
    print_separator()
    print_system_message("CLAUDE AGENT EXAMPLE")

    # Check for Anthropic API key
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print_error("No ANTHROPIC_API_KEY found in environment. Skipping Claude example.")
        print_system_message("To use Claude, add your Anthropic API key to the .env file.")
        return

    # Initialize Claude agent
    print_system_message("Initializing Claude agent...")
    try:
        # Create a temporary directory for the Claude demo
        temp_dir = Path("demo_files/claude_example")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save current directory
        original_dir = os.getcwd()
        
        # Change to the temporary directory
        os.chdir(temp_dir)
        
        # Create user_info dictionary to help with context
        user_info = {
            "workspace_path": os.getcwd(),
            "os": platform.system(),
        }
        
        agent = ClaudeAgent(api_key=anthropic_key, model="claude-3-5-sonnet-latest")
        print_system_message("Claude agent initialized successfully!")
        
        # Example query
        query = "Write a Python function to calculate the factorial of a number using recursion."
        print_system_message(f"Asking Claude: {query}")

        # Get response from the agent
        response = await agent.chat(query, user_info)
        
        # Handle structured response
        if isinstance(response, dict):
            print_assistant_response(response["message"])
            
            # Show tool usage if present
            if response.get("tool_calls"):
                print_info(f"\nAgent used {len(response['tool_calls'])} tool calls:")
                for i, call in enumerate(response['tool_calls'], 1):
                    print_info(f"\n{i}. Tool: {call['name']}")
        else:
            # Backward compatibility
            print_assistant_response(response)
        
        # Change back to original directory
        os.chdir(original_dir)
        
        print_system_message("Claude example completed!")

    except Exception as e:
        print_error(f"Error with Claude agent: {str(e)}")
        traceback.print_exc()
        
        # Ensure we change back to the original directory if an exception occurs
        if 'original_dir' in locals():
            os.chdir(original_dir)


async def run_openai_example():
    """Run an example query with OpenAI agent."""
    print_separator()
    print_system_message("OPENAI AGENT EXAMPLE")

    # Check for OpenAI API key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        print_error("No OPENAI_API_KEY found in environment. Skipping OpenAI example.")
        print_system_message("To use OpenAI, add your OpenAI API key to the .env file.")
        return

    # Initialize OpenAI agent
    print_system_message("Initializing OpenAI agent...")
    try:
        # Create user_info dictionary to help with context
        user_info = {
            "workspace_path": os.getcwd(),
            "os": platform.system(),
        }
        
        agent = OpenAIAgent(api_key=openai_key, model="gpt-4o")
        print_system_message("OpenAI agent initialized successfully!")

        # Example query
        query = "Write a Python function to generate the Fibonacci sequence up to n terms."
        print_system_message(f"Asking OpenAI: {query}")

        # Get response with user_info context
        response = await agent.chat(query, user_info)
        
        # Handle structured response
        if isinstance(response, dict):
            print_assistant_response(response["message"])
            
            # Show tool usage if present
            if response.get("tool_calls"):
                print_info(f"\nAgent used {len(response['tool_calls'])} tool calls:")
                for i, call in enumerate(response['tool_calls'], 1):
                    print_info(f"\n{i}. Tool: {call['name']}")
        else:
            # Backward compatibility
            print_assistant_response(response)

    except Exception as e:
        print_error(f"Error with OpenAI agent: {str(e)}")
        traceback.print_exc()


async def main():
    """
    Main function to demonstrate basic agent usage.
    """
    try:
        clear_screen()
        print_separator()
        print_system_message("CURSOR AGENT BASIC USAGE DEMO")
        print_separator()
    
        # Get API keys from environment variables
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    
        if not openai_api_key and not anthropic_api_key:
            print_error("No API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables.")
            return
    
        # Choose model based on available API keys
        if anthropic_api_key:
            print_system_message("Using Anthropic Claude model (ANTHROPIC_API_KEY found)")
            agent = ClaudeAgent(api_key=anthropic_api_key, model="claude-3-5-sonnet-latest")
        elif openai_api_key:
            print_system_message("Using OpenAI GPT-4 model (OPENAI_API_KEY found)")
            agent = OpenAIAgent(api_key=openai_api_key, model="gpt-4o")
        else:
            print_error("No valid API keys found.")
            return
    
        # Register default tools with the agent
        agent.register_default_tools()
    
        # Define user query
        query = "Please explain what Python decorators are and provide a simple example"
    
        # Prepare user info context
        user_info = {
            "os": platform.system(),
            "workspace_path": os.getcwd(),
            "open_files": [],
        }
    
        print_system_message(f"Sending query to agent: {query}")
    
        try:
            # Get response from agent
            agent_response = await agent.chat(query, user_info)
            
            # Handle structured response
            if isinstance(agent_response, dict):
                print_assistant_response(agent_response["message"])
                
                # Show tool usage if present
                if agent_response.get("tool_calls"):
                    print_info(f"\nAgent used {len(agent_response['tool_calls'])} tool calls:")
                    for i, call in enumerate(agent_response['tool_calls'], 1):
                        print_info(f"\n{i}. Tool: {call['name']}")
                        print_info(f"   Parameters: {json.dumps(call['parameters'], indent=2)}")
                        if call.get('result'):
                            print_info(f"   Result: {call['result']}")
            else:
                # For backward compatibility
                print_assistant_response(agent_response)
    
        except Exception as e:
            print_error(f"Error: {str(e)}")
            traceback.print_exc()
            
        # Run individual examples
        if anthropic_api_key:
            await run_claude_example()
            
        if openai_api_key:
            await run_openai_example()
            
        print_separator()
        print_system_message("BASIC USAGE DEMO COMPLETED")
        
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
