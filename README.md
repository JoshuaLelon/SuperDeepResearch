# Deep Research MCP

A high-level overview of the project that orchestrates deep research queries across multiple products (Gemini, OpenAI, Perplexity, etc.), combines their outputs, and optionally uploads sources to Google Drive.

## Purpose

- Provide a unified interface (MCP server) to run "deep research" queries.
- Query multiple external products using headless browsers.
- Consolidate search results into a single comprehensive report.
- Store references and source material (e.g., in Google Drive).

## Core Components

- **Plan Generation**: Convert a user's query into a structured research plan.  
- **Orchestration**: Loop through multiple products, orchestrate each step, and gather partial results.  
- **Combination**: Merge partial results into one comprehensive report and keep track of references/sources.  
- **Uploading**: Optionally upload source documents or references to Google Drive.  
- **End-to-end Flow**: A single tool that takes a raw query and returns the final compiled report and optional Drive links.

## Project Structure

- `mcp_server/`  
  Contains the main Python MCP server implementation and its tools.  
  See [mcp_server/README.md](./mcp_server/README.md) for details.
- `docs/`  
  Documentation and diagrams. See [docs/README.md](./docs/README.md).  
- `scripts/`  
  Shell scripts for local testing, building, deployment, etc. See [scripts/README.md](./scripts/README.md).
- `pyproject.toml` / `requirements.txt`  
  Python dependency management with either Poetry or pip.

## Installation & Usage

1. Clone the repository locally.  
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   or set up a virtual environment first:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the MCP server:
   ```
   python -m mcp_server.server
   ```
   The server (FastAPI) should be available at `http://localhost:8000`.

## Directory Tree
├── mcp_server/
│ ├── init.py
│ ├── server.py
│ ├── tools/
│ │ ├── init.py
│ │ ├── plan_tool.py
│ │ ├── orchestrator.py
│ │ ├── single_research.py
│ │ ├── combine_tool.py
│ │ ├── upload_tool.py
│ │ └── e2e_tool.py
│ └── README.md
├── docs/
│ ├── diagrams/
│ │ ├── state.md
│ │ ├── sequence.md
│ │ └── flow.md
│ └── README.md
├── scripts/
│ ├── local_test.sh
│ ├── deploy.sh
│ └── README.md
├── pyproject.toml
├── requirements.txt
├── README.md
└── LICENSE

For more details on each subdirectory, see the corresponding `README.md` within that directory.

The MCP server uses a headless browser approach (via `browser-use`) in `single_research.py`
1. Generate plan (`plan_tool.py`)  
2. Orchestrate multi-product searches (`orchestrator.py`)  
3. Combine results (`combine_tool.py`)  
4. (Optionally) upload to Google Drive (`upload_tool.py`)  

Everything is combined in `e2e_tool.py`.