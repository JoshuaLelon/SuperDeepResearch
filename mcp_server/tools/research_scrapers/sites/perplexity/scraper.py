"""Perplexity-based implementation for research scraping."""
import logging
import asyncio
from typing import Optional, Any
from patchright.async_api import async_playwright, Browser, Page

from .base import BaseResearchScraper
from .auth import GeminiAuth
from .config import ScraperConfig, ResearchSite

logger = logging.getLogger(__name__)

class PerplexityScraper(BaseResearchScraper):
    """Perplexity implementation of research scraper"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config)
        self.patchright = None
        self.browser = None
        self.page = None
        
    @property
    def auth(self) -> Optional[GeminiAuth]:
        """No auth required for Perplexity"""
        return None
        
    async def setup(self) -> None:
        """Initialize Patchright browser for Perplexity"""
        logger.info("Starting Patchright browser for Perplexity...")
        try:
            self.patchright = await async_playwright().start()
            self.browser = await self.patchright.chromium.launch(
                headless=self.config.headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-automation',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            context = await self.browser.new_context(
                viewport=self.config.viewport,
                java_script_enabled=True,
                bypass_csp=True,
                ignore_https_errors=True,
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            
            # Add evasion scripts
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.chrome = { runtime: {} };
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
                );
            """)
            
            self.page = await context.new_page()
            await self.page.goto(self.config.site_config.url)
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Browser startup error: {str(e)}")
            raise

    async def cleanup(self) -> None:
        """Clean up Patchright resources"""
        if self.browser:
            logger.info("Cleaning up resources...")
            await self.browser.close()
            self.browser = None
            self.page = None
            if self.patchright:
                await self.patchright.stop()
                self.patchright = None
            logger.info("Browser stopped successfully")

    async def handle_site_specific_research(self, site: ResearchSite, query: str) -> str:
        """Handle research for Perplexity"""
        if site != ResearchSite.PERPLEXITY:
            raise ValueError(f"This scraper only handles Perplexity research, not {site}")
            
        try:
            # Click "Deep Research" button
            logger.info("Looking for Deep Research button...")
            deep_research_button = await self.page.get_by_text("Deep Research", exact=True).click()
            await asyncio.sleep(2)
            
            # Look for input field and enter query
            logger.info("Looking for query input field...")
            input_elem = await self.page.locator('textarea[placeholder*="Ask anything"]').first
            if input_elem:
                logger.info("Found input field, entering query...")
                await input_elem.fill(query)
                await input_elem.press('Enter')
                
                # Wait for response
                logger.info("Waiting for response...")
                await asyncio.sleep(10)
                
                # Look for results
                logger.info("Looking for response content...")
                results = await self.page.locator('.response-content').text_content()
                if results:
                    logger.info("Found results")
                    return results
                
                logger.warning("No results found")
                return "No results found"
            else:
                raise RuntimeError("Query input not found")
            
        except Exception as e:
            logger.error(f"Query submission error: {str(e)}")
            raise
    
    async def execute_research(self, query: str) -> str:
        """Execute research using Perplexity"""
        return await self.handle_site_specific_research(ResearchSite.PERPLEXITY, query) 