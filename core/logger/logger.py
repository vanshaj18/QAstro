"""
Module handles the logging of the application.
"""
import logging
import datetime
import os
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

current_dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"logs/{current_dt}.log"

def setup_logger(file_name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Sets up and configures a logger with both file and console handlers.
    
    Args:
        file_name (str): Name of the logger (typically __name__ or module name).
        log_level (int): Logging level (default: logging.INFO).
                        Options: logging.DEBUG, logging.INFO, logging.WARNING, 
                                 logging.ERROR, logging.CRITICAL
    
    Returns:
        logging.Logger: Configured logger instance.
    
    Example:
        >>> logger = setup_logger(__name__) 
        >>> logger.info("Application started")
    """
    # Create logger
    logger = logging.getLogger(file_name)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    
    # File handler - logs to file
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    
    # Console handler - logs to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger