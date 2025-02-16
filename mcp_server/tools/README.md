# MCP Server Tools

This directory contains Python files that implement the core functionality of the MCP server.

## Contents

- **`plan_tool.py`**  
  Generates a plan from a user query (e.g., which products to query, how to parse them, etc.).

- **`orchestrator.py`**  
  Orchestrates multi-product research. Takes a plan from `plan_tool.py` and calls `single_research.py` for each step.

- **`single_research.py`**  
  Uses headless browser logic to interact with a single product’s website or API.

- **`combine_tool.py`**  
  Combines multiple partial results into a single comprehensive report and gathers references/sources.

- **`upload_tool.py`**  
  Uploads the collected sources or references to Google Drive (or other storage systems in the future).

- **`e2e_tool.py`**  
  The end-to-end pipeline that:
  1. Generates a plan from the user query.  
  2. Orchestrates each step.  
  3. Combines results.  
  4. Optionally uploads sources.  
  5. Returns the final combined report and references.

## Usage Examples

Example usage of an individual tool:
```
python
from mcp_server.tools.plan_tool import generate_plan
my_query = "Investigate the current capabilities of Gemini vs Perplexity AI"
plan = generate_plan(my_query)
print(plan)
```

Example usage of the entire pipeline:
```
python
from mcp_server.tools.e2e_tool import full_research_pipeline
query = "Compare GPT-4 vs Gemini in summarizing climate change data"
result = full_research_pipeline(query, do_upload=True)
print(result["report"])
print(result["sources"])
print(result["driveInfo"])
```


## Adding New Tools

1. Create a new Python file (e.g., `my_new_tool.py`) in `tools/`.  
2. Implement your function(s).  
3. Integrate it in `server.py` or elsewhere if you want to expose it via the MCP server.  
4. Update this `README.md` with details about the new tool.

## Further Reading

- [mcp_server/README.md](../README.md) for how the server is set up.
- [../docs/](../../docs/README.md) for diagrams and technical references.