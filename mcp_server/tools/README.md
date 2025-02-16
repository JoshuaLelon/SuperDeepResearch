# MCP Server

This directory contains the MCP server logic and exposed tools.

## Contents

- **server.py**: Entry point; sets up the MCP server, registers tools/routes.
- **tools**: Directory with all tools:
  - **plan_tool.py**  
    Generates a plan from a user query.
  - **orchestrator.py**  
    Coordinates multi-product research with single product calls.
  - **single_research.py**  
    Performs a single-product search using headless browsing.
  - **combine_tool.py**  
    Combines results into a consolidated report.
  - **upload_tool.py**  
    Uploads sources to Google Drive.
  - **e2e_tool.py**  
    End-to-end pipeline from query to final compiled report.
