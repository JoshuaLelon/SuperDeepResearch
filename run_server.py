"""
Script to run the MCP server with proper path setup.
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server.server import activate_mcp_server

if __name__ == "__main__":
    activate_mcp_server() 