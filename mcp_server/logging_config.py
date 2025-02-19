"""
Centralized logging configuration for the MCP server.
"""
import os
import logging
from pathlib import Path

def setup_logging(name: str) -> logging.Logger:
    """
    Set up logging configuration for the given module name.
    Returns a configured logger instance.
    """
    # Get project root directory (parent of mcp_server)
    project_root = Path(__file__).parent.parent
    log_dir = project_root / "logs"
    
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = log_dir / "mcp_server.log"

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)  # Set file to DEBUG level for detailed logs

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