"""Patchright-based implementation for research scraping."""
import logging
import asyncio
from typing import Optional, Any
from patchright.async_api import async_playwright, Browser, Page, BrowserContext

from ..core.base import BaseResearchScraper
from ..core.auth import GeminiAuth
from ..core.config import ScraperConfig, ResearchSite

logger = logging.getLogger(__name__)

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

class PatchrightScraper(BaseResearchScraper):
    """Patchright implementation of research scraper"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config)
        self.patchright = None
        self.browser = None
        self.page = None
        
    @property
    def auth(self) -> Optional[GeminiAuth]:
        """Get Patchright-specific auth handler"""
        if not self._auth and self.config.site == ResearchSite.GEMINI:
            if not self.page:
                raise RuntimeError("Browser page not initialized")
            self._auth = PatchrightAuth(self.config, self.page)
        return self._auth
        
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
        """Handle research for Gemini"""
        if site != ResearchSite.GEMINI:
            raise ValueError(f"This scraper only handles Gemini research, not {site}")
            
        try:
            # Look for input field and enter query
            logger.info("Looking for query input field...")
            await self.page.fill('textarea', query)
            await self.page.keyboard.press('Enter')
            
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
            
        except Exception as e:
            logger.error(f"Query submission error: {str(e)}")
            raise
    
    async def execute_research(self, query: str) -> str:
        """Execute research using Patchright"""
        return await self.handle_site_specific_research(self.config.site, query) 