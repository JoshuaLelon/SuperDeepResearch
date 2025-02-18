"""
Main entry point for Gemini research automation
"""
import os
import sys
import asyncio
import logging
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler
from .automation import GeminiAutomation
from .config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)

async def run_research(query: str):
    """Run the Gemini research automation"""
    try:
        # Load config
        config = load_config()
        
        # Initialize automation
        automation = GeminiAutomation(config)
        
        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            # Add progress display
            progress.add_task(description="Conducting research...", total=None)
            
            # Run the research
            result = await automation.research_topic(query)
            
            if result:
                logger.info("\nResearch Results:")
                print(result)
                return True
            else:
                logger.error("Research failed to return results")
                return False
                
    except Exception as e:
        logger.error(f"Research failed: {str(e)}")
        return False
        
    finally:
        if "automation" in locals():
            await automation.close()

def main(query: str = typer.Argument(..., help="The research query to process")):
    """Main entry point"""
    try:
        asyncio.run(run_research(query))
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    typer.run(main) 