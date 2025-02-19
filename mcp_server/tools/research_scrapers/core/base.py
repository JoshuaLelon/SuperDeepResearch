"""Base module for research site scraping implementations."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from .config import ScraperConfig, ResearchSite
from .auth import GeminiAuth

class BaseResearchScraper(ABC):
    """Base class for all research site scraper implementations"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self._auth: Optional[GeminiAuth] = None
        self._site_handlers: Dict[ResearchSite, Any] = {}
    
    @property
    @abstractmethod
    def auth(self) -> Optional[GeminiAuth]:
        """Get authentication handler for this scraper if required"""
        pass
    
    @abstractmethod
    async def setup(self) -> None:
        """Initialize browser and prepare for scraping"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources"""
        pass
    
    @abstractmethod
    async def execute_research(self, query: str) -> str:
        """Execute research query and return results"""
        pass
    
    async def login(self) -> bool:
        """Execute login flow using auth handler if required"""
        if not self.auth:
            return True
        return await self.auth.login()
    
    def set_2fa_code(self, code: str) -> None:
        """Set 2FA code for use during login"""
        if self._auth:
            self._auth.set_2fa_code(code)
    
    @abstractmethod
    async def handle_site_specific_research(self, site: ResearchSite, query: str) -> str:
        """Handle research for a specific site"""
        pass 