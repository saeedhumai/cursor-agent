"""
Cursor Agent Tools - Agent module providing the core functionality.
"""

# Import create_agent directly from agent.factory
from agent.factory import create_agent

# Include any other functions or classes that should be available
from agent.base import BaseAgent
from agent.claude_agent import ClaudeAgent
from agent.openai_agent import OpenAIAgent
from agent.ollama_agent import OllamaAgent
from agent.permissions import PermissionOptions
# Import interactive functionality
from agent.interact import run_agent_interactive, run_agent_chat

# Define what should be available when using "from cursor_agent_tools.agent import *"
__all__ = ["create_agent", "BaseAgent", "ClaudeAgent", "OpenAIAgent", "OllamaAgent",
           "run_agent_interactive", "run_agent_chat", "PermissionOptions"] 