#!/usr/bin/env python3
"""
File Tools Demo for Cursor Agent

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

# Demo project directory
DEMO_DIR = os.path.join(os.path.dirname(__file__), "demo_files")


async def run_file_tools_demo(agent):
    """Run the file tools demo with the provided agent.

    Args:
        agent: The initialized agent
    """
    print_separator()
    print_system_message("FILE TOOLS DEMO SCENARIO")
    print_system_message("We'll test the agent's ability to create and manipulate files")
    print_separator()

    # Create a context with our demo directory
    demo_files = []
    if os.path.exists(DEMO_DIR):
        for root, _, files in os.walk(DEMO_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                demo_files.append(file_path)

    # Create user info with the demo project files
    user_info = create_user_info(demo_files, DEMO_DIR)

    # Demo queries
    demo_queries = [
        "Create a simple Python calculator class that supports addition, subtraction, multiplication, and division operations. Include docstrings and a simple test case.",
        "Add a power method to the calculator class that raises a number to a power.",
        "Create a README.md file explaining how to use the calculator.",
    ]

    for i, query in enumerate(demo_queries):
        print_separator()
        print_user_input(query)
        print_system_message("Processing request...")

        try:
            response = await agent.chat(query, user_info)
            print_assistant_response(response)
        except Exception as e:
            print_error(f"Error getting response: {str(e)}")

        # If not the last query, wait for user input
        if i < len(demo_queries) - 1:
            input(f"{Colors.GRAY}Press Enter to continue to the next request...{Colors.RESET}")
        else:
            # Add a small delay for readability at the end
            await asyncio.sleep(1)

    print_separator()
    print_system_message("FILE TOOLS DEMO COMPLETED")
    print_system_message("Here are the files created:")
    
    # List created files
    if os.path.exists(DEMO_DIR):
        for root, _, files in os.walk(DEMO_DIR):
            rel_path = os.path.relpath(root, DEMO_DIR)
            if rel_path == ".":
                prefix = ""
            else:
                prefix = f"{rel_path}/"
            
            for file in files:
                print_system_message(f"  - {prefix}{file}")


async def main():
    """
    Main entry point for the file tools demo.
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
    elif openai_key:
        model = "gpt-4o"
    else:
        print_error("No API keys available")
        sys.exit(1)

    try:
        clear_screen()
        print_separator()
        print_system_message("FILE TOOLS DEMO")
        print_system_message(
            "This demo showcases the agent's ability to create and manipulate files."
        )
        print_separator()

        # Create a demo directory
        os.makedirs(DEMO_DIR, exist_ok=True)
        print_system_message(f"Created demo directory at {DEMO_DIR}")
        
        # Initialize the agent using cursor_agent package
        print_system_message(f"Initializing agent with model {model}...")
        agent = create_agent(model=model)
        print_system_message("Agent initialized successfully!")

        # Run the file tools demo
        await run_file_tools_demo(agent)

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up demo files
        print_system_message("Cleaning up demo files...")
        if os.path.exists(DEMO_DIR):
            shutil.rmtree(DEMO_DIR)
            print_system_message(f"Removed demo directory {DEMO_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
