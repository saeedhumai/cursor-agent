# mypy: ignore-errors
import json
from typing import Any, Dict, List, Optional, Callable, Union

from anthropic import APIError, AsyncAnthropic, AuthenticationError, BadRequestError, RateLimitError

from .base import BaseAgent, AgentResponse, AgentToolCall
from .permissions import PermissionOptions, PermissionRequest, PermissionStatus
from .tools.register_tools import register_default_tools


class ClaudeAgent(BaseAgent):
    """
    Claude Agent that implements the BaseAgent interface using Anthropic's Claude models.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-latest",
        temperature: float = 0.0,
        timeout: int = 180,
        permission_callback: Optional[Callable[[PermissionRequest], PermissionStatus]] = None,
        permission_options: Optional[PermissionOptions] = None,
        **kwargs
    ):
        """
        Initialize a Claude agent.

        Args:
            api_key: Anthropic API key
            model: Claude model to use, default is claude-3-opus
            temperature: Temperature parameter for model (0.0 to 1.0)
            timeout: Timeout in seconds for API requests
            permission_callback: Optional callback for permission requests
            permission_options: Permission configuration options
            **kwargs: Additional parameters to pass to the model
        """
        super().__init__(
            api_key=api_key,
            model=model,
            permission_options=permission_options, 
            permission_callback=permission_callback
        )
        
        self.temperature = temperature
        self.timeout = timeout
        self.extra_kwargs = kwargs
        
        # Initialize Anthropic client
        self.client = AsyncAnthropic(api_key=api_key)

        self.conversation_history = []
        self.available_tools = {}
        self.system_prompt = self._generate_system_prompt()

    def _is_valid_api_key(self, api_key: str) -> bool:
        """
        Validate the format of the Anthropic API key.

        Args:
            api_key: The API key to validate

        Returns:
            True if the key is a valid format, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False

        # Allow dummy keys in test environments
        if api_key == "sk-ant-dummy" or "dummy" in api_key:
            return True

        # Anthropic keys should start with sk-ant- or sk-
        valid_prefix = api_key.startswith(("sk-ant-", "sk-"))

        # Keys should be fairly long and not contain spaces
        valid_length = len(api_key) >= 20 and " " not in api_key

        return valid_prefix and valid_length

    def _generate_system_prompt(self) -> str:
        """
        Generate the system prompt that defines Claude's capabilities and behavior.
        This is an extensive prompt that replicates Claude's behavior in Cursor.
        """
        return """
You are a powerful agentic AI coding assistant, powered by Claude 3.7 Sonnet. You operate exclusively in Cursor, the world's best IDE.

You are pair programming with a USER to solve their coding task.
The task may require creating a new codebase, modifying or debugging an existing codebase, or simply answering a question.
Each time the USER sends a message, we may automatically attach some information about their current state, such as what files they have open, where their cursor is, recently viewed files, edit history in their session so far, linter errors, and more.
This information may or may not be relevant to the coding task, it is up for you to decide.
Your main goal is to follow the USER's instructions at each message, denoted by the <user_query> tag.

<tool_calling>
You have tools at your disposal to solve the coding task. Follow these rules regarding tool calls:
1. ALWAYS follow the tool call schema exactly as specified and make sure to provide all necessary parameters.
2. The conversation may reference tools that are no longer available. NEVER call tools that are not explicitly provided.
3. **NEVER refer to tool names when speaking to the USER.** For example, instead of saying 'I need to use the edit_file tool to edit your file', just say 'I will edit your file'.
4. Only calls tools when they are necessary. If the USER's task is general or you already know the answer, just respond without calling tools.
5. Before calling each tool, first explain to the USER why you are calling it.
</tool_calling>

<making_code_changes>
When making code changes, NEVER output code to the USER, unless requested. Instead use one of the code edit tools to implement the change.
Use the code edit tools at most once per turn.
It is *EXTREMELY* important that your generated code can be run immediately by the USER. To ensure this, follow these instructions carefully:
1. Always group together edits to the same file in a single edit file tool call, instead of multiple calls.
2. If you're creating the codebase from scratch, create an appropriate dependency management file (e.g. requirements.txt) with package versions and a helpful README.
3. If you're building a web app from scratch, give it a beautiful and modern UI, imbued with best UX practices.
4. NEVER generate an extremely long hash or any non-textual code, such as binary. These are not helpful to the USER and are very expensive.
5. Unless you are appending some small easy to apply edit to a file, or creating a new file, you MUST read the the contents or section of what you're editing before editing it.
6. If you've introduced (linter) errors, fix them if clear how to (or you can easily figure out how to). Do not make uneducated guesses. And DO NOT loop more than 3 times on fixing linter errors on the same file. On the third time, you should stop and ask the user what to do next.
7. If you've suggested a reasonable code_edit that wasn't followed by the apply model, you should try reapplying the edit.
</making_code_changes>

<searching_and_reading>
You have tools to search the codebase and read files. Follow these rules regarding tool calls:
1. If available, heavily prefer the semantic search tool to grep search, file search, and list dir tools.
2. If you need to read a file, prefer to read larger sections of the file at once over multiple smaller calls.
3. If you have found a reasonable place to edit or answer, do not continue calling tools. Edit or answer from the information you have found.
</searching_and_reading>

Answer the user's request using the relevant tool(s), if they are available. Check that all the required parameters for each tool call are provided or can reasonably be inferred from context. IF there are no relevant tools or there are missing values for required parameters, ask the user to supply these values; otherwise proceed with the tool calls. If the user provides a specific value for a parameter (for example provided in quotes), make sure to use that value EXACTLY. DO NOT make up values for or ask about optional parameters. Carefully analyze descriptive terms in the request as they may indicate required parameter values that should be included even if not explicitly quoted.

You MUST use the following format when citing code regions or blocks:
```12:15:app/components/Todo.tsx
// ... existing code ...
```
This is the ONLY acceptable format for code citations. The format is ```startLine:endLine:filepath where startLine and endLine are line numbers.
"""

    def _prepare_tools(self) -> Optional[List[Dict[str, Any]]]:
        """
        Prepare the registered tools for Claude API.

        Returns:
            List of tools in the format expected by Claude API, or None if no tools are registered
        """
        if not self.available_tools:
            return None

        tools = []
        for name, tool_data in self.available_tools.items():
            # Claude tools format:
            # {
            #   "name": "tool_name",
            #   "description": "Tool description",
            #   "input_schema": {
            #     "type": "object",
            #     "properties": {
            #       "property_name": {
            #         "type": "string",
            #         "description": "Property description"
            #       },
            #       ...
            #     },
            #     "required": ["property_name", ...]
            #   }
            # }

            tool = {
                "name": name,
                "description": tool_data["schema"]["description"],
                "input_schema": {
                    "type": "object",
                    "properties": tool_data["schema"]["parameters"]["properties"],
                    "required": tool_data["schema"]["parameters"].get("required", []),
                },
            }
            tools.append(tool)
        return tools if tools else None

    def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute the tool calls made by Claude.

        Args:
            tool_calls: List of tool calls to execute

        Returns:
            List of tool call results formatted for the Claude API
        """
        tool_results = []

        for call in tool_calls:
            tool_name = call["name"]
            tool_id = call.get("id")
            arguments = call.get("input", {})

            # Format for user message with tool_result as required by the Claude API
            result_message = {"role": "user", "content": []}

            if tool_name not in self.available_tools:
                # Add error result
                error_msg = f"Tool '{tool_name}' not found. Error: Tool not available."
                result_message["content"].append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "is_error": True,
                        "content": error_msg,
                    }
                )
            else:
                try:
                    function = self.available_tools[tool_name]["function"]
                    # Convert input to the expected format for the function
                    result = function(**arguments)

                    # Format the result based on whether it's a string or a JSON-serializable object
                    content = result if isinstance(result, str) else json.dumps(result)

                    # Add tool result
                    result_message["content"].append(
                        {"type": "tool_result", "tool_use_id": tool_id, "content": content}
                    )
                except Exception as e:
                    error_msg = f"Error executing tool {tool_name}: {str(e)}"
                    result_message["content"].append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "is_error": True,
                            "content": error_msg,
                        }
                    )

            # Only add messages with non-empty content
            if result_message["content"]:
                tool_results.append(result_message)

        return tool_results

    async def chat(self, message: str, user_info: Optional[Dict[str, Any]] = None) -> Union[str, AgentResponse]:
        """
        Send a message to Claude and get a response.

        Args:
            message: The user's message
            user_info: Optional dict containing info about the user's current state

        Returns:
            Either a string response (for backward compatibility) or a structured AgentResponse
            containing the message, tool_calls made, and optional thinking
        """
        # Format the user message with user_info if provided
        formatted_message = self.format_user_message(message, user_info)

        # Add the user message to the conversation history
        self.conversation_history.append({"role": "user", "content": formatted_message})

        # Prepare the messages for the API call - exclude system message from the conversation history
        # because Anthropic API requires system prompt as a separate parameter
        messages = []
        for msg in self.conversation_history:
            if msg["role"] != "system" and msg.get("content"):  # Ensure content is not empty
                messages.append(msg)

        # Always enable tools regardless of message content
        use_tools = True
        # Note: Previous code disabled tools for file-related operations, but this was causing issues
        # with the file_tools_demo and other demos that need to use file tools

        # Prepare tools if needed
        tools = None
        if use_tools:
            tools = self._prepare_tools()
            
        # Initialize the structured response
        processed_tool_calls: List[AgentToolCall] = []
        thinking = None  # Claude doesn't directly expose thinking, but we could add it in the future

        try:
            # Make the API call
            api_params = {
                "model": self.model if self.model else "claude-3-5-sonnet-latest",
                "max_tokens": 4096,
                "temperature": self.temperature,
                "system": self.system_prompt,  # System prompt as a separate parameter
            }
            
            # Add properly typed messages
            typed_messages = []
            for msg in messages:
                if isinstance(msg["content"], str):
                    typed_messages.append({"role": msg["role"], "content": msg["content"]})
                else:
                    # Handle content that's not a string (e.g., structured content)
                    typed_messages.append(msg)
            
            api_params["messages"] = typed_messages

            # Only include tools parameter if we have tools registered and are using tools
            if tools and use_tools:
                api_params["tools"] = tools

            # Make the API call
            response = await self.client.messages.create(**api_params)  # type: ignore

            # Process any tool calls
            if response.content and any(block.type == "tool_use" for block in response.content):
                # Add assistant message with tool calls to conversation history
                assistant_content = []
                for block in response.content:
                    if hasattr(block, "text") and block.text is not None:
                        assistant_content.append({"type": "text", "text": block.text})  # type: ignore
                    elif block.type == "tool_use":
                        assistant_content.append({  # type: ignore
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })
                
                self.conversation_history.append({"role": "assistant", "content": assistant_content})

                # Extract tool calls
                tool_calls = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_calls.append(
                            {"name": block.name, "id": block.id, "input": block.input}
                        )

                # Execute tool calls
                tool_results = self._execute_tool_calls(tool_calls)
                
                # Process and track tool calls for the structured response
                for idx, tool_call in enumerate(tool_calls):
                    tool_name = tool_call["name"]
                    parameters = tool_call["input"]
                    
                    # Find the corresponding result
                    result = None
                    for res in tool_results:
                        for content_block in res.get("content", []):
                            if content_block.get("tool_use_id") == tool_call["id"]:
                                result = content_block.get("content", "")
                                break
                        if result:
                            break
                    
                    # Add to processed tool calls
                    processed_tool_calls.append({
                        "name": tool_name,
                        "parameters": parameters,
                        "result": result
                    })

                # Add tool results to conversation history
                if tool_results:
                    for result in tool_results:
                        self.conversation_history.append(result)

                    # Make a follow-up API call with the tool results
                    follow_up_messages = []
                    for msg in self.conversation_history:
                        if msg["role"] != "system" and msg.get(
                            "content"
                        ):  # Ensure content is not empty
                            follow_up_messages.append(msg)

                    # Make a follow-up API call with the tool results
                    follow_up_response = await self.client.messages.create(  # type: ignore
                        model=self.model if self.model else "claude-3-5-sonnet-latest",
                        system=self.system_prompt,  # System prompt as a separate parameter
                        messages=follow_up_messages,
                        max_tokens=4096,
                        temperature=self.temperature,
                    )

                    # Add the assistant's follow-up response to the conversation history
                    self.conversation_history.append(
                        {"role": "assistant", "content": follow_up_response.content}
                    )

                    # Extract text from the response
                    response_text = "".join(
                        block.text for block in follow_up_response.content if block.type == "text"
                    )
                    
                    # Return structured response
                    return {
                        "message": response_text,
                        "tool_calls": processed_tool_calls,
                        "thinking": thinking
                    }
                else:
                    # No valid tool results were generated
                    error_msg = "Error: Failed to execute tool calls. Please try a different query."
                    
                    return {
                        "message": error_msg,
                        "tool_calls": processed_tool_calls,
                        "thinking": thinking
                    }
            else:
                # Extract text from the response
                response_text = "".join(
                    block.text for block in response.content if block.type == "text"
                )

                # Add the assistant's response to the conversation history
                self.conversation_history.append({"role": "assistant", "content": response.content})

                # Return structured response
                return {
                    "message": response_text,
                    "tool_calls": processed_tool_calls,
                    "thinking": thinking
                }

        except AuthenticationError as e:
            error_msg = f"Error: Authentication failed. Please check your Anthropic API key. Details: {str(e)}"
            return {
                "message": error_msg,
                "tool_calls": [],
                "thinking": None
            }
        except BadRequestError as e:
            # Provide more detailed information about the bad request
            request_info = ""
            if hasattr(e, "request"):
                request_info = f"\nRequest information: {e.request}"
            error_msg = f"Error: Bad request to the Anthropic API. Details: {str(e)}{request_info}"
            return {
                "message": error_msg,
                "tool_calls": [],
                "thinking": None
            }
        except RateLimitError as e:
            error_msg = f"Error: Rate limit exceeded. Please try again later. Details: {str(e)}"
            return {
                "message": error_msg,
                "tool_calls": [],
                "thinking": None
            }
        except APIError as e:
            error_msg = f"Error: Anthropic API error. Details: {str(e)}"
            return {
                "message": error_msg,
                "tool_calls": [],
                "thinking": None
            }
        except Exception as e:
            error_msg = f"Error: An unexpected error occurred. Details: {type(e).__name__}: {str(e)}"
            return {
                "message": error_msg,
                "tool_calls": [],
                "thinking": None
            }

    def register_default_tools(self) -> None:
        """
        Register all the default tools available to the agent.
        """
        # Use the centralized tool registration function
        register_default_tools(self)

    def _permission_request_callback(self, permission_request: PermissionRequest) -> PermissionStatus:
        """
        Implementation of permission request callback for Claude agent.
        
        In a real application, this would interact with the user to get permission.
        For now, we'll default to a console-based interaction.
        
        Args:
            permission_request: The permission request object
            
        Returns:
            PermissionStatus indicating whether the request is granted or denied
        """
        # If yolo mode is enabled, check is already done in PermissionManager
        if self.permission_manager.options.yolo_mode:
            return PermissionStatus.GRANTED
            
        # Default implementation asks on console
        print(f"\n[PERMISSION REQUEST] {permission_request.operation}")
        print(f"Details: {json.dumps(permission_request.details, indent=2)}")
        response = input("Allow this operation? (y/n): ").strip().lower()
        
        if response == 'y' or response == 'yes':
            return PermissionStatus.GRANTED
        else:
            return PermissionStatus.DENIED
