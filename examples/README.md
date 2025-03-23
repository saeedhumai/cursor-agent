# Cursor Agent Examples

This directory contains examples demonstrating how to use the Cursor Agent in different scenarios. All examples use the streamlined import structure from the `cursor_agent.agent` package.

## Available Examples

### Basic Usage
- **File**: `basic_usage.py`
- **Description**: Demonstrates how to create and use agents with both Claude and OpenAI models for simple coding tasks
- **Usage**: `python basic_usage.py`

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

The examples will automatically select an appropriate model based on which API keys are available.

## Creating Your Own Applications

Use these examples as templates for your own applications:

```python
import asyncio
from dotenv import load_dotenv
import os

# Import from the cursor_agent package
from cursor_agent.agent import create_agent
# For interactive applications
from cursor_agent.agent import run_agent_interactive

# Load environment variables
load_dotenv()

# Create and use a regular agent
async def use_regular_agent():
    # Create an agent with your preferred model
    agent = create_agent(model="claude-3-5-sonnet-latest")  # or "gpt-4o"
    
    # Create user context information
    user_info = {
        "workspace_root": os.getcwd(),
        "os": {
            "name": os.name,
            "system": sys.platform,
        },
    }
    
    # Use the agent to get responses
    response = await agent.chat("Your query here", user_info)
    print(response)

# Use the agent in interactive mode
async def use_interactive_agent():
    await run_agent_interactive(
        model="claude-3-5-sonnet-latest",  # or "gpt-4o"
        initial_query="Your initial query",
        max_iterations=10,
        auto_continue=False  # Set to True to continue automatically
    )

# Run your chosen function
asyncio.run(use_regular_agent())
# or
# asyncio.run(use_interactive_agent())
```

Each example demonstrates different aspects of the agent's capabilities and can be adapted for your specific use cases. 