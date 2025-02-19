"""Core abstractions and shared utilities for research scrapers."""

from .base import BaseResearchScraper
from .auth import GeminiAuth
from .config import ScraperConfig, ResearchSite, SiteConfig, SITE_CONFIGS

__all__ = [
    'BaseResearchScraper',
    'GeminiAuth',
    'ScraperConfig',
    'ResearchSite',
    'SiteConfig',
    'SITE_CONFIGS'
] 