# MCP Server (mcp_server)

This directory contains the MCP server logic: a FastAPI-based server that coordinates multi-product deep research.

## Overview

- **`__init__.py`**  
  Exports server activation logic if needed (e.g., `activate_mcp_server`).

- **`server.py`**  
  Main entry point for running the MCP server (FastAPI + uvicorn).  
  - Declares a `FastAPI` app.  
  - Optionally loads routes for each tool.

- **`tools/`**  
  A subdirectory of “tools” modules that implement each major function:
  - Plan generation (`plan_tool.py`)
  - Multi-product orchestration (`orchestrator.py`)
  - Single-product research via headless browser (`single_research.py`)
  - Combination of partial results (`combine_tool.py`)
  - Upload sources to Google Drive (`upload_tool.py`)
  - Complete E2E pipeline (`e2e_tool.py`)

## Running the Server

1. From the project root, install dependencies (see top-level `README.md`).  
2. Start the FastAPI app:
   ```
   python -m mcp_server.server
   ```
3. The server listens on port 8000 by default:
   ```
   http://localhost:8000
   ```

## Endpoints

(Currently, endpoints are placeholders, but generally you’d define routes in `server.py` or a dedicated router module within `tools/`.)

For details on each tool, see [tools/README.md](tools/README.md).

## Updating This Documentation

- When adding new tools or changing the server structure, update this file.  
- Also update the root `README.md` to reflect high-level changes across the project.