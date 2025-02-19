# SuperDeepResearch

A Python-based research automation tool that uses various browser automation approaches to interact with AI research sites like Google Gemini and Perplexity. Integrates with MCP (Model Control Protocol) for tool registration and communication.

## Features

- Support for multiple research sites:
  - Google Gemini with authentication and 2FA
  - Perplexity AI with Deep Research capabilities
- Multiple browser automation approaches:
  - Browser-use library for headless browsing
  - NoDriver (undetected-chromedriver) for automation
  - Patchright (enhanced fork of Playwright) for browser control
- Shared authentication handling with 2FA support
- Configurable browser settings and retry logic
- Clean, modular architecture
- MCP integration for tool registration and communication

## Directory Structure

```
.
├── mcp_server/
│   ├── tools/
│   │   ├── research_scrapers/       # Research automation core
│   │   │   ├── core/               # Core abstractions
│   │   │   ├── sites/              # Site implementations
│   │   │   └── drivers/            # Browser automation
│   │   └── research_engine.py      # Main orchestrator
│   └── server.py                   # MCP server implementation
├── scripts/                        # Test and utility scripts
│   ├── test_browser_use.py
│   ├── test_nodriver.py
│   └── test_patchright.py
└── run_server.py                   # Server entry point
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SuperDeepResearch.git
cd SuperDeepResearch
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Google credentials (required for Gemini only)
```

## Workflows

### Testing Workflow

Test different browser automation approaches with various research sites:

1. Direct testing with scripts:
```bash
# Test Patchright with Perplexity
python -m scripts.test_patchright \
  --query "Compare GPT-4 vs Gemini" \
  --site perplexity \
  --headless true

# Test NoDriver with Gemini
python -m scripts.test_nodriver \
  --query "Analyze AI trends" \
  --site gemini \
  --headless false

# Test Browser-use with either site
python -m scripts.test_browser_use \
  --query "Research quantum computing" \
  --site perplexity \
  --headless true
```

2. Development testing in code:
```python
from mcp_server.tools.research_engine import deep_research, BrowserApproach, ResearchConfig, ResearchSite

# Configure research
config = ResearchConfig(
    headless=True,
    window_width=1920,
    window_height=1080,
    site=ResearchSite.PERPLEXITY
)

# Execute research
result = await deep_research(
    plan="your research query",
    approach=BrowserApproach.PATCHRIGHT,
    site=ResearchSite.PERPLEXITY,
    config=config
)
```

### MCP Server Workflow

1. Start the MCP server:
```bash
python run_server.py
```

2. Use the research tool through MCP:
```python
from mcp.client import MCPClient

# Connect to the server
client = MCPClient()

# Execute research
result = await client.tools.research_tool(
    query="Research quantum computing",
    site="perplexity",
    approach="patchright",
    headless=True
)
```

3. Server Features:
   - Automatic tool registration
   - Error handling and logging
   - Configurable retry logic
   - Multiple site support
   - Browser automation selection

## Configuration

### Environment Variables

Required for Gemini:
- `GOOGLE_EMAIL`: Google account email
- `GOOGLE_PASSWORD`: Google account password
- `GOOGLE_2FA_SECRET`: If 2FA is enabled (recommended)

No authentication required for Perplexity.

### Browser Settings

Browser configuration can be customized through the `ResearchConfig` class:
- Window size
- Network timeouts
- Retry attempts
- Headless mode
- Research site selection

## Development

### Adding New Sites

1. Create site implementation:
   ```
   research_scrapers/sites/new_site/
   ├── __init__.py
   └── scraper.py
   ```

2. Implement the scraper:
   ```python
   from ...core import BaseResearchScraper
   
   class NewSiteScraper(BaseResearchScraper):
       async def execute_research(self, query: str) -> str:
           # Implementation
   ```

3. Add site configuration:
   ```python
   class ResearchSite(str, Enum):
       NEW_SITE = "new_site"
   
   SITE_CONFIGS[ResearchSite.NEW_SITE] = SiteConfig(
       url="https://new-site.com",
       requires_auth=False
   )
   ```

### Adding New Browser Drivers

1. Create driver implementation:
   ```
   research_scrapers/drivers/new_driver.py
   ```

2. Implement the driver:
   ```python
   from ..core import BaseResearchScraper
   
   class NewDriverScraper(BaseResearchScraper):
       async def setup(self) -> None:
           # Implementation
   ```

3. Add to browser approaches:
   ```python
   class BrowserApproach(str, Enum):
       NEW_DRIVER = "new_driver"
   ```

## Documentation

- [docs/README.md](docs/README.md) for technical diagrams and flows
- [mcp_server/README.md](mcp_server/README.md) for server details
- [scripts/README.md](scripts/README.md) for test script usage