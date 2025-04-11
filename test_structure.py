#!/usr/bin/env python3

"""
Test script to verify imports work from both cursor_agent and cursor_agent_tools.
"""

print("Testing cursor_agent imports...")
try:
    from cursor_agent.tools.file_tools import read_file, edit_file, list_directory
    print("✅ cursor_agent.tools.file_tools imports succeeded")
except ImportError as e:
    print(f"❌ cursor_agent.tools.file_tools imports failed: {e}")

try:
    from cursor_agent.tools.search_tools import codebase_search, grep_search
    print("✅ cursor_agent.tools.search_tools imports succeeded")
except ImportError as e:
    print(f"❌ cursor_agent.tools.search_tools imports failed: {e}")

print("\nTesting cursor_agent_tools imports...")
try:
    from cursor_agent_tools.tools.file_tools import read_file, edit_file, list_directory
    print("✅ cursor_agent_tools.tools.file_tools imports succeeded")
except ImportError as e:
    print(f"❌ cursor_agent_tools.tools.file_tools imports failed: {e}")

try:
    from cursor_agent_tools.tools.search_tools import codebase_search, grep_search
    print("✅ cursor_agent_tools.tools.search_tools imports succeeded")
except ImportError as e:
    print(f"❌ cursor_agent_tools.tools.search_tools imports failed: {e}")

print("\nAll tests completed.") 