#!/usr/bin/env python3
import argparse
import asyncio
import glob
import importlib.util
import os
import re
import sys
import unittest
from pathlib import Path

from dotenv import load_dotenv

# Add tests directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tests"))
# Add parent directory to path to allow importing from agent
sys.path.insert(0, os.path.dirname(__file__))
# Import is_real_api_key function from utils
try:
    from utils import is_real_api_key
except ImportError:
    # Fallback validation if utils can't be imported
    def is_real_api_key(api_key, provider):
        if not api_key:
            return False
        # Simple validation checks - provider is used to determine the API key format
        if provider == "anthropic":  # Claude models
            return api_key.startswith(("sk-ant-", "sk-")) and len(api_key) > 20
        elif provider == "openai":   # GPT models
            return api_key.startswith("sk-") and len(api_key) > 20
        return False


# Load environment variables from .env file
# Try to find the .env file in the parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    # Try in the current directory
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        print(f"Loading environment variables from {env_path}")
        load_dotenv(dotenv_path=env_path)
    else:
        print("Warning: No .env file found. API keys may need to be set manually.")


def run_tests(test_name=None):
    """Run the test suite."""
    # Check for required API keys
    if os.environ.get("ANTHROPIC_API_KEY") and os.environ.get("ANTHROPIC_API_KEY").startswith(
        "sk-"
    ):
        print("ANTHROPIC_API_KEY present")
    else:
        print(
            "Warning: ANTHROPIC_API_KEY environment variable not set or appears to be a placeholder"
        )

    if os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_API_KEY").startswith("sk-"):
        print("OPENAI_API_KEY present")
    else:
        print("Warning: OPENAI_API_KEY environment variable not set or appears to be a placeholder")

    if test_name:
        if test_name == "all":
            # Run all tests
            tests = unittest.defaultTestLoader.discover("tests", pattern="test_*.py")
        else:
            # Run a specific test file or test class
            if "." in test_name:
                # Specific test class or method
                test_file, test_class = test_name.split(".", 1)
                module_name = f"tests.{test_file}"

                # Import the module
                spec = importlib.util.find_spec(module_name)
                if spec is None:
                    raise ImportError(f"Cannot find test file: {module_name}")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Create a test suite from the test class
                suite = unittest.defaultTestLoader.loadTestsFromName(test_class, module)
                tests = suite
            else:
                # Specific test file
                test_file = os.path.join("tests", f"test_{test_name}.py")
                if not os.path.exists(test_file):
                    raise FileNotFoundError(f"Test file not found: {test_file}")

                tests = unittest.defaultTestLoader.discover("tests", pattern=f"test_{test_name}.py")
    else:
        # Run all tests
        tests = unittest.defaultTestLoader.discover("tests", pattern="test_*.py")

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(tests)


async def run_demo(demo_name=None, non_interactive=False, demo_list=None):
    """Run a demo script or multiple demo scripts.

    Args:
        demo_name: Name of a specific demo to run, or 'main' for the menu
        non_interactive: When True, run demos in non-interactive mode
        demo_list: List of demo names to run sequentially, or 'all' to run all demos
    """
    # Check for required API keys
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY environment variable not set")
        return

    # Define the demos directory
    demos_dir = os.path.join(os.path.dirname(__file__), "tests", "demo")
    if not os.path.exists(demos_dir):
        print(f"Error: Demo directory not found: {demos_dir}")
        return

    # If we have a list of demos to run, process them sequentially
    if demo_list:
        # Special case for "all" - discover all available demo scripts
        if demo_list.strip().lower() == "all":
            # Find all Python files that aren't utility modules
            excluded_files = {"utils.py", "main.py", "main_demo.py", "__init__.py"}
            demo_files = []
            for file in os.listdir(demos_dir):
                if file.endswith(".py") and file not in excluded_files:
                    demo_name = file[:-3]  # Remove .py extension
                    demo_files.append(demo_name)

            # Check if we found any demos
            if not demo_files:
                print("No demo scripts found in the demo directory.")
                return

            print(f"Running all {len(demo_files)} demo scripts: {', '.join(demo_files)}")

            # Run each demo sequentially
            for demo in demo_files:
                print(f"\nRunning demo: {demo}")
                await _run_single_demo(demos_dir, demo, non_interactive)
            return
        else:
            # Normal case: run specific demos from the comma-separated list
            for demo in demo_list.split(","):
                demo = demo.strip()
                print(f"Running demo: {demo}")
                await _run_single_demo(demos_dir, demo, non_interactive)
            return

    # Run a single demo or the main menu
    if demo_name is None or demo_name == "main":
        if non_interactive:
            print("Cannot run main menu in non-interactive mode. Please specify a demo.")
            return

        # Run the main demo selection menu
        main_script = os.path.join(demos_dir, "main.py")
        if not os.path.exists(main_script):
            print(f"Error: Main demo script not found: {main_script}")
            return

        try:
            # Import and run the main script
            spec = importlib.util.spec_from_file_location("main", main_script)
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)

            # Run the main function
            asyncio.run(main_module.main())
        except Exception as e:
            print(f"Error running main demo: {str(e)}")
            import traceback

            traceback.print_exc()
    else:
        # Run a specific demo
        await _run_single_demo(demos_dir, demo_name, non_interactive)


async def _run_single_demo(demos_dir, demo_name, non_interactive=False):
    """Run a single demo script with the given name.

    Args:
        demos_dir: Path to the demos directory
        demo_name: Name of the demo script to run
        non_interactive: When True, run in non-interactive mode
    """
    demo_script = os.path.join(demos_dir, f"{demo_name}.py")
    if not os.path.exists(demo_script):
        print(f"Error: Demo script not found: {demo_script}")
        return

    try:
        # Import the demo script
        spec = importlib.util.spec_from_file_location(demo_name, demo_script)
        demo_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(demo_module)

        # Check if the module supports non-interactive mode
        if hasattr(demo_module, "main_non_interactive") and non_interactive:
            # Run non-interactive version
            await demo_module.main_non_interactive()
        else:
            # If the module doesn't have a non_interactive mode but we requested it
            if non_interactive:
                print(
                    f"Warning: Demo {demo_name} does not support non-interactive mode, running in normal mode"
                )

            # Run the main function
            if hasattr(demo_module, "main"):
                # Add non_interactive parameter if the function accepts it
                import inspect

                main_sig = inspect.signature(demo_module.main)
                if "non_interactive" in main_sig.parameters:
                    await demo_module.main(non_interactive=non_interactive)
                else:
                    await demo_module.main()
            else:
                print(f"Error: Demo {demo_name} has no main() function")
    except Exception as e:
        print(f"Error running demo: {str(e)}")
        import traceback

        traceback.print_exc()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run tests or demos for the Cursor AI agent")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--test",
        metavar="TEST_NAME",
        help='Specific test to run (e.g. "claude_agent" or "claude_agent.TestClaudeAgent")',
    )
    group.add_argument(
        "--demo",
        nargs="?",
        const="main",
        metavar="DEMO_NAME",
        help='Run a demo script (e.g. "chat_demo" or no value for main menu)',
    )
    group.add_argument(
        "--demo-list",
        metavar="DEMO1,DEMO2",
        help="Run multiple demos sequentially (comma-separated list)",
    )

    # Additional options for demo mode
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run demos in non-interactive mode (skips user input prompts)",
    )

    args = parser.parse_args()

    if args.test:
        # Run tests
        run_tests(args.test)
    elif args.demo is not None or args.demo_list is not None:
        # Run demo(s)
        asyncio.run(
            run_demo(
                demo_name=args.demo, non_interactive=args.non_interactive, demo_list=args.demo_list
            )
        )
    else:
        # Default: run all tests
        run_tests()


if __name__ == "__main__":
    main()
