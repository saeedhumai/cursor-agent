#!/usr/bin/env python3
"""
Utility Functions for Cursor Agent Examples

This module provides helper functions for formatting terminal output,
creating user context information, and other utilities used across
the demo examples.
"""

import os
import platform
import sys
from typing import Any, Dict, List, Optional


# ANSI color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"  # More semantic name than ENDC
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    GRAY = "\033[90m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"


def print_user_query(query: str) -> None:
    """Print a user query."""
    print(f"{Colors.GREEN}USER QUERY: {query}{Colors.RESET}")


# Add backward compatibility for print_user_input
print_user_input = print_user_query


def print_assistant_response(text: str) -> None:
    """Print assistant response with appropriate formatting."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Assistant: {Colors.RESET}{text}")


def print_tool_call(tool_name: str, **kwargs) -> None:
    """Print tool call with appropriate formatting."""
    print(f"\n{Colors.GRAY}[Tool Call] {tool_name}{Colors.RESET}")
    if kwargs:
        for key, value in kwargs.items():
            print(f"{Colors.GRAY}  {key}: {value}{Colors.RESET}")


def print_tool_result(tool_name: str, result: str) -> None:
    """Print tool result with appropriate formatting."""
    if isinstance(result, str):
        # Truncate long results for display
        if len(result) > 500:
            display_result = result[:500] + "... [truncated]"
        else:
            display_result = result
        print(f"\n{Colors.GRAY}[Tool Result] {tool_name}: {display_result}{Colors.RESET}")
    else:
        print(f"\n{Colors.GRAY}[Tool Result] {tool_name}: {result}{Colors.RESET}")


def print_system_message(text: str) -> None:
    """Print system message with appropriate formatting."""
    print(f"{Colors.YELLOW}[System] {text}{Colors.RESET}")


def print_error(text: str) -> None:
    """Print error message with appropriate formatting."""
    print(f"{Colors.RED}[Error] {text}{Colors.RESET}")


def print_separator() -> None:
    """Print a separator line."""
    print(f"{Colors.GRAY}{'=' * 80}{Colors.RESET}")


def create_user_info(open_files: Optional[List[str]] = None, workspace_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a user info dict for the agent with workspace context.
    
    Args:
        open_files: List of currently open files
        workspace_path: Path to the current workspace
        
    Returns:
        Dict with user context information
    """
    if open_files is None:
        open_files = []
        
    if workspace_path is None:
        workspace_path = os.getcwd()
        
    return {
        "open_files": open_files,
        "workspace_path": workspace_path,
        "os": platform.system(),
        "python_version": sys.version,
    }


def clear_screen() -> None:
    """Clear the terminal screen in a cross-platform way."""
    os.system("cls" if platform.system() == "Windows" else "clear")


def print_info(message: str) -> None:
    """Print an informational message."""
    print(f"{Colors.MAGENTA}INFO: {message}{Colors.RESET}")


def print_assistant(prefix: str = "") -> None:
    """Print an assistant message prefix."""
    print(f"{Colors.CYAN}{prefix}{Colors.RESET}", end="")


def print_prompt(prompt: str) -> None:
    """Print a prompt for user input."""
    print(f"{Colors.GREEN}{prompt}{Colors.RESET}", end="")

def print_user_message(message: str) -> None:
    """Print a user message."""
    print(f"{Colors.BLUE}USER: {message}{Colors.RESET}")
