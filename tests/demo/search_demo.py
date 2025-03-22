#!/usr/bin/env python3
"""
Search demo for the Claude agent.
This script demonstrates the agent's capabilities for searching and understanding codebases.
"""

import os
import sys
import asyncio
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import the Claude agent
from agent.claude_agent import ClaudeAgent

# Import demo utilities
from tests.demo.utils import (
    print_user_input, 
    print_assistant_response,
    print_tool_call, 
    print_tool_result,
    print_system_message,
    print_error,
    print_separator,
    clear_screen,
    create_user_info,
    Colors
)

# Demo project directory
DEMO_DIR = os.path.join(os.path.dirname(__file__), "demo_project")

def setup_demo_project():
    """Set up a demo project with multiple files for the search demo."""
    
    # Create the demo project directory if it doesn't exist
    os.makedirs(DEMO_DIR, exist_ok=True)
    
    # Create main.py
    with open(os.path.join(DEMO_DIR, "main.py"), "w") as f:
        f.write("""#!/usr/bin/env python3
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
""")
    
    # Create models directory and user.py
    os.makedirs(os.path.join(DEMO_DIR, "models"), exist_ok=True)
    with open(os.path.join(DEMO_DIR, "models", "user.py"), "w") as f:
        f.write("""#!/usr/bin/env python3
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
""")
    
    # Create utils directory with logger.py and config.py
    os.makedirs(os.path.join(DEMO_DIR, "utils"), exist_ok=True)
    
    with open(os.path.join(DEMO_DIR, "utils", "logger.py"), "w") as f:
        f.write("""#!/usr/bin/env python3
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
""")
    
    with open(os.path.join(DEMO_DIR, "utils", "config.py"), "w") as f:
        f.write("""#!/usr/bin/env python3
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
""")

    # Create database.py
    with open(os.path.join(DEMO_DIR, "database.py"), "w") as f:
        f.write("""#!/usr/bin/env python3
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
""")

    # Create a README.md file
    with open(os.path.join(DEMO_DIR, "README.md"), "w") as f:
        f.write("""# Demo Project

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
""")

    # Create an empty config.yaml file
    with open(os.path.join(DEMO_DIR, "config.yaml"), "w") as f:
        f.write("""# Application configuration
database_url: "memory://demo"
log_level: "INFO"
debug_mode: false
max_users: 100
""")
    
    print_system_message(f"Demo project created at {DEMO_DIR}")

async def run_search_demo(agent, non_interactive=False):
    """Run the search demo scenario.
    
    Args:
        agent: The initialized Claude agent
        non_interactive: If True, don't wait for user input between steps
    """
    print_separator()
    print_system_message("SEARCH DEMO SCENARIO")
    print_system_message("We'll explore the demo project codebase with the Claude agent")
    print_separator()
    
    # Create a context with our demo project files
    demo_files = []
    for root, _, files in os.walk(DEMO_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            demo_files.append(file_path)
    
    # Create user info with the demo project files
    user_info = create_user_info(demo_files)
    
    # Enhance user_info with file contents
    if 'open_files' not in user_info:
        user_info['open_files'] = []
    else:
        # Clear any existing open_files to avoid format issues
        user_info['open_files'] = []
    
    # Add file contents to the open_files info - use simple string paths
    # instead of complex dictionaries to avoid issues with the tools
    user_info['open_files'] = demo_files
    
    # Add file_contents separately as a dictionary for reference
    user_info['file_contents'] = {}
    for file_path in demo_files:
        try:
            if os.path.isfile(file_path):  # Ensure it's a file
                with open(file_path, 'r') as f:
                    content = f.read()
                user_info['file_contents'][file_path] = content
        except Exception as e:
            print_error(f"Error reading file {file_path}: {str(e)}")
    
    # Demo queries
    demo_queries = [
        "How does the logging system work in this project?",
        "What operations can be performed on users in the database?",
        "Show me how the application handles configuration.",
        "Explain the overall architecture of this project."
    ]
    
    for i, query in enumerate(demo_queries):
        print_separator()
        print_user_input(query)
        print_system_message("Processing request...")
        
        try:
            response = await agent.chat(query, user_info)
            print_assistant_response(response)
        except Exception as e:
            print_error(f"Error getting response: {str(e)}")
        
        # If not the last query and in interactive mode, wait for user input
        if i < len(demo_queries) - 1 and not non_interactive:
            input(f"{Colors.GRAY}Press Enter to continue to the next question...{Colors.ENDC}")
        elif non_interactive:
            # Add a small delay for readability in non-interactive mode
            await asyncio.sleep(3)
    
    print_separator()
    print_system_message("SEARCH DEMO COMPLETED")

async def main(non_interactive=False):
    """Main entry point for the demo.
    
    Args:
        non_interactive: When True, run in non-interactive mode without pauses
    """
    # Load environment variables
    env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
    if env_path.exists():
        print_system_message(f"Loading environment variables from {env_path}")
        load_dotenv(dotenv_path=env_path)
    
    # Check if API key is present
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print_error("ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)
    
    try:
        clear_screen()
        print_separator()
        print_system_message("CODE SEARCH DEMO")
        print_system_message("This demo showcases the Claude agent's ability to search and understand codebases.")
        
        if non_interactive:
            print_system_message("Running in non-interactive mode (no pauses between steps)")
        
        print_separator()
        
        # Set up the demo project
        setup_demo_project()
        
        # Initialize the Claude agent
        print_system_message("Initializing Claude agent...")
        agent = ClaudeAgent(api_key=api_key)
        agent.register_default_tools()
        print_system_message("Claude agent initialized successfully!")
        
        # Run the search demo
        await run_search_demo(agent, non_interactive=non_interactive)
        
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up demo files
        print_system_message("Cleaning up demo files...")
        if os.path.exists(DEMO_DIR):
            shutil.rmtree(DEMO_DIR)
            print_system_message(f"Removed demo directory {DEMO_DIR}")

# Add a dedicated non-interactive main function for backwards compatibility
async def main_non_interactive():
    """Run the demo in non-interactive mode without pauses between steps."""
    await main(non_interactive=True)

if __name__ == "__main__":
    asyncio.run(main())