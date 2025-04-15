"""
Re-export of the create_agent function from the main agent package.
"""

# Simply re-export the create_agent function
from agent.factory import create_agent

# Export the same symbols
__all__ = ["create_agent"] 