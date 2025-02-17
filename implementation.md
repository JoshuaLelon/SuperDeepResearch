# Implementation Plan

Below is a step-by-step plan (formatted as a series of checklist items) for implementing the MCP server that combines multiple deep research products into a single comprehensive report, optionally uploading sources to Google Drive. Each checklist item includes tasks and reference code snippets.

---

## 1. Project Initialization

- [ ] Create a new Python project (or reuse your existing structure)  
  - [ ] Ensure you have the recommended project files:  
    - pyproject.toml or setup.py to manage dependencies  
    - requirements.txt for quick installation  
    - README.md to explain the project at a high level  

Example snippet (pyproject.toml):
```toml
[project]
name = "deep-research-mcp"
version = "0.1.0"
description = "MCP server for multi-product deep research"

[project.scripts]
activate_mcp_server = "mcp_server:activate_mcp_server"

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

- [ ] Update or create a top-level README.md with:  
  - [ ] Purpose of the project  
  - [ ] Installation steps  
  - [ ] Usage instructions (running the MCP server, endpoints, etc.)

---

## 2. Install and Configure Dependencies

- [ ] Install necessary Python libraries:  
  - [ ] fastapi, uvicorn (server and HTTP)  
  - [ ] requests or httpx (for potential web requests)  
  - [ ] google-auth libraries (for Drive uploads)  
  - [ ] browser-use (for headless browser research)  
  - [ ] LangChain (py) or LangGraph (py) if needed for building the plan logic  
  - [ ] MCP Python SDK references (based on @Docs: MCP / @python-sdk)

Example snippet (requirements.txt):
```text
fastapi==0.103.2
uvicorn==0.23.2
requests==2.31.0
google-auth==2.21.0
google-auth-oauthlib==1.0.0
httpx==0.24.1
browser-use==0.0.1
langchain==0.0.1
langgraph==0.0.1
```

- [ ] Create or update the __init__.py and server.py to load/install these dependencies at runtime if needed.

---

## 3. Set Up the FastAPI MCP Server

- [ ] Create or update mcp_server/server.py:
  - [ ] Import FastAPI.  
  - [ ] Instantiate your FastAPI app.  
  - [ ] If using the MCP Python SDK, ensure the server is recognized as an MCP-compliant endpoint. (Review the @python-sdk for examples.)  
  - [ ] (Optional) If you plan to register routes for each tool, consider a router-based approach.

Example snippet (server.py):
```python
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Deep Research MCP Server")

def activate_mcp_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    activate_mcp_server()
```

- [ ] Update mcp_server/README.md to include details on how to run:
  - [ ] “python -m mcp_server.server”  

---

## 4. Implement the Tool: Query → Research Plan

- [ ] Create or update mcp_server/tools/plan_tool.py:
  - [ ] A function that takes a user’s query string and returns a structured plan dict.  
  - [ ] (Optionally) Integrate LangChain or LangGraph to parse or refine the plan.

Example snippet (plan_tool.py):
```python
def generate_plan(query: str) -> Dict[str, Any]:
    # Optionally use LangChain or LangGraph for advanced logic
    plan = {
        "query": query,
        "steps": [
            {"product": "gemini",      "search_terms": [query]},
            {"product": "perplexity",  "search_terms": [query]},
            {"product": "openai",      "search_terms": [query]}
        ]
    }
    return plan
```

- [ ] Update mcp_server/tools/README.md to document:
  - [ ] The purpose of plan_tool.py  
  - [ ] Example usage  

---

## 5. Implement the Tool: Single-Product Research

- [ ] Create or update mcp_server/tools/single_research.py:
  - [ ] A function that performs a headless browser search for one product using browser-use  
  - [ ] For advanced usage, consult @relishplus as a reference on how to script browser tasks  

Example snippet (single_research.py):
```python
def single_product_research(product: str, terms: List[str]) -> str:
    # Pseudo-code for browser-based search
    # - e.g. from browser_use.expansion import Browser
    # - browser.run_search(...)
    return f"Sample results for {product} with terms: {terms}"
```

- [ ] Update mcp_server/tools/README.md with:
  - [ ] Overviews on how single_research.py uses browser-use  

---

## 6. Implement the Tool: Orchestrator

- [ ] Create or update mcp_server/tools/orchestrator.py:
  - [ ] A function that takes the plan from plan_tool.py  
  - [ ] Loops through each “product” step, calling single_product_research  
  - [ ] Collects all partial results into a list

Example snippet (orchestrator.py):
```python
def orchestrate(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    for step in plan.get("steps", []):
        product = step["product"]
        terms = step["search_terms"]
        partial = single_product_research(product, terms)
        results.append({
            "product": product,
            "results": partial
        })
    return results
```

- [ ] Document usage in mcp_server/tools/README.md  

---

## 7. Implement the Tool: Combine Multiple Results

- [ ] Create or update mcp_server/tools/combine_tool.py:
  - [ ] A function that merges partial results into a single big “report” string, and optionally compiles all sources into a single list.  

Example snippet (combine_tool.py):
```python
def combine_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    report_fragments = []
    sources = []
    for item in results:
        report_fragments.append(item["results"])
        sources.append(f"Source: {item['product']}")
    combined_report = "\n\n".join(report_fragments)
    return {
        "report": combined_report,
        "sources": sources
    }
```

- [ ] Document usage in mcp_server/tools/README.md  

---

## 8. Implement the Tool: Upload to Google Drive

- [ ] Create or update mcp_server/tools/upload_tool.py:
  - [ ] A function to upload local or in-memory data to Google Drive  

Example snippet (upload_tool.py):
```python
def upload_to_drive(sources: List[str]) -> List[Dict[str, str]]:
    drive_refs = []
    for src in sources:
        # Integrate google-auth requirements or googleapiclient
        # Upload logic omitted for brevity
        drive_refs.append({"src": src, "driveId": f"drive_id_{src}"})
    return drive_refs
```

- [ ] Document usage in mcp_server/tools/README.md  

---

## 9. Implement the Tool: Full End-to-End Pipeline

- [ ] Create or update mcp_server/tools/e2e_tool.py:
  - [ ] A function that:  
    1) Calls generate_plan(query)  
    2) Calls orchestrate(plan)  
    3) Calls combine_results(partials)  
    4) Optionally calls upload_to_drive(sources)  
    5) Returns the final single “super report” + drive references  

Example snippet (e2e_tool.py):
```python
def full_research_pipeline(query: str, do_upload: bool = False) -> Dict[str, Any]:
    plan = generate_plan(query)
    partials = orchestrate(plan)
    combined = combine_results(partials)

    drive_info = None
    if do_upload:
        drive_info = upload_to_drive(combined["sources"])

    return {
        "report": combined["report"],
        "sources": combined["sources"],
        "driveInfo": drive_info
    }
```

- [ ] Document usage in mcp_server/tools/README.md  

---

## 10. Register the Tools with MCP

- [ ] If you wish to directly expose these Python functions as MCP Tools:  
  - [ ] Use the MCP Python SDK (from @Docs: MCP / @python-sdk)  
  - [ ] Create definitions (e.g., JSON schema) for each tool’s input and output, so Claude Desktop can call them

Example snippet (tool registration):
```python
# pseudo-code referencing MCP types
from mcp_sdk.types import ToolDefinition

UPLOAD_TOOL = ToolDefinition(
    name="upload_to_drive",
    description="Uploads a list of string references to GDrive.",
    input_schema={"type": "object", "properties": {...}},
    output_schema={"type": "object", "properties": {...}},
    func=upload_to_drive
)
```

- [ ] Ensure the server is aware of your tool definitions (via some config step or through dynamic discovery).  

---

## 11. Document and Verify Everything

- [ ] Update the top-level README.md to reflect new features and usage instructions.  
- [ ] Update mcp_server/README.md and each relevant subdirectory’s README.md with references to the new or changed files.  
- [ ] Provide usage examples for local testing, e.g.:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m mcp_server.server
```

---

## 12. Testing Strategy

- [ ] Write at least basic unit tests:
  - [ ] plan_tool_test.py  
  - [ ] single_research_test.py  
  - [ ] orchestrator_test.py  
  - [ ] combine_tool_test.py  
  - [ ] upload_tool_test.py  
  - [ ] e2e_tool_test.py  

- [ ] Consider integration tests that:  
  - [ ] Launch a local server  
  - [ ] Make requests to each tool’s endpoint  
  - [ ] Validate combined results and (optionally) Drive upload references  

Example snippet (pytest):
```python
def test_plan_tool():
    plan = generate_plan("Test Query")
    assert "steps" in plan
    assert len(plan["steps"]) > 0
```

---

## 13. Deployment (Optional)

- [ ] If containerizing:
  - [ ] Create a Dockerfile for building the FastAPI server  
  - [ ] Use a script (e.g., scripts/deploy.sh) to push to a registry  
  - [ ] Confirm environment variables for Google credentials are set up in the container  

Example snippet (Dockerfile):
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-m", "mcp_server.server"]
```

---

## 14. Final Verification

- [ ] Start the server (python -m mcp_server.server)  
- [ ] Open Claude Desktop or your preferred MCP host  
- [ ] Connect to the new server  
- [ ] Call the full_research_pipeline query to confirm results.  
- [ ] Confirm that sources are uploaded to Drive if do_upload=True  

```bash
python -m mcp_server.server  # Launch
# In Claude Desktop (or client)...

# "Call e2e tool with query: 'Summarize the pros/cons of GPT-4 vs. Gemini'."
```

---

## Conclusion

Completing this plan will yield a fully functional MCP server integrating multiple deep research products, culminating in one comprehensive report. You’ll expose six primary tools (upload, combine, plan generation, single research, orchestrator, end-to-end) and optionally connect them to Claude Desktop or any MCP-compatible client.  

If you have further questions about any step, consult the references (@Docs: LangChain (py), @Docs: LangGraph (py), @Docs: MCP, @python-sdk, @relishplus) for deeper implementation details.

