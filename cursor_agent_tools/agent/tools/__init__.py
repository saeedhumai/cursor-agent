"""
Compatibility layer for cursor_agent_tools.agent.tools.

This module re-exports tools modules from cursor_agent_tools.tools for backward compatibility.
"""

# Import tool modules
import cursor_agent_tools.tools.file_tools as file_tools
import cursor_agent_tools.tools.search_tools as search_tools
import cursor_agent_tools.tools.system_tools as system_tools
import cursor_agent_tools.tools.register_tools as register_tools

# Re-export all from the tool modules
__all__ = (
    file_tools.__all__
    + search_tools.__all__
    + system_tools.__all__
    + register_tools.__all__
)

# Try to import optional tools that might be available
try:
    import cursor_agent_tools.tools.image_tools as image_tools
    __all__ += image_tools.__all__
except ImportError:
    pass

try:
    import cursor_agent_tools.tools.web_tools as web_tools  # type: ignore
    __all__ += web_tools.__all__
except ImportError:
    pass
