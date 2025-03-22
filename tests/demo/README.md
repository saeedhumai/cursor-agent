# AI Agent Demo Scripts

This directory contains demonstration scripts that showcase the capabilities of the AI agent implementation. These demos are designed to provide visual examples of how the agent works with different types of tasks.

## Prerequisites

Before running any demos, make sure you have:

1. The required environment variables set up (especially `ANTHROPIC_API_KEY`)
2. Installed all dependencies from the project's `requirements.txt`

## Running a Demo

You can run demos using the test runner with the `--demo` flag:

```bash
# Navigate to the project root
cd /path/to/civai-nova-api/cursor

# Run a specific demo
python run_tests.py --demo chat_demo

# Run a demo in non-interactive mode (no pauses or user input)
python run_tests.py --demo chat_demo --non-interactive

# Run multiple demos in sequence
python run_tests.py --demo-list chat_demo,file_tools_demo

# Run all demos
python run_tests.py --demo-list all

# Run all demos in non-interactive mode
python run_tests.py --demo-list all --non-interactive
```

You can also run the main demo menu which provides an interactive selection:

```bash
python run_tests.py --demo
```

## Available Demos

### 1. Chat Demo (`chat_demo.py`)

An interactive chat demonstration that allows you to converse with the Claude agent. The demo creates a sample file for context and provides a clean interface for seeing the agent's responses, including any tool calls it makes.

**Features:**
- Interactive chat with the Claude agent
- Visualizes tool calls and their results
- Sample file creation for file-based operations
- Clean terminal UI with color-coded outputs
- Supports non-interactive mode with predefined queries

### 2. File Tools Demo (`file_tools_demo.py`)

A scripted demonstration showing how the agent can manipulate files and generate code. This demo creates a simple calculator implementation and shows how the agent can complete missing functions and create test files.

**Features:**
- Demonstrates file reading and writing capabilities
- Shows code generation and modification
- Includes test file creation
- Supports both interactive mode (with pauses) and non-interactive mode

### 3. Search Demo (`search_demo.py`)

A demonstration of the agent's ability to search and understand codebases. This demo creates a small demo project with multiple files and demonstrates how the agent can answer questions about the codebase.

**Features:**
- Creates a sample multi-file project structure
- Demonstrates semantic code search capabilities
- Shows how the agent answers questions about code structure
- Runs through predefined scenarios to showcase understanding
- Supports non-interactive mode for automated demonstrations

## Demo Mode Options

All demos now support the following modes:

### Interactive Mode (Default)

When run without special parameters, demos will operate in interactive mode, which:
- Pauses between steps and waits for user input
- Allows for a more guided experience
- Enables you to follow along at your own pace

### Non-Interactive Mode

When run with the `--non-interactive` flag, demos will:
- Run through all steps automatically without pausing
- Use predefined queries instead of requesting user input
- Complete faster and require no user intervention
- Be suitable for automated testing or demonstrations

### Multiple Demo Execution

When using the `--demo-list` parameter, you can:
- Specify a comma-separated list of demos to run in sequence
- Use `all` to run all available demos
- Combine with `--non-interactive` to run all demos without user input

## Utilities

All demos use the shared utilities in `utils.py`, which provides:

- Colored terminal output
- Formatted display of user inputs, agent responses, and tool calls
- Helper functions for creating sample files and user context

## Creating New Demos

When creating new demos, follow these guidelines:

1. Import the shared utilities from `utils.py`
2. Create a dedicated directory for demo files (with cleanup in a `finally` block)
3. Use the visualization functions for consistent UI
4. Implement both interactive and non-interactive modes
5. Add a `main_non_interactive()` function for backwards compatibility
6. Document the demo's purpose in this README

## Debugging Demo Issues

If a demo isn't working correctly:

1. Check that your API keys are correctly set up in the environment
2. Ensure you're running the script from the project root directory
3. Look for error messages in red text that may indicate issues
4. If using Claude, make sure your API key is valid and has sufficient quota
5. Try running in non-interactive mode to isolate user input issues

## Contributing

If you've created a useful demo, please add it to this directory and update this README with information about what your demo showcases.

When contributing a new demo, make sure it supports both interactive and non-interactive modes for maximum flexibility. 