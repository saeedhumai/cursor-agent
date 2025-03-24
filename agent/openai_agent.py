# mypy: ignore-errors
import json
from typing import Any, Dict, List, Optional, Callable, cast, Union

from openai import AsyncOpenAI, BadRequestError, RateLimitError, APIError, AuthenticationError

from .base import BaseAgent, AgentResponse, AgentToolCall
from .permissions import PermissionOptions, PermissionRequest, PermissionStatus
from .tools.register_tools import register_default_tools


class OpenAIAgent(BaseAgent):
    """
    OpenAI Agent that implements the BaseAgent interface using OpenAI's models.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo",
        temperature: float = 0.0,
        timeout: int = 180,
        permission_callback: Optional[Callable[[PermissionRequest], PermissionStatus]] = None,
        permission_options: Optional[PermissionOptions] = None,
        **kwargs
    ):
        """
        Initialize an OpenAI agent.

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use, default is gpt-4-turbo
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

        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=api_key)

        self.conversation_history = []
        self.available_tools = {}
        self.system_prompt = self._generate_system_prompt()

    def _is_valid_api_key(self, api_key: str) -> bool:
        """
        Validate the format of the OpenAI API key.

        Args:
            api_key: The API key to validate

        Returns:
            True if the key is a valid format, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False

        # OpenAI keys should start with sk-
        valid_prefix = api_key.startswith("sk-")

        # Keys should be fairly long and not contain spaces
        valid_length = len(api_key) >= 20 and " " not in api_key

        return valid_prefix and valid_length

    def _generate_system_prompt(self) -> str:
        """
        Generate the system prompt that defines the agent's capabilities and behavior.
        This is an extensive prompt that replicates Claude's behavior in Cursor.
        """
        return """
You are a powerful agentic AI coding assistant, powered by OpenAI's advanced models. You operate exclusively in Cursor, the world's best IDE.

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
        Prepare the registered tools for OpenAI API.

        Returns:
            List of tools in the format expected by OpenAI API, or None if no tools are registered
        """
        if not self.available_tools:
            return None

        tools = []
        for name, tool_data in self.available_tools.items():
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": tool_data["schema"]["description"],
                        "parameters": {
                            "type": "object",
                            "properties": tool_data["schema"]["parameters"]["properties"],
                            "required": tool_data["schema"]["parameters"].get("required", []),
                        },
                    },
                }
            )
        return tools if tools else None

    def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute the tool calls made by OpenAI.

        Args:
            tool_calls: List of tool calls to execute

        Returns:
            List of tool call results
        """
        tool_results = []

        for call in tool_calls:
            try:
                # Handle both dict format and ChatCompletionMessageToolCall objects
                if hasattr(call, "function"):
                    # It's an object
                    tool_name = call.function.name
                    try:
                        arguments = json.loads(call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    tool_call_id = call.id
                else:
                    # It's a dict
                    tool_name = call["function"]["name"]
                    try:
                        arguments = json.loads(call["function"]["arguments"])
                    except json.JSONDecodeError:
                        arguments = {}
                    # Cast to str to handle potential missing 'id' attribute
                    tool_call_id = cast(str, call.get("id", "unknown_id"))

                if tool_name not in self.available_tools:
                    result = {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": f"Error: Tool '{tool_name}' not found",
                    }
                else:
                    function = self.available_tools[tool_name]["function"]
                    result_content = function(**arguments)
                    result = {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": (
                            json.dumps(result_content)
                            if isinstance(result_content, dict)
                            else str(result_content)
                        ),
                    }
                tool_results.append(result)
            except Exception as e:
                # Log the error - in production, this would go to a proper logging system
                print(f"Error executing tool call: {str(e)}")
                # We still need to add a response to maintain the conversation flow
                if "tool_call_id" in locals():
                    tool_results.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,  # type: ignore
                            "content": f"Error: {str(e)}",
                        }
                    )

        return tool_results

    async def chat(self, message: str, user_info: Optional[Dict[str, Any]] = None) -> Union[str, AgentResponse]:
        """
        Send a message to the OpenAI API and get a response.

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

        # Prepare the messages for the API call
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history

        # Prepare tools
        tools = self._prepare_tools()

        # Initialize the structured response
        processed_tool_calls: List[AgentToolCall] = []

        try:
            # Make the API call
            response = await self.client.chat.completions.create(  # type: ignore
                model=self.model if self.model else "gpt-4-turbo",
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None,
                max_tokens=4096,
                temperature=self.temperature,
            )

            # Get the assistant's response
            assistant_message = response.choices[0].message

            # Track thinking (not directly supported by OpenAI but we can add it in the future)
            thinking = None

            # Check if there are any tool calls
            if assistant_message.tool_calls:
                # Add the assistant's response to the conversation history
                self.conversation_history.append(
                    {
                        "role": "assistant",
                        "content": assistant_message.content or "",
                        "tool_calls": assistant_message.tool_calls,
                    }
                )

                # Execute the tool calls
                tool_results = self._execute_tool_calls(assistant_message.tool_calls)

                # Process and track tool calls for the structured response
                for idx, tool_call in enumerate(assistant_message.tool_calls):
                    tool_name = tool_call.function.name
                    try:
                        parameters = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        parameters = {}

                    # Find the corresponding result
                    result = None
                    for res in tool_results:
                        if res.get("tool_call_id") == tool_call.id:
                            result = res.get("content", "")
                            break

                    # Add to processed tool calls
                    processed_tool_calls.append({
                        "name": tool_name,
                        "parameters": parameters,
                        "result": result
                    })

                # Add the tool results to the conversation history
                for result in tool_results:
                    self.conversation_history.append(result)

                # Make a follow-up API call with the tool results
                follow_up_messages = (
                    messages
                    + [
                        {
                            "role": "assistant",
                            "content": assistant_message.content or "",
                            "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "function": {
                                        "name": tool_call.function.name,
                                        "arguments": tool_call.function.arguments,
                                    },
                                    "type": "function",
                                }
                                for tool_call in assistant_message.tool_calls
                            ],
                        }
                    ]
                    + tool_results
                )

                follow_up_response = await self.client.chat.completions.create(
                    model=self.model if self.model else "gpt-4-turbo", messages=follow_up_messages, max_tokens=4096, temperature=self.temperature
                )

                # Add the assistant's follow-up response to the conversation history
                follow_up_message = follow_up_response.choices[0].message
                self.conversation_history.append(
                    {"role": "assistant", "content": follow_up_message.content}
                )

                response_text = follow_up_message.content or ""

                # Return structured response
                return {
                    "message": response_text,
                    "tool_calls": processed_tool_calls,
                    "thinking": thinking
                }
            else:
                # Add the assistant's response to the conversation history
                self.conversation_history.append(
                    {"role": "assistant", "content": assistant_message.content}
                )

                response_text = assistant_message.content or ""

                # Return structured response
                return {
                    "message": response_text,
                    "tool_calls": processed_tool_calls,
                    "thinking": thinking
                }

        except AuthenticationError as e:
            error_msg = f"Error: Authentication failed. Please check your OpenAI API key. Details: {str(e)}"
            return {
                "message": error_msg,
                "tool_calls": [],
                "thinking": None
            }
        except BadRequestError as e:
            error_msg = f"Error: Bad request to the OpenAI API. Details: {str(e)}"
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
            error_msg = f"Error: OpenAI API error. Details: {str(e)}"
            return {
                "message": error_msg,
                "tool_calls": [],
                "thinking": None
            }
        except Exception as e:
            error_msg = f"Error: An unexpected error occurred. Details: {str(e)}"
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
        Implementation of permission request callback for OpenAI agent.

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
