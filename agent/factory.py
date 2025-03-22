from typing import Any, Optional, Union

from .claude_agent import ClaudeAgent
from .openai_agent import OpenAIAgent


def create_agent(
    provider: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs: Any
) -> Union[ClaudeAgent, OpenAIAgent]:
    """
    Create an agent based on the specified provider.

    Args:
        provider: The provider to use ('claude' or 'openai')
        api_key: The API key to use
        model: The model to use
        **kwargs: Additional keyword arguments to pass to the agent constructor

    Returns:
        An instance of the requested agent type
    """
    if provider.lower() == "claude":
        model_str = "claude-3-5-sonnet-latest" if model is None else model
        return ClaudeAgent(api_key=api_key, model=model_str, **kwargs)
    elif provider.lower() == "openai":
        model_str = "gpt-4o" if model is None else model
        return OpenAIAgent(api_key=api_key, model=model_str, **kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
