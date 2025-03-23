#!/usr/bin/env python3
"""
Demo project main entry point.
"""

import logging
from models.user import User
from utils.config import Config
from utils.logger import setup_logger
from database import Database

# Set up logging
setup_logger()
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application."""
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
