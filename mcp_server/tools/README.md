# MCP Server Tools

This directory contains various tools and utilities used by the MCP server.

## Directory Structure

```
tools/
├── gemini_scrapers_base/     # Base utilities for research site scraping
│   ├── __init__.py          # Exports shared components
│   ├── auth.py              # Authentication handling
│   ├── base.py              # Base scraper class
│   ├── config.py            # Shared configuration
│   ├── browser_use_impl.py  # Browser-use implementation
│   ├── nodriver_impl.py     # NoDriver implementation
│   ├── patchright_impl.py   # Patchright implementation
│   └── perplexity_impl.py   # Perplexity implementation
└── single_research.py       # Main entry point for research
```

## Research Tools

The research functionality is centralized in `single_research.py`, which provides support for multiple research sites and browser automation approaches:

### Research Sites

1. **Gemini**: Google's Gemini AI research interface
   - Requires Google account authentication
   - Supports 2FA
   - Full chat history and context

2. **Perplexity**: Perplexity AI's Deep Research interface
   - No authentication required
   - Advanced research capabilities
   - Source citations and references

### Browser Automation Approaches

1. **Browser-use**: Uses the browser-use library for headless browsing
2. **NoDriver**: Uses undetected-chromedriver for automation
3. **Patchright**: Uses Patchright (enhanced fork of Playwright) for browser automation

### Configuration

All approaches share common configuration through the `ScraperConfig` class, which handles:
- Browser window size and settings
- Network timeouts
- Authentication credentials
- Retry logic
- Site selection

### Authentication

Authentication is handled through the `GeminiAuth` base class for sites that require it:
- Google account login flow
- 2FA support
- Login verification

### Usage

To use any of the research approaches:

```python
from mcp_server.tools.single_research import deep_research, BrowserApproach, ResearchConfig, ResearchSite

# Configure research
config = ResearchConfig(
    headless=True,
    window_width=1920,
    window_height=1080,
    site=ResearchSite.PERPLEXITY  # or GEMINI
)

# Execute research using chosen approach
result = await deep_research(
    plan="your research query",
    approach=BrowserApproach.PATCHRIGHT,  # or BROWSER_USE, or NODRIVER
    site=ResearchSite.PERPLEXITY,  # or GEMINI
    config=config
)
```

### Testing

Each approach has a dedicated test script in the `scripts/` directory:
- `test_browser_use.py`
- `test_nodriver.py`
- `test_patchright.py`

Run tests with:
```bash
python -m scripts.test_nodriver --query "your query" --site perplexity --headless true
```

## Environment Variables

Required environment variables for Gemini:
- `GOOGLE_EMAIL`: Google account email
- `GOOGLE_PASSWORD`: Google account password

Optional:
- `GOOGLE_2FA_SECRET`: If 2FA is enabled (recommended)

## MCP Integration

The research functionality is exposed as an MCP tool through `server.py`. The tool accepts:
- `query`: Research query to execute
- `site`: Research site to use (optional, defaults to Gemini)
- `approach`: Browser approach to use (optional)
- `headless`: Whether to run in headless mode (optional)
- `max_retries`: Maximum retry attempts (optional)

## Usage Examples

Example usage of the research tool:
```python
from mcp_server.tools.single_research import deep_research, BrowserApproach, ResearchSite

# Using Perplexity with Patchright
result = await deep_research(
    "Compare GPT-4 vs Gemini in summarizing climate change data",
    approach=BrowserApproach.PATCHRIGHT,
    site=ResearchSite.PERPLEXITY
)
print(result)

# Using Gemini with NoDriver
result = await deep_research(
    "Analyze recent Gemini updates",
    approach=BrowserApproach.NODRIVER,
    site=ResearchSite.GEMINI
)
print(result)
```

## Adding New Research Sites

1. Create a new implementation file in `gemini_scrapers_base/` (e.g., `new_site_impl.py`)
2. Implement the `BaseResearchScraper` interface
3. Add the new site to the `ResearchSite` enum in `config.py`
4. Add site configuration to `SITE_CONFIGS` in `config.py`
5. Create a test script in `scripts/`
6. Update this documentation

## Further Reading

- [mcp_server/README.md](../README.md) for server setup
- [gemini_scrapers_base/README.md](gemini_scrapers_base/README.md) for implementation details
- [../docs/](../../docs/README.md) for diagrams and technical references