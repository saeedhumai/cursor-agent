#!/usr/bin/env python3
"""
Database access layer for the application.
"""

import logging
from typing import List, Optional, Dict, Any
from models.user import User

logger = logging.getLogger(__name__)

class Database:
    """Simple in-memory database for demonstration purposes."""
    
    def __init__(self, connection_string: str):
        """
        Initialize the database.
        
        Args:
            connection_string: Database connection string (not used in this demo)
        """
        self._connection_string = connection_string
        logger.info(f"Connecting to database: {connection_string}")
        
        # In-memory storage
        self._users: Dict[str, User] = {}
        
        logger.info("Database initialized")
    
    def save_user(self, user: User) -> bool:
        """
        Save a user to the database.
        
        Args:
            user: User object to save
            
        Returns:
            True if successful
        """
        if not user.username:
            logger.error("Cannot save user with empty username")
            return False
        
        self._users[user.username] = user
        logger.debug(f"Saved user: {user.username}")
        return True
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Retrieve a user by username.
        
        Args:
            username: The username to look up
            
        Returns:
            User object if found, None otherwise
        """
        user = self._users.get(username)
        if user:
            logger.debug(f"Retrieved user: {username}")
        else:
            logger.debug(f"User not found: {username}")
        return user
    
    def get_all_users(self) -> List[User]:
        """
        Get all users in the database.
        
        Returns:
            List of User objects
        """
        users = list(self._users.values())
        logger.debug(f"Retrieved {len(users)} users")
        return users
    
    def delete_user(self, username: str) -> bool:
        """
        Delete a user from the database.
        
        Args:
            username: Username of the user to delete
            
        Returns:
            True if user was deleted, False if not found
        """
        if username in self._users:
            del self._users[username]
            logger.info(f"Deleted user: {username}")
            return True
        
        logger.warning(f"Attempted to delete non-existent user: {username}")
        return False
    
    def search_users(self, **criteria) -> List[User]:
        """
        Search for users matching the given criteria.
        
        Args:
            **criteria: Field-value pairs to match
            
        Returns:
            List of matching User objects
        """
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
