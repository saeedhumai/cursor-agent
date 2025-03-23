#!/usr/bin/env python3
"""
Code Search Example for Cursor Agent

This script demonstrates the agent's capabilities for searching and understanding codebases.
It showcases how the agent can navigate through code, find relevant information,
and answer questions about the structure and functionality of a project.
"""

import asyncio
import os
import sys
import shutil
from pathlib import Path

from dotenv import load_dotenv

# Import from cursor_agent package
from cursor_agent.agent import create_agent

# Ensure the examples directory is in the path
examples_dir = Path(__file__).parent
if str(examples_dir) not in sys.path:
    sys.path.append(str(examples_dir))

# Import utility functions
try:
    from utils import (
        Colors,
        clear_screen,
        print_error,
        print_separator,
        print_system_message,
        print_user_input,
        print_assistant_response,
        create_user_info
    )
except ImportError:
    # Add project root to path as fallback
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    try:
        from examples.utils import (
            Colors,
            clear_screen,
            print_error,
            print_separator,
            print_system_message,
            print_user_input,
            print_assistant_response,
            create_user_info
        )
    except ImportError:
        raise ImportError("Unable to import utility functions. Make sure utils.py is in the examples directory.")

# Load environment variables
load_dotenv()

# Create a temporary directory for the example project
EXAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_project")
os.makedirs(EXAMPLE_DIR, exist_ok=True)
print_system_message(f"Example project created at {EXAMPLE_DIR}")


def setup_example_project():
    """Set up an example project with multiple files for the code search example."""

    # Create the example project directory if it doesn't exist
    os.makedirs(EXAMPLE_DIR, exist_ok=True)

    # Create main.py
    with open(os.path.join(EXAMPLE_DIR, "main.py"), "w") as f:
        f.write(
            """#!/usr/bin/env python3
\"\"\"
Demo project main entry point.
\"\"\"

import logging
from models.user import User
from utils.config import Config
from utils.logger import setup_logger
from database import Database

# Set up logging
setup_logger()
logger = logging.getLogger(__name__)

def main():
    \"\"\"Main entry point for the application.\"\"\"
    logger.info("Starting application")
    
    # Load configuration
    config = Config()
    config.load("config.yaml")
    
    # Initialize database
    db = Database(config.get("database_url"))
    
    # Example user operations
    user = User("john_doe", "john@example.com")
    db.save_user(user)
    
    all_users = db.get_all_users()
    logger.info(f"Found {len(all_users)} users in database")
    
    # Perform some business logic
    for user in all_users:
        logger.debug(f"Processing user: {user.username}")
        # Do something with each user...
    
    logger.info("Application shutting down")

if __name__ == "__main__":
    main()
"""
        )

    # Create models directory and user.py
    os.makedirs(os.path.join(EXAMPLE_DIR, "models"), exist_ok=True)
    with open(os.path.join(EXAMPLE_DIR, "models", "user.py"), "w") as f:
        f.write(
            """#!/usr/bin/env python3
\"\"\"
User model definition.
\"\"\"

import logging
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger(__name__)

@dataclass
class User:
    \"\"\"Represents a user in the system.\"\"\"
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    preferences: Optional[dict] = None
    
    def __post_init__(self):
        logger.debug(f"Created new User: {self.username}")
    
    def full_name(self) -> str:
        \"\"\"Return the user's full name.\"\"\"
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def deactivate(self):
        \"\"\"Deactivate this user.\"\"\"
        self.is_active = False
        logger.info(f"User {self.username} has been deactivated")
    
    def update_email(self, new_email: str):
        \"\"\"Update the user's email address.\"\"\"
        old_email = self.email
        self.email = new_email
        logger.info(f"Updated email for {self.username} from {old_email} to {new_email}")
    
    def set_preference(self, key: str, value):
        \"\"\"Set a user preference.\"\"\"
        if self.preferences is None:
            self.preferences = {}
        self.preferences[key] = value
        logger.debug(f"Set preference {key} for user {self.username}")
"""
        )

    # Create utils directory with logger.py and config.py
    os.makedirs(os.path.join(EXAMPLE_DIR, "utils"), exist_ok=True)

    with open(os.path.join(EXAMPLE_DIR, "utils", "logger.py"), "w") as f:
        f.write(
            """#!/usr/bin/env python3
\"\"\"
Logging configuration for the application.
\"\"\"

import os
import logging
import logging.handlers
from typing import Optional

def setup_logger(log_level: str = "INFO", log_file: Optional[str] = None):
    \"\"\"
    Set up the application logger.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
    \"\"\"
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Create a separate logger for sensitive operations
    security_logger = logging.getLogger("security")
    if log_file:
        security_file = os.path.join(
            os.path.dirname(log_file), "security.log"
        )
        security_handler = logging.FileHandler(security_file)
        security_handler.setFormatter(formatter)
        security_logger.addHandler(security_handler)
    
    logging.info("Logger initialized")
"""
        )

    with open(os.path.join(EXAMPLE_DIR, "utils", "config.py"), "w") as f:
        f.write(
            """#!/usr/bin/env python3
\"\"\"
Configuration management for the application.
\"\"\"

import os
import logging
import yaml
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class Config:
    \"\"\"
    Configuration manager that loads settings from YAML files
    with environment variable override support.
    \"\"\"
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
    
    def load(self, config_file: str):
        \"\"\"
        Load configuration from a YAML file.
        
        Args:
            config_file: Path to the YAML configuration file
        \"\"\"
        try:
            if not os.path.exists(config_file):
                logger.warning(f"Config file {config_file} not found, using defaults")
                return
            
            with open(config_file, 'r') as f:
                self._config = yaml.safe_load(f)
            
            logger.info(f"Loaded configuration from {config_file}")
            
            # Check for environment variable overrides
            self._apply_env_overrides()
            
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise
    
    def _apply_env_overrides(self):
        \"\"\"Apply environment variable overrides to the configuration.\"\"\"
        prefix = "APP_"
        for env_var, value in os.environ.items():
            if env_var.startswith(prefix):
                # Convert APP_DATABASE_URL to database_url
                config_key = env_var[len(prefix):].lower()
                self._config[config_key] = value
                logger.debug(f"Override config {config_key} from environment variable")
    
    def get(self, key: str, default: Any = None) -> Any:
        \"\"\"
        Get a configuration value.
        
        Args:
            key: The configuration key
            default: Default value if key doesn't exist
            
        Returns:
            The configuration value or default
        \"\"\"
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        \"\"\"
        Set a configuration value.
        
        Args:
            key: The configuration key
            value: The value to set
        \"\"\"
        self._config[key] = value
        logger.debug(f"Set config {key}")
"""
        )

    # Create database.py
    with open(os.path.join(EXAMPLE_DIR, "database.py"), "w") as f:
        f.write(
            """#!/usr/bin/env python3
\"\"\"
Database access layer for the application.
\"\"\"

import logging
from typing import List, Optional, Dict, Any
from models.user import User

logger = logging.getLogger(__name__)

class Database:
    \"\"\"Simple in-memory database for demonstration purposes.\"\"\"
    
    def __init__(self, connection_string: str):
        \"\"\"
        Initialize the database.
        
        Args:
            connection_string: Database connection string (not used in this demo)
        \"\"\"
        self._connection_string = connection_string
        logger.info(f"Connecting to database: {connection_string}")
        
        # In-memory storage
        self._users: Dict[str, User] = {}
        
        logger.info("Database initialized")
    
    def save_user(self, user: User) -> bool:
        \"\"\"
        Save a user to the database.
        
        Args:
            user: User object to save
            
        Returns:
            True if successful
        \"\"\"
        if not user.username:
            logger.error("Cannot save user with empty username")
            return False
        
        self._users[user.username] = user
        logger.debug(f"Saved user: {user.username}")
        return True
    
    def get_user(self, username: str) -> Optional[User]:
        \"\"\"
        Retrieve a user by username.
        
        Args:
            username: The username to look up
            
        Returns:
            User object if found, None otherwise
        \"\"\"
        user = self._users.get(username)
        if user:
            logger.debug(f"Retrieved user: {username}")
        else:
            logger.debug(f"User not found: {username}")
        return user
    
    def get_all_users(self) -> List[User]:
        \"\"\"
        Get all users in the database.
        
        Returns:
            List of User objects
        \"\"\"
        users = list(self._users.values())
        logger.debug(f"Retrieved {len(users)} users")
        return users
    
    def delete_user(self, username: str) -> bool:
        \"\"\"
        Delete a user from the database.
        
        Args:
            username: Username of the user to delete
            
        Returns:
            True if user was deleted, False if not found
        \"\"\"
        if username in self._users:
            del self._users[username]
            logger.info(f"Deleted user: {username}")
            return True
        
        logger.warning(f"Attempted to delete non-existent user: {username}")
        return False
    
    def search_users(self, **criteria) -> List[User]:
        \"\"\"
        Search for users matching the given criteria.
        
        Args:
            **criteria: Field-value pairs to match
            
        Returns:
            List of matching User objects
        \"\"\"
        results = []
        
        for user in self._users.values():
            match = True
            for field, value in criteria.items():
                if not hasattr(user, field) or getattr(user, field) != value:
                    match = False
                    break
            
            if match:
                results.append(user)
        
        logger.debug(f"Search found {len(results)} users matching {criteria}")
        return results
"""
        )

    # Create a README.md file
    with open(os.path.join(EXAMPLE_DIR, "README.md"), "w") as f:
        f.write(
            """# Demo Project

This is a simple demo project showcasing a typical Python application structure.

## Structure

- `main.py` - Main entry point for the application
- `models/` - Data models including User class
- `utils/` - Utility modules for logging and configuration
- `database.py` - Simple in-memory database implementation

## Usage

Run the application with:

```
python main.py
```

Note: This is a demonstration project and does not have any real functionality.
"""
        )

    # Create an empty config.yaml file
    with open(os.path.join(EXAMPLE_DIR, "config.yaml"), "w") as f:
        f.write(
            """# Application configuration
database_url: "memory://demo"
log_level: "INFO"
debug_mode: false
max_users: 100
"""
        )

    print_system_message(f"Example project created at {EXAMPLE_DIR}")


async def run_code_search_example(agent):
    """Run the code search example scenario.

    Args:
        agent: The initialized agent
    """
    print_separator()
    print_system_message("CODE SEARCH EXAMPLE SCENARIO")
    print_system_message("We'll explore the example project codebase with the Claude agent")
    print_separator()

    # Create a context with our example project files
    example_files = []
    for root, _, files in os.walk(EXAMPLE_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            example_files.append(file_path)

    # Create user info with the example project files
    user_info = create_user_info(example_files)

    # Enhance user_info with file contents
    if "open_files" not in user_info:
        user_info["open_files"] = []
    else:
        # Clear any existing open_files to avoid format issues
        user_info["open_files"] = []

    # Add file contents to the open_files info - use simple string paths
    # instead of complex dictionaries to avoid issues with the tools
    user_info["open_files"] = example_files

    # Add file_contents separately as a dictionary for reference
    user_info["file_contents"] = {}
    for file_path in example_files:
        try:
            if os.path.isfile(file_path):  # Ensure it's a file
                with open(file_path, "r") as f:
                    content = f.read()
                user_info["file_contents"][file_path] = content
        except Exception as e:
            print_error(f"Error reading file {file_path}: {str(e)}")

    # Example queries
    example_queries = [
        "How does the logging system work in this project?",
        "What operations can be performed on users in the database?",
        "Show me how the application handles configuration.",
        "Explain the overall architecture of this project.",
    ]

    for i, query in enumerate(example_queries):
        print_separator()
        print_user_input(query)
        print_system_message("Processing request...")

        try:
            response = await agent.chat(query, user_info)
            print_assistant_response(response)
        except Exception as e:
            print_error(f"Error getting response: {str(e)}")

        # If not the last query, wait for user input
        if i < len(example_queries) - 1:
            input(f"{Colors.GRAY}Press Enter to continue to the next question...{Colors.RESET}")
        else:
            # Add a small delay for readability at the end
            await asyncio.sleep(1)

    print_separator()
    print_system_message("CODE SEARCH EXAMPLE COMPLETED")


async def main():
    """
    Main entry point for the code search example.
    """
    # Load environment variables
    load_dotenv()

    # Check for API keys
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not anthropic_key and not openai_key:
        print_error("No API keys found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file.")
        sys.exit(1)
    
    # Select model based on available keys
    if anthropic_key:
        model = "claude-3-5-sonnet-latest"
    elif openai_key:
        model = "gpt-4o"
    else:
        print_error("No API keys available")
        sys.exit(1)

    try:
        clear_screen()
        print_separator()
        print_system_message("CODE SEARCH EXAMPLE")
        print_system_message(
            "This example showcases the agent's ability to search and understand codebases."
        )
        print_separator()

        # Set up the example project
        setup_example_project()

        # Initialize the agent using cursor_agent package
        print_system_message(f"Initializing agent with model {model}...")

        # Use the cursor_agent.agent factory function
        agent = create_agent(model=model)
        print_system_message("Agent initialized successfully!")

        # Run the code search example
        await run_code_search_example(agent)

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up example files
        print_system_message("Cleaning up example files...")
        if os.path.exists(EXAMPLE_DIR):
            shutil.rmtree(EXAMPLE_DIR)
            print_system_message(f"Removed example directory {EXAMPLE_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
