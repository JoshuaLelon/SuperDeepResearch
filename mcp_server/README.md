# MCP Server (mcp_server)

This directory contains the MCP server code that orchestrates deep research across multiple products and tools.

## Overview

- **`__init__.py`**: Initializes the MCP Server package.  
- **`server.py`**: Main entry point for running the MCP server.  
  - Uses FastAPI with uvicorn to expose endpoints.  
  - Expects to configure all relevant tools and routes here.  

## Usage

1. **Install dependencies** using your chosen Python environment (see project-level [requirements.txt] or [pyproject.toml]).  
2. **Run the server**:
   ```bash
   python -m mcp_server.server
   ```
3. **Access** the MCP endpoints at `http://localhost:8000`.

## Technical Detail

- Built with FastAPI, running on uvicorn.  
- Tools are expected to be registered in `server.py` or a dedicated `tools` subpackage (not yet shown).  

## Updating Documentation

If you make changes here, also update the higher-level `README.md` files in the project, detailing any new tools or endpoints provided by this server.