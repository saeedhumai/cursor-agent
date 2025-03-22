#!/usr/bin/env python3
"""
Main demo menu for Claude agent demos.
This script provides a menu for all available demos.
"""

import asyncio
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
    create_user_info,
    print_assistant_response,
    print_error,
    print_separator,
    print_system_message,
    print_tool_call,
    print_tool_result,
    print_user_input,
)

# List of available demos
AVAILABLE_DEMOS = {
    "1": {
        "name": "chat_demo",
        "description": "Interactive chat demo with basic Q&A and file interaction",
    },
    "2": {
        "name": "file_tools_demo",
        "description": "File manipulation and code generation demo",
    },
    "3": {
        "name": "search_demo",
        "description": "Code search and exploration demo",
    },
}


async def display_menu():
    """Display the main menu and get user selection."""
    print_separator()
    print_system_message("CLAUDE AGENT DEMO MENU")
    print_system_message("Choose a demo to run:")
    print_separator()

    for key, demo in AVAILABLE_DEMOS.items():
        print(f"{Colors.CYAN}{key}.{Colors.ENDC} {demo['description']}")

    print(f"{Colors.CYAN}q.{Colors.ENDC} Quit")
    print_separator()

    choice = input(f"{Colors.GRAY}Enter your choice: {Colors.ENDC}")
    return choice


async def run_demo(demo_name, non_interactive=False):
    """Run a specific demo.

    Args:
        demo_name: Name of the demo to run
        non_interactive: When True, run in non-interactive mode without pauses
    """
    try:
        # Import the demo module dynamically
        module_name = f"tests.demo.{demo_name}"
        __import__(module_name)
        demo_module = sys.modules[module_name]

        # Check if the module has a non-interactive main function
        if non_interactive and hasattr(demo_module, "main_non_interactive"):
            await demo_module.main_non_interactive()
        else:
            # Fall back to regular main function with non_interactive param if supported
            if non_interactive:
                # Check if main accepts non_interactive parameter
                import inspect

                sig = inspect.signature(demo_module.main)
                if "non_interactive" in sig.parameters:
                    await demo_module.main(non_interactive=True)
                else:
                    print_system_message(
                        f"Warning: {demo_name} does not support non-interactive mode"
                    )
                    await demo_module.main()
            else:
                await demo_module.main()

    except ImportError:
        print_error(f"Demo '{demo_name}' not found")
    except Exception as e:
        print_error(f"Error running {demo_name}: {str(e)}")
        import traceback

        traceback.print_exc()


async def run_all_demos(non_interactive=False):
    """Run all available demos in sequence.

    Args:
        non_interactive: When True, run in non-interactive mode without pauses
    """
    print_system_message("RUNNING ALL DEMOS")

    for demo_info in AVAILABLE_DEMOS.values():
        demo_name = demo_info["name"]
        print_separator()
        print_system_message(f"Starting demo: {demo_name}")
        await run_demo(demo_name, non_interactive=non_interactive)

        if not non_interactive:
            input(f"{Colors.GRAY}Press Enter to continue to the next demo...{Colors.ENDC}")

    print_system_message("ALL DEMOS COMPLETED")


async def run_demo_list(demo_list, non_interactive=False):
    """Run a list of specified demos in sequence.

    Args:
        demo_list: List of demo names to run
        non_interactive: When True, run in non-interactive mode without pauses
    """
    for demo_name in demo_list:
        # Find the demo name regardless of number format
        actual_demo_name = None
        for key, info in AVAILABLE_DEMOS.items():
            if info["name"] == demo_name or key == demo_name:
                actual_demo_name = info["name"]
                break

        if actual_demo_name:
            print_separator()
            print_system_message(f"Starting demo: {actual_demo_name}")
            await run_demo(actual_demo_name, non_interactive=non_interactive)

            if not non_interactive and demo_name != demo_list[-1]:
                input(f"{Colors.GRAY}Press Enter to continue to the next demo...{Colors.ENDC}")
        else:
            print_error(f"Demo '{demo_name}' not found")


async def main(non_interactive=False, demo_list=None):
    """Main entry point for the demo menu.

    Args:
        non_interactive: When True, run in non-interactive mode
        demo_list: Optional list of demo names to run in sequence
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
        print_system_message("CLAUDE AGENT DEMOS")

        if non_interactive:
            print_system_message("Running in non-interactive mode")

        if demo_list:
            # Run specific demos from the list
            if demo_list == ["all"]:
                await run_all_demos(non_interactive=non_interactive)
            else:
                await run_demo_list(demo_list, non_interactive=non_interactive)
        else:
            # Interactive menu mode (only if not non-interactive)
            if non_interactive:
                print_error("Non-interactive mode requires specifying demos to run.")
                print_system_message(
                    "Available demos: "
                    + ", ".join(info["name"] for info in AVAILABLE_DEMOS.values())
                )
                return

            while True:
                choice = await display_menu()

                if choice.lower() == "q":
                    break
                elif choice in AVAILABLE_DEMOS:
                    demo_name = AVAILABLE_DEMOS[choice]["name"]
                    await run_demo(demo_name)
                elif choice == "all":
                    await run_all_demos()
                else:
                    print_error("Invalid choice. Please try again.")

        print_separator()
        print_system_message("Demo session completed.")

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback

        traceback.print_exc()

    except KeyboardInterrupt:
        print_separator()
        print_system_message("Demo session interrupted.")


# Add a dedicated non-interactive main function for backwards compatibility
async def main_non_interactive():
    """Run all demos in non-interactive mode."""
    await main(non_interactive=True, demo_list=["all"])


if __name__ == "__main__":
    asyncio.run(main())
