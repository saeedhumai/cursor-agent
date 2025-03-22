# AI Agent Demos Showcase

This document showcases the available demos that demonstrate the capabilities of the AI agent implementation in the cursor project.

## Chat Demo

The Chat Demo provides an interactive chat session with the Claude agent.

**What Actually Happens:**
1. The demo creates a sample Python file with a simple "Hello World" function
2. It initializes a Claude agent with your Anthropic API key
3. The demo runs through the following predefined queries in non-interactive mode:
   - "What does this code do?" - Claude analyzes the sample file and explains its purpose
   - "Can you modify it to print a custom message?" - Claude uses the edit_file tool to update the code
   - "Could you create a test for this function?" - Claude uses the create_file tool to generate a test file
4. For each query, you'll see:
   - The query itself in green text
   - Claude's response in blue text
   - Any tool calls highlighted with their parameters
   - The results of the tool calls in yellow text
5. In interactive mode, you can type your own questions and see Claude's responses
6. The demo cleans up the created files when complete

When Claude makes a tool call, you'll see exactly what file it's editing and what changes it's making. For example, when asked to modify the hello world function, Claude will edit the file to change the message and explain its changes.

## File Tools Demo

The File Tools Demo shows Claude creating and working with a calculator implementation.

**What Actually Happens:**
1. The demo creates a skeleton calculator.py file with add and subtract functions, but missing multiply and divide
2. It presents Claude with this task: "Complete the calculator.py module by adding the multiply and divide functions. Then create test cases for all functions."
3. Claude reads the existing calculator.py file to understand its structure and style
4. Claude uses create_file or edit_file to add the missing multiply function with proper docstrings
5. Claude adds the divide function, usually with zero division protection
6. Claude then creates a new test_calculator.py file with pytest test cases for all four functions
7. The terminal output shows the full tool calls and responses so you can see the exact code Claude generates
8. In non-interactive mode, files remain available for 30 seconds before cleanup so you can examine them

For example, when Claude adds the multiply function, it typically includes proper docstrings matching the existing style:
```python
def multiply(a, b):
    """
    Multiply two numbers and return the result.
    
    Args:
        a (float): First number
        b (float): Second number
        
    Returns:
        float: The product of a and b
    """
    return a * b
```

## Search Demo

The Search Demo shows Claude's ability to understand and explain a complex codebase.

**What Actually Happens:**
1. The demo creates a complete sample project with multiple Python files:
   - main.py - Application entry point
   - models/user.py - User model definition
   - utils/logger.py - Logging configuration
   - utils/config.py - Configuration management
   - database.py - Database access layer
   - README.md - Project documentation
   - config.yaml - Configuration file
2. It provides all these files to Claude as context
3. The demo then asks Claude four specific questions about the codebase:
   - "How does the logging system work in this project?" - Claude analyzes the logger.py file and explains the logging architecture
   - "What operations can be performed on users in the database?" - Claude examines the database.py file and details all the available user operations
   - "Show me how the application handles configuration." - Claude reviews config.py and explains the configuration system
   - "Explain the overall architecture of this project." - Claude synthesizes information from all files to provide a complete architectural overview
4. For each query, you see Claude's detailed explanation of that specific aspect of the codebase
5. Claude often includes code snippets in its responses to illustrate key points

For the database operations question, Claude provides specific details on each method available:
- save_user(user): Saves a user to the database, returns True if successful
- get_user(username): Retrieves a user by username, returns User or None
- get_all_users(): Returns a list of all User objects
- delete_user(username): Removes a user, returns True if successful
- search_users(**criteria): Finds users matching criteria, returns a list

## Demo Implementation Details

Each demo follows this execution flow:

1. **Setup Phase:**
   - Creates a clean demo directory (e.g., tests/demo/demo_files/)
   - Generates the necessary sample files
   - Displays the exact path where files are created

2. **Agent Initialization:**
   - Loads the ANTHROPIC_API_KEY from environment
   - Creates a ClaudeAgent instance with the key
   - Registers all default tools (file operations, search, terminal commands)
   - Logs successful initialization

3. **Demo Execution:**
   - In interactive mode: Displays prompts and waits for user input
   - In non-interactive mode: Automatically runs through predetermined queries
   - Each query is processed through the agent.chat() method
   - Tool calls are executed and their results displayed

4. **Visualization:**
   - User inputs appear in green
   - System messages appear in yellow
   - Claude responses appear in blue
   - Tool calls and results are clearly marked and color-coded
   - File paths are always shown in full

5. **Cleanup:**
   - The demo removes all created files
   - In non-interactive mode, there's a delay before cleanup
   - The directory where files were created is also removed

Running these demos provides a realistic example of how Claude can understand and manipulate code in a real-world context. 