"""
single_research.py

Implements headless browser-based research for a single product.
"""
import sys
import logging

# Completely disable all logging before importing anything else
logging.getLogger().setLevel(logging.CRITICAL)
for handler in logging.getLogger().handlers[:]:
    logging.getLogger().removeHandler(handler)
logging.getLogger().addHandler(logging.NullHandler())

# Now import other modules
from typing import Any, List
from langchain_openai import ChatOpenAI
from browser_use import Agent, BrowserConfig, Browser, BrowserContextConfig
from dotenv import load_dotenv

load_dotenv()

def single_product_research(product: str, plan: str) -> str:
    """
    Uses the 'browser-use' library for headless browsing, similar to how relishplus does it (without depending on relishplus).
    Returns text or structured data after navigating and extracting page results.
    """
    return f"Results from {product} with plan: {plan}"

async def gemini_deep_research(plan: str) -> str:
    """
    Uses the 'browser-use' library for headless browsing, similar to how relishplus does it (without depending on relishplus).
    Returns text or structured data after navigating and extracting page results.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0
    )
    
    # Configure browser context
    context_config = BrowserContextConfig(
        browser_window_size={'width': 1920, 'height': 1080},  # Larger window for better visibility
        wait_for_network_idle_page_load_time=3.0  # Give more time for dynamic content
    )
    
    # Configure browser
    browser_config = BrowserConfig(
        headless=True,
        disable_security=True,
        new_context_config=context_config
    )
    
    # Initialize browser with config
    browser = Browser(config=browser_config)
    
    # Create agent with browser and limit response size
    agent = Agent(
        task=plan,
        llm=llm,
        browser=browser,
        generate_gif=False,  # Disable GIF generation to avoid filesystem issues
        max_input_tokens=32000,  # Reduce token limit to keep responses smaller
        max_actions_per_step=3  # Limit actions per step to reduce response size
    )
    
    try:
        # Run with fewer steps to limit total response size
        result = await agent.run(max_steps=5)
        return result.final_result() or "No results found"
    finally:
        await browser.close()  # Ensure browser is closed after use

# Basic configuration
