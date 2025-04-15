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

# Add direct import of create_agent to fix import issue
from agent.factory import create_agent

# Handle submodule imports using PEP 302 import hooks
import sys
import os
import importlib.abc
import importlib.util
from importlib.machinery import ModuleSpec
from types import ModuleType

# Create a more robust proxy module system
class AgentProxyFinder(importlib.abc.MetaPathFinder):
    def __init__(self, package_name, base_package):
        self.package_name = package_name
        self.base_package = base_package
    
    def find_spec(self, fullname, path, target=None):
        # Only handle modules within our package namespace
        if not fullname.startswith(f"{self.package_name}."):
            return None
            
        # Get the subpath after the package prefix
        parts = fullname.split('.')
        if len(parts) < 2:  # Must have at least one submodule
            return None
            
        # Get the corresponding path in the base package
        base_parts = [self.base_package] + parts[1:]
        base_module_name = '.'.join(base_parts)
        
        # Check if this is a module in the base package
        try:
            # Attempt to import from the base package
            spec = importlib.util.find_spec(base_module_name)
            
            if spec is not None:
                # Create a spec for our proxy module
                return ModuleSpec(
                    name=fullname,
                    loader=AgentProxyLoader(base_module_name, self.package_name),
                    origin=spec.origin,
                    is_package=spec.submodule_search_locations is not None
                )
        except ImportError:
            pass
            
        return None

class ProxyModule(ModuleType):
    """A proxy module that forwards all attribute access to the original module."""
    def __init__(self, name, original_module, parent_package=None):
        super().__init__(name)
        self._original_module = original_module
        self._parent_package = parent_package
        
        # Copy all attributes from the original module
        for attr_name in dir(original_module):
            if not attr_name.startswith('_'):  # Skip internal attributes
                try:
                    setattr(self, attr_name, getattr(original_module, attr_name))
                except (AttributeError, ImportError):
                    pass
        
        # Special handling for certain modules and functions
        if name.endswith('.agent'):
            # For .agent modules, add all needed imports from agent package
            try:
                # Import create_agent from parent package
                if parent_package:
                    parent_mod = importlib.import_module(parent_package)
                    if hasattr(parent_mod, 'create_agent'):
                        setattr(self, 'create_agent', parent_mod.create_agent)
                
                # Import all agent classes and utilities directly
                from agent.base import BaseAgent
                setattr(self, 'BaseAgent', BaseAgent)
                
                from agent.claude_agent import ClaudeAgent
                setattr(self, 'ClaudeAgent', ClaudeAgent)
                
                from agent.openai_agent import OpenAIAgent
                setattr(self, 'OpenAIAgent', OpenAIAgent)
                
                from agent.ollama_agent import OllamaAgent
                setattr(self, 'OllamaAgent', OllamaAgent)
                
                from agent.permissions import PermissionOptions
                setattr(self, 'PermissionOptions', PermissionOptions)
                
                from agent.interact import run_agent_interactive, run_agent_chat
                setattr(self, 'run_agent_interactive', run_agent_interactive)
                setattr(self, 'run_agent_chat', run_agent_chat)
            except (AttributeError, ImportError) as e:
                # Log the error but continue
                print(f"Warning: Could not import some agent classes: {e}")
                pass

    def __getattr__(self, name):
        # For any attributes not copied, delegate to the original module
        return getattr(self._original_module, name)

class AgentProxyLoader(importlib.abc.Loader):
    def __init__(self, base_module_name, parent_package=None):
        self.base_module_name = base_module_name
        self.parent_package = parent_package
    
    def create_module(self, spec):
        # Import the base module
        base_module = importlib.import_module(self.base_module_name)
        
        # Return a proxy module that wraps the base module
        return ProxyModule(spec.name, base_module, self.parent_package)
    
    def exec_module(self, module):
        # Nothing to execute, our proxy is already set up
        pass

# Register our hook
sys.meta_path.insert(0, AgentProxyFinder("cursor_agent_tools", "agent")) 