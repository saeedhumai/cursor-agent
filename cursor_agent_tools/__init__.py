import os
import importlib
import inspect
from typing import List, Type, Any, Dict, Callable, Optional, Union, Tuple

# Import core functionality directly
from .base import BaseAgent
from .factory import create_agent
from .permissions import PermissionOptions

# Import interact functions
from .interact import run_agent_interactive, run_agent_chat

# Explicitly import agent classes for better type checking
from .claude_agent import ClaudeAgent
from .openai_agent import OpenAIAgent
from .ollama_agent import OllamaAgent

# Dynamic agent class discovery (keeping for backward compatibility)
_agent_classes = {}


def _is_agent_class(obj: Any) -> bool:
    return (
        inspect.isclass(obj)
        and issubclass(obj, BaseAgent)
        and obj is not BaseAgent
    )


# Agent module directory
_current_dir = os.path.dirname(os.path.abspath(__file__))

# Load all Python files in the current directory that might contain agent implementations
for _file in os.listdir(_current_dir):
    if _file.endswith('_agent.py') and not _file.startswith('__'):
        _module_name = _file[:-3]  # Remove .py extension
        try:
            _module = importlib.import_module(f'.{_module_name}', package='cursor_agent_tools')
            # Find all agent classes in the module
            for _name, _obj in inspect.getmembers(_module, _is_agent_class):
                # Add to our agent classes dict
                _agent_classes[_name] = _obj
                # We no longer need to add to globals as we're explicitly importing
        except ImportError as e:
            print(f"Warning: Could not import {_module_name}: {e}")


# Create __all__ list dynamically
__all__ = ["BaseAgent", "create_agent", "PermissionOptions", "run_agent_interactive", "run_agent_chat",
           "ClaudeAgent", "OpenAIAgent", "OllamaAgent"] + list(_agent_classes.keys())
