"""Site-specific implementations for research scrapers."""

from .gemini.scraper import GeminiScraper
from .perplexity.scraper import PerplexityScraper

__all__ = [
    'GeminiScraper',
    'PerplexityScraper'
] 