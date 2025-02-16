"""
orchestrator.py

Coordinates multi-product research based on a plan.
"""

from typing import Dict, Any, List
from .single_research import single_product_research

def orchestrate(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Loops through plan steps, performs single product research, collects results.
    """
    results = []
    for step in plan.get("steps", []):
        product = step["product"]
        terms = step["search_terms"]
        partial = single_product_research(product=product, terms=terms)
        results.append({
            "product": product,
            "results": partial
        })
    return results 