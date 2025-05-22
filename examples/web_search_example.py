#!/usr/bin/env python3
"""
Example showing how to use the cursor agent for web search.

This script demonstrates how to use the web search tool to search
for up-to-date information on the internet using Google Custom Search API.
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

from cursor_agent_tools import ClaudeAgent
from cursor_agent_tools import OpenAIAgent
from examples.utils import (
    Colors, print_error, print_system_message, 
    print_user_query, print_assistant_response, 
    print_info, print_separator
)

# Load environment variables from .env file
load_dotenv()

async def run_web_search_example():
    """Run the web search example."""
    try:
        print_system_message("Initializing agent...")
        
        # Get API keys
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        google_search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
        
        # Check if Google API keys are available
        if not google_api_key or not google_search_engine_id:
            print_error("Google API key or Search Engine ID not found. Please set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables.")
            print_system_message("To use the web search tool, you need Google API credentials.")
            print_system_message("1. Create a Google Cloud project and enable Custom Search API")
            print_system_message("2. Create API key: https://console.cloud.google.com/apis/credentials")
            print_system_message("3. Create a Custom Search Engine: https://programmablesearchengine.google.com/")
            print_system_message("4. Add these to your .env file:")
            print_system_message("   GOOGLE_API_KEY=your_api_key")
            print_system_message("   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id")
            return
        
        # Variable to track if we should continue with example
        can_continue = True
            
        # Choose model based on available API keys
        if openai_key:
            try:
                agent = OpenAIAgent(
                    api_key=openai_key,
                    model="gpt-4o"
                )
                print_system_message("Using GPT-4o model")
            except Exception as e:
                print_error(f"Error initializing OpenAI model: {str(e)}")
                if anthropic_key:
                    print_system_message("Falling back to Claude model...")
                    agent = ClaudeAgent(
                        api_key=anthropic_key,
                        model="claude-3-5-sonnet-latest"
                    )
                    print_system_message("Using Claude model")
                else:
                    can_continue = False
                    print_error("No valid API keys available. Please check your API keys and credit balance.")
                    return
        elif anthropic_key:
            try:
                agent = ClaudeAgent(
                    api_key=anthropic_key,
                    model="claude-3-5-sonnet-latest"
                )
                print_system_message("Using Claude model")
            except Exception as e:
                print_error(f"Error initializing Claude model: {str(e)}")
                can_continue = False
                print_error("No valid API keys available. Please check your API keys and credit balance.")
                return
        else:
            print_error("No API keys found. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables.")
            return
        
        if not can_continue:
            return
        
        # Register only the web_search tool
        agent.register_default_tools()
        
        print_system_message("Registered default tools, including web_search")
        
        # Create a basic user info context
        user_info = {
            "os": platform.system(),
            "workspace_path": os.getcwd(),
        }
        
        # Demo query for web search
        query = "What are the latest developments in quantum computing in 2025?"
        
        print_system_message("Sending web search query...")
        print_user_query(query)
        
        # Get the response from the agent
        try:
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
                        if call["name"] == "web_search":
                            print_info(f"   Search term: {call['parameters'].get('search_term', 'N/A')}")
                            if call.get('result') and isinstance(call.get('result'), dict) and call['result'].get('results'):
                                result_count = call['result'].get('total_results', 0)
                                print_info(f"   Found {result_count} results")
                else:
                    print_info("\nAgent completed the task without using any tools.")
            else:
                # Backward compatibility
                print_assistant_response(response)
        except Exception as e:
            print_error(f"API Error: {str(e)}")
            print_system_message("Failed to get response from the API. Check your API keys and credit balance.")
            return  # Exit early if we can't get a response
            
        # Try another query with force=True
        print_separator()
        force_query = "Show me information about classical computing in 2025, force web search."
        
        print_system_message("Sending another query with force=True...")
        print_user_query(force_query)
        
        # Get the response for the second query
        try:
            force_response = await agent.chat(force_query, user_info)
            
            # Process the structured response
            if isinstance(force_response, dict):
                # Print the agent's message
                print_assistant_response(force_response["message"])
                
                # Show tool usage if present
                if force_response.get("tool_calls"):
                    print_info(f"\nAgent used {len(force_response['tool_calls'])} tool calls:")
                    for i, call in enumerate(force_response["tool_calls"], 1):
                        print_info(f"\n{i}. Tool: {call['name']}")
                        if call["name"] == "web_search":
                            print_info(f"   Search term: {call['parameters'].get('search_term', 'N/A')}")
                            print_info(f"   Force: {call['parameters'].get('force', False)}")
                            if call.get('result') and isinstance(call.get('result'), dict) and call['result'].get('results'):
                                result_count = call['result'].get('total_results', 0)
                                print_info(f"   Found {result_count} results")
                else:
                    print_info("\nAgent completed the task without using any tools.")
            else:
                # Backward compatibility
                print_assistant_response(force_response)
        except Exception as e:
            print_error(f"API Error: {str(e)}")
            print_system_message("Failed to get response from the API. Check your API keys and credit balance.")
            
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        traceback.print_exc()

async def main():
    """Main entry point for the web search example."""
    
    try:
        print_separator()
        print_system_message("WEB SEARCH EXAMPLE")
        print_separator()
        
        # Run the web search example
        await run_web_search_example()
        
        print_separator()
        print_system_message("WEB SEARCH EXAMPLE COMPLETED")
        
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        traceback.print_exc()
        
if __name__ == "__main__":
    asyncio.run(main()) 