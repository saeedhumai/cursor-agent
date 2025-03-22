#!/usr/bin/env python3
"""
Interactive Agent Demo for the Claude agent.
This script demonstrates the agent's capabilities for multi-step, iterative task completion.
It shows how the agent can break down a complex task (creating a FastAPI Todo list API)
into manageable steps and implement them incrementally.
"""

import asyncio
import json
import os
import shutil
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import the main functionality from main.py
from main import run_agent_interactive

# Import demo utilities
from tests.demo.utils import (
    Colors,
    clear_screen,
    create_user_info,
    print_assistant_response,
    print_error,
    print_separator,
    print_system_message,
    print_tool_call,
    print_tool_result,
    print_user_input,
)

# Define the task for the interactive agent
TODO_API_TASK = """Create a simple Todo list backend API using FastAPI with the following features:
1. A Todo model with id, title, description, and completed status
2. CRUD endpoints (Create, Read, Update, Delete)
3. GET /todos - List all todos
4. GET /todos/{id} - Get a specific todo
5. POST /todos - Create a new todo
6. PUT /todos/{id} - Update a todo
7. DELETE /todos/{id} - Delete a todo
8. Data validation
9. Simple in-memory storage for todos
10. Include a requirements.txt file

Make it well-structured and follow best practices."""


async def main(non_interactive=False, auto_continue=False):
    """Main entry point for the demo.

    Args:
        non_interactive: When True, run in fully automated mode without user input
        auto_continue: When True, continue automatically between steps without prompting
    """
    # Load environment variables
    env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if env_path.exists():
        print_system_message(f"Loading environment variables from {env_path}")
        load_dotenv(dotenv_path=env_path)

    # Check if API key is present
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print_error("ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    try:
        clear_screen()
        print_separator()
        print_system_message("INTERACTIVE AGENT DEMO")
        print_system_message(
            "This demo showcases the enhanced interactive agent's ability to handle complex, multi-step tasks."
        )
        print_system_message("We'll create a FastAPI Todo List API through multiple iterations.")

        if non_interactive:
            print_system_message("Running in fully automated mode - no user input required")
        else:
            print_system_message(
                "You'll be prompted after each step to continue, ask questions, or end the demo"
            )

        print_separator()

        # Create a demo directory for the todo API project
        demo_dir = os.path.join(os.path.dirname(__file__), "demo_files")
        todo_api_dir = os.path.join(demo_dir, "todo_api")
        os.makedirs(demo_dir, exist_ok=True)
        os.makedirs(todo_api_dir, exist_ok=True)

        # Set the working directory to the todo API directory
        original_dir = os.getcwd()
        os.chdir(todo_api_dir)
        print_system_message(f"Changed working directory to {todo_api_dir}")

        # Maximum number of iterations
        max_iterations = 6 if non_interactive else 10

        print_system_message("Starting interactive agent...")
        print_system_message(f"Task: {TODO_API_TASK}")
        print_separator()

        # Run the interactive agent to create the Todo API
        await run_agent_interactive(
            provider="claude",
            initial_query=TODO_API_TASK,
            max_iterations=max_iterations,
            auto_continue=auto_continue or non_interactive,
        )

        # List the files created
        print_separator()
        print_system_message("Files created by the agent:")
        for root, dirs, files in os.walk(todo_api_dir):
            level = root.replace(todo_api_dir, "").count(os.sep)
            indent = " " * 4 * level
            print(f"{indent}{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                print(f"{sub_indent}{file} ({size} bytes)")

        # Keep files around for a while in non-interactive mode
        if non_interactive:
            print_separator()
            print_system_message(
                f"Demo completed. Files will be kept for 30 seconds for inspection."
            )
            print_system_message(f"Todo API files are located at: {todo_api_dir}")
            await asyncio.sleep(30)
        else:
            print_separator()
            print_system_message("Demo completed.")
            print_system_message(f"Todo API files are located at: {todo_api_dir}")
            input(f"{Colors.YELLOW}Press Enter to clean up and exit...{Colors.ENDC}")

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback

        traceback.print_exc()

    finally:
        # Change back to original directory
        os.chdir(original_dir)

        # Clean up demo files
        if "todo_api_dir" in locals() and os.path.exists(todo_api_dir):
            print_system_message(f"Cleaning up demo files in {todo_api_dir}...")
            try:
                shutil.rmtree(todo_api_dir)
                print_system_message("Cleanup completed.")
            except Exception as e:
                print_error(f"Error cleaning up: {str(e)}")
                print_system_message("You may need to manually delete the demo files.")


# Add a dedicated non-interactive main function for automated testing
async def main_non_interactive():
    """Run the demo in non-interactive mode with auto-continuation."""
    await main(non_interactive=True, auto_continue=True)


if __name__ == "__main__":
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Run the interactive agent demo")
    parser.add_argument(
        "--non-interactive", action="store_true", help="Run in non-interactive mode"
    )
    parser.add_argument(
        "--auto-continue", action="store_true", help="Continue automatically between steps"
    )
    args = parser.parse_args()

    asyncio.run(main(non_interactive=args.non_interactive, auto_continue=args.auto_continue))
