"""Authentication module for Gemini scraping."""
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Optional

from .config import ScraperConfig

class GeminiAuth(ABC):
    """Base class for Gemini authentication across different browser implementations"""
    
    def __init__(self, config: ScraperConfig):
        self.config = config
        self._2fa_code: Optional[str] = None
    
    @abstractmethod
    async def navigate_to_login(self) -> None:
        """Navigate to the Google login page"""
        pass
    
    @abstractmethod
    async def enter_email(self) -> None:
        """Enter email and proceed to password step"""
        pass
    
    @abstractmethod
    async def enter_password(self) -> None:
        """Enter password and submit"""
        pass
    
    @abstractmethod
    async def handle_2fa(self) -> None:
        """Handle 2FA if required"""
        pass
    
    @abstractmethod
    async def verify_login_success(self) -> bool:
        """Verify successful login"""
        pass
    
    async def login(self) -> bool:
        """Execute full login flow"""
        try:
            await self.navigate_to_login()
            await self.enter_email()
            await asyncio.sleep(1)  # Brief pause for animation
            await self.enter_password()
            
            # Check if 2FA is needed
            try:
                await self.handle_2fa()
            except Exception as e:
                # If no 2FA prompt found, continue
                pass
            
            return await self.verify_login_success()
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")
    
    def set_2fa_code(self, code: str) -> None:
        """Set 2FA code for use during login"""
        self._2fa_code = code 