#!/usr/bin/env python3
"""
Configuration management for the application.
"""

import os
import logging
import yaml
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class Config:
    """
    Configuration manager that loads settings from YAML files
    with environment variable override support.
    """
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
    
    def load(self, config_file: str):
        """
        Load configuration from a YAML file.
        
        Args:
            config_file: Path to the YAML configuration file
        """
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
        """Apply environment variable overrides to the configuration."""
        prefix = "APP_"
        for env_var, value in os.environ.items():
            if env_var.startswith(prefix):
                # Convert APP_DATABASE_URL to database_url
                config_key = env_var[len(prefix):].lower()
                self._config[config_key] = value
                logger.debug(f"Override config {config_key} from environment variable")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key
            default: Default value if key doesn't exist
            
        Returns:
            The configuration value or default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: The configuration key
            value: The value to set
        """
        self._config[key] = value
        logger.debug(f"Set config {key}")
