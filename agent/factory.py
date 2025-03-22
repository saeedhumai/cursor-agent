from typing import Optional, Dict, Any

from .base import BaseAgent
from .claude_agent import ClaudeAgent
from .openai_agent import OpenAIAgent

def create_agent(provider: str, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs) -> BaseAgent:
    """
    Create an agent based on the specified provider.
    
    Args:
        provider: The provider to use ('claude' or 'openai')
        api_key: The API key to use
        model: The model to use
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        An instance of the appropriate agent
    """
    provider = provider.lower()
    
    if provider == 'claude' or provider == 'anthropic':
        if model is None:
            model = "claude-3-7-sonnet-latest"
        agent = ClaudeAgent(api_key=api_key, model=model, **kwargs)
    elif provider == 'openai':
        if model is None:
            model = "gpt-4o"
        agent = OpenAIAgent(api_key=api_key, model=model, **kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported providers are 'claude' and 'openai'.")
    
    # Register default tools
    agent.register_default_tools()
    
    return agent 