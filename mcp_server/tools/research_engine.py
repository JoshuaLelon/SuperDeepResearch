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

from ..logging_config import setup_logging

# Set up logging
logger = setup_logging(__name__)
logger.setLevel(logging.INFO)

# Create console handler with formatting
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Now import other modules
from langchain_openai import ChatOpenAI
from browser_use import Agent, BrowserConfig, Browser, BrowserContextConfig
from .research_scrapers import (
    ScraperConfig,
    ResearchSite,
    BrowserUseDriver,
    NoDriverDriver,
    PatchrightDriver
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
    driver = BrowserUseDriver(ScraperConfig(
        headless=config.headless,
        window_size=(config.window_width, config.window_height),
        network_idle_timeout=config.network_idle_timeout,
        site=config.site
    ))
    
    try:
        await driver.setup()
        await driver.login()
        result = await driver.execute_research(query)
        return result
    finally:
        await driver.cleanup()

async def browse_with_nodriver(query: str, config: ResearchConfig) -> str:
    """Execute research using NoDriver automation"""
    driver = NoDriverDriver(ScraperConfig(
        headless=config.headless,
        window_size=(config.window_width, config.window_height),
        site=config.site
    ))
    
    try:
        await driver.setup()
        await driver.login()
        result = await driver.execute_research(query)
        return result
    finally:
        await driver.cleanup()

async def browse_with_patchright(query: str, config: ResearchConfig) -> str:
    """Execute research using Patchright automation"""
    logger.info(f"Starting Patchright research for site: {config.site}")
    
    driver = PatchrightDriver(ScraperConfig(
        headless=config.headless,
        window_size=(config.window_width, config.window_height),
        site=config.site
    ))
    
    try:
        logger.info("Setting up browser...")
        await driver.setup()
        logger.info("Browser setup complete")
        
        logger.info("Attempting login...")
        await driver.login()
        logger.info("Login complete")
        
        logger.info("Executing research query...")
        result = await driver.execute_research(query)
        logger.info("Research complete")
        return result
    except Exception as e:
        logger.error(f"Research failed: {str(e)}")
        raise
    finally:
        logger.info("Cleaning up browser resources...")
        await driver.cleanup()
        logger.info("Cleanup complete")

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
            if attempt > 0:
                logger.info(f"Retry attempt {attempt + 1}/{config.max_retries}")
                # Add increasing delay between retries
                delay = attempt * 2
                logger.info(f"Waiting {delay} seconds before retry...")
                await asyncio.sleep(delay)
            return await research_func(plan, config)
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == config.max_retries - 1:
                logger.error("Max retries reached, giving up.")
                raise
            logger.warning(f"Will retry in {(attempt + 1) * 2} seconds...")

# Basic configuration
