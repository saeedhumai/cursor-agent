#!/usr/bin/env python3
"""
File tools demo for the Claude agent.
This script demonstrates the agent's capabilities for file manipulation and code generation.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import the Claude agent
from agent.claude_agent import ClaudeAgent

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

# Demo directory for file operations
DEMO_DIR = os.path.join(os.path.dirname(__file__), "demo_files")
os.makedirs(DEMO_DIR, exist_ok=True)


async def run_predefined_scenario(agent, pause_between_steps=True):
    """Run a predefined scenario demonstrating file operations.

    Args:
        agent: The initialized Claude agent
        pause_between_steps: If True, pause between steps for user to read
    """

    # Create a starter file for the demo
    starter_file_path = os.path.join(DEMO_DIR, "calculator.py")
    with open(starter_file_path, "w") as f:
        f.write(
            """def add(a, b):
    \"\"\"Add two numbers and return the result.\"\"\"
    return a + b

def subtract(a, b):
    \"\"\"Subtract b from a and return the result.\"\"\"
    return a - b

# TODO: Implement multiply and divide functions

if __name__ == "__main__":
    print(f"1 + 2 = {add(1, 2)}")
    print(f"5 - 3 = {subtract(5, 3)}")
"""
        )

    print_system_message(f"Created starter file at {starter_file_path}")

    # Show the scenario steps
    print_separator()
    print_system_message("DEMO SCENARIO: Completing Calculator Implementation")
    print_system_message("We'll guide the Claude agent to add missing calculator functions")
    print_separator()

    # Step 1: Task description
    query = "I have a calculator.py file that needs the multiply and divide functions implemented. Can you help me complete it?"
    print_user_input(query)

    # Add a fake user context with the file open
    user_info = create_user_info([starter_file_path])

    print_system_message("Processing request...")
    response = await agent.chat(query, user_info)

    # Show the response with tool calls visualized
    print_assistant_response(response)
    print_separator()

    # Show the modified file
    if os.path.exists(starter_file_path):
        with open(starter_file_path, "r") as f:
            modified_code = f.read()

        print_system_message("UPDATED FILE CONTENTS:")
        print(f"{Colors.CYAN}{modified_code}{Colors.ENDC}")

    # If we're pausing between steps, wait for user input
    if pause_between_steps:
        input(f"{Colors.GRAY}Press Enter to continue to the next step...{Colors.ENDC}")
    else:
        # Add a small delay for readability in non-interactive mode
        await asyncio.sleep(2)

    # Step 2: Ask for a test case
    print_separator()
    query = "Can you create a test file to verify all the calculator functions?"
    print_user_input(query)

    print_system_message("Processing request...")
    response = await agent.chat(query, user_info)

    # Show the response
    print_assistant_response(response)

    # Find the test file if created
    test_files = [f for f in os.listdir(DEMO_DIR) if f.startswith("test_") and f.endswith(".py")]
    if test_files:
        test_file_path = os.path.join(DEMO_DIR, test_files[0])
        with open(test_file_path, "r") as f:
            test_code = f.read()

        print_separator()
        print_system_message(f"TEST FILE CREATED: {test_files[0]}")
        print(f"{Colors.CYAN}{test_code}{Colors.ENDC}")
    await asyncio.sleep(10)
    print_separator()
    print_system_message("DEMO COMPLETED")
    print_system_message(
        "The agent has successfully implemented the missing functions and created a test file."
    )

    # If we're pausing at the end, wait for user input before returning
    if pause_between_steps:
        input(f"{Colors.GRAY}Press Enter to exit the demo...{Colors.ENDC}")


async def main(non_interactive=False):
    """Main entry point for the demo.

    Args:
        non_interactive: When True, run in non-interactive mode without pauses
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
        print_system_message("FILE TOOLS DEMO")
        print_system_message(
            "This demo showcases the Claude agent's ability to manipulate files and generate code."
        )

        if non_interactive:
            print_system_message("Running in non-interactive mode (no pauses between steps)")

        print_separator()

        # Initialize the Claude agent
        print_system_message("Initializing Claude agent...")
        agent = ClaudeAgent(api_key=api_key)
        agent.register_default_tools()
        print_system_message("Claude agent initialized successfully!")

        # Run the predefined scenario
        await run_predefined_scenario(agent, pause_between_steps=not non_interactive)

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up demo files
        print_system_message("Cleanup process is disabled to allow examining the files")
        # if os.path.exists(DEMO_DIR):
        #     for file in os.listdir(DEMO_DIR):
        #         file_path = os.path.join(DEMO_DIR, file)
        #         try:
        #             if os.path.isfile(file_path):
        #                 os.unlink(file_path)
        #         except Exception as e:
        #             print_error(f"Error deleting {file_path}: {str(e)}")


# Add a dedicated non-interactive main function for backwards compatibility
async def main_non_interactive():
    """Run the demo in non-interactive mode without pauses between steps."""
    await main(non_interactive=True)


if __name__ == "__main__":
    asyncio.run(main())
