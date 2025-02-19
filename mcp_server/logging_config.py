"""
Centralized logging configuration for the MCP server.
"""
import os
import logging

def setup_logging(name: str) -> logging.Logger:
    """
    Set up logging configuration for the given module name.
    Returns a configured logger instance.
    """
    log_dir = os.path.expanduser("~/Library/Logs/Claude")
    log_file = os.path.join(log_dir, "mcp_server.log")

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)  # Set console to INFO level

    # Get logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    # Remove any existing handlers to avoid duplicates
    logger.handlers = []
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger 