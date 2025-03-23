#!/usr/bin/env python3
"""
User model definition.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger(__name__)

@dataclass
class User:
    """Represents a user in the system."""
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    preferences: Optional[dict] = None
    
    def __post_init__(self):
        logger.debug(f"Created new User: {self.username}")
    
    def full_name(self) -> str:
        """Return the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def deactivate(self):
        """Deactivate this user."""
        self.is_active = False
        logger.info(f"User {self.username} has been deactivated")
    
    def update_email(self, new_email: str):
        """Update the user's email address."""
        old_email = self.email
        self.email = new_email
        logger.info(f"Updated email for {self.username} from {old_email} to {new_email}")
    
    def set_preference(self, key: str, value):
        """Set a user preference."""
        if self.preferences is None:
            self.preferences = {}
        self.preferences[key] = value
        logger.debug(f"Set preference {key} for user {self.username}")
