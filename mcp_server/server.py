"""
Primary MCP server entry point. 
Registers all necessary tools and runs the server.
"""
import sys
import logging
import asyncio
from typing import Optional

# Completely disable all logging before importing anything else
logging.getLogger().setLevel(logging.CRITICAL)
for handler in logging.getLogger().handlers[:]:
    logging.getLogger().removeHandler(handler)
logging.getLogger().addHandler(logging.NullHandler())

# Now import other modules
from mcp.server.fastmcp import FastMCP
from mcp_server.tools.research_engine import (
    deep_research,
    BrowserApproach,
    ResearchConfig,
    ResearchSite
)

def log_to_stderr(message: str) -> None:
    """Log a message to stderr that will be captured by MCP."""
    print(message, file=sys.stderr, flush=True)

# Initialize FastMCP server
mcp = FastMCP("SuperDeepResearch")

async def research_tool(
    query: str,
    site: Optional[str] = None,
    approach: Optional[str] = None,
    headless: bool = True,
    max_retries: int = 3
) -> str:
    """
    MCP tool for executing research using specified browser approach and site.
    
    Args:
        query: Research query to execute
        site: Research site to use (gemini or perplexity)
        approach: Browser approach to use (browser_use, nodriver, or playwright)
        headless: Whether to run in headless mode
        max_retries: Maximum number of retry attempts
    
    Returns:
        Research results as text
    """
    browser_approach = BrowserApproach(approach or BrowserApproach.PATCHRIGHT)
    research_site = ResearchSite(site or ResearchSite.GEMINI)
    config = ResearchConfig(headless=headless, max_retries=max_retries)
    
    try:
        result = await deep_research(query, browser_approach, research_site, config)
        return result
    except Exception as e:
        log_to_stderr(f"Research failed: {str(e)}")
        raise

# Register the research tool
try:
    log_to_stderr("Registering research tool...")
    mcp.tool()(research_tool)
    log_to_stderr("Successfully registered research tool")
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



