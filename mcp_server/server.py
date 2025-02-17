"""
Primary MCP server entry point. 
Registers all necessary tools and runs the server.
"""
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP


# Initialize FastMCP server
mcp = FastMCP("weather3")

from .tools.plan_tool import generate_plan
from .tools.orchestrator import orchestrate
from .tools.combine_tool import combine_results
from .tools.upload_tool import upload_to_drive
from .tools.e2e_tool import full_research_pipeline

# Register the functions as a tool
mcp.tool()(generate_plan) # maybe a prompt
mcp.tool()(orchestrate)
mcp.tool()(combine_results) # maybe a prompt
mcp.tool()(upload_to_drive)
mcp.tool()(full_research_pipeline)

def activate_mcp_server(host: str = "0.0.0.0", port: int = 8000):
    """Activate the MCP server with the given host and port."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    activate_mcp_server()
