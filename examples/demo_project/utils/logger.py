#!/usr/bin/env python3
"""
Logging configuration for the application.
"""

import os
import logging
import logging.handlers
from typing import Optional

def setup_logger(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Set up the application logger.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
    """
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
