#!/usr/bin/env python3

"""
Test script to verify imports work correctly.
Tests all important imports mentioned in README.md from agent, cursor_agent, and cursor_agent_tools packages.
"""

print("=== Testing base agent imports ===")

try:
    import agent
    print("Import of agent: SUCCESS")
except ImportError as e:
    print(f"Import of agent: FAILED - {e}")

try:
    import agent.tools.file_tools
    print("Import of agent.tools.file_tools: SUCCESS")
except ImportError as e:
    print(f"Import of agent.tools.file_tools: FAILED - {e}")

try:
    from agent.factory import create_agent
    print("Import of agent.factory.create_agent: SUCCESS")
except ImportError as e:
    print(f"Import of agent.factory.create_agent: FAILED - {e}")

try:
    from agent.base import BaseAgent
    print("Import of agent.base.BaseAgent: SUCCESS")
except ImportError as e:
    print(f"Import of agent.base.BaseAgent: FAILED - {e}")

try:
    from agent.claude_agent import ClaudeAgent
    print("Import of agent.claude_agent.ClaudeAgent: SUCCESS")
except ImportError as e:
    print(f"Import of agent.claude_agent.ClaudeAgent: FAILED - {e}")

try:
    from agent.openai_agent import OpenAIAgent
    print("Import of agent.openai_agent.OpenAIAgent: SUCCESS")
except ImportError as e:
    print(f"Import of agent.openai_agent.OpenAIAgent: FAILED - {e}")

try:
    from agent.ollama_agent import OllamaAgent
    print("Import of agent.ollama_agent.OllamaAgent: SUCCESS")
except ImportError as e:
    print(f"Import of agent.ollama_agent.OllamaAgent: FAILED - {e}")

try:
    from agent.permissions import PermissionOptions
    print("Import of agent.permissions.PermissionOptions: SUCCESS")
except ImportError as e:
    print(f"Import of agent.permissions.PermissionOptions: FAILED - {e}")

try:
    from agent.interact import run_agent_interactive, run_agent_chat
    print("Import of agent.interact functions: SUCCESS")
except ImportError as e:
    print(f"Import of agent.interact functions: FAILED - {e}")

print("\n=== Testing cursor_agent imports ===")

try:
    import cursor_agent
    print("Import of cursor_agent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent: FAILED - {e}")

try:
    from cursor_agent import create_agent
    print("Import of cursor_agent.create_agent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent.create_agent: FAILED - {e}")

try:
    from cursor_agent.agent import create_agent
    print("Import of cursor_agent.agent.create_agent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent.agent.create_agent: FAILED - {e}")

try:
    from cursor_agent.agent import BaseAgent
    print("Import of cursor_agent.agent.BaseAgent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent.agent.BaseAgent: FAILED - {e}")

try:
    from cursor_agent.agent import ClaudeAgent, OpenAIAgent
    print("Import of cursor_agent.agent model agents: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent.agent model agents: FAILED - {e}")

try:
    from cursor_agent.agent import run_agent_interactive, run_agent_chat
    print("Import of cursor_agent.agent interact functions: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent.agent interact functions: FAILED - {e}")

try:
    import cursor_agent.tools.file_tools
    print("Import of cursor_agent.tools.file_tools: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent.tools.file_tools: FAILED - {e}")

try:
    from cursor_agent.tools.file_tools import read_file, edit_file
    print("Import of cursor_agent.tools.file_tools functions: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent.tools.file_tools functions: FAILED - {e}")

print("\n=== Testing cursor_agent_tools imports ===")

try:
    import cursor_agent_tools
    print("Import of cursor_agent_tools: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools: FAILED - {e}")

try:
    from cursor_agent_tools import create_agent
    print("Import of cursor_agent_tools.create_agent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.create_agent: FAILED - {e}")

try:
    from cursor_agent_tools.agent import create_agent
    print("Import of cursor_agent_tools.agent.create_agent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.agent.create_agent: FAILED - {e}")

try:
    from cursor_agent_tools.agent import BaseAgent
    print("Import of cursor_agent_tools.agent.BaseAgent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.agent.BaseAgent: FAILED - {e}")

try:
    from cursor_agent_tools.agent import ClaudeAgent, OpenAIAgent, OllamaAgent
    print("Import of cursor_agent_tools.agent model agents: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.agent model agents: FAILED - {e}")

try:
    from cursor_agent_tools.agent import run_agent_interactive, run_agent_chat
    print("Import of cursor_agent_tools.agent interact functions: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.agent interact functions: FAILED - {e}")

try:
    from cursor_agent_tools.agent import PermissionOptions
    print("Import of cursor_agent_tools.agent.PermissionOptions: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.agent.PermissionOptions: FAILED - {e}")

try:
    import cursor_agent_tools.tools.file_tools
    print("Import of cursor_agent_tools.tools.file_tools: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.tools.file_tools: FAILED - {e}")

try:
    from cursor_agent_tools.tools.file_tools import read_file
    print("Import of read_file from cursor_agent_tools.tools.file_tools: SUCCESS")
except ImportError as e:
    print(f"Import of read_file from cursor_agent_tools.tools.file_tools: FAILED - {e}")

try:
    from cursor_agent_tools.tools.file_tools import edit_file, list_directory, delete_file
    print("Import of cursor_agent_tools.tools.file_tools advanced functions: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.tools.file_tools advanced functions: FAILED - {e}")

try:
    from cursor_agent_tools.tools.search_tools import codebase_search, grep_search, file_search
    print("Import of cursor_agent_tools.tools.search_tools functions: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.tools.search_tools functions: FAILED - {e}")

try:
    from cursor_agent_tools.tools.system_tools import run_terminal_command
    print("Import of cursor_agent_tools.tools.system_tools.run_terminal_cmd: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.tools.system_tools.run_terminal_cmd: FAILED - {e}")

print("\n=== Import testing completed ===")