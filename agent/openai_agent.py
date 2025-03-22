import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Union, Callable
import re

from openai import AsyncOpenAI, APIError, AuthenticationError, RateLimitError, BadRequestError

from .base import BaseAgent
from .tools import *

class OpenAIAgent(BaseAgent):
    """
    OpenAI Agent that implements the BaseAgent interface using OpenAI's models.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the OpenAI Agent.
        
        Args:
            api_key: OpenAI API key. If not provided, will attempt to load from OPENAI_API_KEY env var.
            model: OpenAI model to use. Defaults to gpt-4o.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided either as an argument or as OPENAI_API_KEY environment variable")
        
        # Validate API key format
        if not self._is_valid_api_key(self.api_key):
            raise ValueError(f"The provided OpenAI API key appears to be invalid. It should start with 'sk-'.")
            
        self.model = model
        try:
            self.client = AsyncOpenAI(api_key=self.api_key)
            # Try to make a minimal API call to validate the key
            # This will be implemented in a future version if needed
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")
            
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
        valid_length = len(api_key) >= 20 and ' ' not in api_key
        
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
    
    def _prepare_tools(self) -> List[Dict[str, Any]]:
        """
        Format the registered tools into the format expected by OpenAI's API.
        """
        tools = []
        for name, tool_data in self.available_tools.items():
            tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool_data["schema"]["description"],
                    "parameters": {
                        "type": "object",
                        "properties": tool_data["schema"]["parameters"]["properties"],
                        "required": tool_data["schema"]["parameters"].get("required", [])
                    }
                }
            })
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
                if hasattr(call, 'function'):
                    # It's an object
                    tool_name = call.function.name
                    try:
                        arguments = json.loads(call.function.arguments)
                    except:
                        arguments = {}
                    tool_call_id = call.id
                else:
                    # It's a dict
                    tool_name = call["function"]["name"]
                    try:
                        arguments = json.loads(call["function"]["arguments"])
                    except:
                        arguments = {}
                    tool_call_id = call["id"]
                
                if tool_name not in self.available_tools:
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": json.dumps({"error": f"Tool {tool_name} not found"})
                    })
                    continue
                    
                try:
                    function = self.available_tools[tool_name]["function"]
                    result = function(**arguments)
                    
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": json.dumps(result) if not isinstance(result, str) else result
                    })
                except Exception as e:
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": json.dumps({"error": str(e)})
                    })
            except Exception as e:
                # Handle the case where we can't even parse the tool call
                tool_call_id = getattr(call, 'id', 'unknown')
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": "unknown",
                    "content": json.dumps({"error": f"Failed to parse tool call: {str(e)}"})
                })
                    
        return tool_results
    
    async def chat(self, message: str, user_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a message to OpenAI and get a response.
        
        Args:
            message: The user's message
            user_info: Optional dict containing info about the user's current state
            
        Returns:
            OpenAI's response
        """
        # Format the user message with user_info if provided
        formatted_message = self.format_user_message(message, user_info)
        
        # Add the user message to the conversation history
        self.conversation_history.append({"role": "user", "content": formatted_message})
        
        # Prepare the messages for the API call
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
        
        # Prepare tools
        tools = self._prepare_tools()
        
        try:
            # Make the API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=4096,
                temperature=0.7
            )
            
            # Get the assistant's response
            assistant_message = response.choices[0].message
            
            # Check if there are any tool calls
            if assistant_message.tool_calls:
                # Add the assistant's response to the conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": assistant_message.tool_calls
                })
                
                # Execute the tool calls
                tool_results = self._execute_tool_calls(assistant_message.tool_calls)
                
                # Add the tool results to the conversation history
                self.conversation_history.extend(tool_results)
                
                # Make a follow-up API call with the tool results
                follow_up_messages = messages + [
                    {
                        "role": "assistant",
                        "content": assistant_message.content or "",
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                },
                                "type": "function"
                            } for tool_call in assistant_message.tool_calls
                        ]
                    }
                ] + tool_results
                
                follow_up_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=follow_up_messages,
                    max_tokens=4096,
                    temperature=0.7
                )
                
                # Add the assistant's follow-up response to the conversation history
                follow_up_message = follow_up_response.choices[0].message
                self.conversation_history.append({
                    "role": "assistant",
                    "content": follow_up_message.content
                })
                
                return follow_up_message.content or ""
            else:
                # Add the assistant's response to the conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message.content
                })
                
                return assistant_message.content or ""
        
        except AuthenticationError as e:
            return f"Error: Authentication failed. Please check your OpenAI API key. Details: {str(e)}"
        except BadRequestError as e:
            return f"Error: Bad request to the OpenAI API. Details: {str(e)}"
        except RateLimitError as e:
            return f"Error: Rate limit exceeded. Please try again later. Details: {str(e)}"
        except APIError as e:
            return f"Error: OpenAI API error. Details: {str(e)}"
        except Exception as e:
            return f"Error: An unexpected error occurred. Details: {str(e)}"
    
    def register_default_tools(self) -> None:
        """
        Register a set of default tools that mimic Cursor's capabilities.
        """
        # File tools
        self.register_tool(
            name="read_file",
            function=read_file,
            description="Read the contents of a file.",
            parameters={
                "properties": {
                    "target_file": {"description": "The path of the file to read.", "type": "string"},
                    "offset": {"description": "The offset to start reading from.", "type": "integer"},
                    "limit": {"description": "The number of lines to read.", "type": "integer"},
                    "should_read_entire_file": {"description": "Whether to read the entire file.", "type": "boolean"}
                },
                "required": ["target_file"]
            }
        )
        
        self.register_tool(
            name="edit_file",
            function=edit_file,
            description="Edit a file in the codebase.",
            parameters={
                "properties": {
                    "target_file": {"description": "The target file to modify.", "type": "string"},
                    "instructions": {"description": "A single sentence instruction describing what you are going to do for the edit.", "type": "string"},
                    "code_edit": {"description": "The precise lines of code that you wish to edit.", "type": "string"}
                },
                "required": ["target_file", "instructions", "code_edit"]
            }
        )
        
        self.register_tool(
            name="delete_file",
            function=delete_file,
            description="Delete a file at the specified path.",
            parameters={
                "properties": {
                    "target_file": {"description": "The path of the file to delete.", "type": "string"}
                },
                "required": ["target_file"]
            }
        )
        
        self.register_tool(
            name="create_file",
            function=create_file,
            description="Create a new file with the given content.",
            parameters={
                "properties": {
                    "file_path": {"description": "Path where the file should be created", "type": "string"},
                    "content": {"description": "Content to write to the file", "type": "string"}
                },
                "required": ["file_path", "content"]
            }
        )
        
        self.register_tool(
            name="list_dir",
            function=list_directory,
            description="List the contents of a directory.",
            parameters={
                "properties": {
                    "relative_workspace_path": {"description": "Path to list contents of, relative to the workspace root.", "type": "string"},
                    "explanation": {"description": "One sentence explanation as to why this tool is being used.", "type": "string"}
                },
                "required": ["relative_workspace_path"]
            }
        )
        
        # Search tools
        self.register_tool(
            name="codebase_search",
            function=codebase_search,
            description="Find snippets of code from the codebase most relevant to the search query.",
            parameters={
                "properties": {
                    "query": {"description": "The search query to find relevant code.", "type": "string"},
                    "target_directories": {"description": "Glob patterns for directories to search over", "items": {"type": "string"}, "type": "array"},
                    "explanation": {"description": "One sentence explanation as to why this tool is being used.", "type": "string"}
                },
                "required": ["query"]
            }
        )
        
        self.register_tool(
            name="grep_search",
            function=grep_search,
            description="Fast text-based regex search that finds exact pattern matches within files or directories.",
            parameters={
                "properties": {
                    "query": {"description": "The regex pattern to search for", "type": "string"},
                    "explanation": {"description": "One sentence explanation as to why this tool is being used.", "type": "string"},
                    "case_sensitive": {"description": "Whether the search should be case sensitive", "type": "boolean"},
                    "include_pattern": {"description": "Glob pattern for files to include", "type": "string"},
                    "exclude_pattern": {"description": "Glob pattern for files to exclude", "type": "string"}
                },
                "required": ["query"]
            }
        )
        
        self.register_tool(
            name="file_search",
            function=file_search,
            description="Fast file search based on fuzzy matching against file path.",
            parameters={
                "properties": {
                    "query": {"description": "Fuzzy filename to search for", "type": "string"},
                    "explanation": {"description": "One sentence explanation as to why this tool is being used.", "type": "string"}
                },
                "required": ["query"]
            }
        )
        
        self.register_tool(
            name="web_search",
            function=web_search,
            description="Search the web for information about any topic.",
            parameters={
                "properties": {
                    "search_term": {"description": "The search term to look up on the web", "type": "string"},
                    "explanation": {"description": "One sentence explanation as to why this tool is being used.", "type": "string"}
                },
                "required": ["search_term"]
            }
        )
        
        # System tools
        self.register_tool(
            name="run_terminal_cmd",
            function=run_terminal_command,
            description="Run a terminal command.",
            parameters={
                "properties": {
                    "command": {"description": "The terminal command to execute", "type": "string"},
                    "explanation": {"description": "One sentence explanation as to why this command needs to be run.", "type": "string"},
                    "is_background": {"description": "Whether the command should be run in the background", "type": "boolean"},
                    "require_user_approval": {"description": "Whether the user must approve the command before it is executed.", "type": "boolean"}
                },
                "required": ["command", "is_background", "require_user_approval"]
            }
        ) 