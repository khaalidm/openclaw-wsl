"""
Logging utilities for OpenClaw Agent
"""
import sys
from loguru import logger


def setup_logger(level: str = "INFO"):
    """
    Configure the application logger.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    """
    logger.remove()
    
    # Console output with colors
    logger.add(
        sys.stderr,
        level=level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True
    )
    
    # File output
    logger.add(
        "logs/openclaw_{time:YYYY-MM-DD}.log",
        level=level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="7 days",
        compression="zip"
    )
    
    return logger


def get_logger():
    """Get the configured logger instance."""
    return logger
