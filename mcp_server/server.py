"""
Primary MCP server entry point. 
Registers all necessary tools and runs the server.
"""
import uvicorn
from fastapi import FastAPI

# Placeholder for an actual tools config function:
# from .tools import configure_tools

app = FastAPI(title="Deep Research MCP Server")

# Example of how you'd load your tool routes
# def load_tools():
#     configure_tools(app)

def activate_mcp_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Activates the MCP server using uvicorn.
    """
    # load_tools()
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    activate_mcp_server() 