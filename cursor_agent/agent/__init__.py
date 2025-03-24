"""
Cursor Agent - Agent module providing the core functionality.
"""

# Import and re-export the create_agent function from the original agent.factory
from agent.factory import create_agent

# Include any other functions or classes that should be available
from agent.base import BaseAgent
from agent.claude_agent import ClaudeAgent
from agent.openai_agent import OpenAIAgent
from agent.permissions import PermissionOptions
# Import interactive functionality
from agent.interact import run_agent_interactive, run_agent_chat

# Define what should be available when using "from cursor_agent.agent import *"
__all__ = ["create_agent", "BaseAgent", "ClaudeAgent", "OpenAIAgent", 
           "run_agent_interactive", "run_agent_chat", "PermissionOptions"] 