"""
Logger module for cursor-agent.

This module provides a standardized logging configuration for all cursor-agent components.
"""

import logging
import os
import sys
from typing import Optional

# Default log format includes timestamp, level, and message
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Environment variable to control log level
LOG_LEVEL_ENV_VAR = "CURSOR_AGENT_LOG_LEVEL"

# Color codes for terminal outpu
COLORS = {
    "RESET": "\033[0m",
    "DEBUG": "\033[36m",    # Cyan
    "INFO": "\033[32m",     # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",    # Red
    "CRITICAL": "\033[35m",  # Magenta
}


class ColoredFormatter(logging.Formatter):
    """Logging formatter that adds color to terminal output."""

    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        return super().format(record)


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger instance configured with standardized settings.

    Args:
        name: The name of the logger, typically __name__
        level: Optional log level override (default: from environment or INFO)

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure the logger if it hasn't been configured ye
    if not logger.handlers:
        # Determine the log level (from environment variable or default)
        if level is None:
            env_level = os.environ.get(LOG_LEVEL_ENV_VAR)
            if env_level:
                try:
                    level = getattr(logging, env_level.upper())
                except AttributeError:
                    level = logging.INFO
            else:
                level = logging.INFO

        logger.setLevel(level)

        # Create console handler with color formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Use colored output for terminal
        formatter = ColoredFormatter(DEFAULT_LOG_FORMAT)
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger


def setup_logging(level: Optional[int] = None, log_file: Optional[str] = None) -> None:
    """
    Setup logging globally with optional file output.

    Args:
        level: Optional log level override (default: from environment or INFO)
        log_file: Optional path to write logs to a file
    """
    # Get the root logger
    root_logger = logging.getLogger()

    # Determine the log level
    if level is None:
        env_level = os.environ.get(LOG_LEVEL_ENV_VAR)
        if env_level:
            try:
                level = getattr(logging, env_level.upper())
            except AttributeError:
                level = logging.INFO
        else:
            level = logging.INFO

    root_logger.setLevel(level)

    # Remove existing handlers (for reconfiguration cases)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter(DEFAULT_LOG_FORMAT))
    root_logger.addHandler(console_handler)

    # File handler (if requested)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        root_logger.addHandler(file_handler)
