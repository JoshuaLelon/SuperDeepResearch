"""
research_engine.py

Main orchestrator for executing deep research across different AI research sites
using various browser automation approaches.
"""
import sys
import logging
import asyncio
from typing import Any, Dict, Optional
from enum import Enum
from dataclasses import dataclass

# Completely disable all logging before importing anything else
logging.getLogger().setLevel(logging.CRITICAL)
for handler in logging.getLogger().handlers[:]:
    logging.getLogger().removeHandler(handler)
logging.getLogger().addHandler(logging.NullHandler())

# Now import other modules
from langchain_openai import ChatOpenAI
from browser_use import Agent, BrowserConfig, Browser, BrowserContextConfig
from .research_scrapers import (
    ScraperConfig,
    ResearchSite,
    BrowserUseScraper,
    NoDriverScraper,
    PatchrightScraper,
    GeminiScraper,
    PerplexityScraper
)
from dotenv import load_dotenv

load_dotenv()

class BrowserApproach(str, Enum):
    BROWSER_USE = "browser_use"
    NODRIVER = "nodriver"
    PATCHRIGHT = "patchright"

@dataclass
class ResearchConfig:
    """Configuration for research execution"""
    headless: bool = True
    window_width: int = 1920
    window_height: int = 1080
    network_idle_timeout: float = 3.0
    max_steps: int = 5
    max_retries: int = 3
    site: ResearchSite = ResearchSite.GEMINI

async def browse_with_browser_use(query: str, config: ResearchConfig) -> str:
    """Execute research using browser-use library"""
    scraper = BrowserUseScraper(ScraperConfig(
        headless=config.headless,
        window_size=(config.window_width, config.window_height),
        network_idle_timeout=config.network_idle_timeout,
        site=config.site
    ))
    
    try:
        await scraper.setup()
        await scraper.login()
        result = await scraper.execute_research(query)
        return result
    finally:
        await scraper.cleanup()

async def browse_with_nodriver(query: str, config: ResearchConfig) -> str:
    """Execute research using NoDriver automation"""
    scraper = NoDriverScraper(ScraperConfig(
        headless=config.headless,
        window_size=(config.window_width, config.window_height),
        site=config.site
    ))
    
    try:
        await scraper.setup()
        await scraper.login()
        result = await scraper.execute_research(query)
        return result
    finally:
        await scraper.cleanup()

async def browse_with_patchright(query: str, config: ResearchConfig) -> str:
    """Execute research using Patchright automation"""
    if config.site == ResearchSite.PERPLEXITY:
        scraper = PerplexityScraper(ScraperConfig(
            headless=config.headless,
            window_size=(config.window_width, config.window_height),
            site=config.site
        ))
    else:
        scraper = GeminiScraper(ScraperConfig(
            headless=config.headless,
            window_size=(config.window_width, config.window_height),
            site=config.site
        ))
    
    try:
        await scraper.setup()
        await scraper.login()
        result = await scraper.execute_research(query)
        return result
    finally:
        await scraper.cleanup()

async def deep_research(
    plan: str,
    approach: BrowserApproach = BrowserApproach.PATCHRIGHT,
    site: ResearchSite = ResearchSite.GEMINI,
    config: Optional[ResearchConfig] = None
) -> str:
    """
    Main entry point for research. Executes research using the specified browser approach
    and research site.
    
    Args:
        plan: The research query or plan to execute
        approach: Which browser automation approach to use
        site: Which research site to use
        config: Optional configuration for the research execution
    
    Returns:
        Research results as text
    """
    if config is None:
        config = ResearchConfig(site=site)
    else:
        config.site = site
    
    approach_map = {
        BrowserApproach.BROWSER_USE: browse_with_browser_use,
        BrowserApproach.NODRIVER: browse_with_nodriver,
        BrowserApproach.PATCHRIGHT: browse_with_patchright,
    }
    
    research_func = approach_map[approach]
    
    for attempt in range(config.max_retries):
        try:
            return await research_func(plan, config)
        except Exception as e:
            if attempt == config.max_retries - 1:
                raise
            logging.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
            await asyncio.sleep(1)  # Brief pause before retry

# Basic configuration
