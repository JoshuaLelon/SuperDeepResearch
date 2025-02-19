#!/usr/bin/env python3
"""Test script for Patchright-based research across different sites."""
import asyncio
import argparse
from typing import Optional

from mcp_server.tools.research_engine import (
    deep_research,
    BrowserApproach,
    ResearchConfig,
    ResearchSite
)

async def main(query: str, site: str = "gemini", headless: bool = True) -> None:
    """Execute research using Patchright approach"""
    try:
        research_site = ResearchSite(site.lower())
    except ValueError:
        print(f"Invalid site: {site}. Must be one of: {', '.join(s.value for s in ResearchSite)}")
        return
        
    config = ResearchConfig(headless=headless, site=research_site)
    
    try:
        result = await deep_research(
            plan=query,
            approach=BrowserApproach.PATCHRIGHT,
            site=research_site,
            config=config
        )
        print("\nResearch Results:")
        print("-" * 80)
        print(result)
        print("-" * 80)
    except Exception as e:
        print(f"\nError during research: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Patchright-based research")
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Research query to execute"
    )
    parser.add_argument(
        "--site",
        type=str,
        default="gemini",
        choices=[s.value for s in ResearchSite],
        help="Research site to use (default: gemini)"
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        default=True,
        help="Show browser window (default: run in headless mode)"
    )
    
    args = parser.parse_args()
    asyncio.run(main(args.query, args.site, args.headless)) 