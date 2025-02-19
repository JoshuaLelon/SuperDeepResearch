"""
Script to run the MCP server with proper path setup.
Provides access to the Gemini research tool via MCP.
"""
import sys
import os
import logging
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from mcp_server.server import activate_mcp_server

if __name__ == "__main__":
    activate_mcp_server() 