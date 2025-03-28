"""
Utility module for registering agent tools with permission handling.
"""

from typing import Any

from ..logger import get_logger
from . import (
    file_tools,
    search_tools,
    system_tools,
    image_tools,
)

# Initialize logger
logger = get_logger(__name__)


def register_default_tools(agent: Any) -> None:
    """
    Register all available tools with the provided agent.

    The agent reference is automatically injected into the tool functions
    by the agent framework for permission handling.

    Args:
        agent: The agent instance to register tools with
    """
    logger.info("Registering default tools for agent")
    
    # File tools with permission checks
    agent.register_tool(
        "read_file",
        lambda target_file, offset=None, limit=None, should_read_entire_file=None: file_tools.read_file(
            target_file, offset, limit, should_read_entire_file, agent
        ),
        "Read the contents of a file.",
        {
            "type": "object",
            "properties": {
                "target_file": {"type": "string", "description": "The path of the file to read"},
                "offset": {
                    "type": "integer",
                    "description": "The line number to start reading from (1-indexed)",
                },
                "limit": {"type": "integer", "description": "The number of lines to read"},
                "should_read_entire_file": {
                    "type": "boolean",
                    "description": "Whether to read the entire file",
                },
            },
            "required": ["target_file"],
        },
    )
    logger.debug("Registered tool: read_file")

    agent.register_tool(
        "edit_file",
        lambda target_file, instructions, code_edit: file_tools.edit_file(
            target_file, instructions, code_edit, agent
        ),
        "Edit a file in the codebase.",
        {
            "type": "object",
            "properties": {
                "target_file": {"type": "string", "description": "The target file to modify"},
                "instructions": {
                    "type": "string",
                    "description": "A single sentence instruction describing the edit",
                },
                "code_edit": {"type": "string", "description": "The precise lines of code to edit"},
            },
            "required": ["target_file", "instructions", "code_edit"],
        },
    )
    logger.debug("Registered tool: edit_file")

    agent.register_tool(
        "delete_file",
        lambda target_file: file_tools.delete_file(target_file, agent),
        "Delete a file at the specified path.",
        {
            "type": "object",
            "properties": {
                "target_file": {"type": "string", "description": "The path of the file to delete"},
            },
            "required": ["target_file"],
        },
    )
    logger.debug("Registered tool: delete_file")

    agent.register_tool(
        "create_file",
        lambda file_path, content: file_tools.create_file(file_path, content, agent),
        "Create a new file with the given content.",
        {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path where the file should be created",
                },
                "content": {"type": "string", "description": "Content to write to the file"},
            },
            "required": ["file_path", "content"],
        },
    )
    logger.debug("Registered tool: create_file")

    agent.register_tool(
        "list_directory",
        lambda relative_workspace_path: file_tools.list_directory(relative_workspace_path, agent),
        "List the contents of a directory.",
        {
            "type": "object",
            "properties": {
                "relative_workspace_path": {
                    "type": "string",
                    "description": "Path to list contents of",
                },
            },
            "required": ["relative_workspace_path"],
        },
    )
    logger.debug("Registered tool: list_directory")

    # System tools
    agent.register_tool(
        "run_terminal_command",
        lambda command, explanation=None, is_background=False, require_user_approval=True: system_tools.run_terminal_command(
            command, explanation, is_background, require_user_approval, agent
        ),
        "Run a terminal command. IMPORTANT: Always use non-interactive flags that works for the command you are running (like --yes, -y, --no-interaction, yes | , --quiet, or equivalent). i.e git commit -m 'commit message' --no-interaction or yes | npx create-next-app@latest --no-interactive",
        {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The terminal command to execute. MUST be non-interactive and should include all necessary flags to prevent or bypass prompts."},
                "explanation": {
                    "type": "string",
                    "description": "Explanation of why this command needs to be run",
                },
                "is_background": {
                    "type": "boolean",
                    "description": "Whether to run in the background",
                },
                "require_user_approval": {
                    "type": "boolean",
                    "description": "Whether user approval is required",
                },
            },
            "required": ["command"],
        },
    )
    logger.debug("Registered tool: run_terminal_command")

    # Search tools
    agent.register_tool(
        "codebase_search",
        lambda query, target_directories=None: search_tools.codebase_search(
            query, target_directories, agent
        ),
        "Search the codebase using semantic search.",
        {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant code",
                },
                "target_directories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Directories to search over",
                },
            },
            "required": ["query"],
        },
    )
    logger.debug("Registered tool: codebase_search")

    agent.register_tool(
        "grep_search",
        lambda query, case_sensitive=False, include_pattern=None, exclude_pattern=None: search_tools.grep_search(
            query, case_sensitive, include_pattern, exclude_pattern, agent
        ),
        "Fast text-based search using regex patterns.",
        {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The regex pattern to search for"},
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Whether the search is case sensitive",
                },
                "include_pattern": {
                    "type": "string",
                    "description": "Glob pattern for files to include",
                },
                "exclude_pattern": {
                    "type": "string",
                    "description": "Glob pattern for files to exclude",
                },
            },
            "required": ["query"],
        },
    )
    logger.debug("Registered tool: grep_search")

    agent.register_tool(
        "file_search",
        lambda query: search_tools.file_search(query, agent),
        "Fast file search based on fuzzy matching against file path.",
        {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Fuzzy filename to search for"},
            },
            "required": ["query"],
        },
    )
    logger.debug("Registered tool: file_search")

    # Web search
    agent.register_tool(
        "web_search",
        lambda search_term: search_tools.web_search(search_term, agent),
        "Search the web for information.",
        {
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": "The search term to look up on the web",
                },
            },
            "required": ["search_term"],
        },
    )
    logger.debug("Registered tool: web_search")
    
    # Image query tool
    agent.register_tool(
        "query_images",
        lambda query, image_paths: image_tools.query_images(query, image_paths, agent),
        "Query an AI model about one or more images.",
        {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The question or query about the image(s)",
                },
                "image_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of local paths to image files to analyze",
                },
            },
            "required": ["query", "image_paths"],
        },
    )
    logger.debug("Registered tool: query_images")
    
    logger.info(f"Successfully registered {len(agent.available_tools)} tools")
