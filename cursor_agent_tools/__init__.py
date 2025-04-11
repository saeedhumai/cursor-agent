"""
Cursor Agent Tools - A Python-based AI agent that replicates Cursor's coding assistant capabilities.

This package provides an AI agent with code generation, editing, and analysis capabilities,
working with both Claude (Anthropic) and OpenAI models.
"""

# Version information
__version__ = "0.1.25" 

# Import everything from the agent package
from agent import *

# Get all exports from agent
import agent
__all__ = agent.__all__

# Expose submodules
from agent import base, claude_agent, openai_agent, factory, permissions, interact 