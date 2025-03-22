# Cursor Agent Examples

This directory contains various examples demonstrating how to use the Cursor Agent in different scenarios.

## Available Examples

### Basic Chat Example
- **File**: `chat_demo.py`
- **Description**: Demonstrates basic chat interaction with the agent
- **Usage**: `python chat_demo.py`

### File Tools Demo
- **File**: `file_tools_demo.py`
- **Description**: Shows how to use file operations tools (read, edit, create, delete)
- **Usage**: `python file_tools_demo.py`

### Interactive Demo
- **File**: `interactive_demo.py`
- **Description**: An interactive session with the agent that responds to user inputs
- **Usage**: `python interactive_demo.py`

### Search Demo
- **File**: `search_demo.py`
- **Description**: Demonstrates codebase search, grep search, and file search capabilities
- **Usage**: `python search_demo.py`

### Main Demo
- **File**: `main_demo.py`
- **Description**: A comprehensive demo showcasing the main features of the agent
- **Usage**: `python main_demo.py`

## Running All Demos

You can run all demos in sequence using the main runner:

```bash
python main.py --demo-list all
```

Or run specific demos:

```bash
python main.py --demo-list chat_demo,file_tools_demo
```

## Non-Interactive Mode

All demos support non-interactive mode for automated testing:

```bash
python chat_demo.py --non-interactive
```

## Configuration

You can configure the demos by setting environment variables:

- `ANTHROPIC_API_KEY`: Your Anthropic API key (for Claude)
- `OPENAI_API_KEY`: Your OpenAI API key
- `PROVIDER`: The provider to use (claude or openai)
- `MODEL`: The specific model to use with the provider

## Creating Your Own Examples

Feel free to use these examples as templates for your own use cases. The standard pattern is:

1. Import the agent factory
2. Create an agent with desired configuration
3. Implement the main logic for your use case
4. Add both interactive and non-interactive modes

See the existing examples for reference implementation patterns. 