"""Browser-Use based implementation for research scraping."""
import logging
import asyncio
from typing import Optional, Any, Type
from browser_use import Agent, BrowserConfig, Browser, BrowserContextConfig
from langchain_openai import ChatOpenAI

from ..core.base import BaseResearchScraper
from ..core.auth import GeminiAuth
from ..core.config import ScraperConfig, ResearchSite
from ....logging_config import setup_logging
from ..sites.perplexity.scraper import PerplexitySiteInstructions
from ..sites.gemini.scraper import GeminiSiteInstructions

logger = setup_logging(__name__)

class BrowserUseAuth(GeminiAuth):
    """Browser-Use specific implementation of Gemini authentication"""
    
    def __init__(self, config: ScraperConfig, agent: Agent):
        super().__init__(config)
        self.agent = agent
        
    async def navigate_to_login(self) -> None:
        """Navigation handled by Browser-Use agent"""
        pass

    async def enter_email(self) -> None:
        """Email entry handled by Browser-Use agent"""
        pass

    async def enter_password(self) -> None:
        """Password entry handled by Browser-Use agent"""
        pass

    async def handle_2fa(self) -> None:
        """2FA handled by Browser-Use agent"""
        pass

    async def verify_login_success(self) -> bool:
        """Verification handled by Browser-Use agent"""
        return True

class BrowserUseDriver(BaseResearchScraper):
    """Browser-Use implementation of research scraper"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config)
        self.browser = None
        self.agent = None
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.0)
        self._site_instructions = None
        
    @property
    def site_instructions(self) -> Any:
        """Get the appropriate site instructions for the current site"""
        if not self._site_instructions:
            site_map = {
                ResearchSite.PERPLEXITY: PerplexitySiteInstructions,
                ResearchSite.GEMINI: GeminiSiteInstructions
            }
            self._site_instructions = site_map[self.config.site].BrowserUse
        return self._site_instructions
        
    async def setup(self) -> None:
        """Initialize Browser-Use browser"""
        logger.info("Starting Browser-Use browser...")
        try:
            context_config = BrowserContextConfig(
                browser_window_size={'width': 1920, 'height': 1080},
                wait_for_network_idle_page_load_time=3.0
            )
            
            browser_config = BrowserConfig(
                headless=self.config.headless,
                disable_security=True,
                new_context_config=context_config
            )
            
            self.browser = Browser(config=browser_config)
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Browser startup error: {str(e)}")
            raise

    async def cleanup(self) -> None:
        """Clean up Browser-Use resources"""
        if self.browser:
            logger.info("Cleaning up resources...")
            await self.browser.close()
            self.browser = None
            self.agent = None
            logger.info("Browser stopped successfully")

    async def handle_site_specific_research(self, site: ResearchSite, query: str) -> str:
        """Handle research using site-specific instructions"""
        instructions = self.site_instructions.instructions
        
        try:
            # Create task using site-specific template and instructions
            task = self.site_instructions.TASK_TEMPLATE.format(
                url=self.config.site_config.url,
                query=query,
                input_selectors=", ".join(instructions.selectors.input_field),
                response_selectors=", ".join(instructions.selectors.response_content),
                pre_wait=instructions.navigation.pre_input_wait_time,
                post_wait=instructions.navigation.post_input_wait_time,
                response_wait=instructions.navigation.response_wait_time
            )
            
            # Create agent with the task
            self.agent = Agent(
                task=task,
                llm=self.llm,
                browser=self.browser,
                generate_gif=False,
                max_input_tokens=32000,
                max_actions_per_step=3
            )
            
            # Execute the task and get results
            logger.info("Executing Browser-Use agent task...")
            result = await self.agent.run(max_steps=5)
            
            if result.final_result():
                logger.info("Found results")
                return result.final_result()
            
            logger.warning("No results found")
            return "No results found"
            
        except Exception as e:
            logger.error(f"Query submission error: {str(e)}")
            raise
    
    async def execute_research(self, query: str) -> str:
        """Execute research using Browser-Use"""
        return await self.handle_site_specific_research(self.config.site, query) 