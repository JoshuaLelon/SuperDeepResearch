# Implementation Plan

- [x] **Organize "single_research.py" to house multiple scraping functions** (one per underlying browser approach):  
  • `browse_with_browser_use()`  
  • `browse_with_nodriver()`  
  • `browse_with_patchwright()`  

  Each function should:  
  1) Initialize its respective headless browser solution.  
  2) Handle the full Google Gemini login flow, including 2FA.  
  3) Perform a research query.  
  4) Return results.  

  Then, `gemini_deep_research(plan)` can call the relevant function, depending on which browser approach is chosen.

- [x] **Remove duplication in "mcp_server/tools/gemini_research/" and "mcp_server/tools/browser_use/"** by extracting all shared scraping/auth logic (including 2FA details) into a single, central utility module. Suggested name: `mcp_server/tools/gemini_scrapers_base/`.  
  1) Move any common config (e.g., window size, wait times, environment vars for `GOOGLE_EMAIL` and `GOOGLE_PASSWORD`) into this location.  
  2) Provide base classes or helper methods, e.g., `login_to_gemini(page, config)` that each sub-scraper can call.  

- [x] **In "scripts/" create a dedicated test script for each function** from "single_research.py":  
  • `test_browser_use.py` → calls `browse_with_browser_use()`  
  • `test_nodriver.py` → calls `browse_with_nodriver()`  
  • `test_patchwright.py` → calls `browse_with_patchwright()`  

  Each script:  
  1) Accepts a command-line query argument (e.g. `--query`).  
  2) Accepts an optional flag for headless vs. non-headless mode (e.g., `--headless true/false`).  
  3) Invokes the relevant function, performing the query.  
  4) Logs or prints success/failure messages in plain text.

- [x] **Update "run_server.py"** so it imports "server.py," and **in "server.py"**, register "single_research.py."  
  1) Created a new `research_tool` async function in server.py that wraps `gemini_deep_research`
  2) Added proper error handling and logging
  3) Made the tool configurable with parameters for approach, headless mode, and retries
  4) Registered the tool with MCP server
  5) Updated run_server.py with proper environment loading and logging configuration

- [x] **Clean up "mcp_server/tools/browser_use" and "mcp_server/tools/gemini_research" directories**:  
  1) Updated `__init__.py` files to be minimal wrappers around the centralized code
  2) They now only re-export the necessary functions and types from single_research.py
  3) Reduced code duplication and maintained a single source of truth

- [x] **Amend all README.md files** to reflect these changes:  
  1) Root "README.md": mention that "single_research.py" is the main entry point for Gemini scraping, referencing the new central "gemini_scrapers_base."  
  2) "mcp_server/README.md" and the "tools/README.md" inside it: describe how the scraping logic is centralized and how to choose a specific browser approach.  
  3) "scripts/README.md": explain each test script's usage (e.g., `python -m scripts.test_browser_use --query "Gemini capabilities" --headless true`).  
  4) Ensure each directory "README.md" includes the updated tree structure and references.  

- [x] **Handle environment variables consistently** in the new central utility, especially the `GOOGLE_EMAIL`, `GOOGLE_PASSWORD`, and any 2FA tokens or codes needed for Gemini.  

- [x] **After refactoring, finalize all README.md docs** ensuring they list new file names, function signatures, script usage instructions, and mention the mandatory 2FA steps if required.

# Summary

In this refactor, we've successfully consolidated several different approaches to Gemini research—browser_use, NoDriver, and Patchwright—into a single, more coherent system. The key accomplishments include:

1. **Centralized Implementation**:
   - All core functionality now lives in `single_research.py`
   - Browser-specific directories are minimal wrappers
   - Shared configuration and utilities in `gemini_scrapers_base`

2. **MCP Integration**:
   - Created a configurable `research_tool` in server.py
   - Added proper error handling and logging
   - Made browser approach, headless mode, and retries configurable

3. **Clean Architecture**:
   - Single source of truth for implementation
   - Minimal code duplication
   - Clear separation of concerns

4. **User Experience**:
   - Consistent interface across all browser approaches
   - Simple configuration through environment variables
   - Clear documentation and usage instructions

The final directory structure looks like this:

```bash
.
├── README.md
├── run_server.py
├── scripts
│   ├── README.md
│   ├── test_browser_use.py
│   ├── test_nodriver.py
│   ├── test_patchwright.py
│   └── ...
├── mcp_server
│   ├── server.py
│   ├── README.md
│   ├── tools
│   │   ├── README.md
│   │   ├── gemini_scrapers_base
│   │   │   ├── __init__.py
│   │   │   ├── login.py
│   │   │   ├── config.py
│   │   │   └── ...
│   │   ├── single_research.py
│   │   ├── browser_use
│   │   │   └── __init__.py
│   │   └── gemini_research
│   │       └── __init__.py
├── docs
│   ├── README.md
│   └── diagrams
│       ├── flow.md
│       ├── sequence.md
│       └── state.md
├── requirements.txt
├── pyproject.toml
└── LICENSE
```

All tasks from the implementation plan have been completed, resulting in a more maintainable and user-friendly codebase. Users can now easily switch between browser approaches while maintaining consistent behavior and configuration options.
