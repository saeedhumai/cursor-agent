#!/usr/bin/env python3
"""
Main demo script for the Claude agent.
This script provides a menu to run various demos.
"""

import asyncio
import importlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import demo utilities
from tests.demo.utils import (
    Colors,
    clear_screen,
    print_error,
    print_separator,
    print_system_message,
)

# Available demos
DEMOS = {
    "1": {
        "name": "Chat Demo",
        "description": "Interactive chat with the Claude agent",
        "module": "chat_demo",
    },
    "2": {
        "name": "File Tools Demo",
        "description": "Demonstrates file manipulation and code generation",
        "module": "file_tools_demo",
    },
    "3": {
        "name": "Search Demo",
        "description": "Demonstrates codebase search and exploration",
        "module": "search_demo",
    },
}


async def run_demo(demo_key):
    """Run the selected demo module."""
    try:
        # Import the demo module dynamically
        demo_module = DEMOS[demo_key]["module"]
        module = importlib.import_module(demo_module)

        # Run the main function of the demo
        await module.main()
        return True
    except Exception as e:
        print_error(f"Error running demo: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def print_menu():
    """Print the demo selection menu."""
    print_separator()
    print_system_message("CLAUDE AGENT DEMOS")
    print_system_message("Select a demo to run:")
    print()

    for key, demo in DEMOS.items():
        print(f"  {Colors.CYAN}[{key}]{Colors.ENDC} {Colors.BOLD}{demo['name']}{Colors.ENDC}")
        print(f"      {Colors.GRAY}{demo['description']}{Colors.ENDC}")

    print()
    print(f"  {Colors.CYAN}[q]{Colors.ENDC} Quit")
    print_separator()


async def main():
    """Main entry point for the demo menu."""
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

    while True:
        clear_screen()
        print_menu()

        choice = input(f"{Colors.GREEN}Enter choice: {Colors.ENDC}")

        if choice.lower() in ["q", "quit", "exit"]:
            break

        if choice in DEMOS:
            clear_screen()
            print_system_message(f"Running {DEMOS[choice]['name']}...")

            # Run the selected demo
            success = await run_demo(choice)

            if success:
                print_system_message(f"Demo completed. Press Enter to return to menu...")
            else:
                print_error(f"Demo failed. Press Enter to return to menu...")

            input()
        else:
            print_error("Invalid choice. Press Enter to try again...")
            input()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_system_message("\nExiting demo menu...")
        sys.exit(0)
