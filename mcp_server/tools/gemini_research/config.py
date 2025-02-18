"""
Configuration for Gemini research automation
"""
from dataclasses import dataclass
from typing import List, Optional
import os
import yaml
from dotenv import load_dotenv

@dataclass
class ResearchPreferences:
    """Research preferences configuration"""
    model: str = "gemini-1.5-pro"
    max_depth: int = 3
    include_citations: bool = True
    focus_areas: List[str] = None
    headless: bool = True

@dataclass
class Config:
    """Main configuration class"""
    research_preferences: ResearchPreferences
    google_api_key: Optional[str] = None
    google_email: Optional[str] = None
    google_password: Optional[str] = None

def load_config() -> Config:
    """Load configuration from environment and config file"""
    load_dotenv()
    
    # Load from config.yml if it exists
    config_path = os.path.join(os.path.dirname(__file__), "config.yml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
    else:
        config_data = {}
        
    # Extract research preferences
    research_prefs = config_data.get("research_preferences", {})
    research_preferences = ResearchPreferences(
        model=research_prefs.get("model", "gemini-1.5-pro"),
        max_depth=research_prefs.get("max_depth", 3),
        include_citations=research_prefs.get("include_citations", True),
        focus_areas=research_prefs.get("focus_areas", []),
        headless=research_prefs.get("headless", True)
    )
    
    # Get credentials from environment
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_email = os.getenv("GOOGLE_EMAIL")
    google_password = os.getenv("GOOGLE_PASSWORD")
    
    # Create config object
    return Config(
        research_preferences=research_preferences,
        google_api_key=google_api_key,
        google_email=google_email,
        google_password=google_password
    ) 