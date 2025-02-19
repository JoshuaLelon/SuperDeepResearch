# Research Scrapers

This module provides a framework for scraping research from various AI research sites using different browser automation approaches.

## Architecture

The framework is organized into three main components:

1. **Site Instructions** (`sites/`):
   - Each site (e.g., Perplexity, Gemini) has its own module containing all site-specific instructions
   - Instructions include selectors, navigation steps, and authentication methods
   - Each site's instructions are organized by driver (Patchright, NoDriver, Browser-Use)

2. **Drivers** (`drivers/`):
   - Browser automation implementations that know HOW to execute instructions
   - Each driver reads site-specific instructions and executes them using its automation approach
   - Available drivers:
     - `PatchrightDriver`: Uses Patchright for automation
     - `NoDriverDriver`: Uses NoDriver for automation
     - `BrowserUseDriver`: Uses Browser-Use for automation

3. **Core** (`core/`):
   - Base classes and shared functionality
   - Configuration and type definitions
   - Authentication base classes

## Usage

```python
from research_scrapers import (
    ScraperConfig,
    ResearchSite,
    BrowserUseDriver  # or NoDriverDriver, PatchrightDriver
)

# Create configuration
config = ScraperConfig(
    headless=True,
    window_size=(1920, 1080),
    site=ResearchSite.PERPLEXITY
)

# Initialize driver
driver = BrowserUseDriver(config)

# Execute research
async def do_research():
    try:
        await driver.setup()
        await driver.login()  # If required
        result = await driver.execute_research("Your research query")
        print(result)
    finally:
        await driver.cleanup()
```

## Adding New Sites

1. Create a new directory under `sites/` for your site
2. Create a `scraper.py` with site-specific instructions:
   ```python
   class YourSiteInstructions:
       class Patchright:
           instructions = DriverInstructions(...)
           
       class NoDriver:
           instructions = DriverInstructions(...)
           
       class BrowserUse:
           instructions = DriverInstructions(...)
   ```

## Adding New Drivers

1. Create a new driver class in `drivers/`
2. Inherit from `BaseResearchScraper`
3. Implement the required methods to execute site instructions using your automation approach

## Configuration

The `ScraperConfig` class accepts:
- `headless`: Whether to run in headless mode
- `window_size`: Browser window dimensions
- `site`: Which research site to use (from `ResearchSite` enum)
- `auth_cookies`: Optional authentication cookies
- Additional site-specific configuration

## Testing

### Unit Tests
Run the test suite:
```bash
pytest tests/
```

### Integration Tests
Test specific browser automation:
```bash
python -m scripts.test_browser_use --query "test query" --site perplexity
python -m scripts.test_nodriver --query "test query" --site gemini
python -m scripts.test_patchright --query "test query" --site perplexity
```

### Test Configuration
Set up test environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `GOOGLE_EMAIL`: Google account email
- `GOOGLE_PASSWORD`: Google account password
- `OPENAI_API_KEY`: OpenAI API key (for Browser-Use)

### Browser Profiles
For development/testing:
1. Use a separate browser profile
2. Log in to required services manually
3. Export cookies to avoid repeated logins

### Debugging
Enable verbose logging:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

Common issues:
- Browser detection: Try different evasion settings
- Auth failures: Check credentials and cookies
- Timeouts: Adjust wait times
- Selectors: Update if site UI changes 