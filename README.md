# Cursor Agent

![License](https://img.shields.io/github/license/civai-technologies/cursor-agent)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Anthropic](https://img.shields.io/badge/Anthropic-Claude-blueviolet)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT4-green)

A Python-based AI agent that replicates Cursor's coding assistant capabilities, enabling function calling, code generation, and intelligent coding assistance with both Claude and OpenAI models.

## 🌟 Features

This AI Agent implementation provides a comprehensive set of capabilities:

### Core Abilities

- **Model Flexibility**: Works with both Claude (Anthropic) and OpenAI models
- **Code Generation**: Generate complete, functional code based on natural language descriptions
- **Code Editing**: Make precise edits to existing code files
- **Code Analysis**: Review and analyze code for bugs, improvements, and optimizations
- **Function Calling**: Invoke registered tools and functions based on user requests
- **Conversational Context**: Maintain a conversation history for coherent back-and-forth interactions
- **Project-Aware Responses**: Consider project context when answering questions

### Tool Functions

The agent supports a comprehensive set of tools:

- **File Operations**:
  - **read_file**: Read file contents with flexible line range control
  - **edit_file**: Make precise edits to files with clear instructions
  - **delete_file**: Remove files from the filesystem
  - **create_file**: Create new files with specified content
  - **list_dir**: List directory contents to understand project structure

- **Search Capabilities**:
  - **codebase_search**: Semantic search of codebases to find relevant code snippets
  - **grep_search**: Perform regex-based text search in files
  - **file_search**: Fuzzy search for files by name
  - **web_search**: Search the web for up-to-date information

- **System Operations**:
  - **run_terminal_cmd**: Execute terminal commands with user approval

All tools are implemented with actual functionality and can be extended with custom tools as needed.

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [API Documentation](#api-documentation)
- [Advanced Usage](#advanced-usage)
- [Limitations and Considerations](#limitations-and-considerations)
- [Roadmap](#roadmap)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## 🚀 Installation

### Prerequisites

- Python 3.8+
- API keys for Anthropic and/or OpenAI

### Via pip

```bash
pip install cursor-agent
```

### From Source

```bash
git clone https://github.com/civai-technologies/cursor-agent.git
cd cursor-agent
pip install -e .  # Install in development mode

# Or with development dependencies
pip install -e ".[dev]"
```

### Environment Setup

Create a `.env` file in your project root (copy from `.env.example`):

```ini
# Environment (local, development, production)
ENVIRONMENT=local

# OpenAI configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.0

# Anthropic configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_API_MODEL=claude-3-opus-20240229
ANTHROPIC_TEMPERATURE=0.0
```

## ⚡ Quick Start

```python
import asyncio
from agent.factory import create_agent

async def main():
    # Create a Claude agent instance
    agent = create_agent(provider='claude')
    
    # Chat with the agent
    response = await agent.chat("Create a Python function to calculate Fibonacci numbers")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔍 Usage Examples

### Chat with Different Models

```python
# Use Claude
claude_agent = create_agent(provider='claude')
response = await claude_agent.chat("What's a good way to implement a cache in Python?")

# Use OpenAI
openai_agent = create_agent(provider='openai')
response = await openai_agent.chat("What's a good way to implement a cache in Python?")
```

### Providing Project Context

```python
user_info = {
    "open_files": ["src/main.py", "src/utils.py"],
    "cursor_position": {"file": "src/main.py", "line": 42},
    "recent_files": ["src/config.py", "tests/test_main.py"],
    "os": "darwin",
    "workspace_path": "/Users/username/projects/myproject"
}

response = await agent.chat("Fix the bug in the main function", user_info=user_info)
```

### Custom Tool Registration

```python
def custom_tool(param1, param2):
    # Tool implementation
    return {"result": f"Processed {param1} and {param2}"}

# Register the tool
agent.register_tool(
    name="custom_tool",
    function=custom_tool,
    description="Custom tool that does something useful",
    parameters={
        "properties": {
            "param1": {"description": "First parameter", "type": "string"},
            "param2": {"description": "Second parameter", "type": "string"}
        },
        "required": ["param1", "param2"]
    }
)
```

For more examples, check the [examples](examples/) directory.

## 🏗️ Project Structure

```
cursor-agent/
├── agent/                   # Core agent implementation
│   ├── __init__.py          # Package exports
│   ├── base.py              # Base agent class
│   ├── claude_agent.py      # Claude-specific implementation
│   ├── openai_agent.py      # OpenAI-specific implementation
│   ├── factory.py           # Agent factory function
│   └── tools/               # Tool implementations
│       ├── __init__.py      # Tool exports
│       ├── file_tools.py    # File operations
│       ├── search_tools.py  # Search functionalities
│       └── system_tools.py  # System commands
├── examples/                # Example usage scripts
│   ├── chat_demo.py         # Simple chat example
│   ├── file_tools_demo.py   # File operations example
│   ├── interactive_demo.py  # Interactive agent session
│   └── ...
├── tests/                   # Unit and integration tests
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore patterns
├── CODE_OF_CONDUCT.md       # Code of conduct for contributors
├── CONTRIBUTING.md          # Contribution guidelines
├── LICENSE                  # MIT License
├── README.md                # This file
├── SECURITY.md              # Security policy
├── constraints.md           # Implementation constraints
├── requirements.txt         # Project dependencies
├── run_tests.py             # Test runner script
└── setup.py                 # Package installation
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | None |
| `ANTHROPIC_API_MODEL` | Claude model to use | claude-3-opus-20240229 |
| `ANTHROPIC_TEMPERATURE` | Claude temperature setting | 0.0 |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `OPENAI_API_MODEL` | OpenAI model to use | gpt-4o |
| `OPENAI_TEMPERATURE` | OpenAI temperature setting | 0.0 |
| `ENVIRONMENT` | Environment mode | local |

### Agent Configuration

When creating an agent, you can customize its behavior:

```python
agent = create_agent(
    provider='claude',               # 'claude' or 'openai'
    model='claude-3-opus-20240229',  # Specific model to use
    temperature=0.2,                 # Creativity level
    system_prompt=None,              # Custom system prompt
    tools=None                       # Custom tools dictionary
)
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

### Development Setup

1. Fork and clone the repository
2. Create a virtual environment
3. Install development dependencies: `pip install -e ".[dev]"`
4. Set up API keys in a `.env` file
5. Submit pull requests for features or fixes

## 📚 API Documentation

### Agent Factory

```python
def create_agent(
    provider: str = "claude",
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    system_prompt: Optional[str] = None,
    tools: Optional[Dict] = None,
) -> BaseAgent:
    """
    Create an agent instance based on the specified provider.
    
    Args:
        provider: The provider to use (claude or openai)
        model: The specific model to use
        temperature: The temperature setting for generation
        system_prompt: Custom system prompt to use
        tools: Custom tools dictionary
        
    Returns:
        An instance of BaseAgent (either ClaudeAgent or OpenAIAgent)
    """
```

### Base Agent Methods

```python
class BaseAgent:
    async def chat(
        self, user_message: str, user_info: Optional[Dict] = None
    ) -> str:
        """Send a message to the agent and get a response."""
        
    def register_tool(
        self, name: str, function: Callable, description: str, parameters: Dict
    ) -> None:
        """Register a custom tool with the agent."""
        
    async def _prepare_tools(self) -> Dict:
        """Prepare tools for the provider API."""
        
    async def _execute_tool_calls(self, tool_calls: List[Dict]) -> List[Dict]:
        """Execute tool calls and return results."""
```

For complete API documentation, refer to the docstrings in the source code.

## 🔧 Advanced Usage

### Customizing System Prompts

The agent uses a detailed system prompt to guide behavior. You can modify this:

```python
custom_system_prompt = """
You are an AI assistant specialized in helping with data science tasks.
Focus on suggesting pandas and numpy solutions.
"""

agent = create_agent(
    provider='claude',
    system_prompt=custom_system_prompt
)
```

### Tool Implementation

Tools are Python functions registered with the agent. Example custom tool:

```python
def database_query(query: str, connection_string: str):
    """Execute a database query and return results."""
    # Implementation...
    return {"results": [...]}

agent.register_tool(
    name="database_query",
    function=database_query,
    description="Execute a SQL query against a database",
    parameters={
        "properties": {
            "query": {"description": "SQL query to execute", "type": "string"},
            "connection_string": {"description": "Database connection string", "type": "string"}
        },
        "required": ["query", "connection_string"]
    }
)
```

## ⚠️ Limitations and Considerations

- **API Key Security**: Keep your API keys secure and never commit them to repositories
- **Context Windows**: Models have token limits that restrict the amount of code they can process
- **Tool Execution**: Function calling executes code on your system - implement proper security
- **Rate Limits**: APIs have rate limits that may restrict usage
- **Costs**: Using the APIs incurs costs based on token usage

For a detailed list of constraints and workarounds, see the [constraints.md](constraints.md) file.

## 🛣️ Roadmap

- Streaming responses
- Support for more providers (e.g., Gemini, Llama, etc.)
- Web interface
- Multi-user support with authentication
- Vector-based codebase search
- Testing tools integration
- Comprehensive demo suite
- Documentation website

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Anthropic](https://www.anthropic.com/) for the Claude API
- [OpenAI](https://openai.com/) for the OpenAI API
- [Cursor](https://cursor.sh/) for inspiration

## 👤 Author

Nifemi Alpine (Founder of [CIVAI TECHNOLOGIES](https://civai.co))

[![Twitter](https://img.shields.io/twitter/follow/usecodenaija?style=social)](https://twitter.com/usecodenaija) 