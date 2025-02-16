"""
plan_tool.py

Generates a structured research plan given a query.
"""

from typing import Dict, Any, List

def generate_plan(query: str) -> Dict[str, Any]:
    """
    Use query text to derive a step-by-step plan of research tasks.
    """
    # Example of a plan: which products to query, how to parse them, etc.
    plan = {
        "query": query,
        "steps": [
            {"product": "gemini", "search_terms": [query]},
            {"product": "perplexity", "search_terms": [query]},
            {"product": "custom", "search_terms": [query]},
        ]
    }
    return plan 