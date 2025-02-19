"""NoDriver-based implementation for research scraping."""
import logging
from typing import Optional, Any
import nodriver
from nodriver import Browser, Config
from langchain_openai import ChatOpenAI

from ..core.base import BaseResearchScraper
from ..core.auth import GeminiAuth
from ..core.config import ScraperConfig, ResearchSite

logger = logging.getLogger(__name__)

class NoDriverAuth(GeminiAuth):
    """NoDriver-specific implementation of Gemini authentication"""
    
    def __init__(self, config: ScraperConfig, page: Any):
        super().__init__(config)
        self.page = page
        
    async def navigate_to_login(self) -> None:
        """Navigate to Google login page"""
        await self.page.sleep(2)
        sign_in_button = await self.page.find("Sign in", best_match=True)
        if sign_in_button:
            await sign_in_button.click()
            await self.page.sleep(2)
        else:
            raise RuntimeError("Sign in button not found")

    async def enter_email(self) -> None:
        """Enter email and proceed"""
        email_elem = await self.page.select('input[type="email"]')
        if not email_elem:
            email_elem = await self.page.find("email", best_match=True)
        
        if email_elem:
            await email_elem.send_keys(self.config.google_email)
            next_button = await self.page.find("Next", best_match=True)
            if next_button:
                await next_button.click()
                await self.page.sleep(2)
            else:
                raise RuntimeError("Next button not found after email")
        else:
            raise RuntimeError("Email input not found")

    async def enter_password(self) -> None:
        """Enter password and submit"""
        pwd_elem = await self.page.select('input[type="password"]')
        if pwd_elem:
            await pwd_elem.send_keys(self.config.google_password)
            next_button = await self.page.find("Next", best_match=True)
            if next_button:
                await next_button.click()
                await self.page.sleep(5)
            else:
                raise RuntimeError("Next button not found after password")
        else:
            raise RuntimeError("Password input not found")

    async def handle_2fa(self) -> None:
        """Handle 2FA if required"""
        if self._2fa_code:
            # Look for 2FA input
            code_input = await self.page.select('input[type="tel"]')
            if code_input:
                await code_input.send_keys(self._2fa_code)
                next_button = await self.page.find("Next", best_match=True)
                if next_button:
                    await next_button.click()
                    await self.page.sleep(5)

    async def verify_login_success(self) -> bool:
        """Verify successful login"""
        try:
            # Wait for Gemini interface to load
            await self.page.sleep(2)
            return True
        except Exception:
            return False

class NoDriverScraper(BaseResearchScraper):
    """NoDriver implementation of Gemini scraper"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config)
        self.gemini_url = "https://gemini.google.com/app"
        self.driver = None
        self.page = None
        
    @property
    def auth(self) -> GeminiAuth:
        """Get NoDriver-specific auth handler"""
        if not self._auth:
            if not self.page:
                raise RuntimeError("Browser page not initialized")
            self._auth = NoDriverAuth(self.config, self.page)
        return self._auth
        
    async def setup(self) -> None:
        """Initialize NoDriver browser"""
        logger.info("Starting NoDriver browser...")
        try:
            self.driver = await nodriver.start(
                headless=self.config.headless,
                browser_args=['--no-sandbox', '--disable-dev-shm-usage'],
                no_sandbox=True
            )
            self.page = await self.driver.get(self.config.site_config.url)
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Browser startup error: {str(e)}")
            raise

    async def cleanup(self) -> None:
        """Clean up NoDriver resources"""
        if self.driver:
            logger.info("Cleaning up resources...")
            self.driver.stop()
            self.driver = None
            self.page = None
            logger.info("Browser stopped successfully")

    async def handle_site_specific_research(self, site: ResearchSite, query: str) -> str:
        """Handle research for specific sites"""
        if site == ResearchSite.PERPLEXITY:
            try:
                # Click "Deep Research" button
                logger.info("Looking for Deep Research button...")
                deep_research_button = await self.page.find("Deep Research", best_match=True)
                if deep_research_button:
                    await deep_research_button.click()
                    await self.page.sleep(2)
                
                # Look for input field and enter query
                logger.info("Looking for query input field...")
                input_elem = await self.page.select('textarea[placeholder*="Ask anything"]')
                if not input_elem:
                    input_elem = await self.page.find("Ask anything", best_match=True)
                
                if input_elem:
                    logger.info("Found input field, entering query...")
                    await input_elem.send_keys(query)
                    await input_elem.send_keys("\n")
                    
                    # Wait for response
                    logger.info("Waiting for response...")
                    await self.page.sleep(10)
                    
                    # Look for results
                    logger.info("Looking for response content...")
                    results = await self.page.find(".response-content", best_match=True)
                    if results:
                        logger.info("Found results")
                        return await results.text()
                    
                    logger.warning("No results found")
                    return "No results found"
                else:
                    raise RuntimeError("Query input not found")
                
            except Exception as e:
                logger.error(f"Query submission error: {str(e)}")
                raise
        elif site == ResearchSite.GEMINI:
            try:
                # Look for input field
                logger.info("Looking for query input field...")
                input_elem = await self.page.select("textarea")
                if not input_elem:
                    input_elem = await self.page.find("Enter a prompt here", best_match=True)
                
                if input_elem:
                    logger.info("Found input field, entering query...")
                    await input_elem.send_keys(query)
                    await input_elem.send_keys("\n")
                    
                    # Wait for response
                    logger.info("Waiting for response...")
                    await self.page.sleep(10)
                    
                    # Look for results
                    logger.info("Looking for response content...")
                    results = await self.page.find(".response-content", best_match=True)
                    if results:
                        logger.info("Found results, extracting text...")
                        return await results.text()
                    logger.warning("No results found")
                    return "No results found"
                else:
                    raise RuntimeError("Query input not found")
                
            except Exception as e:
                logger.error(f"Query submission error: {str(e)}")
                raise
        else:
            raise ValueError(f"Unsupported research site: {site}")

    async def execute_research(self, query: str) -> str:
        """Execute research using NoDriver"""
        return await self.handle_site_specific_research(self.config.site, query) 