"""
Primary MCP server entry point. 
Registers all necessary tools and runs the server.
"""
import sys
import logging

# Completely disable all logging before importing anything else
logging.getLogger().setLevel(logging.CRITICAL)
for handler in logging.getLogger().handlers[:]:
    logging.getLogger().removeHandler(handler)
logging.getLogger().addHandler(logging.NullHandler())

# Now import other modules
import httpx
from mcp.server.fastmcp import FastMCP
from mcp_server.tools import (
    # generate_plan,
    # orchestrate,
    # combine_results,
    # upload_to_drive,
    full_research_pipeline
)

def log_to_stderr(message: str) -> None:
    """Log a message to stderr that will be captured by MCP."""
    print(message, file=sys.stderr, flush=True)

# Initialize FastMCP server
mcp = FastMCP("weather3")

# Register the functions as a tool
# mcp.tool()(generate_plan)
# mcp.tool()(orchestrate)
# mcp.tool()(combine_results)
# mcp.tool()(upload_to_drive)
try:
    log_to_stderr("Attempting to register full_research_pipeline tool...")
    mcp.tool()(full_research_pipeline)
    log_to_stderr("Successfully registered full_research_pipeline tool")
except Exception as e:
    log_to_stderr(f"Error: Failed to register tool: {str(e)}")
    raise

def activate_mcp_server(host: str = "0.0.0.0", port: int = 8000):
    """Activate the MCP server with the given host and port."""
    try:
        log_to_stderr("Starting MCP server...")
        mcp.run(transport='stdio')
        log_to_stderr("MCP server running")
    except Exception as e:
        log_to_stderr(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    activate_mcp_server()



