"""Patchright-based implementation for research scraping."""
import logging
import asyncio
from typing import Optional, Any, Type
from patchright.async_api import async_playwright, Browser, Page, BrowserContext

from ..core.base import BaseResearchScraper
from ..core.auth import GeminiAuth
from ..core.config import ScraperConfig, ResearchSite
from ....logging_config import setup_logging
from ..sites.perplexity.scraper import PerplexitySiteInstructions
from ..sites.gemini.scraper import GeminiSiteInstructions

logger = setup_logging(__name__)

class PatchrightAuth(GeminiAuth):
    """Patchright-specific implementation of Gemini authentication"""
    
    def __init__(self, config: ScraperConfig, page: Page):
        super().__init__(config)
        self.page = page
        
    async def navigate_to_login(self) -> None:
        """Navigate to Google login page"""
        await asyncio.sleep(2)
        try:
            # Try the action button first
            sign_in_button = await self.page.locator('[data-test-id="action-button"]').click()
        except Exception:
            try:
                # Try the link version
                sign_in_button = await self.page.get_by_role("link", name="Sign in").click()
            except Exception:
                # We might already be on the login page
                pass
        
        # Wait for the login page to load
        await asyncio.sleep(5)
        
        # Check if we're already on the login page
        current_url = self.page.url
        if not current_url.startswith("https://accounts.google.com"):
            raise RuntimeError("Failed to reach Google login page")

    async def enter_email(self) -> None:
        """Enter email and proceed"""
        await self.page.fill('input[type="email"]', self.config.google_email)
        await self.page.click('button:has-text("Next")')
        await asyncio.sleep(2)

    async def enter_password(self) -> None:
        """Enter password and submit"""
        await self.page.fill('input[type="password"]', self.config.google_password)
        await self.page.click('button:has-text("Next")')
        await asyncio.sleep(5)

    async def handle_2fa(self) -> None:
        """Handle 2FA if required"""
        if self._2fa_code:
            try:
                await self.page.fill('input[type="tel"]', self._2fa_code)
                await self.page.click('button:has-text("Next")')
                await asyncio.sleep(5)
            except Exception:
                # No 2FA prompt found
                pass

    async def verify_login_success(self) -> bool:
        """Verify successful login"""
        try:
            # Wait for Gemini interface to load
            await asyncio.sleep(2)
            return True
        except Exception:
            return False

class PatchrightDriver(BaseResearchScraper):
    """Patchright implementation of research scraper"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config)
        self.patchright = None
        self.browser = None
        self.page = None
        self._site_instructions = None
        
    @property
    def site_instructions(self) -> Any:
        """Get the appropriate site instructions for the current site"""
        if not self._site_instructions:
            site_map = {
                ResearchSite.PERPLEXITY: PerplexitySiteInstructions,
                ResearchSite.GEMINI: GeminiSiteInstructions
            }
            self._site_instructions = site_map[self.config.site].Patchright
        return self._site_instructions
        
    async def setup(self) -> None:
        """Initialize Patchright browser"""
        logger.info("Starting Patchright browser...")
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
        """Handle research using site-specific instructions"""
        instructions = self.site_instructions.instructions
        
        try:
            # Look for input field using site-specific selectors
            logger.info("Looking for query input field...")
            input_elem = None
            for selector in instructions.selectors.input_field:
                try:
                    input_elem = await self.page.locator(selector).first
                    if input_elem:
                        break
                except Exception:
                    continue
            
            if input_elem:
                logger.info("Found input field, entering query...")
                await asyncio.sleep(instructions.navigation.pre_input_wait_time)
                
                # Use site-specific submit method
                await self.site_instructions.submit_query(self.page, query)
                
                await asyncio.sleep(instructions.navigation.post_input_wait_time)
                
                # Look for results using site-specific selectors
                logger.info("Looking for response content...")
                await asyncio.sleep(instructions.navigation.response_wait_time)
                
                for selector in instructions.selectors.response_content:
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
        """Execute research using Patchright"""
        return await self.handle_site_specific_research(self.config.site, query) 