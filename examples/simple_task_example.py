#!/usr/bin/env python3
"""
Simple Task Example for Cursor Agent

This script demonstrates the basic usage of the cursor agent to accomplish a simple task.
It shows how to create agents, process queries, and execute responses interactively.
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Import from cursor_agent package
from cursor_agent.agent import run_agent_interactive

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
        print_system_message
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
            print_system_message
        )
    except ImportError:
        raise ImportError("Unable to import utility functions. Make sure utils.py is in the examples directory.")

# Load environment variables
load_dotenv()


async def main():
    """
    Main entry point for the example.
    """
    # Load environment variables
    load_dotenv()

    # Check for API keys
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not anthropic_key and not openai_key:
        print_error("No API keys found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file.")
        sys.exit(1)
    
    # Select model based on available keys
    if anthropic_key:
        model = "claude-3-5-sonnet-latest"
    else:
        model = "gpt-4o"
    
    try:
        clear_screen()
        print_separator()
        print_system_message("SIMPLE TASK EXAMPLE")
        print_system_message("This example shows the cursor agent solving a simple task interactively.")
        print_separator()
        
        print_system_message(f"Using model: {model}")
        print_system_message("You'll be asked to provide a task for the agent to solve.")
        print_separator()
        
        # Get task from user
        task = input(f"{Colors.BOLD}Enter a task for the agent: {Colors.RESET}")
        if not task:
            task = "Write a Python function to check if a string is a palindrome."
            print_system_message(f"Using default task: {task}")
        
        # Store original directory
        original_dir = os.getcwd()
        
        # Create example_files directory if it doesn't exist
        example_dir = Path(original_dir) / "example_files" / "simple_task_example"
        example_dir.mkdir(parents=True, exist_ok=True)
        
        # Change to the example_files directory
        os.chdir(example_dir)
        print_system_message(f"Working in directory: {os.getcwd()}")
        
        # Run the agent
        await run_agent_interactive(
            model=model,
            initial_query=task,
            max_iterations=10,
            auto_continue=True
        )
        
        # Change back to the original directory
        os.chdir(original_dir)
        
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Ensure we change back to the original directory if an exception occurs
        if 'original_dir' in locals():
            os.chdir(original_dir)
            
    finally:
        # Make sure we always return to the original directory
        if 'original_dir' in locals():
            os.chdir(original_dir)
        print_separator()
        print_system_message("SIMPLE TASK EXAMPLE COMPLETED")


if __name__ == "__main__":
    asyncio.run(main())
