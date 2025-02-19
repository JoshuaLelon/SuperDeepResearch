"""Configuration module for research site scraping."""
import os
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from enum import Enum

class ResearchSite(str, Enum):
    GEMINI = "gemini"
    PERPLEXITY = "perplexity"

@dataclass
class SiteConfig:
    """Configuration for a specific research site"""
    url: str
    login_url: Optional[str] = None
    requires_auth: bool = False
    auth_type: Optional[str] = None

SITE_CONFIGS = {
    ResearchSite.GEMINI: SiteConfig(
        url="https://gemini.google.com/app",
        login_url="https://accounts.google.com",
        requires_auth=True,
        auth_type="google"
    ),
    ResearchSite.PERPLEXITY: SiteConfig(
        url="https://www.perplexity.ai",
        requires_auth=False
    )
}

@dataclass
class ScraperConfig:
    """Shared configuration for all scraper implementations"""
    # Browser settings
    headless: bool = True
    window_size: Tuple[int, int] = (1920, 1080)
    network_idle_timeout: float = 3.0
    max_retries: int = 3
    
    # Site selection
    site: ResearchSite = ResearchSite.GEMINI
    
    # Authentication settings
    google_email: Optional[str] = None
    google_password: Optional[str] = None
    
    def __post_init__(self):
        """Load credentials from environment if not provided"""
        if self.site == ResearchSite.GEMINI:
            if not self.google_email:
                self.google_email = os.getenv("GOOGLE_EMAIL")
            if not self.google_password:
                self.google_password = os.getenv("GOOGLE_PASSWORD")
            
            if not self.google_email or not self.google_password:
                raise ValueError("Google credentials must be provided via constructor or environment variables")
    
    @property
    def site_config(self) -> SiteConfig:
        """Get configuration for the selected site"""
        return SITE_CONFIGS[self.site]
    
    @property
    def viewport(self) -> Dict[str, int]:
        """Get viewport settings in format expected by Playwright"""
        return {"width": self.window_size[0], "height": self.window_size[1]}
    
    @property
    def window_size_str(self) -> str:
        """Get window size in format expected by some browser drivers"""
        return f"{self.window_size[0]},{self.window_size[1]}" 