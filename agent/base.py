import os
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Callable

class BaseAgent(ABC):
    """
    Base abstract class for AI agents that use function calling capabilities.
    This defines the common interface for all agents regardless of the underlying provider.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the agent.
        
        Args:
            api_key: API key for the model provider. If not provided, will attempt to load from environment.
            model: Model to use. If not provided, will use the default model.
        """
        self.api_key = api_key
        self.model = model
        self.conversation_history = []
        self.available_tools = {}
        self.system_prompt = self._generate_system_prompt()
    
    @abstractmethod
    def _generate_system_prompt(self) -> str:
        """
        Generate the system prompt that defines the agent's capabilities and behavior.
        
        Returns:
            The system prompt as a string
        """
        pass
    
    @abstractmethod
    async def chat(self, message: str, user_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a message to the AI and get a response.
        
        Args:
            message: The user's message
            user_info: Optional dict containing info about the user's current state
            
        Returns:
            The AI's response
        """
        pass
    
    def register_tool(self, name: str, function: Callable, description: str, parameters: Dict[str, Any]) -> None:
        """
        Register a function that can be called by the AI.
        
        Args:
            name: Name of the function
            function: The actual function to call
            description: Description of what the function does
            parameters: Dict describing the parameters the function takes
        """
        self.available_tools[name] = {
            "function": function,
            "schema": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
    
    @abstractmethod
    def _prepare_tools(self) -> Any:
        """
        Format the registered tools into the format expected by the provider's API.
        
        Returns:
            Tools in the format expected by the provider
        """
        pass
    
    @abstractmethod
    def _execute_tool_calls(self, tool_calls: Any) -> List[Dict[str, Any]]:
        """
        Execute the tool calls made by the AI.
        
        Args:
            tool_calls: Tool calls in the format provided by the specific model
            
        Returns:
            List of tool call results
        """
        pass
    
    def format_user_message(self, message: str, user_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Format the user message with user_info if provided.
        
        Args:
            message: The user's message
            user_info: Optional dict containing info about the user's current state
            
        Returns:
            Formatted message
        """
        if user_info:
            return f"<user_info>\n{json.dumps(user_info, indent=2)}\n</user_info>\n\n<user_query>\n{message}\n</user_query>"
        else:
            return f"<user_query>\n{message}\n</user_query>" 