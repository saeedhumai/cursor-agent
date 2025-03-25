"""
Factory for creating different types of AI agents.

This module provides a unified API for creating various agents (OpenAI, Claude, etc.)
with consistent configuration.
"""

import os
from typing import Optional, Callable, Any

from agent.base import BaseAgent
from agent.claude_agent import ClaudeAgent
from agent.logger import get_logger
from agent.openai_agent import OpenAIAgent
from agent.permissions import PermissionOptions, PermissionRequest, PermissionStatus

# Initialize logger
logger = get_logger(__name__)

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
    temperature: float = 0.0,
    timeout: int = 180,
    permission_callback: Optional[Callable[[PermissionRequest], PermissionStatus]] = None,
    permissions: Optional[PermissionOptions] = None,
    default_tool_timeout: int = 300,
    **kwargs: Any
) -> BaseAgent:
    """
    Create an agent based on the specified model.

    Args:
        model: The name of the model to use (e.g., "gpt-4o", "claude-3-opus")
        api_key: The API key to use for the model provider
        temperature: The temperature to use for the model
        timeout: The timeout in seconds for model responses
        permission_callback: A callback function to handle permission requests
        permissions: Optional PermissionOptions object containing permission settings
        default_tool_timeout: Maximum execution time in seconds for tool calls (default: 300)
        **kwargs: Additional model-specific arguments

    Returns:
        An agent instance configured with the specified parameters
    """
    model = model.lower()  # Normalize model name to lowercase
    logger.info(f"Creating agent with model: {model}")
    logger.debug(f"Agent parameters: temperature={temperature}, timeout={timeout}, default_tool_timeout={default_tool_timeout}")

    # Set up permission options if not provided
    if permissions is None:
        permissions = PermissionOptions()
        logger.debug("Using default permission options")
    else:
        logger.debug(f"Using custom permission options, yolo_mode={permissions.yolo_mode}")

    # Handle OpenAI models
    if any(name in model for name in ["gpt-", "openai"]):
        logger.debug("Detected OpenAI model")
        # Use environment variable if no API key is provided
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OpenAI API key not provided and not found in environment")
                raise ValueError("OpenAI API key not provided and not found in environment")
            else:
                logger.debug("Using OpenAI API key from environment")

        logger.info(f"Creating OpenAIAgent with model {model}")
        return OpenAIAgent(
            model=model,
            api_key=api_key,
            temperature=temperature,
            timeout=timeout,
            permission_callback=permission_callback,
            permission_options=permissions,
            default_tool_timeout=default_tool_timeout,
            **kwargs
        )

    # Handle Anthropic/Claude models
    elif any(name in model for name in ["claude", "anthropic"]):
        logger.debug("Detected Anthropic/Claude model")
        # Use environment variable if no API key is provided
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.error("Anthropic API key not provided and not found in environment")
                raise ValueError("Anthropic API key not provided and not found in environment")
            else:
                logger.debug("Using Anthropic API key from environment")

        logger.info(f"Creating ClaudeAgent with model {model}")
        return ClaudeAgent(
            model=model,
            api_key=api_key,
            temperature=temperature,
            timeout=timeout,
            permission_callback=permission_callback,
            permission_options=permissions,
            default_tool_timeout=default_tool_timeout,
            **kwargs
        )

    # Raise error for unsupported models
    else:
        logger.error(f"Unsupported model: {model}")
        raise ValueError(f"Unsupported model: {model}")
