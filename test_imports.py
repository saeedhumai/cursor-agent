#!/usr/bin/env python3

"""
Test script to verify imports work correctly.
Tests both direct imports from cursor_agent_tools and backward-compatible imports from cursor_agent_tools.agent.
"""

print("=== Testing direct cursor_agent_tools imports ===")

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
    from cursor_agent_tools.base import BaseAgent
    print("Import of cursor_agent_tools.base.BaseAgent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.base.BaseAgent: FAILED - {e}")

try:
    from cursor_agent_tools.claude_agent import ClaudeAgent
    print("Import of cursor_agent_tools.claude_agent.ClaudeAgent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.claude_agent.ClaudeAgent: FAILED - {e}")

try:
    from cursor_agent_tools.openai_agent import OpenAIAgent
    print("Import of cursor_agent_tools.openai_agent.OpenAIAgent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.openai_agent.OpenAIAgent: FAILED - {e}")

try:
    from cursor_agent_tools.ollama_agent import OllamaAgent
    print("Import of cursor_agent_tools.ollama_agent.OllamaAgent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.ollama_agent.OllamaAgent: FAILED - {e}")

try:
    from cursor_agent_tools.permissions import PermissionOptions
    print("Import of cursor_agent_tools.permissions.PermissionOptions: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.permissions.PermissionOptions: FAILED - {e}")

try:
    from cursor_agent_tools.interact import run_agent_interactive, run_agent_chat
    print("Import of cursor_agent_tools.interact functions: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.interact functions: FAILED - {e}")

try:
    from cursor_agent_tools.factory import create_agent
    print("Import of cursor_agent_tools.factory.create_agent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.factory.create_agent: FAILED - {e}")

try:
    import cursor_agent_tools.tools.file_tools
    print("Import of cursor_agent_tools.tools.file_tools: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.tools.file_tools: FAILED - {e}")

try:
    from cursor_agent_tools.tools.file_tools import read_file
    print("Import of cursor_agent_tools.tools.file_tools.read_file: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.tools.file_tools.read_file: FAILED - {e}")

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
    print("Import of cursor_agent_tools.tools.system_tools.run_terminal_command: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.tools.system_tools.run_terminal_command: FAILED - {e}")

print("\n=== Testing backward-compatible cursor_agent_tools.agent imports ===")

try:
    import cursor_agent_tools.agent
    print("Import of cursor_agent_tools.agent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.agent: FAILED - {e}")

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
    from cursor_agent_tools.agent import ClaudeAgent
    print("Import of cursor_agent_tools.agent.ClaudeAgent: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.agent.ClaudeAgent: FAILED - {e}")

try:
    from cursor_agent_tools.agent.tools.file_tools import read_file
    print("Import of cursor_agent_tools.agent.tools.file_tools.read_file: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.agent.tools.file_tools.read_file: FAILED - {e}")

print("\n=== Import testing completed ===")