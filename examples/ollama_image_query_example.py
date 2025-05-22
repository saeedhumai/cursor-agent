#!/usr/bin/env python3
"""
Ollama Image Query Example for Cursor Agent

This script demonstrates multimodal capabilities with the Cursor Agent
using locally hosted Ollama models that support vision.
"""

import asyncio
import os
import sys
import traceback
import shutil
from pathlib import Path
import urllib.request
import platform

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


# Default test image URL (Python logo)
DEFAULT_IMAGE_URL = "https://raw.githubusercontent.com/python/cpython/main/Doc/logo.png"


async def run_ollama_image_query():
    """Demonstrates image query functionality with an Ollama model that supports vision."""
    print_separator()
    print_system_message("OLLAMA IMAGE QUERY EXAMPLE")
    
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
                print_system_message("Try running: ollama pull llava")
                return
                
            print_info(f"Available Ollama models: {', '.join(available_models)}")
            
            # Look for vision-capable models first (llava, bakllava)
            vision_models = [m for m in available_models if 'llava' in m.lower()]
            
            if vision_models:
                selected_model = vision_models[0]
                print_system_message(f"Using vision-capable Ollama model: {selected_model}")
            else:
                print_error("No vision-capable models found. This example may not work.")
                print_system_message("Try running: ollama pull llava")
                # Fall back to first available model
                selected_model = available_models[0]
                print_system_message(f"Falling back to model: {selected_model} (may not support vision)")
            
        except Exception as e:
            print_error(f"Failed to connect to Ollama: {str(e)}")
            print_system_message("Is Ollama running? Try: ollama serve")
            return
        
        # Create a demo directory
        demo_dir = Path("demo_files/ollama_image_demo")
        demo_dir.mkdir(parents=True, exist_ok=True)
        
        # Download a test image if not provided
        image_path = os.path.join(demo_dir, "test_image.png")
        if not os.path.exists(image_path):
            print_system_message(f"Downloading test image to {image_path}...")
            urllib.request.urlretrieve(DEFAULT_IMAGE_URL, image_path)
            print_system_message("Image downloaded successfully")
        
        # Initialize the Ollama agent
        print_system_message("Initializing Ollama agent...")
        
        agent = create_agent(
            model=f"ollama-{selected_model}",
            temperature=0.2,
        )
        
        # Print agent info
        print_system_message("Ollama agent initialized successfully!")
        print_info(f"Model: ollama-{selected_model}")
        
        # Display image query info
        print_system_message("Running image query...")
        print_info(f"Image path: {image_path}")
        
        # Example image queries
        queries = [
            "What do you see in this image?",
            "Describe this image in detail.",
            "What does this image represent?",
        ]
        
        for i, query in enumerate(queries, 1):
            print_separator()
            print_system_message(f"Query {i}/{len(queries)}")
            print_user_message(query)
            
            try:
                # Get response from agent using image query
                response = await agent.query_image(
                    image_paths=[image_path],
                    query=query
                )
                
                # Display response
                print_assistant_response(response)
                
            except Exception as e:
                print_error(f"Error querying image: {str(e)}")
                print_error("This model may not support multimodal capabilities.")
                print_system_message("Try using a vision-capable model like 'llava'.")
                break
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        traceback.print_exc()
    
    print_system_message("Ollama image query example completed!")
    print_separator()


async def main():
    """Main function to run the Ollama image query example."""
    clear_screen()
    await run_ollama_image_query()


if __name__ == "__main__":
    asyncio.run(main()) 