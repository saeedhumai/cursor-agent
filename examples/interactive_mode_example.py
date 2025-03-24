#!/usr/bin/env python3
"""
Interactive Mode Example for Cursor Agent

This script demonstrates the agent's capabilities in interactive mode,
allowing the user to engage in a conversation with the agent and see how 
it responds to different queries.
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

# Default task for example mode
DEFAULT_TASK = """Create a simple Todo list API with FastAPI with the following features:
1. A Todo model with id, title, description, and completed status
2. CRUD endpoints (Create, Read, Update, Delete)
3. Simple in-memory storage for todos
Include docstrings and proper error handling.
"""


async def main():
    """
    Main entry point for the interactive example.
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
    if openai_key:
        selected_model = "gpt-4o"
    else:
        selected_model = "claude-3-5-sonnet-latest"
    
    # Initialize initial query with default
    initial_query = DEFAULT_TASK
    
    try:
        clear_screen()
        print_separator()
        print_system_message("INTERACTIVE MODE EXAMPLE")
       
        # Non-interactive mode - use default values
        print_system_message("Running in non-interactive mode with predefined task")
        print_system_message(f"Using model: {selected_model}")
        print_system_message("Task: Create a FastAPI Todo list API")
        print_separator()
    
        # Store original directory
        original_dir = os.getcwd()
        
        # Create example_files directory if it doesn't exist
        example_dir = Path(original_dir) / "example_files" / "interactive_example"
        example_dir.mkdir(parents=True, exist_ok=True)
        
        # Change to the example_files directory
        os.chdir(example_dir)
        print_system_message(f"Working in directory: {os.getcwd()}")
        print_separator()
        
        # Run the interactive agent using cursor_agent.agent.run_agent_interactive
        await run_agent_interactive(
            model=selected_model,
            initial_query=initial_query,
            max_iterations=20,
            auto_continue=True  # Auto-continue in non-interactive mode
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
        print_system_message("INTERACTIVE EXAMPLE COMPLETED")


if __name__ == "__main__":
    asyncio.run(main())
