"""Perplexity-based implementation for research scraping."""
import logging
from typing import Optional, Any, List
from dataclasses import dataclass
import asyncio
import random
import time

from .....logging_config import setup_logging
from ...core.base import BaseResearchScraper
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

class PerplexitySiteInstructions:
    """
    Contains all instructions for scraping Perplexity, organized by driver.
    Each driver section contains the exact selectors, navigation steps, and other
    instructions needed to scrape Perplexity using that specific driver.
    """
    
    class Patchright:
        """Instructions specific to Patchright automation"""
        selectors = SelectorSet(
            input_field=[
                'textarea[placeholder*="Ask anything"]',
                'textarea[placeholder*="Message Perplexity"]',
                'textarea[placeholder*="Ask"]',
                'textarea[placeholder*="Message"]',
                'textarea[role="textbox"]',
                'textarea',
                '[contenteditable="true"]',
                '[role="textbox"]'
            ],
            submit_button=None,  # Uses Enter key instead
            response_content=[
                '.response-content',
                '[data-message-author-role="assistant"]',
                '.prose',
                '.markdown-content',
                '[role="article"]',
                '[role="presentation"]'
            ]
        )
        
        navigation = NavigationSteps(
            pre_input_wait_time=2.0,
            post_input_wait_time=2.0,
            response_wait_time=15.0
        )

        @staticmethod
        async def handle_login_flow(page: Any) -> Any:
            """Handle the entire login flow until Google popup"""
            logger.info("Starting login flow...")
            
            # Find and click login button
            login_selectors = [
                'button:has-text("Log in")',
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                'a:has-text("Log in")',
                'a:has-text("Login")',
                'a:has-text("Sign in")'
            ]
            
            # Try each login selector
            for selector in login_selectors:
                try:
                    login_button = await page.wait_for_selector(selector, timeout=5000, state='visible')
                    if login_button:
                        logger.info(f"Found login button with selector: {selector}")
                        # Move mouse like a human would
                        box = await login_button.bounding_box()
                        if box:
                            await page.mouse.move(
                                box['x'] + box['width'] / 2,
                                box['y'] + box['height'] / 2,
                                steps=10
                            )
                            await asyncio.sleep(0.1)
                        await login_button.click()
                        break
                except Exception:
                    continue
            
            # Wait for modal to appear and stabilize
            logger.info("Waiting for login modal to stabilize...")
            await asyncio.sleep(2)
            
            # Find and click Google login
            logger.info("Looking for Google login button...")
            
            try:
                # Add more human-like browser properties
                await page.evaluate('''() => {
                    // Add common browser properties
                    Object.defineProperty(navigator, 'webdriver', { get: () => false });
                    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                    Object.defineProperty(navigator, 'plugins', { get: () => [
                        { name: 'Chrome PDF Plugin' },
                        { name: 'Chrome PDF Viewer' },
                        { name: 'Native Client' }
                    ]});
                    
                    // Add Chrome specific properties
                    window.chrome = {
                        app: { isInstalled: false },
                        runtime: {},
                        loadTimes: function(){},
                        csi: function(){},
                        webstore: {}
                    };
                    
                    // Add WebGL
                    const getParameter = WebGLRenderingContext.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) {
                            return 'Intel Inc.';
                        }
                        if (parameter === 37446) {
                            return 'Intel Iris OpenGL Engine';
                        }
                        return getParameter(parameter);
                    };
                }''')
                
                # Create new page for Google login
                context = page.context
                google_page = await context.new_page()
                await google_page.goto('https://accounts.google.com')
                
                # Wait for button to be ready and visible
                google_button = await page.wait_for_selector('button:has-text("Continue with Google")', state='visible', timeout=5000)
                
                if not google_button:
                    raise Exception("Could not find Google login button")
                
                # Wait for any animations to complete
                await asyncio.sleep(1)
                
                # Get button position for human-like interaction
                box = await google_button.bounding_box()
                if not box:
                    raise Exception("Could not get button position")
                    
                # Move mouse like a human would
                await page.mouse.move(
                    box['x'] + box['width'] / 2,
                    box['y'] + box['height'] / 2,
                    steps=10
                )
                await asyncio.sleep(0.1)
                
                # Remove any intercepting elements
                await page.evaluate('''() => {
                    // Remove all overlays and intercepting elements
                    document.querySelectorAll('div[class*="overlay"], div[class*="modal"], div[class*="backdrop"], div[class*="dialog"]').forEach(el => {
                        if (el.style.zIndex > 0) {
                            el.style.zIndex = '-1';
                        }
                        el.style.pointerEvents = 'none';
                    });
                    
                    // Find the Google button using text content
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const googleButton = buttons.find(btn => 
                        btn.textContent.includes('Continue with Google') && 
                        btn.querySelector('svg')
                    );
                    
                    if (googleButton) {
                        // Ensure the button and its container are clickable
                        googleButton.style.pointerEvents = 'auto';
                        googleButton.style.zIndex = '9999';
                        let parent = googleButton.parentElement;
                        while (parent && parent !== document.body) {
                            parent.style.pointerEvents = 'auto';
                            parent.style.zIndex = '9999';
                            parent = parent.parentElement;
                        }
                    }
                }''')
                
                # Wait for styles to apply
                await asyncio.sleep(0.5)
                
                # Click with JavaScript to ensure the event triggers
                await page.evaluate('''() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const googleButton = buttons.find(btn => 
                        btn.textContent.includes('Continue with Google') && 
                        btn.querySelector('svg')
                    );
                    if (googleButton) {
                        const rect = googleButton.getBoundingClientRect();
                        const clickEvent = new MouseEvent('click', {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: rect.left + rect.width / 2,
                            clientY: rect.top + rect.height / 2
                        });
                        googleButton.dispatchEvent(clickEvent);
                    }
                }''')
                
                logger.info("Successfully clicked Google button")
                
                # Wait for Google login page to load
                await google_page.wait_for_load_state('networkidle')
                
                return google_page
                
            except Exception as e:
                logger.error(f"Error during Google login: {str(e)}")
                raise Exception("Could not click Google login button")

        @staticmethod
        async def handle_research(page: Any, query: str) -> str:
            """Handle the entire research flow after login"""
            logger.info("Starting research flow...")
            
            # Find input field
            input_selectors = [
                'textarea[placeholder*="Ask anything"]',
                'textarea[placeholder*="Message Perplexity"]',
                'textarea[placeholder*="Ask"]',
                'textarea[placeholder*="Message"]',
                'textarea[role="textbox"]',
                'textarea',
                '[contenteditable="true"]',
                '[role="textbox"]'
            ]
            
            # Try each input selector
            input_field = None
            for selector in input_selectors:
                try:
                    input_field = await page.wait_for_selector(selector, timeout=5000, state='visible')
                    if input_field:
                        logger.info(f"Found input field with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not input_field:
                raise Exception("Could not find input field")
            
            # Enter query
            logger.info("Entering query...")
            await input_field.click()
            await input_field.fill(query)
            await input_field.press('Enter')
            
            # Wait for response
            logger.info("Waiting for response...")
            response_selectors = [
                '.response-content',
                '[data-message-author-role="assistant"]',
                '.prose',
                '.markdown-content',
                '[role="article"]',
                '[role="presentation"]'
            ]
            
            # Try to get response with timeout
            start_time = time.time()
            max_wait = 15.0
            
            while time.time() - start_time < max_wait:
                for selector in response_selectors:
                    try:
                        content = await page.wait_for_selector(selector, timeout=5000)
                        if content:
                            text = await content.text_content()
                            if text and len(text.strip()) > 0:
                                logger.info("Found response content")
                                return text.strip()
                    except Exception:
                        continue
                await asyncio.sleep(1)
            
            raise Exception("No response found after timeout")
    
    class NoDriver:
        """Instructions specific to NoDriver automation"""
        selectors = SelectorSet(
            input_field=[
                'textarea[placeholder*="Ask anything"]',
                'textarea[placeholder*="Message Perplexity"]'
            ],
            submit_button=None,
            response_content=[
                '.response-content',
                '.markdown-content'
            ]
        )
        
        navigation = NavigationSteps(
            pre_input_wait_time=2.0,
            post_input_wait_time=2.0,
            response_wait_time=10.0
        )
    
    class BrowserUse:
        """Instructions specific to Browser-Use automation"""
        selectors = SelectorSet(
            input_field=[
                'textarea[placeholder*="Ask anything"]',
                'textarea[placeholder*="Message Perplexity"]'
            ],
            submit_button=None,
            response_content=[
                '.response-content',
                '.markdown-content'
            ]
        )
        
        navigation = NavigationSteps(
            pre_input_wait_time=3.0,
            post_input_wait_time=3.0,
            response_wait_time=10.0
        )

class PerplexityScraper(BaseResearchScraper):
    """Perplexity implementation of research scraper"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config)
        self.patchright = None
        self.browser = None
        self.page = None
        
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