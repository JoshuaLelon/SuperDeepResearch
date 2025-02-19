# Research Scrapers

This module implements a layered architecture for browser automation across different AI research sites.

## Architecture

The implementation is split into two distinct layers:

### 1. Browser Automation Layer (`drivers/`)
The "HOW" layer - handles different ways to automate browsers:
- `browser_use.py` - Uses browser-use library with LLM-based agent
- `nodriver.py` - Uses undetected-chromedriver for stealth automation
- `patchright.py` - Uses enhanced Playwright for robust control

Each driver implementation:
- Handles browser lifecycle (setup/cleanup)
- Manages authentication flows
- Provides basic browser operations

### 2. Site-Specific Layer (`sites/`)
The "WHAT" layer - handles site-specific interactions:
- `gemini/` - Gemini-specific UI interactions and flows
- `perplexity/` - Perplexity-specific UI interactions and flows

Each site implementation:
- Defines site-specific UI selectors and interactions
- Handles site-specific response parsing
- Manages site-specific authentication requirements

### Core Layer (`core/`)
Shared abstractions and utilities:
- `base.py` - Base scraper interface
- `auth.py` - Authentication base classes
- `config.py` - Configuration and site definitions

## Adding New Components

### New Browser Automation Approach
1. Add new driver in `drivers/`
2. Implement `BaseResearchScraper`
3. Handle browser lifecycle and auth
4. Register in `drivers/__init__.py`

### New Research Site
1. Add site config to `core/config.py`
2. Create site directory in `sites/`
3. Implement site-specific scraper
4. Register in `sites/__init__.py`

## Usage

```python
from mcp_server.tools.research_scrapers import (
    ScraperConfig,
    ResearchSite,
    BrowserUseScraper,  # or NoDriverScraper, PatchrightScraper
)

# Configure scraping
config = ScraperConfig(
    headless=True,
    site=ResearchSite.PERPLEXITY  # or GEMINI
)

# Create scraper instance
scraper = BrowserUseScraper(config)

# Execute research
try:
    await scraper.setup()
    await scraper.login()  # if required
    result = await scraper.execute_research("your query")
finally:
    await scraper.cleanup()
```

## Testing

Each browser automation approach has a dedicated test script in `scripts/`:
- `test_browser_use.py`
- `test_nodriver.py`
- `test_patchright.py`

Run tests with:
```bash
python -m scripts.test_patchright --query "query" --site perplexity --headless true
``` 