#!/usr/bin/env python3
"""
Utility functions for the demo scripts.
This module provides helper functions for colored output and other utilities.
"""

import os
import sys
from typing import Any, Dict, Optional


# ANSI color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    GRAY = "\033[90m"


def print_user_input(text: str) -> None:
    """Print user input with appropriate formatting."""
    print(f"\n{Colors.BOLD}{Colors.GREEN}User: {Colors.ENDC}{text}")


def print_assistant_response(text: str) -> None:
    """Print assistant response with appropriate formatting."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Assistant: {Colors.ENDC}{text}")


def print_tool_call(tool_name: str, **kwargs) -> None:
    """Print tool call with appropriate formatting."""
    print(f"\n{Colors.YELLOW}[Tool Call]: {tool_name}{Colors.ENDC}")
    if kwargs:
        for key, value in kwargs.items():
            print(f"  {Colors.GRAY}└─ {key}: {value}{Colors.ENDC}")


def print_tool_result(tool_name: str, result: str) -> None:
    """Print tool result with appropriate formatting."""
    # Truncate long results for better display
    if len(result) > 500:
        result = result[:500] + "... (truncated)"

    print(f"{Colors.CYAN}[Tool Result]: {tool_name}{Colors.ENDC}")
    print(f"  {Colors.GRAY}{result}{Colors.ENDC}")


def print_system_message(text: str) -> None:
    """Print system message with appropriate formatting."""
    print(f"\n{Colors.HEADER}[System]: {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    """Print error message with appropriate formatting."""
    print(f"\n{Colors.RED}[Error]: {text}{Colors.ENDC}")


def print_separator() -> None:
    """Print a separator line."""
    terminal_width = os.get_terminal_size().columns
    print(f"\n{Colors.GRAY}{'-' * terminal_width}{Colors.ENDC}")


def create_user_info(open_files: Optional[list] = None) -> Dict[str, Any]:
    """Create a sample user info dictionary for testing."""
    return {
        "open_files": open_files or ["test_file.py"],
        "cursor_position": {"file": "test_file.py", "line": 10},
        "recent_files": ["other_file.py"],
        "os": "darwin",
        "workspace_path": "/tmp/test_workspace",
    }


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")
