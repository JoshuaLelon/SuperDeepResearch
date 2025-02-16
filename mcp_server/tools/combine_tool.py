"""
combine_tool.py

Combines multiple partial research results into a single report.
"""

from typing import List, Dict, Any

def combine_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple product outputs into a single report with collected sources.
    """
    combined_text = []
    combined_sources = []
    for item in results:
        combined_text.append(str(item["results"]))
        combined_sources.append(f"Source: {item['product']}")
    return {
        "report": "\n\n".join(combined_text),
        "sources": combined_sources
    } 