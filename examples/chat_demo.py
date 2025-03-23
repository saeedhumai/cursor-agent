#!/usr/bin/env python3
"""
Chat Demo for Cursor Agent

This script demonstrates the agent's conversational capabilities,
allowing extended interaction with the agent through multiple queries.
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Import from cursor_agent package
from cursor_agent.agent import create_agent

# Ensure the examples directory is in the path
examples_dir = Path(__file__).parent
if str(examples_dir) not in sys.path:
    sys.path.append(str(examples_dir))

# Import utility functions
try:
    from utils import (
        Colors,
        clear_screen,
        print_error,
        print_separator,
        print_system_message,
        print_user_query,
        print_assistant_response,
        create_user_info
    )
except ImportError:
    # Add project root to path as fallback
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    try:
        from examples.utils import (
            Colors,
            clear_screen,
            print_error,
            print_separator,
            print_system_message,
            print_user_query,
            print_assistant_response,
            create_user_info
        )
    except ImportError:
        raise ImportError("Unable to import utility functions. Make sure utils.py is in the examples directory.")

# Load environment variables
load_dotenv()


async def main():
    """
    Main entry point for the chat demo.
    """
    # Load environment variables
    load_dotenv()

    # Check for API keys
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not anthropic_key and not openai_key:
        print_error("No API keys found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file.")
        sys.exit(1)
    
    # Select model based on available keys and user preference
    model = None
    models = []
    
    if anthropic_key:
        models.append("claude-3-5-sonnet-latest")
    if openai_key:
        models.append("gpt-4o")
    
    try:
        clear_screen()
        print_separator()
        print_system_message("CHAT DEMO")
        print_system_message("This demo showcases the agent's conversational capabilities.")
        print_separator()
        
        # Prompt for model if multiple are available
        if len(models) > 1:
            print_system_message("Available models:")
            for i, m in enumerate(models, 1):
                print_system_message(f"{i}. {m}")
            print_separator()
            
            selection = input(f"{Colors.BLUE}Select a model (1-{len(models)}): {Colors.RESET}")
            try:
                model_index = int(selection) - 1
                if model_index < 0 or model_index >= len(models):
                    raise ValueError
                model = models[model_index]
            except ValueError:
                print_error(f"Invalid selection. Using {models[0]} as default.")
                model = models[0]
        else:
            model = models[0]
        
        print_system_message(f"Using model: {model}")
        print_separator()
        
        # Initialize agent
        agent = create_agent(model=model)
        print_system_message("Agent initialized. Type 'exit' to quit the chat.")
        
        # Create user info for chat
        user_info = create_user_info()
        
        # Start conversation
        conversation_active = True
        while conversation_active:
            print_separator()
            query = input(f"{Colors.GREEN}Enter your query: {Colors.RESET}")
            
            if query.lower() in ["exit", "quit", "q"]:
                print_system_message("Exiting chat...")
                conversation_active = False
                continue
            
            try:
                print_system_message("Processing query...")
                print_user_query(query)
                
                # Get response
                response = await agent.chat(query, user_info)
                print_assistant_response(response)
                
            except Exception as e:
                print_error(f"Error getting response: {str(e)}")
                
        print_separator()
        print_system_message("CHAT DEMO COMPLETED")
        
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
