# MCP Server (mcp_server)

This directory contains the MCP server logic: a server that coordinates Gemini research using multiple browser automation approaches. The server uses FastMCP (MCP's Python SDK) for tool registration and communication.

## Overview

- **`__init__.py`**  
  Exports server activation logic (e.g., `activate_mcp_server`).

- **`server.py`**  
  Main entry point for running the MCP server.  
  - Initializes FastMCP instance
  - Registers research tools
  - Handles error logging and reporting
  - Communicates via stdio transport

- **`tools/`**  
  Contains the core research functionality:
  - **`gemini_scrapers_base/`**: Shared utilities and implementations
    - Base classes and interfaces
    - Authentication handling
    - Browser-specific implementations (Browser-use, NoDriver, Patchright)
  - **`single_research.py`**: Main entry point for research execution

## Running the Server

1. From the project root, install dependencies (see top-level `README.md`).  
2. Start the MCP server:
   ```bash
   python run_server.py
   ```
3. The server communicates via stdio and can be used with any MCP client.

## Using the Research Tool

```python
from mcp_server.tools.single_research import (
    gemini_deep_research,
    BrowserApproach,
    ResearchConfig
)

# Configure research
config = ResearchConfig(
    headless=True,
    window_width=1920,
    window_height=1080
)

# Execute research using chosen approach
result = await gemini_deep_research(
    plan="your research query",
    approach=BrowserApproach.PATCHRIGHT,  # or BROWSER_USE, or NODRIVER
    config=config
)
```

## Browser Automation Approaches

1. **Browser-use**
   - Uses browser-use library
   - LLM-based agent for navigation
   - Handles complex interactions

2. **NoDriver**
   - Uses undetected-chromedriver
   - Stealth browser automation
   - Detection bypass features

3. **Patchright**
   - Enhanced fork of Playwright
   - Additional evasion techniques
   - Robust browser control

## Testing

Each approach has a dedicated test script in `scripts/`:
```bash
# Test NoDriver
python -m scripts.test_nodriver --query "query" --headless true

# Test Browser-use
python -m scripts.test_browser_use --query "query" --headless true

# Test Patchright
python -m scripts.test_patchright --query "query" --headless true
```

## Documentation

For more details, see:
- [tools/README.md](tools/README.md) for tool-specific documentation
- [tools/gemini_scrapers_base/README.md](tools/gemini_scrapers_base/README.md) for implementation details
- [../docs/](../docs/README.md) for diagrams and technical references

## MCP Integration

The server exposes a single MCP tool for research that accepts:
- `query`: The research query to execute
- `approach`: Browser approach to use (optional, defaults to browser_use)
- `headless`: Whether to run in headless mode (optional, defaults to true)
- `max_retries`: Maximum retry attempts (optional, defaults to 3)

The tool is registered with FastMCP and communicates via stdio transport, making it compatible with any MCP client.

## Updating This Documentation

- When adding new tools or changing the server structure, update this file.
- Also update the root `README.md` to reflect high-level changes across the project.

## Example Usage

With the MCP Python SDK integrated, you can connect a local MCP client (like Claude Desktop or your own MCP client) to use the provided tools in `tools/`. For details on each tool, see [tools/README.md](tools/README.md).
