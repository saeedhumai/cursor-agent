#!/usr/bin/env python3
"""
Basic Usage Demo for Cursor Agent

This script demonstrates the basic usage of the cursor agent with different models.
It shows how to create agents and get responses to simple coding queries.
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Import from cursor_agent package
from cursor_agent.agent import create_agent, run_agent_interactive

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
        print_assistant_response
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
            print_assistant_response
        )
    except ImportError:
        raise ImportError("Unable to import utility functions. Make sure utils.py is in the examples directory.")

# Load environment variables
load_dotenv()


async def run_claude_example():
    """Run an example query with Claude agent."""
    print_separator()
    print_system_message("CLAUDE AGENT EXAMPLE")

    # Check for Anthropic API key
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print_error("No ANTHROPIC_API_KEY found in environment. Skipping Claude example.")
        print_system_message("To use Claude, add your Anthropic API key to the .env file.")
        return

    # Initialize Claude agent
    print_system_message("Initializing Claude agent...")
    try:
        # Create a temporary directory for the Claude demo
        temp_dir = Path("demo_files/claude_example")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save current directory
        original_dir = os.getcwd()
        
        # Change to the temporary directory
        os.chdir(temp_dir)
        
        # Example query
        query = "Write a Python function to calculate the factorial of a number using recursion."
        print_system_message(f"Asking Claude: {query}")

        # Use run_agent_interactive with a single iteration
        await run_agent_interactive(
            model="claude-3-5-sonnet-latest",
            initial_query=query,
            max_iterations=1,
            auto_continue=True
        )
        
        # Change back to original directory
        os.chdir(original_dir)
        
        print_system_message("Claude example completed!")

    except Exception as e:
        print_error(f"Error with Claude agent: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Ensure we change back to the original directory if an exception occurs
        if 'original_dir' in locals():
            os.chdir(original_dir)


async def run_openai_example():
    """Run an example query with OpenAI agent."""
    print_separator()
    print_system_message("OPENAI AGENT EXAMPLE")

    # Check for OpenAI API key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        print_error("No OPENAI_API_KEY found in environment. Skipping OpenAI example.")
        print_system_message("To use OpenAI, add your OpenAI API key to the .env file.")
        return

    # Initialize OpenAI agent
    print_system_message("Initializing OpenAI agent...")
    try:
        # Create user_info dictionary to help with context
        user_info = {
            "workspace_root": os.getcwd(),
            "os": {
                "name": os.name,
                "system": sys.platform,
            },
        }
        
        agent = create_agent(model="gpt-4o")
        print_system_message("OpenAI agent initialized successfully!")

        # Example query
        query = "Write a Python function to generate the Fibonacci sequence up to n terms."
        print_system_message(f"Asking OpenAI: {query}")

        # Get response with user_info context
        response = await agent.chat(query, user_info)
        print_assistant_response(response)

    except Exception as e:
        print_error(f"Error with OpenAI agent: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point for the basic usage demo."""

    try:
        clear_screen()
        print_separator()
        print_system_message("BASIC USAGE DEMO")
        print_system_message("This demo shows how to use the cursor agent with different models.")
        print_separator()

        # Run Claude example
        await run_claude_example()

        # Run OpenAI example
        await run_openai_example()

        print_separator()
        print_system_message("BASIC USAGE DEMO COMPLETED")

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
