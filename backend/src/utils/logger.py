"""
Logging utilities for the RAG Book Chatbot backend.
"""

import logging
import sys
from src.config import settings


def setup_logger(name: str = "rag_book_chatbot") -> logging.Logger:
    """
    Set up and configure a logger with consistent formatting.

    Args:
        name: Name of the logger

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


# Global logger instance
logger = setup_logger()
