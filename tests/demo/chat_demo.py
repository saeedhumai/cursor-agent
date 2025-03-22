#!/usr/bin/env python3
"""
Chat demo for the Claude agent.
This script demonstrates the agent's capabilities for interactive conversation.
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

# Sample queries for non-interactive mode
SAMPLE_QUERIES = [
    "What can you do as an AI assistant?",
    "How do you handle file operations?",
    "Can you search through codebases?",
    "Write a simple Python function to calculate the factorial of a number.",
    "What's in the sample.py file?",
]


async def main(non_interactive=False):
    """Main entry point for the demo.

    Args:
        non_interactive: When True, run in non-interactive mode with predefined queries
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
        print_system_message("CHAT DEMO")
        print_system_message(
            "This demo showcases the Claude agent's ability to have a conversation and answer questions."
        )

        if non_interactive:
            print_system_message("Running in non-interactive mode with predefined queries")
        else:
            print_system_message("Type 'exit' or 'quit' to end the demo")

        print_separator()

        # Create a sample Python file for demo
        demo_dir = os.path.join(os.path.dirname(__file__), "demo_files")
        os.makedirs(demo_dir, exist_ok=True)

        # Clean up any previously created factorial files
        for file in os.listdir(demo_dir):
            if file.startswith("factorial_") and file.endswith(".py"):
                try:
                    os.unlink(os.path.join(demo_dir, file))
                except Exception as e:
                    print_error(f"Error cleaning up file {file}: {str(e)}")

        # Create a sample Python file
        sample_file = os.path.join(demo_dir, "sample.py")

        with open(sample_file, "w") as f:
            f.write(
                """def greet(name):
    \"\"\"Greet a person by name.\"\"\"
    return f"Hello, {name}!"

def calculate_sum(numbers):
    \"\"\"Calculate the sum of a list of numbers.\"\"\"
    return sum(numbers)

def is_palindrome(text):
    \"\"\"Check if a string is a palindrome (reads the same forwards and backwards).\"\"\"
    # Remove spaces and convert to lowercase
    text = text.replace(" ", "").lower()
    return text == text[::-1]

if __name__ == "__main__":
    print(greet("World"))
    print(f"Sum of [1, 2, 3, 4, 5]: {calculate_sum([1, 2, 3, 4, 5])}")
    print(f"Is 'radar' a palindrome? {is_palindrome('radar')}")
    print(f"Is 'hello' a palindrome? {is_palindrome('hello')}")
"""
            )

        # Initialize the Claude agent
        print_system_message("Initializing Claude agent...")
        agent = ClaudeAgent(api_key=api_key)
        agent.register_default_tools()
        print_system_message("Claude agent initialized successfully!")

        # Create user info with sample file
        user_info = create_user_info([sample_file])

        # Make sure the file path is properly added to user_info
        if "open_files" not in user_info:
            user_info["open_files"] = []

        # Ensure the sample file is in the open_files with full path
        user_info["open_files"].append(
            {
                "path": sample_file,
                "name": os.path.basename(sample_file),
                "content": open(sample_file, "r").read(),
            }
        )

        if non_interactive:
            # Run through predefined queries
            for query in SAMPLE_QUERIES:
                print_separator()
                print_user_input(query)
                print_system_message("Processing request...")

                try:
                    response = await agent.chat(query, user_info)
                    if response:
                        print_assistant_response(response)

                        # Special handling for factorial query
                        if "factorial" in query and "function" in query:
                            # Create a unique factorial file with timestamp
                            import time

                            timestamp = int(time.time())
                            factorial_file = os.path.join(demo_dir, f"factorial_{timestamp}.py")

                            # Extract code from response if present
                            import re

                            code_match = re.search(
                                r"```(?:python)?\s*(.+?)```", response, re.DOTALL
                            )
                            if code_match:
                                code = code_match.group(1).strip()
                                try:
                                    with open(factorial_file, "w") as f:
                                        f.write(code)
                                    print_system_message(
                                        f"Created factorial implementation at {factorial_file}"
                                    )
                                except Exception as e:
                                    print_error(f"Error creating factorial file: {str(e)}")
                    else:
                        print_error(
                            "No response received. This may be due to an issue with tool handling."
                        )

                    # Add a small delay for readability
                    await asyncio.sleep(2)

                except Exception as e:
                    print_error(f"Error getting response: {str(e)}")
        else:
            # Interactive mode
            while True:
                print_separator()
                query = input(f"{Colors.YELLOW}You: {Colors.ENDC}")

                if query.lower() in ["exit", "quit", "q"]:
                    break

                print_system_message("Processing request...")

                try:
                    response = await agent.chat(query, user_info)
                    if response:
                        print_assistant_response(response)
                    else:
                        print_error(
                            "No response received. This may be due to an issue with tool handling."
                        )
                except Exception as e:
                    print_error(f"Error getting response: {str(e)}")

        print_separator()
        print_system_message("Demo completed.")

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up demo files
        if "demo_dir" in locals() and os.path.exists(demo_dir):
            for file in os.listdir(demo_dir):
                file_path = os.path.join(demo_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print_error(f"Error deleting {file_path}: {str(e)}")


# Add a dedicated non-interactive main function for backwards compatibility
async def main_non_interactive():
    """Run the demo in non-interactive mode with predefined queries."""
    await main(non_interactive=True)


if __name__ == "__main__":
    asyncio.run(main())
