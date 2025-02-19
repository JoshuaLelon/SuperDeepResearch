"""
NoDriver-based browser automation for Gemini research
"""
import logging
import asyncio
import sys
from typing import Optional
import nodriver as uc
from .config import Config, load_config

logger = logging.getLogger(__name__)

class GeminiNoDriverAutomation:
    """Handles browser automation for Gemini research using NoDriver"""
    
    def __init__(self, config: Config):
        self.config = config
        self.gemini_url = "https://gemini.google.com/app"
        self.driver = None
        
    async def setup_browser(self):
        """Initialize NoDriver browser with configuration"""
        logger.info("Starting browser...")
        try:
            browser = await uc.start(
                headless=self.config.research_preferences.headless,
                browser_args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            logger.info("Browser started successfully")
            return browser
        except Exception as e:
            logger.error(f"Browser startup error: {str(e)}")
            raise

    async def handle_login(self, page):
        """Handle Google login process"""
        logger.info("Checking login status...")
        
        try:
            # Wait for initial page load
            await page.sleep(2)
            
            # Look for sign in button
            logger.info("Looking for sign in button...")
            sign_in_button = await page.find("Sign in", best_match=True)
            if sign_in_button:
                logger.info("Found sign in button, clicking...")
                await sign_in_button.click()
                await page.sleep(2)
                
                # Handle email
                logger.info("Looking for email input...")
                email_elem = await page.select('input[type="email"]')
                if not email_elem:
                    logger.info("Email input not found, trying alternative selector...")
                    email_elem = await page.find("email", best_match=True)
                
                if email_elem:
                    logger.info("Found email input, entering email...")
                    await email_elem.send_keys(self.config.google_email)
                    
                    logger.info("Looking for next button...")
                    next_button = await page.find("Next", best_match=True)
                    if next_button:
                        await next_button.click()
                        await page.sleep(2)
                        
                        # Handle password
                        logger.info("Looking for password input...")
                        pwd_elem = await page.select('input[type="password"]')
                        if pwd_elem:
                            logger.info("Found password input, entering password...")
                            await pwd_elem.send_keys(self.config.google_password)
                            
                            logger.info("Looking for final next button...")
                            next_button = await page.find("Next", best_match=True)
                            if next_button:
                                await next_button.click()
                                logger.info("Waiting for login completion...")
                                await page.sleep(5)
                            else:
                                raise RuntimeError("Next button not found after password")
                        else:
                            raise RuntimeError("Password input not found")
                    else:
                        raise RuntimeError("Next button not found after email")
                else:
                    raise RuntimeError("Email input not found")

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise

    async def setup_research_mode(self, page):
        """Set up Gemini research mode"""
        logger.info("Setting up research mode...")
        
        try:
            await page.sleep(2)
            logger.info("Looking for model selector...")
            model_selector = await page.find("Gemini 1.5 Pro with Deep Research", best_match=True)
            if model_selector:
                logger.info("Found model selector, clicking...")
                await model_selector.click()
                await page.sleep(1)
                
                logger.info("Looking for Try Now button...")
                try_now = await page.find("Try Now", best_match=True)
                if try_now:
                    logger.info("Found Try Now button, clicking...")
                    await try_now.click()
                    await page.sleep(2)
            else:
                logger.warning("Model selector not found")
                
        except Exception as e:
            logger.error(f"Research mode setup error: {str(e)}")
            raise

    async def submit_query(self, page, query: str) -> str:
        """Submit query and get results"""
        logger.info(f"Submitting query: {query}")
        
        try:
            # Look for input field
            logger.info("Looking for query input field...")
            input_elem = await page.select("textarea")
            if not input_elem:
                logger.info("Textarea not found, trying alternative selector...")
                input_elem = await page.find("Enter a prompt here", best_match=True)
            
            if input_elem:
                logger.info("Found input field, entering query...")
                await input_elem.send_keys(query)
                await input_elem.send_keys("\n")
                
                # Wait for response
                logger.info("Waiting for response...")
                await page.sleep(10)
                
                # Look for results
                logger.info("Looking for response content...")
                results = await page.find(".response-content", best_match=True)
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

    async def research_topic(self, query: str) -> str:
        """Conduct research on a given topic using Gemini"""
        try:
            logger.info(f"Starting research on query: {query}")
            
            if not self.config.google_email or not self.config.google_password:
                raise ValueError("Google credentials not found in config")
                
            # Setup browser
            self.driver = await self.setup_browser()
            logger.info(f"Navigating to {self.gemini_url}...")
            page = await self.driver.get(self.gemini_url)
            
            # Handle login and setup
            await self.handle_login(page)
            await self.setup_research_mode(page)
            
            # Submit query and get results
            result = await self.submit_query(page, query)
            logger.info("Research completed successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to conduct research: {str(e)}")
            return f"Research failed: {str(e)}"
            
        finally:
            if self.driver:
                logger.info("Closing browser...")
                self.driver.stop()
                logger.info("Browser stopped successfully")

    async def close(self):
        """Close browser"""
        if self.driver:
            logger.info("Cleaning up resources...")
            self.driver.stop()
            logger.info("Browser stopped successfully") 