#!/usr/bin/env python3
"""
Interactive Agent Module for cursor_agent package.

This module provides functions for running interactive agent conversations,
allowing multi-step problem solving and task completion.
"""

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

from .factory import create_agent
from .permissions import PermissionOptions

# Load environment variables from .env file
# Try to find the .env file in the parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Try in the current directory
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

# Define enhanced system prompt similar to what Cursor uses
CURSOR_SYSTEM_PROMPT = """
You are a powerful agentic AI coding assistant, powered by Claude. You operate in a coding environment.

You are pair programming with a USER to solve their coding task.
The task may require creating a new codebase, modifying or debugging an existing codebase, or simply answering a question.
Each time the USER sends a message, we automatically attach information about their current state, such as what files they have open, where their cursor is, recently viewed files, edit history in their session so far, and more.
This information may be relevant to the coding task, so consider it carefully.
Your main goal is to follow the USER's instructions at each message.

<tool_calling>
You have tools at your disposal to solve the coding task. Follow these rules regarding tool calls:
1. ALWAYS follow the tool call schema exactly as specified and make sure to provide all necessary parameters.
2. NEVER call tools that are not explicitly provided.
3. Only call tools when they are necessary. If the USER's task is general or you already know the answer, just respond without calling tools.
4. Before calling each tool, explain to the USER why you are calling it.
</tool_calling>

<making_code_changes>
When making code changes, NEVER output code to the USER, unless requested. Instead use the code edit tools to implement the change.
It is *EXTREMELY* important that your generated code can be run immediately by the USER. To ensure this, follow these instructions carefully:
1. Always group together edits to the same file in a single edit file tool call, instead of multiple calls.
2. If you're creating the codebase from scratch, create an appropriate dependency management file with package versions and a helpful README.
3. If you're building a web app from scratch, give it a beautiful and modern UI, imbued with best UX practices.
4. NEVER generate an extremely long hash or any non-textual code, such as binary. These are not helpful to the USER.
5. Unless you are appending some small edit to a file, or creating a new file, you MUST read the contents or section of what you're editing before editing it.
6. If you've introduced errors, fix them if clear how to. Do not make uneducated guesses.
</making_code_changes>

<searching_and_reading>
You have tools to search the codebase and read files. Follow these rules regarding tool calls:
1. If available, prefer the semantic search tool to grep search, file search, and list dir tools.
2. If you need to read a file, prefer to read larger sections of the file at once over multiple smaller calls.
3. If you have found a reasonable place to edit or answer, do not continue calling tools.
</searching_and_reading>

You MUST use the following format when citing code regions or blocks:
```12:15:app/components/Todo.tsx
// ... existing code ...
```
This is the ONLY acceptable format for code citations. The format is ```startLine:endLine:filepath where startLine and endLine are line numbers.

When breaking down complex tasks, consider each step carefully and use the appropriate tools for each part of the problem. Work iteratively toward a complete solution.
"""


# ANSI color codes for terminal output formatting
class Colors:
    HEADER = "\033[95m"  # Pink/Purple
    BLUE = "\033[94m"  # Blue
    CYAN = "\033[96m"  # Cyan
    GREEN = "\033[92m"  # Green
    YELLOW = "\033[93m"  # Yellow
    RED = "\033[91m"  # Red
    GRAY = "\033[90m"  # Gray
    ENDC = "\033[0m"  # End color
    BOLD = "\033[1m"  # Bold
    UNDERLINE = "\033[4m"  # Underline


async def print_status_before_agent(message: str, details: Optional[str] = None) -> None:
    """
    Simple utility function to print status messages before the agent is initialized.

    Args:
        message: The status message to print
        details: Optional details to include
    """
    print(f"\nℹ️ {message}")
    if details:
        print(f"  {details}")


async def print_agent_information(agent: Any, information_type: str, content: str, details: Optional[Union[Dict[str, Any], str]] = None) -> None:
    """
    Print formatted information from the agent to the user using AI-generated formatting.
    Uses the agent itself to generate styling and formatting.

    Args:
        agent: The agent instance to use for generating formatted output
        information_type: Type of information (thinking, tool_call, tool_result, plan, etc.)
        content: The main content to display
        details: Optional details/metadata to display (dict or string)
    """
    try:
        # Get terminal width (if needed for formatting)
        # terminal_width = os.get_terminal_size().columns
        # except Exception:
        #     terminal_width = 80  # Default if can't get terminal size

        # Convert details to a string representation if it's a dict
        details_str = ""
        if details:
            if isinstance(details, dict):
                details_str = "\n".join([f"{k}: {v}" for k, v in details.items()])
            else:
                details_str = str(details)

        # Create a temporary user info to avoid polluting the main conversation
        temp_user_info = {"temporary_context": True, "is_formatting_request": True}

        # Prepare the formatting prompt
        format_prompt = f"""Format the following "{information_type}" information for console display:

CONTENT: {content}

{f"DETAILS: {details_str}" if details else ""}

Use ANSI color codes to style the output with appropriate colors depending on the type.
Thinking: Gray
Response: Green
Error: Red
Status: Cyan/Blue
Tools: Yellow
Plan: Green with numbering
File operation: Blue
Command: Green

Return ONLY the formatted text with ANSI codes that I can directly print to the console.
Do not include explanation text or markdown code blocks."""

        # Use the agent to generate the formatted output
        formatted_output = await agent.chat(format_prompt, temp_user_info)

        # Print the output
        print(formatted_output)

    except Exception:
        # Fallback to basic formatting if the agent call fails
        separator = "─" * 80
        print(f"\n{separator}")
        print(f"[{information_type.upper()}]: {content}")
        if details:
            print(f"Details: {details}")
        print(f"{separator}")


async def check_for_user_input_request(agent: Any, response: str) -> Union[str, bool]:
    """
    Use the AI to determine if the agent's response is explicitly requesting user input.

    Args:
        agent: The agent instance to use for analyzing the response
        response: The response from the agent

    Returns:
        False if no input is needed, or a string containing the input prompt if needed
    """
    try:
        # Create a temporary user info to avoid polluting the main conversation
        temp_user_info = {"temporary_context": True, "is_system_request": True}

        # Ask the agent to analyze if input is needed
        analysis_prompt = f"""Analyze the following AI assistant response and determine if it is explicitly requesting user input or clarification:

RESPONSE: {response}

Rules for determining if input is needed:
1. Look for direct questions that require an answer
2. Look for phrases like "could you provide", "can you provide", "please let me know", etc.
3. Ignore rhetorical questions or statements where the AI says "I could" or "I will"
4. Check for any explicit request for information, preference, decision, or guidance

If user input IS needed:
- Return a concise prompt to show the user that captures what information is being requested
- Format it as: "INPUT_NEEDED: your prompt here"

If user input is NOT needed:
- Return only: "NO_INPUT_NEEDED"
"""

        # Get the analysis from the agent
        analysis: str = await agent.chat(analysis_prompt, temp_user_info)

        # Process the result
        if "INPUT_NEEDED:" in analysis:
            # Extract the prompt from the response
            user_prompt = analysis.split("INPUT_NEEDED:", 1)[1].strip()
            return user_prompt

        return False

    except Exception:
        # Fallback to simpler detection if the agent call fails
        # Check for common phrases that indicate the agent is asking for input
        input_request_phrases = [
            "could you provide", "can you provide", "please let me know",
            "what would you like", "how would you like", "do you have a preference"
        ]

        # Check for question marks (direct questions)
        if "?" in response:
            return "Please provide the requested information:"

        # Check for common phrases
        for phrase in input_request_phrases:
            if phrase in response.lower():
                return "Please provide the requested information:"

        return False


async def run_single_query(agent: Any, query: str, user_info: Optional[Dict[str, Any]] = None, use_custom_system_prompt: bool = False) -> str:
    """
    Run a single query and return the response.

    Args:
        agent: The initialized agent
        query: The query to send
        user_info: Optional user context information
        use_custom_system_prompt: Whether to use the custom system prompt

    Returns:
        The agent's response
    """
    # If we're using the custom system prompt, inject it into the agent
    if use_custom_system_prompt:
        original_system_prompt = agent.system_prompt
        agent.system_prompt = CURSOR_SYSTEM_PROMPT
        agent_response: str = await agent.chat(query, user_info)
        # Restore original system prompt
        agent.system_prompt = original_system_prompt
        return agent_response

    response_text: str = await agent.chat(query, user_info)
    return response_text


async def run_agent_interactive(
    model: str = "claude-3-5-sonnet-latest",
    initial_query: str = "",
    max_iterations: int = 10,
    auto_continue: bool = True,
) -> str:
    """
    Run the agent in interactive mode, allowing back-and-forth conversation.

    Args:
        model: The model to use (e.g., 'claude-3-5-sonnet-latest', 'gpt-4o')
        initial_query: The initial task/query to send to the agent
        max_iterations: Maximum number of iterations to perform
        auto_continue: If True, continue automatically; otherwise prompt user after each step

    Returns:
        A summary of the conversation outcome
    """
    await print_status_before_agent(f"Creating agent with model {model}...")

    # Create permission options with yolo mode disabled and allowing only ls and cat commands
    permissions = PermissionOptions(
        yolo_mode=False,
        command_allowlist=["ls", "cat"],
        delete_file_protection=True
    )

    # Create agent with the configured permissions
    agent = create_agent(model=model, permissions=permissions)
    agent.system_prompt = CURSOR_SYSTEM_PROMPT
    agent.register_default_tools()

    # Now we can use the agent with our print function
    await print_agent_information(agent, "status", "Initializing conversation with initial task")
    await print_agent_information(agent, "status", "Task description", initial_query)

    # Initialize detailed conversation context (similar to Cursor)
    workspace_path = os.getcwd()
    user_info: Dict[str, Any] = {
        "open_files": [],  # Files currently open
        "cursor_position": None,  # Current cursor position
        "recent_files": [],  # Recently accessed files
        "os": sys.platform,  # OS information
        "workspace_path": workspace_path,  # Current workspace
        "command_history": [],  # Recently executed commands
        "tool_calls": [],  # History of tool calls
        "tool_results": [],  # Results of tool calls
        "file_contents": {},  # Cache of file contents
        "user_edits": [],  # Recent edits made by user
        "recent_errors": [],  # Recent errors encountered
    }

    # Track created/modified files to populate open_files
    created_or_modified_files: set[str] = set()

    # Multi-turn conversation loop
    iteration = 1
    query = initial_query

    # Configuration for tool call limits per iteration
    max_tool_calls_per_iteration = 5  # Maximum number of tool calls before asking for confirmation
    current_iteration_tool_calls = 0  # Counter for tool calls in the current iteration - initialize once

    # Prepend planning instructions only on first iteration
    if iteration == 1:
        await print_agent_information(agent, "thinking", "Breaking down the task and creating a plan...")
        query = f"""I'll help you complete this task step by step. I'll break it down and use tools like reading/creating/editing files and running commands as needed.

TASK: {initial_query}

First, I'll create a plan for how to approach this task, then implement it step by step.
"""

    while iteration <= max_iterations:
        await print_agent_information(agent, "status", f"Running iteration {iteration}/{max_iterations}")
        await print_agent_information(
            agent, "status", "Processing query", query[:100] + "..." if len(query) > 100 else query
        )

        try:
            # Update user_info with current workspace state - similar to how Cursor updates context
            user_info = update_workspace_state(user_info, created_or_modified_files)

            # Show thinking animation
            await print_agent_information(agent, "thinking", "Processing your request...")

            # Get agent response with Cursor-like system prompt
            start_time = time.time()

            # Use the enhanced system prompt (like Cursor does)
            response = await run_single_query(
                agent, query, user_info, use_custom_system_prompt=True
            )

            duration = time.time() - start_time

            # Print full response
            await print_agent_information(agent, "response", response)
            await print_agent_information(agent, "status", f"Response generated in {duration:.2f} seconds")

            # Extract and track tool calls from the response
            # This mimics how Cursor extracts and processes tool calls
            tool_calls = extract_tool_calls(response)
            for tool_call in tool_calls:
                tool_name = tool_call.get("tool", "")
                args = tool_call.get("args", {})

                # Ensure tool_name is a string
                await print_agent_information(agent, "tool_call", str(tool_name), args)

                # Make sure tool_calls is a list before appending
                if isinstance(user_info["tool_calls"], list):
                    user_info["tool_calls"].append(tool_call)
                else:
                    user_info["tool_calls"] = [tool_call]

                current_iteration_tool_calls += 1

                # Track file operations to update open_files
                if tool_call.get("tool") == "create_file" or tool_call.get("tool") == "edit_file":
                    file_path = tool_call.get("args", {}).get("file_path") or tool_call.get(
                        "args", {}
                    ).get("target_file")
                    if file_path:
                        created_or_modified_files.add(file_path)
                        await print_agent_information(agent, "file_operation", f"Modified {file_path}")

                # Track terminal commands
                if tool_call.get("tool") == "run_terminal_cmd":
                    command = tool_call.get("args", {}).get("command")
                    if command:
                        # Make sure command_history is a list before appending
                        if isinstance(user_info["command_history"], list):
                            user_info["command_history"].append(command)
                        else:
                            user_info["command_history"] = [command]
                        # Convert command to string to ensure it's a valid type
                        await print_agent_information(agent, "command", f"Executed command: {command}")

                # Check if we've reached the tool call limit for this iteration
                if current_iteration_tool_calls >= max_tool_calls_per_iteration:
                    await print_agent_information(agent, "status", f"Reached maximum of {max_tool_calls_per_iteration} tool calls in this iteration")
                    print(f"\n{Colors.YELLOW}The agent has made {current_iteration_tool_calls} tool calls in this iteration.{Colors.ENDC}")
                    print(f"{Colors.YELLOW}Would you like to continue allowing the agent to make more changes?{Colors.ENDC}")
                    choice = input(f"{Colors.GREEN}Continue? (y/n): {Colors.ENDC}")
                    if choice.lower() != 'y':
                        await print_agent_information(agent, "status", "User requested to stop after reaching tool call limit.")
                        # Continue to the next part of the current iteration, but don't perform more tool calls
                        break
                    else:
                        # Instead of resetting the counter, just increase the limit for this iteration
                        max_tool_calls_per_iteration += 5
                        await print_agent_information(agent, "status", f"Continuing with tool calls. New limit is {max_tool_calls_per_iteration}.")

            # Check if task is complete
            if is_task_complete(response):
                await print_agent_information(agent, "status", "Task has been completed successfully!")
                break

            # Check if the agent is explicitly asking for user input
            user_prompt = await check_for_user_input_request(agent, response)
            if user_prompt:
                await print_agent_information(agent, "status", "The agent is requesting additional information from you.")
                user_input = input(f"{Colors.GREEN}{user_prompt} {Colors.ENDC}")

                # Get a continuation prompt that incorporates the user input
                query = await get_continuation_prompt(agent, iteration, response, user_input)

                # Reset tool call counter when user provides new input - this is a new logical iteration
                current_iteration_tool_calls = 0
                iteration += 1
                continue

            # Determine next step (with more Cursor-like continuation)
            if auto_continue:
                # Auto-continue with a more natural prompt generated by the agent
                query = await get_continuation_prompt(agent, iteration, response)
                await print_agent_information(agent, "status", "Automatically continuing to next step...")
                time.sleep(2)  # Brief pause for readability
            else:
                # No defined objective, continuation, prompt user for direction
                await print_agent_information(agent, "response", "How can I help you further with this task? Please provide any guidance or specific requests.")
                user_input = input(f"{Colors.GREEN}Your input: {Colors.ENDC}")

                # Get a continuation prompt that incorporates the user input
                query = await get_continuation_prompt(agent, iteration, response, user_input)

                # Reset tool call counter when user provides new input
                current_iteration_tool_calls = 0
                iteration += 1
                continue

            iteration += 1

            # Limit length of history in user_info to prevent context overflow
            # This is similar to how Cursor manages context window limits
            if isinstance(user_info["tool_calls"], list) and len(user_info["tool_calls"]) > 10:
                user_info["tool_calls"] = user_info["tool_calls"][-10:]
            if isinstance(user_info["command_history"], list) and len(user_info["command_history"]) > 5:
                user_info["command_history"] = user_info["command_history"][-5:]

            # Print an informative message if the agent's response suggests a task is still in progress
            if auto_continue and "in progress" in response.lower() and iteration < max_iterations:
                print(f"{Colors.YELLOW}Task appears to be in progress. Continuing automatically...{Colors.ENDC}")

            # If this was the last iteration, inform the user
            if iteration >= max_iterations:
                print(f"{Colors.RED}Reached maximum iterations ({max_iterations}). Stopping.{Colors.ENDC}")

            # Check if task is complete
            if is_task_complete(response):
                print(f"{Colors.GREEN}Task appears to be complete!{Colors.ENDC}")
                return response

        except Exception as e:
            await print_agent_information(agent, "error", f"Error in iteration {iteration}", str(e))
            user_info["recent_errors"].append(str(e))

            print(f"\n{Colors.YELLOW}Options:{Colors.ENDC}")
            print(f"{Colors.YELLOW}1. Retry this iteration{Colors.ENDC}")
            print(f"{Colors.YELLOW}2. Continue with error information{Colors.ENDC}")
            print(f"{Colors.YELLOW}3. End the conversation{Colors.ENDC}")
            choice = input(f"{Colors.GREEN}Enter your choice (1-3): {Colors.ENDC}")

            if choice == "1":
                # Just retry the same iteration
                continue
            elif choice == "2":
                # Continue but inform the agent about the error
                query = f"There was an error in the previous step: {str(e)}. Please adjust your approach and continue."
                iteration += 1
            else:
                break

    await print_agent_information(agent, "status", f"Conversation ended after {iteration-1} iterations.")
    return "Conversation complete."


def extract_tool_calls(response: str) -> List[Dict[str, Any]]:
    """
    Extract tool calls from the agent's response.

    Args:
        response: The response from the agent

    Returns:
        A list of tool call dictionaries
    """
    tool_calls = []

    # Simple extraction based on common patterns
    # In a real implementation, you would use more robust parsing

    # Look for patterns like "```python\nagent.create_file(...)" or "I'll create a file..."
    # followed by tool usage

    # This is a simplified example - Cursor uses more sophisticated parsing
    if "create_file" in response:
        # Extract file creation details
        lines = response.split("\n")
        for i, line in enumerate(lines):
            if "create_file" in line and i < len(lines) - 1:
                tool_calls.append(
                    {
                        "tool": "create_file",
                        "args": {
                            "file_path": (
                                lines[i + 1].strip().strip("\"'")
                                if "file_path" in line
                                else "unknown"
                            ),
                        },
                    }
                )

    if "edit_file" in response:
        # Extract file editing details
        lines = response.split("\n")
        for i, line in enumerate(lines):
            if "edit_file" in line and i < len(lines) - 1:
                tool_calls.append(
                    {
                        "tool": "edit_file",
                        "args": {
                            "target_file": (
                                lines[i + 1].strip().strip("\"'")
                                if "target_file" in line
                                else "unknown"
                            ),
                        },
                    }
                )

    if "run_terminal_cmd" in response:
        # Extract terminal commands
        lines = response.split("\n")
        for i, line in enumerate(lines):
            if "run_terminal_cmd" in line and i < len(lines) - 1:
                tool_calls.append(
                    {
                        "tool": "run_terminal_cmd",
                        "args": {
                            "command": (
                                lines[i + 1].strip().strip("\"'")
                                if "command" in line
                                else "unknown"
                            ),
                        },
                    }
                )

    return tool_calls


def is_task_complete(response: str) -> bool:
    """
    Analyze if the response suggests the task is complete.

    Args:
        response: The response from the agent

    Returns:
        True if the task appears to be complete, False otherwise
    """
    # Look for various forms of task completion statements
    completion_indicators = [
        "task complete",
        "task is complete",
        "completed all the required tasks",
        "successfully implemented all",
        "all requirements have been met",
        "implementation is now complete",
        "successfully created all the necessary",
        "the project is now ready",
        "everything is now implemented",
        "all features are now implemented",
    ]

    response_lower = response.lower()

    # Check for completion indicators with additional context check
    # (Cursor does more sophisticated analysis)
    for indicator in completion_indicators:
        if indicator in response_lower:
            # Check if it's a real completion and not part of a plan
            if (
                "next"
                not in response_lower[
                    response_lower.index(indicator) : response_lower.index(indicator) + 50
                ]
            ):
                return True

    # Check for summary sections that typically indicate completion
    if (
        "summary of what we've accomplished" in response_lower
        and "next steps" not in response_lower
    ):
        return True

    # Check for concluding sections
    if ("in conclusion" in response_lower or "to summarize" in response_lower) and (
        "all requirements" in response_lower or "all functionality" in response_lower
    ):
        return True

    return False


async def get_continuation_prompt(agent: Any, iteration: int, last_response: str, user_input: Optional[str] = None) -> str:
    """
    Generate a continuation prompt for the agent to continue its work.

    Args:
        agent: The agent instance
        iteration: Current iteration number
        last_response: The agent's last response
        user_input: Optional user input to incorporate

    Returns:
        A prompt string for the agent to continue
    """
    try:
        # Create a temporary user info to avoid polluting the main conversation
        temp_user_info = {"temporary_context": True, "is_system_request": True}

        # Extract what happened in the last response
        # We'll try to capture:
        # 1. What tools were called
        # 2. What results/progress was made
        # 3. What issues or errors occurred

        # Base analysis prompt
        analysis_prompt = f"""Analyze the following assistant response from iteration {iteration} and help create a continuation prompt.

RESPONSE: {last_response}

Analyze and summarize what happened in this interaction, focusing on:
1. What tools were called and their results
2. What was accomplished or learned
3. What issues or errors occurred that need to be fixed
4. What next steps were planned but not executed

Return a concise 1-2 sentence summary of the current state and progress.
"""

        # Use the agent to generate the continuation prompt
        continuation_prompt: str = await agent.chat(analysis_prompt, temp_user_info)

        return continuation_prompt

    except Exception as ex:
        # If there's an error getting a continuation prompt, just return the response
        print(f"Error getting continuation prompt: {str(ex)}")
        # Return a default continuation prompt
        return "Continue with the next steps based on the previous results."


def update_workspace_state(user_info: Dict[str, Any], created_or_modified_files: set) -> Dict[str, Any]:
    """
    Update the user_info with information about files that were created or modified.

    Args:
        user_info: The user information dictionary
        created_or_modified_files: Set of files that were created or modified

    Returns:
        Updated user_info dictionary
    """
    # Save the current workspace path
    workspace_path = user_info.get("workspace_path", os.getcwd())

    # Update open_files with recently created/modified files
    # (in Cursor, this would reflect actually open files in the editor)
    if created_or_modified_files:
        if "open_files" not in user_info or not isinstance(user_info["open_files"], list):
            user_info["open_files"] = []

        for file_path in created_or_modified_files:
            if file_path not in user_info["open_files"]:
                user_info["open_files"].append(file_path)
                # Can't use async function in a sync function
                print(f"\n📄 File Operation: Added {file_path} to open files")

    # Simulate cursor position in the most recently modified file
    if "open_files" in user_info and isinstance(user_info["open_files"], list) and user_info["open_files"]:
        most_recent_file = user_info["open_files"][-1]
        try:
            line_count = 0
            with open(most_recent_file, "r") as f:
                line_count = len(f.readlines())

            user_info["cursor_position"] = {
                "file": most_recent_file,
                "line": min(10, line_count),  # Arbitrary position for simulation
                "column": 0,
            }
        except Exception as ex:
            print(f"Error setting cursor position: {str(ex)}")

    # Update list of recently modified files across the workspace
    recent_files = []
    try:
        for root, _, files in os.walk(workspace_path):
            for file in files:
                if file.endswith(
                    (".py", ".txt", ".md", ".json", ".yaml", ".yml", ".js", ".ts", ".html", ".css")
                ):
                    file_path = os.path.join(root, file)
                    try:
                        recent_files.append(
                            {"path": file_path, "modified": os.path.getmtime(file_path)}
                        )
                    except Exception as ex:
                        print(f"Error getting file info: {str(ex)}")

        # Sort by modification time and take the 10 most recent
        recent_files = sorted(recent_files, key=lambda x: x["modified"], reverse=True)[:10]
        recent_file_paths = [file["path"] for file in recent_files]
        user_info["recent_files"] = recent_file_paths

        # Update file_contents for open files
        # This is similar to how Cursor provides file contents in context
        if "open_files" in user_info and isinstance(user_info["open_files"], list) and user_info["file_contents"] is not None:
            if not isinstance(user_info["file_contents"], dict):
                user_info["file_contents"] = {}

            for file_path in user_info["open_files"]:
                try:
                    if os.path.isfile(file_path):
                        with open(file_path, "r") as f:
                            file_content = f.read()
                            user_info["file_contents"][file_path] = file_content
                except Exception as ex:
                    # Can't use async function in a sync function
                    print(f"\n❌ Error: Error reading file {file_path}")
                    print(f"  {str(ex)}")

    except Exception as ex:
        # Can't use async function in a sync function
        print(f"\n❌ Error: Error updating workspace state: {str(ex)}")

    return user_info


async def run_agent_chat(
    model: str = "claude-3-5-sonnet-latest",
    query: str = "",
) -> str:
    """
    Run a single agent chat without interactive mode.

    Args:
        model: The model to use (e.g., 'claude-3-5-sonnet-latest', 'gpt-4o')
        query: The query to send to the agent

    Returns:
        The agent's response
    """
    # Create a simple fallback print function for before the agent is initialized
    await print_status_before_agent(f"Creating agent with model {model}...")
    agent = create_agent(model=model)
    agent.register_default_tools()

    await print_agent_information(agent, "status", f"Sending query to agent: {query}")
    response: str = await agent.chat(query)

    await print_agent_information(agent, "response", response)

    return response


# Main entry point and argument handling remain in the original main.py file
# This module is designed to be imported and used by other modules
