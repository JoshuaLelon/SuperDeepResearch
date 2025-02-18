#!/usr/bin/env python3
import asyncio
import sys
import os
import argparse
import logging
from rich.logging import RichHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)

# test with:
# headless mode: zsh -c 'source ~/anaconda3/etc/profile.d/conda.sh && conda activate mcp && python scripts/test_deep_research.py "your research query"'
# visible mode: zsh -c 'source ~/anaconda3/etc/profile.d/conda.sh && conda activate mcp && python scripts/test_deep_research.py "your research query" --no-headless' 

# Add the parent directory to Python path so we can import from mcp_server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.tools.gemini_research import GeminiAutomation, load_config, ResearchPreferences, Config

async def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run Gemini research')
    parser.add_argument('query', help='The research query to process')
    parser.add_argument('--no-headless', action='store_true', help='Run browser in visible mode')
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting Gemini research automation...")
        # Load config and modify headless setting
        config = load_config()
        config.research_preferences.headless = not args.no_headless
        
        # Initialize automation
        automation = GeminiAutomation(config)
        
        # Run research
        result = await automation.research_topic(args.query)
        logger.info("\nResearch Results:")
        print(result)
        
    except Exception as e:
        logger.error(f"Error during research: {e}")
        
    finally:
        if 'automation' in locals():
            await automation.close()

if __name__ == "__main__":
    asyncio.run(main()) 