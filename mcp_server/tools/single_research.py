"""
single_research.py

Implements headless browser-based research for a single product.
"""
from typing import Any, List
from langchain_openai import ChatOpenAI
from browser_use import Agent

from dotenv import load_dotenv
load_dotenv()


def single_product_research(product: str, plan: str) -> str:
    """
    Uses the 'browser-use' library for headless browsing, similar to how relishplus does it (without depending on relishplus).
    Returns text or structured data after navigating and extracting page results.
    """
    # with BrowserSession(headless=True) as browser:
    #     product_url = f"https://gemini.google.com/app"
    #     browser.go_to(product_url)
    #     for t in terms:
    #         browser.type("input[name='q']", t)
    #         browser.click("button[type='submit']")
    #         # Optionally wait for new content to load, e.g., time.sleep(...) or browser.wait_until(...)
    #     extracted = browser.get_page_text()  # Placeholder for final extraction
    #     return f"Results from {product} with {terms}:\n{extracted[:250]}..."
    print(f"Researching {product} with plan: {plan}")
    return f"Results from {product} with plan: {plan}"

async def gemini_deep_research(plan: str) -> str:
    """
    Uses the 'browser-use' library for headless browsing, similar to how relishplus does it (without depending on relishplus).
    Returns text or structured data after navigating and extracting page results.
    """
    llm = ChatOpenAI(model="gpt-4o")
    agent = Agent(
        task=plan,
        llm=llm,
    )
    result = await agent.run()
    print(result)
    return result