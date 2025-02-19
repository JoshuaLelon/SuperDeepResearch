"""Gemini-specific implementation for research scraping."""
import logging
import asyncio
from typing import Optional, Any
from patchright.async_api import async_playwright, Browser, Page

from ...core.base import BaseResearchScraper
from ...core.auth import GeminiAuth
from ...core.config import ScraperConfig, ResearchSite

logger = logging.getLogger(__name__)

class GeminiPatchrightAuth(GeminiAuth):
    """Patchright-specific implementation of Gemini authentication"""
    
    def __init__(self, config: ScraperConfig, page: Page):
        super().__init__(config)
        self.page = page
        
    async def navigate_to_login(self) -> None:
        """Navigate to Google login page"""
        try:
            # Try the action button first
            await self.page.wait_for_selector('[data-test-id="action-button"]', timeout=5000)
            await self.page.locator('[data-test-id="action-button"]').click()
        except Exception:
            try:
                # Try the link version
                await self.page.wait_for_selector('a:has-text("Sign in")', timeout=5000)
                await self.page.get_by_role("link", name="Sign in").click()
            except Exception:
                # We might already be on the login page
                pass
        
        # Wait for the login page to load
        await self.page.wait_for_url("**/accounts.google.com/**", timeout=10000)
        
        # Check if we're already on the login page
        current_url = self.page.url
        if not current_url.startswith("https://accounts.google.com"):
            raise RuntimeError("Failed to reach Google login page")

    async def enter_email(self) -> None:
        """Enter email and proceed"""
        await self.page.wait_for_selector('input[type="email"]', timeout=5000)
        await self.page.fill('input[type="email"]', self.config.google_email)
        await self.page.click('button:has-text("Next")')
        await self.page.wait_for_selector('input[type="password"]', timeout=5000)

    async def enter_password(self) -> None:
        """Enter password and submit"""
        await self.page.fill('input[type="password"]', self.config.google_password)
        await self.page.click('button:has-text("Next")')
        # Wait for either 2FA input or successful redirect
        try:
            await self.page.wait_for_url("**/bard.google.com/**", timeout=10000)
        except Exception:
            # Might need 2FA
            pass

    async def handle_2fa(self) -> None:
        """Handle 2FA if required"""
        if self._2fa_code:
            try:
                await self.page.wait_for_selector('input[type="tel"]', timeout=5000)
                await self.page.fill('input[type="tel"]', self._2fa_code)
                await self.page.click('button:has-text("Next")')
                await self.page.wait_for_url("**/bard.google.com/**", timeout=10000)
            except Exception:
                # No 2FA prompt found
                pass

    async def verify_login_success(self) -> bool:
        """Verify successful login"""
        try:
            # Wait for Gemini interface to load
            await self.page.wait_for_selector('textarea[aria-label*="chat input"]', timeout=5000)
            return True
        except Exception:
            return False

class GeminiScraper(BaseResearchScraper):
    """Gemini implementation of research scraper"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config)
        self.patchright = None
        self.browser = None
        self.page = None
        
    @property
    def auth(self) -> Optional[GeminiAuth]:
        """Get Gemini auth handler"""
        if not self._auth:
            if not self.page:
                raise RuntimeError("Browser page not initialized")
            self._auth = GeminiPatchrightAuth(self.config, self.page)
        return self._auth
        
    async def setup(self) -> None:
        """Initialize Patchright browser for Gemini"""
        logger.info("Starting Patchright browser for Gemini...")
        try:
            logger.info("Initializing Playwright...")
            self.patchright = await async_playwright().start()
            
            logger.info("Launching browser with anti-detection settings...")
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
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-blink-features=AutomationControlled',
                    '--ignore-certificate-errors',
                    '--no-first-run',
                    '--no-service-autorun',
                    '--password-store=basic'
                ]
            )
            
            logger.info("Creating browser context...")
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                java_script_enabled=True,
                bypass_csp=True,
                ignore_https_errors=True,
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/Los_Angeles',
                permissions=['geolocation', 'notifications'],
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
                    'sec-ch-ua-arch': '"arm"',
                    'sec-ch-ua-bitness': '"64"',
                    'sec-ch-ua-form-factors': '"Desktop"',
                    'sec-ch-ua-full-version': '"132.0.6834.160"',
                    'sec-ch-ua-full-version-list': '"Not A(Brand";v="8.0.0.0", "Chromium";v="132.0.6834.160", "Google Chrome";v="132.0.6834.160"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-model': '""',
                    'sec-ch-ua-platform': '"macOS"',
                    'sec-ch-ua-platform-version': '"15.3.0"',
                    'sec-ch-ua-wow64': '?0',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',
                    'x-browser-channel': 'stable',
                    'x-browser-copyright': 'Copyright 2025 Google LLC. All rights reserved.',
                }
            )
            
            # Set initial cookies if provided in config
            if self.config.auth_cookies:
                logger.info("Setting authentication cookies from config...")
                await context.add_cookies(self.config.auth_cookies)
            
            logger.info("Adding evasion scripts...")
            await context.add_init_script("""
                // Override property
                const newProto = navigator.__proto__;
                delete newProto.webdriver;
                navigator.__proto__ = newProto;
                
                // Add language
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Add plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Add Chrome
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Modify permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
                );
            """)
            
            logger.info("Creating new page...")
            self.page = await context.new_page()
            
            # Enable request/response logging
            async def log_request(request):
                logger.info("=== REQUEST DETAILS ===")
                logger.info(f"URL: {request.url}")
                logger.info(f"Method: {request.method}")
                logger.info("Headers:")
                for key, value in request.headers.items():
                    logger.info(f"  {key}: {value}")
                if request.post_data:
                    logger.info(f"Post data: {request.post_data}")
                
                # Log resource type and frame info
                logger.info(f"Resource type: {request.resource_type}")
                logger.info(f"Is navigation request: {request.is_navigation_request()}")
            
            async def log_response(response):
                logger.info("=== RESPONSE DETAILS ===")
                logger.info(f"URL: {response.url}")
                logger.info(f"Status: {response.status}")
                logger.info("Response headers:")
                headers = await response.all_headers()
                for key, value in headers.items():
                    logger.info(f"  {key}: {value}")
                
                # Get cookies from response
                context = response.request.frame.page.context
                cookies = await context.cookies()
                if cookies:
                    logger.info("Cookies:")
                    for cookie in cookies:
                        logger.info(f"  {cookie['name']}: {cookie['value']}")
                        logger.info(f"    Domain: {cookie['domain']}")
                        logger.info(f"    Path: {cookie['path']}")
                        logger.info(f"    Secure: {cookie['secure']}")
                        logger.info(f"    HttpOnly: {cookie['httpOnly']}")
            
            async def log_error(error):
                logger.error("=== REQUEST ERROR ===")
                request = error.request
                logger.error(f"Failed URL: {request.url}")
                logger.error(f"Error text: {error.error_text}")
                logger.error("Request headers:")
                for key, value in request.headers.items():
                    logger.error(f"  {key}: {value}")
            
            self.page.on("request", log_request)
            self.page.on("response", log_response)
            self.page.on("requestfailed", log_error)
            
            logger.info(f"Navigating to Gemini...")
            try:
                # Try direct access first
                logger.info("Attempting direct access with cookies...")
                response = await self.page.goto("https://gemini.google.com/", wait_until='domcontentloaded', timeout=15000)
                
                if response and response.ok:
                    logger.info("Successfully accessed Gemini directly")
                    return
                
                # If direct access fails, try login
                logger.info("Direct access failed, attempting login...")
                await self.login()
                
            except Exception as e:
                logger.error(f"Failed to access Gemini: {str(e)}")
                current_url = self.page.url
                logger.error(f"Current URL: {current_url}")
                raise
                
            logger.info("Browser setup completed successfully")
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
            # Wait for and handle any welcome/intro modals
            try:
                welcome_button = await self.page.get_by_text("Got it", exact=True)
                if welcome_button:
                    await welcome_button.click()
                    await asyncio.sleep(1)
            except Exception:
                pass  # No welcome modal found
            
            # Look for input field and enter query
            logger.info("Looking for query input field...")
            input_elem = await self.page.locator('textarea[aria-label*="chat input"]').first
            if not input_elem:
                input_elem = await self.page.locator('textarea[placeholder*="Enter a prompt"]').first
            
            if input_elem:
                logger.info("Found input field, entering query...")
                await input_elem.fill(query)
                await input_elem.press('Enter')
                
                # Wait for response
                logger.info("Waiting for response...")
                await asyncio.sleep(10)
                
                # Look for results in the chat container
                logger.info("Looking for response content...")
                results = await self.page.locator('.chat-message[role="presentation"]').last.text_content()
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
        """Execute research using Gemini"""
        return await self.handle_site_specific_research(ResearchSite.GEMINI, query) 