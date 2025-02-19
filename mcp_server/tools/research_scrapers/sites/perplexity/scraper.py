"""Perplexity-based implementation for research scraping."""
import logging
import asyncio
from typing import Optional, Any
from patchright.async_api import async_playwright, Browser, Page
from dataclasses import dataclass

from ....logging_config import setup_logging
from ...core.base import BaseResearchScraper
from ...core.auth import GeminiAuth
from ...core.config import ScraperConfig, ResearchSite

logger = setup_logging(__name__)

@dataclass
class SelectorSet:
    """Common selectors used across different actions"""
    input_field: List[str]
    submit_button: Optional[str]
    response_content: List[str]

@dataclass
class NavigationSteps:
    """Common navigation steps"""
    pre_input_wait_time: float
    post_input_wait_time: float
    response_wait_time: float

@dataclass
class DriverInstructions:
    """Base class for driver-specific instructions"""
    selectors: SelectorSet
    navigation: NavigationSteps
    requires_auth: bool = False

class PerplexitySiteInstructions:
    """
    Contains all instructions for scraping Perplexity, organized by driver.
    Each driver section contains the exact selectors, navigation steps, and other
    instructions needed to scrape Perplexity using that specific driver.
    """
    
    class Patchright:
        """Instructions specific to Patchright automation"""
        instructions = DriverInstructions(
            selectors=SelectorSet(
                input_field=[
                    'textarea[placeholder*="Ask anything"]',
                    'textarea[placeholder*="Message Perplexity"]'
                ],
                submit_button=None,  # Uses Enter key instead
                response_content=[
                    '.response-content',
                    '[data-message-author-role="assistant"]',
                    '.prose',
                    '.markdown-content'
                ]
            ),
            navigation=NavigationSteps(
                pre_input_wait_time=2.0,
                post_input_wait_time=2.0,
                response_wait_time=15.0
            )
        )
        
        # Additional Patchright-specific methods
        @staticmethod
        async def submit_query(page: Any, query: str) -> None:
            """How to submit a query using Patchright"""
            await page.fill('textarea', query)
            await page.keyboard.press('Enter')
    
    class NoDriver:
        """Instructions specific to NoDriver automation"""
        instructions = DriverInstructions(
            selectors=SelectorSet(
                input_field=[
                    'textarea[placeholder*="Ask anything"]',
                    'textarea[placeholder*="Message Perplexity"]'
                ],
                submit_button=None,
                response_content=[
                    '.response-content',
                    '.markdown-content'
                ]
            ),
            navigation=NavigationSteps(
                pre_input_wait_time=2.0,
                post_input_wait_time=2.0,
                response_wait_time=10.0
            )
        )
        
        # Additional NoDriver-specific methods
        @staticmethod
        async def submit_query(page: Any, query: str) -> None:
            """How to submit a query using NoDriver"""
            input_elem = await page.select('textarea[placeholder*="Ask anything"]')
            if not input_elem:
                input_elem = await page.find("Ask anything", best_match=True)
            await input_elem.send_keys(query)
            await input_elem.send_keys("\n")
    
    class BrowserUse:
        """Instructions specific to Browser-Use automation"""
        instructions = DriverInstructions(
            selectors=SelectorSet(
                input_field=[
                    'textarea[placeholder*="Ask anything"]',
                    'textarea[placeholder*="Message Perplexity"]'
                ],
                submit_button=None,
                response_content=[
                    '.response-content',
                    '.markdown-content'
                ]
            ),
            navigation=NavigationSteps(
                pre_input_wait_time=3.0,
                post_input_wait_time=3.0,
                response_wait_time=10.0
            )
        )
        
        # Task template for Browser-Use agent
        TASK_TEMPLATE = """
        Go to {url}
        Wait for the input field to appear
        Enter this research query: {query}
        Press Enter and wait for the complete response
        Extract the response content
        """

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
            # Look for input field and enter query
            logger.info("Looking for query input field...")
            input_elem = await self.page.locator('textarea[placeholder*="Ask anything"]').first
            if not input_elem:
                # Try alternate placeholder text
                input_elem = await self.page.locator('textarea[placeholder*="Message Perplexity"]').first
            
            if input_elem:
                logger.info("Found input field, entering query...")
                await input_elem.fill(query)
                await input_elem.press('Enter')
                
                # Wait for response
                logger.info("Waiting for response...")
                await asyncio.sleep(15)  # Increased wait time for thorough response
                
                # Look for results with multiple possible selectors
                logger.info("Looking for response content...")
                selectors = [
                    '.response-content',
                    '[data-message-author-role="assistant"]',
                    '.prose',
                    '.markdown-content'
                ]
                
                for selector in selectors:
                    try:
                        results = await self.page.locator(selector).text_content()
                        if results:
                            logger.info(f"Found results using selector: {selector}")
                            return results
                    except Exception:
                        continue
                
                logger.warning("No results found with any selector")
                return "No results found"
            else:
                raise RuntimeError("Query input not found")
            
        except Exception as e:
            logger.error(f"Query submission error: {str(e)}")
            raise
    
    async def execute_research(self, query: str) -> str:
        """Execute research using Perplexity"""
        return await self.handle_site_specific_research(ResearchSite.PERPLEXITY, query) 