"""
Logging utilities
"""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", format_string: Optional[str] = None):
    """
    Setup logging configuration

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Optional custom format string
    """
    log_format = format_string or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
