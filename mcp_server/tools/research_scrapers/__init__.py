"""Research scraper implementations for various AI research sites."""

from .core import (
    BaseResearchScraper,
    GeminiAuth,
    ScraperConfig,
    ResearchSite,
    SiteConfig,
    SITE_CONFIGS
)
from .drivers import (
    BrowserUseScraper,
    NoDriverScraper,
    PatchrightScraper
)
from .sites import (
    GeminiScraper,
    PerplexityScraper
)

__all__ = [
    # Core
    'BaseResearchScraper',
    'GeminiAuth',
    'ScraperConfig',
    'ResearchSite',
    'SiteConfig',
    'SITE_CONFIGS',
    # Drivers
    'BrowserUseScraper',
    'NoDriverScraper',
    'PatchrightScraper',
    # Sites
    'GeminiScraper',
    'PerplexityScraper'
] 