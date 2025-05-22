"""
Compatibility layer for cursor_agent_tools.agent.

This module re-exports all functionality from cursor_agent_tools for backward compatibility.
"""

# Re-export main objects from cursor_agent_tools
from cursor_agent_tools import (
    # Core functionality
    BaseAgent,
    create_agent,
    run_agent_interactive,
    run_agent_chat,
    PermissionOptions,

    # Agent implementations
    ClaudeAgent,
    OpenAIAgent,
    OllamaAgent,
)

# Re-export from specific modules if needed
from cursor_agent_tools.permissions import (
    PermissionManager,
    PermissionRequest,
    PermissionStatus,
)

# Make tools available through the agent module if needed
from cursor_agent_tools import tools
