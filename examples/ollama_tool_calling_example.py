#!/usr/bin/env python3
"""
Ollama Tool Calling Example for Cursor Agent

This script demonstrates tool calling functionality with the Cursor Agent
using locally hosted Ollama models.
"""

import asyncio
import os
import sys
import traceback
from pathlib import Path
import platform
import json

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
    print_info,
    print_user_message
)


async def run_ollama_tool_calling():
    """Demonstrates tool calling functionality with an Ollama model."""
    print_separator()
    print_system_message("OLLAMA TOOL CALLING EXAMPLE")
    
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
            temperature=0.1,  # Lower temperature for more deterministic tool usage
        )
        
        # Register default tools with the agent
        print_system_message("Registering tools...")
        agent.register_default_tools()
        print_info(f"Registered {len(agent.available_tools)} tools with the agent")
        
        # Create a demo directory
        demo_dir = Path("demo_files/ollama_tools_demo")
        demo_dir.mkdir(parents=True, exist_ok=True)
        
        # Save current directory
        original_dir = os.getcwd()
        
        # Change to the demo directory
        os.chdir(demo_dir)
        print_system_message(f"Working in directory: {os.getcwd()}")
        
        # Create user_info dictionary with context
        user_info = {
            "workspace_path": os.getcwd(),
            "os": platform.system(),
            "open_files": [],
            "cursor_position": None,
            "recent_files": []
        }
        
        # Example queries that should trigger tool usage
        queries = [
            "Create a new Python file called 'calculator.py' that implements a basic calculator class with add, subtract, multiply, and divide methods.",
            "List the files in the current directory.",
            "Read the content of calculator.py and add a method to calculate the square root.",
            "Run the Python file to test if it works. Add a simple main function that demonstrates the calculator."
        ]
        
        for i, query in enumerate(queries, 1):
            print_separator()
            print_system_message(f"Query {i}/{len(queries)}")
            print_user_message(query)
            
            # Get response from agent
            response = await agent.chat(query, user_info)
            
            # Display response
            if isinstance(response, dict):
                print_assistant_response(response["message"])
                
                # Show tool usage
                if response.get("tool_calls"):
                    print_info(f"\nAgent used {len(response['tool_calls'])} tool call(s):")
                    for j, call in enumerate(response['tool_calls'], 1):
                        print_info(f"\nTool {j}: {call['name']}")
                        if call.get('parameters'):
                            print_info(f"Parameters: {json.dumps(call['parameters'], indent=2)}")
                        if call.get('output'):
                            # Truncate long outputs for display
                            output = call['output']
                            if isinstance(output, str) and len(output) > 500:
                                output = output[:500] + "... [truncated]"
                            print_info(f"Output: {output}")
            else:
                # For string responses (backward compatibility)
                print_assistant_response(response)
        
        # Change back to original directory
        os.chdir(original_dir)
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        traceback.print_exc()
        
        # Ensure we change back to the original directory if an exception occurs
        if 'original_dir' in locals():
            os.chdir(original_dir)
    
    print_system_message("Ollama tool calling example completed!")
    print_separator()


async def main():
    """Main function to run the Ollama tool calling example."""
    clear_screen()
    await run_ollama_tool_calling()


if __name__ == "__main__":
    asyncio.run(main()) 