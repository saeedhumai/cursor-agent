from typing import Any, Optional, Union

from .claude_agent import ClaudeAgent
from .openai_agent import OpenAIAgent

# Dictionary mapping providers to their supported models
# This makes it easy to determine which provider to use based on a model name
MODEL_MAPPING = {
    "claude": [
        "claude-3-5-sonnet-latest",
        "claude-3-7-sonnet-latest",
        "claude-3-5-sonnet",
        "claude-3.5-sonnet",
        "claude-3-sonnet",
        "claude-3-haiku",
        "claude-3.5-haiku"
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-2024-05-13",
        "gpt-4o-2024-08-06",
        "gpt-4o-mini",
        "gpt-4",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "gpt-3.5"
    ]
}

# For model normalization (e.g., handling model aliases)
MODEL_NORMALIZATION = {
    "gpt-4o-2024-05-13": "gpt-4o",
    "gpt-4o-2024-08-06": "gpt-4o",
    "gpt-4-turbo": "gpt-4",
    "claude-3.5-sonnet": "claude-3-5-sonnet-latest"
}


def create_agent(
    model: str,
    api_key: Optional[str] = None,
    **kwargs: Any
) -> Union[ClaudeAgent, OpenAIAgent]:
    """
    Create an agent based on the specified model.

    Args:
        model: The model to use (e.g., 'claude-3-5-sonnet-latest', 'gpt-4o')
        api_key: The API key to use
        **kwargs: Additional keyword arguments to pass to the agent constructor

    Returns:
        An instance of the appropriate agent type based on the model name
    """
    # Determine the provider based on the model name
    provider = None
    for prov, models in MODEL_MAPPING.items():
        if model in models or any(model.startswith(m.split('-')[0]) for m in models):
            provider = prov
            break
    
    # Normalize the model name if needed
    normalized_model = MODEL_NORMALIZATION.get(model, model)
    
    # Create the appropriate agent based on the provider
    if provider == "claude":
        return ClaudeAgent(api_key=api_key, model=normalized_model, **kwargs)
    elif provider == "openai":
        return OpenAIAgent(api_key=api_key, model=normalized_model, **kwargs)
    else:
        # If we couldn't determine provider from the model name, try prefix matching
        if model.startswith("claude-"):
            return ClaudeAgent(api_key=api_key, model=model, **kwargs)
        elif model.startswith("gpt-"):
            return OpenAIAgent(api_key=api_key, model=model, **kwargs)
        else:
            raise ValueError(f"Unsupported model: {model}. Cannot determine the appropriate provider.")
