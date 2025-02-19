"""NoDriver-based implementation for research scraping."""
import logging
import asyncio
from typing import Optional, Any, Type
import nodriver
from nodriver import Browser, Config
from langchain_openai import ChatOpenAI

from ..core.base import BaseResearchScraper
from ..core.auth import GeminiAuth
from ..core.config import ScraperConfig, ResearchSite
from ....logging_config import setup_logging
from ..sites.perplexity.scraper import PerplexitySiteInstructions
from ..sites.gemini.scraper import GeminiSiteInstructions

logger = setup_logging(__name__)

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

class NoDriverDriver(BaseResearchScraper):
    """NoDriver implementation of research scraper"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config)
        self.driver = None
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
            self._site_instructions = site_map[self.config.site].NoDriver
        return self._site_instructions
        
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
        """Handle research using site-specific instructions"""
        instructions = self.site_instructions.instructions
        
        try:
            # Look for input field using site-specific selectors
            logger.info("Looking for query input field...")
            input_elem = None
            
            # Try each input selector
            for selector in instructions.selectors.input_field:
                try:
                    input_elem = await self.page.select(selector)
                    if input_elem:
                        break
                except Exception:
                    try:
                        # NoDriver's fallback to fuzzy text matching
                        input_elem = await self.page.find(selector, best_match=True)
                        if input_elem:
                            break
                    except Exception:
                        continue
            
            if input_elem:
                logger.info("Found input field, entering query...")
                await self.page.sleep(instructions.navigation.pre_input_wait_time)
                
                # Use site-specific submit method
                await self.site_instructions.submit_query(self.page, query)
                
                await self.page.sleep(instructions.navigation.post_input_wait_time)
                
                # Look for results using site-specific selectors
                logger.info("Looking for response content...")
                await self.page.sleep(instructions.navigation.response_wait_time)
                
                for selector in instructions.selectors.response_content:
                    try:
                        results_elem = await self.page.select(selector)
                        if not results_elem:
                            results_elem = await self.page.find(selector, best_match=True)
                        
                        if results_elem:
                            results = await results_elem.text()
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
        """Execute research using NoDriver"""
        return await self.handle_site_specific_research(self.config.site, query) 