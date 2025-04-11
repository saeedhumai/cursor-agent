#!/usr/bin/env python3

"""
Test script to verify imports work correctly.
"""

try:
    import agent.tools.file_tools
    print("Import of agent.tools.file_tools: SUCCESS")
except ImportError as e:
    print(f"Import of agent.tools.file_tools: FAILED - {e}")

try:
    import cursor_agent_tools.tools.file_tools
    print("Import of cursor_agent_tools.tools.file_tools: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent_tools.tools.file_tools: FAILED - {e}")

try:
    import cursor_agent.tools.file_tools
    print("Import of cursor_agent.tools.file_tools: SUCCESS")
except ImportError as e:
    print(f"Import of cursor_agent.tools.file_tools: FAILED - {e}")

try:
    from cursor_agent_tools.tools.file_tools import read_file
    print("Import of read_file from cursor_agent_tools.tools.file_tools: SUCCESS")
except ImportError as e:
    print(f"Import of read_file from cursor_agent_tools.tools.file_tools: FAILED - {e}") 