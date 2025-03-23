#!/usr/bin/env python3
"""
File Manipulation Example for Cursor Agent

This script demonstrates the agent's capabilities for file manipulation,
showing how it can create, read, and modify files to accomplish tasks.
"""

import asyncio
import os
import sys
import shutil
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
        print_user_input,
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
            print_user_input,
            print_assistant_response,
            create_user_info
        )
    except ImportError:
        raise ImportError("Unable to import utility functions. Make sure utils.py is in the examples directory.")

# Load environment variables
load_dotenv()

# Create a temporary directory for the demo files
EXAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_files")
os.makedirs(EXAMPLE_DIR, exist_ok=True)
print_system_message(f"Example directory created at {EXAMPLE_DIR}")


async def run_file_tools_example(agent):
    """Run the file tools example with the provided agent."""
    print_separator()
    print_system_message("FILE MANIPULATION EXAMPLE SCENARIO")
    print_system_message("We'll create and modify files with the agent")

    # Create a context with our example directory
    example_files = []
    if os.path.exists(EXAMPLE_DIR):
        for root, _, files in os.walk(EXAMPLE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                example_files.append(file_path)

    # Create user info with the example project files
    user_info = create_user_info(example_files, EXAMPLE_DIR)

    # Example queries
    example_queries = [
        "Create a simple Python calculator class that supports addition, subtraction, multiplication, and division operations. Include docstrings and a simple test case.",
        "Add a power method to the calculator class that raises a number to a power.",
        "Create a README.md file that explains the calculator's functionality and how to use it."
    ]

    for i, query in enumerate(example_queries):
        print_separator()
        print_system_message(f"Example Query {i+1}:")
        print_user_input(query)
        print_system_message("Processing request...")
        
        response = await agent.chat(query, user_info)
        print_assistant_response(response)
        
        # Update the file list after each query
        example_files = []
        for root, _, files in os.walk(EXAMPLE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                example_files.append(file_path)
        
        if i < len(example_queries) - 1:
            user_info = create_user_info(example_files, EXAMPLE_DIR)
    
    print_separator()
    print_system_message("FILE MANIPULATION EXAMPLE COMPLETED")


async def main():
    """
    Main entry point for the file manipulation example.
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Load API keys from environment variables
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        # Determine available models based on API keys
        available_models = []
        if anthropic_api_key:
            available_models.append("claude-3-5-sonnet-latest")
        if openai_api_key:
            available_models.append("gpt-4o")
        
        if not available_models:
            print_error("No API keys found. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY")
            return
        
        # Print example header
        print_separator()
        print_system_message("FILE MANIPULATION EXAMPLE")
        print_system_message(
            "This example showcases the agent's ability to create and manipulate files."
        )
        
        # Create a example directory
        os.makedirs(EXAMPLE_DIR, exist_ok=True)
        print_system_message(f"Created example directory at {EXAMPLE_DIR}")
        
        # Initialize the agent using cursor_agent package
        model = "claude-3-5-sonnet-latest" if "claude-3-5-sonnet-latest" in available_models else available_models[0]
        print_system_message(f"Initializing agent with model {model}...")
        agent = create_agent(model=model)
        print_system_message("Agent initialized successfully!")
        
        # Run the file tools example
        await run_file_tools_example(agent)

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up example files
        print_system_message("Cleaning up example files...")
        if os.path.exists(EXAMPLE_DIR):
            shutil.rmtree(EXAMPLE_DIR)
            print_system_message(f"Removed example directory {EXAMPLE_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
