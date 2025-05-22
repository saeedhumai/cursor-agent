#!/usr/bin/env python3
"""
Ollama Chat Example for Cursor Agent

This script demonstrates basic chat functionality with the Cursor Agent
using locally hosted Ollama models.
"""

import asyncio
import os
import sys
import traceback
from pathlib import Path

# Add the parent directory to the path so we can import the agent package
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from cursor_agent_tools import create_agent
from examples.utils import (
    Colors,
    clear_screen,
    print_error,
    print_separator,
    print_system_message,
    print_assistant_response,
    print_info
)


async def run_ollama_basic_chat():
    """Demonstrates basic chat functionality with an Ollama model."""
    print_separator()
    print_system_message("OLLAMA BASIC CHAT EXAMPLE")
    
    try:
        # Detect available Ollama models
        import ollama
        try:
            print_system_message("Checking for available Ollama models...")
            
            models_response = ollama.list()
            available_models = []
            
            for model_info in models_response.models:
                model_name = model_info.model
                if ":" in model_name:
                    # Remove tag (e.g., ":latest") if present
                    model_name = model_name.split(":")[0]
                available_models.append(model_name)
            
            if not available_models:
                print_error("No Ollama models found. Please install Ollama and pull at least one model.")
                print_system_message("Try running: ollama pull llama3")
                return
                
            print_info(f"Available Ollama models: {', '.join(available_models)}")
            
            # Choose the first available model
            selected_model = available_models[0]
            print_system_message(f"Using Ollama model: {selected_model}")
            
        except Exception as e:
            print_error(f"Failed to connect to Ollama: {str(e)}")
            print_system_message("Is Ollama running? Try: ollama serve")
            return
        
        # Initialize the Ollama agent
        print_system_message("Initializing Ollama agent...")
        
        agent = create_agent(
            model=f"ollama-{selected_model}",
            temperature=0.2,  # Set lower temperature for more deterministic responses
        )
        
        print_system_message("Ollama agent initialized successfully!")
        
        # Example query
        query = "Write a Python function to generate the Fibonacci sequence using a generator."
        print_system_message(f"Asking Ollama: {query}")
        
        # Get response from agent
        response = await agent.chat(query)
        
        # Display response
        if isinstance(response, dict):
            print_assistant_response(response["message"])
            
            # Show tool usage if present
            if response.get("tool_calls"):
                print_info(f"\nAgent used {len(response['tool_calls'])} tool calls:")
                for i, call in enumerate(response['tool_calls'], 1):
                    print_info(f"\n{i}. Tool: {call['name']}")
        else:
            # For string responses (backward compatibility)
            print_assistant_response(response)
            
        # Follow-up query
        follow_up_query = "Can you explain the time and space complexity of this implementation?"
        print_system_message(f"Follow-up question: {follow_up_query}")
        
        # Get follow-up response
        follow_up_response = await agent.chat(follow_up_query)
        
        # Display follow-up response
        if isinstance(follow_up_response, dict):
            print_assistant_response(follow_up_response["message"])
        else:
            print_assistant_response(follow_up_response)
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        traceback.print_exc()
    
    print_system_message("Ollama basic chat example completed!")
    print_separator()


async def main():
    """Main function to run the Ollama chat example."""
    clear_screen()
    await run_ollama_basic_chat()


if __name__ == "__main__":
    asyncio.run(main()) 