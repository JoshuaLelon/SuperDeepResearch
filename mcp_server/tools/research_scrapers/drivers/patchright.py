"""Patchright-based implementation for research scraping."""
import logging
import asyncio
from typing import Optional, Any, Type
from patchright.async_api import async_playwright, Browser, Page, BrowserContext
import random
import time

from ..core.base import BaseResearchScraper
from ..core.auth import GeminiAuth
from ..core.config import ScraperConfig, ResearchSite
from ....logging_config import setup_logging
from ..sites.perplexity.scraper import PerplexitySiteInstructions
from ..sites.gemini.scraper import GeminiSiteInstructions

logger = setup_logging(__name__)

class PatchrightAuth(GeminiAuth):
    """Patchright-specific implementation of Google authentication"""
    
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
        self._auth = None
        self._site_instructions = None
        self.playwright = None  # Initialize playwright attribute
        
    @property
    def auth(self) -> Optional[GeminiAuth]:
        """Get Patchright auth handler"""
        if not self.config or not self.config.site_config.requires_auth:
            return None
        if not self._auth:
            if not self.page:
                raise RuntimeError("Browser page not initialized")
            self._auth = PatchrightAuth(self.config, self.page)
        return self._auth

    @property
    def site_instructions(self) -> Any:
        """Get the appropriate site instructions for the current site"""
        if not self._site_instructions:
            site_map = {
                ResearchSite.PERPLEXITY: PerplexitySiteInstructions,
                ResearchSite.GEMINI: GeminiSiteInstructions
            }
            # Create an instance of the instructions class
            self._site_instructions = site_map[self.config.site].Patchright()
        return self._site_instructions
        
    async def setup(self) -> None:
        """Initialize browser and page with evasion techniques"""
        if not self.page:
            logger.info("Setting up browser...")
            
            # Initialize playwright
            self.playwright = await async_playwright().start()
            
            # Configure browser launch options
            browser_args = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-extensions',
                '--disable-blink-features=AutomationControlled',
                '--disable-automation',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--enable-javascript',
                '--window-size=1920,1080'
            ]
            
            # Launch browser with configured options
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                args=browser_args
            )
            
            # Configure context with advanced evasion
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                java_script_enabled=True,
                bypass_csp=True,
                ignore_https_errors=True,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1'
                }
            )
            
            # Add advanced evasion scripts
            await context.add_init_script("""
                // Mask automation indicators
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                
                // Mock Chrome runtime
                window.chrome = {
                    runtime: {},
                    app: {},
                    csi: function(){},
                    loadTimes: function(){}
                };
                
                // Override permissions query
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
                );
                
                // Add WebGL support
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
                
                // Add touch support
                const touchEvent = new TouchEvent("touchstart", {
                    touches: [{
                        identifier: 1,
                        pageX: 150,
                        pageY: 150,
                        screenX: 150,
                        screenY: 150,
                        clientX: 150,
                        clientY: 150,
                        target: document.body
                    }],
                    targetTouches: [],
                    changedTouches: [],
                    view: window,
                    bubbles: true,
                    cancelable: true
                });
                
                // Randomize canvas fingerprint
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type) {
                    const context = originalGetContext.apply(this, arguments);
                    if (type === '2d') {
                        const originalFillText = context.fillText;
                        context.fillText = function() {
                            arguments[0] = arguments[0] + ' ';
                            return originalFillText.apply(this, arguments);
                        }
                    }
                    return context;
                };
            """)
            
            self.page = await context.new_page()
            
            # Configure page-specific settings
            await self.page.set_extra_http_headers({
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            })
            
            # Set up request interception for Cloudflare
            await self.page.route("**/*", self._handle_request)
            
            logger.info("Browser setup complete")
            
    async def _handle_request(self, route, request):
        """Handle intercepted requests to bypass Cloudflare"""
        # Skip image and font requests to reduce detection
        if request.resource_type in ['image', 'font', 'media']:
            await route.abort()
            return
            
        # Add random delays to appear more human-like
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Continue with modified headers
        headers = {
            **request.headers,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        await route.continue_(headers=headers)

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
        """Handle research for a specific site"""
        if site != self.config.site:
            raise ValueError(f"This driver only handles {self.config.site} research, not {site}")
            
        try:
            # Navigate to site
            logger.info(f"Navigating to {self.config.site_config.url}...")
            await self.page.goto(self.config.site_config.url)
            await self.page.wait_for_load_state('networkidle')
            
            # Only handle login if site requires auth
            if self.config.site_config.requires_auth:
                popup = await self.site_instructions.handle_login_flow(self.page)
                await self._handle_google_login(popup)
                await popup.wait_for_event('close', timeout=30000)
            
            # Let scraper handle the research
            return await self.site_instructions.handle_research(self.page, query)
            
        except Exception as e:
            logger.error(f"Error during research: {str(e)}")
            raise

    async def execute_research(self, query: str) -> str:
        """Execute research using Patchright"""
        return await self.handle_site_specific_research(self.config.site, query)

    async def navigate_to_site(self) -> None:
        """Navigate to the target site and handle any challenges"""
        logger.info(f"Navigating to {self.config.site_config.url}...")
        
        try:
            # Navigate with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Navigate with multiple strategies
                    for strategy in ['domcontentloaded', 'load', 'networkidle']:
                        try:
                            response = await self.page.goto(
                                self.config.site_config.url,
                                wait_until=strategy,
                                timeout=30000
                            )
                            
                            # Check for Cloudflare challenge
                            if await self._is_cloudflare_challenge():
                                logger.info("Detected Cloudflare challenge, attempting to solve...")
                                await self._handle_cloudflare_challenge()
                            
                            # Verify we're on the correct page
                            if await self._verify_page_loaded():
                                logger.info("Successfully navigated to site")
                                return
                                
                        except Exception as e:
                            logger.warning(f"Navigation failed with strategy {strategy}: {str(e)}")
                            continue
                            
                    # If we get here, all strategies failed
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5  # Exponential backoff
                        logger.info(f"Retrying navigation in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                    
                except Exception as e:
                    logger.error(f"Navigation attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        continue
                    raise
                    
        except Exception as e:
            logger.error(f"All navigation attempts failed: {str(e)}")
            raise
            
    async def _is_cloudflare_challenge(self) -> bool:
        """Check if we're on a Cloudflare challenge page"""
        try:
            # Check for common Cloudflare elements
            cloudflare_indicators = [
                "//h1[contains(text(), 'Checking your browser')]",
                "//h1[contains(text(), 'Just a moment')]",
                "//div[contains(text(), 'DDoS protection by Cloudflare')]",
                "#challenge-running",
                "#challenge-form",
                "#challenge-stage"
            ]
            
            for indicator in cloudflare_indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=1000)
                    if element:
                        return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            logger.warning(f"Error checking for Cloudflare challenge: {str(e)}")
            return False
            
    async def _handle_cloudflare_challenge(self) -> None:
        """Handle Cloudflare challenge page"""
        try:
            # Wait for initial challenge animation
            await asyncio.sleep(2)
            
            # Wait for challenge to complete
            success_indicators = [
                "//h1[contains(text(), 'Please verify you are a human')]",
                "#success-text",
                "#challenge-success"
            ]
            
            # Wait for success indicators to disappear
            max_wait = 30  # Maximum seconds to wait
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                challenge_present = False
                
                for indicator in success_indicators:
                    try:
                        element = await self.page.wait_for_selector(indicator, timeout=1000)
                        if element:
                            challenge_present = True
                            break
                    except:
                        continue
                        
                if not challenge_present:
                    logger.info("Cloudflare challenge appears to be solved")
                    return
                    
                await asyncio.sleep(1)
                
            raise Exception("Timed out waiting for Cloudflare challenge to complete")
            
        except Exception as e:
            logger.error(f"Error handling Cloudflare challenge: {str(e)}")
            raise
            
    async def _verify_page_loaded(self) -> bool:
        """Verify we've successfully loaded the target page"""
        try:
            await self.page.wait_for_load_state('networkidle')
            return True
        except Exception as e:
            logger.warning(f"Error verifying page load: {str(e)}")
            return False

    async def _handle_google_login(self, target: Any) -> None:
        """Handle the Google login process in either a popup or iframe"""
        try:
            # Wait for email input
            email_input = await target.wait_for_selector('input[type="email"]', timeout=10000)
            if email_input:
                await email_input.fill(self.config.google_email)
                await target.click('button:has-text("Next")')
                await asyncio.sleep(2)
                
                # Wait for password input
                password_input = await target.wait_for_selector('input[type="password"]', timeout=10000)
                if password_input:
                    await password_input.fill(self.config.google_password)
                    await target.click('button:has-text("Next")')
                    await asyncio.sleep(5)
                    
                    # Handle 2FA if needed
                    try:
                        two_factor_input = await target.wait_for_selector('input[type="tel"]', timeout=5000)
                        if two_factor_input and self._2fa_code:
                            await two_factor_input.fill(self._2fa_code)
                            await target.click('button:has-text("Next")')
                            await asyncio.sleep(5)
                    except Exception:
                        # No 2FA needed
                        pass
                else:
                    raise Exception("Password input not found")
            else:
                raise Exception("Email input not found")
                
        except Exception as e:
            logger.error(f"Google login failed: {str(e)}")
            raise

    async def _continue_with_research(self, query: str) -> str:
        """Continue with research after successful login"""
        try:
            # Wait for pre-input delay
            await asyncio.sleep(self.site_instructions.navigation.pre_input_wait_time)
            
            # Find and fill input field
            input_field = None
            for selector in self.site_instructions.selectors.input_field:
                try:
                    input_field = await self.page.wait_for_selector(selector, state='visible', timeout=5000)
                    if input_field:
                        logger.info(f"Found input field with selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} not found: {str(e)}")
                    continue
                    
            if not input_field:
                raise Exception("Could not find input field")
                
            # Type query with human-like delays
            logger.info("Entering query...")
            await input_field.click()
            for char in query:
                await input_field.type(char, delay=random.uniform(50, 150))
                
            # Wait for post-input delay
            await asyncio.sleep(self.site_instructions.navigation.post_input_wait_time)
            
            # Submit query
            logger.info("Submitting query...")
            await input_field.press('Enter')
            
            # Wait for response with timeout
            logger.info("Waiting for response...")
            max_wait = self.site_instructions.navigation.response_wait_time
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                # Check for response content
                for selector in self.site_instructions.selectors.response_content:
                    try:
                        content = await self.page.wait_for_selector(selector, timeout=5000)
                        if content:
                            text = await content.text_content()
                            if text and len(text.strip()) > 0:
                                logger.info("Found response content")
                                return text.strip()
                    except Exception as e:
                        logger.debug(f"Selector {selector} not found: {str(e)}")
                        continue
                        
                # Check for Cloudflare challenge
                if await self._is_cloudflare_challenge():
                    logger.info("Detected Cloudflare challenge during response, attempting to solve...")
                    await self._handle_cloudflare_challenge()
                    
                await asyncio.sleep(1)
                
            raise Exception(f"No response found after {max_wait} seconds")
            
        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            raise 