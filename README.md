# Deep Research MCP

High-level overview of the project:

- **Purpose**: Orchestrate queries across multiple deep research platforms, combine results, and upload sources.
- **Structure**:
  - `mcp_server`: Python MCP server and tool definitions.
  - `docs`: Documentation and diagrams.
  - `scripts`: Deployment and local testing scripts.

## Project Structure

- `mcp_server/` - Contains the Python MCP server and tools.
+ `scripts/` - Contains shell scripts for testing, building, and deploying the project.

## Installation & Usage
No changes needed here, but reference the scripts for quick test / deploy operations.


## Directory Tree 
├── mcp_server/
│   ├── __init__.py
│   ├── server.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── plan_tool.py
│   │   ├── orchestrator.py
│   │   ├── single_research.py
│   │   ├── combine_tool.py
│   │   ├── upload_tool.py
│   └── README.md
│   └── e2e_tool.py
├── docs/
│   ├── diagrams/
│   │   ├── state.md
│   │   ├── sequence.md
│   │   ├── flow.md
│   └── README.md
├── scripts/
│   ├── local_test.sh
│   └── deploy.sh
├── pyproject.toml
├── requirements.txt
├── README.md
└── LICENSE

## mcp_server

Contains the MCP server implementation which orchestrates deep research:
- Exposes API endpoints to create a research plan, conduct multi-product analysis, combine results, and optionally upload sources to Google Drive.
- Built using FastAPI and uvicorn.

See [mcp_server/README.md](./mcp_server/README.md) for details.