#!/usr/bin/env python3
"""
Chat Conversation Example for Cursor Agent

This script demonstrates the agent's conversational capabilities,
allowing extended interaction with the agent through multiple queries.
"""

import asyncio
import os
import sys
import traceback
from pathlib import Path
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
    print_user_query,
    print_assistant_response,
    print_info
)

# Load environment variables
load_dotenv()


async def main():
    """
    Main entry point for the chat conversation example.
    """
    try:
        # Setup: Get API keys and validate
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not openai_api_key and not anthropic_api_key:
            print_error("No API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables.")
            return
        
        # Choose which model to use based on available API keys
        if anthropic_api_key:
            agent = ClaudeAgent(
                api_key=anthropic_api_key,
                model="claude-3-5-sonnet-latest"
            )
            print_system_message("Using Anthropic Claude model")
        else:
            agent = OpenAIAgent(
                api_key=openai_api_key,
                model="gpt-4o"
            )
            print_system_message("Using OpenAI GPT-4 model")
        
        # Register all default tools with the agent
        agent.register_default_tools()
        
        # User information context - in a real app, this would be populated with actual user data
        user_info = {
            "os": platform.system(),
            "workspace_path": os.getcwd(),
            "open_files": [],
            "shell": os.environ.get("SHELL", "unknown"),
        }
        
        clear_screen()
        print_separator()
        print_system_message("CHAT CONVERSATION DEMO")
        print_system_message("Type 'exit' to quit the conversation")
        print_separator()
        
        conversation_history = []
        conversation_count = 0
        
        while True:
            conversation_count += 1
            
            # Get user input
            print(f"{Colors.CYAN}User: {Colors.RESET}", end="")
            user_input = input()
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit", "q"]:
                print_system_message("Exiting conversation...")
                break
            
            print("") # Add some spacing
            
            # Add user message to conversation history
            conversation_history.append({"role": "user", "content": user_input})
            
            try:
                # Get response from agent
                print_system_message("Agent is thinking...")
                response = await agent.chat(user_input, user_info)
                
                # Handle structured response format
                if isinstance(response, dict):
                    agent_message = response["message"]
                    tool_calls = response.get("tool_calls", [])
                    
                    # Print the agent's response
                    print(f"{Colors.GREEN}Agent: {Colors.RESET}")
                    print(agent_message)
                    
                    # If there were tool calls, print a summary
                    if tool_calls:
                        print_info(f"\nThe agent used {len(tool_calls)} tool(s) in this response.")
                        for i, call in enumerate(tool_calls, 1):
                            print_info(f"  {i}. {call['name']}")
                    
                    # Add agent response to conversation history
                    conversation_history.append({"role": "assistant", "content": agent_message})
                else:
                    # Backward compatibility with string responses
                    print(f"{Colors.GREEN}Agent: {Colors.RESET}")
                    print(response)
                    
                    # Add agent response to conversation history
                    conversation_history.append({"role": "assistant", "content": response})
                
                print("") # Add some spacing
                
            except Exception as e:
                print_error(f"An error occurred: {str(e)}")
                traceback.print_exc()
        
        print_separator()
        print_system_message("Chat conversation demo completed")
        print_system_message(f"Total exchanges: {conversation_count}")
            
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
