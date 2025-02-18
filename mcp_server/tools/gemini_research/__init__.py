"""
Gemini research automation package
"""
from .automation import GeminiAutomation
from .config import Config, ResearchPreferences, load_config

__all__ = ['GeminiAutomation', 'Config', 'ResearchPreferences', 'load_config'] 