# Cursor Agent Examples

This directory contains examples demonstrating how to use the Cursor Agent in different scenarios. All examples use the streamlined import structure from the `cursor_agent_tools` package.

## Available Examples

### Basic Usage
- **File**: `basic_usage.py`
- **Description**: Demonstrates how to create and use agents with both Claude and OpenAI models for simple coding tasks
- **Usage**: `python basic_usage.py`

### Ollama Chat
- **File**: `ollama_chat_example.py`
- **Description**: Shows how to use the agent with locally hosted Ollama models for chat functionality
- **Usage**: `python ollama_chat_example.py`
- **Requirements**: Ollama server running with at least one model installed (e.g., `ollama pull llama3`)

### Ollama Tool Calling
- **File**: `ollama_tool_calling_example.py`
- **Description**: Demonstrates using Ollama models with tool calling capabilities to manipulate files and perform tasks
- **Usage**: `python ollama_tool_calling_example.py`
- **Requirements**: Ollama server running with at least one model installed

### Ollama Image Query
- **File**: `ollama_image_query_example.py`
- **Description**: Shows how to use vision-capable Ollama models for analyzing images
- **Usage**: `python ollama_image_query_example.py`
- **Requirements**: Ollama server running with a vision-capable model (e.g., `ollama pull llava`)

### Chat Conversation
- **File**: `chat_conversation_example.py`
- **Description**: Interactive chat session that allows conversational capabilities with the agent
- **Usage**: `python chat_conversation_example.py`

### Interactive Mode
- **File**: `interactive_mode_example.py`
- **Description**: Demonstrates how to use the agent in interactive mode, with a predefined task for the FastAPI Todo API
- **Usage**: 
  - Non-interactive mode (default): `python interactive_mode_example.py`
  - Interactive mode: `python interactive_mode_example.py --interactive`

### File Manipulation
- **File**: `file_manipulation_example.py`
- **Description**: Shows how to use file operations tools (create, read, edit, delete) to build a calculator implementation
- **Usage**: `python file_manipulation_example.py`

### Code Search
- **File**: `code_search_example.py`
- **Description**: Demonstrates the agent's ability to understand and explore a complex codebase
- **Usage**: `python code_search_example.py`

### Simple Task
- **File**: `simple_task_example.py`
- **Description**: Shows how to use the agent to solve a simple task interactively
- **Usage**: `python simple_task_example.py`

## Example Descriptions

### Basic Usage
This example showcases two examples:
1. **Claude Example**: Creates a Claude agent and asks it to write a Python function for calculating factorials using recursion
2. **OpenAI Example**: Creates an OpenAI agent and asks it to write a Python function for generating the Fibonacci sequence

### Ollama Chat
This example demonstrates using locally hosted Ollama models:
1. Automatically detects available models on your Ollama server
2. Creates an agent using the first available model
3. Asks the model to write a Python function using a generator
4. Shows how to handle follow-up questions in the conversation context

### Ollama Tool Calling
Demonstrates the agent's ability to use tools with Ollama models:
1. Registers all default tools with the agent
2. Creates a Python calculator class file
3. Lists files in the directory
4. Reads and edits the file to add functionality
5. Runs the file to test it
6. Shows detailed information about tool calls and their outputs

### Ollama Image Query
Shows multimodal capabilities with Ollama:
1. Looks for vision-capable models like LLaVA
2. Downloads a test image (Python logo)
3. Sends the image to the model with various queries
4. Displays the model's analysis of the image

### Chat Conversation
An interactive conversation with the agent:
- Allows selecting a model if multiple are available (Claude or OpenAI)
- Maintains conversation context between queries
- Provides formatted output for readability
- Type 'exit', 'quit', or 'q' to end the conversation

### Interactive Mode
Demonstrates the `run_agent_interactive` function:
- In non-interactive mode (default): Uses a predefined task to create a FastAPI Todo API
- In interactive mode: Allows selecting a model and entering a custom query
- Supports auto-continuation through multiple iterations

### File Manipulation
Shows the agent creating and manipulating files:
1. Creates a Python calculator class with basic operations
2. Adds a power method to the calculator class
3. Creates a README for the calculator

### Code Search
Shows the agent's ability to understand a codebase:
1. Creates a sample project with multiple Python files
2. Provides all files to the agent as context
3. Asks questions about the logging system, database operations, configuration, and architecture
4. The agent analyzes the code and provides detailed explanations

### Simple Task
Shows how to use the agent to solve a simple task interactively.

## Configuration

All examples support configuration through environment variables:

- `ANTHROPIC_API_KEY`: Your Anthropic API key (for Claude models)
- `OPENAI_API_KEY`: Your OpenAI API key (for GPT models)
- `OLLAMA_HOST`: Your Ollama server address (default: http://localhost:11434)

The examples will automatically select an appropriate model based on which API keys are available.

For Ollama examples, the scripts automatically detect and use available models on your local Ollama server.
If you want to use a specific Ollama model, you can pull it using the Ollama CLI:

```bash
ollama pull llama3    # Pull Llama 3 model
ollama pull mistral   # Pull Mistral model
ollama pull llava     # Pull LLaVA model (for image examples)
```

## Creating Your Own Applications

Use these examples as templates for your own applications:

```python
import asyncio
from dotenv import load_dotenv
import os
import sys

# Import from the cursor_agent_tools package
from cursor_agent_tools import create_agent
# For interactive applications
from cursor_agent_tools import run_agent_interactive

# Load environment variables
load_dotenv()

# Create and use a regular agent
async def use_regular_agent():
    # Create an agent with your preferred model
    # Option 1: Claude model
    agent1 = create_agent(model="claude-3-5-sonnet-latest")
    
    # Option 2: OpenAI model
    agent2 = create_agent(model="gpt-4o")
    
    # Option 3: Local Ollama model
    agent3 = create_agent(
        model="ollama-llama3",  # Replace with your preferred Ollama model
        host="http://localhost:11434"  # Optional, defaults to this value
    )
    
    # Choose one agent to use
    agent = agent3  # Using Ollama in this example
    
    # Register default tools if needed
    agent.register_default_tools()
    
    # Create user context information
    user_info = {
        "workspace_path": os.getcwd(),
        "os": os.name,
        "platform": sys.platform,
    }
    
    # Use the agent to get responses
    response = await agent.chat("Your query here", user_info)
    
    # Handle the response
    if isinstance(response, dict):
        print(response["message"])
        if response.get("tool_calls"):
            print(f"Agent used {len(response['tool_calls'])} tool calls")
    else:
        print(response)

# Use the agent in interactive mode
async def use_interactive_agent():
    await run_agent_interactive(
        model="ollama-llama3",  # Can use any supported model type
        initial_query="Your initial query",
        max_iterations=10,
        auto_continue=False  # Set to True to continue automatically
    )

# Use image query capabilities (for vision-capable models)
async def use_image_query():
    # Create agent with vision capabilities
    agent = create_agent(model="ollama-llava")  # Or claude-3-opus, gpt-4o
    
    # Query an image
    image_response = await agent.query_image(
        image_paths=["path/to/your/image.jpg"],
        query="Describe what you see in this image"
    )
    print(image_response)

# Run your chosen function
asyncio.run(use_regular_agent())
# or
# asyncio.run(use_interactive_agent())
# or
# asyncio.run(use_image_query())
```

Each example demonstrates different aspects of the agent's capabilities and can be adapted for your specific use cases. 