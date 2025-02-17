"""
plan_tool.py

Generates a structured research plan given a query.
"""

# from typing import Dict, Any, List

def generate_plan(query: str) -> str:
    """
    Use query text to derive a step-by-step plan of research tasks.
    """
    print(f"Generating plan for query: {query}. currently returning dummy plan.")

    return """
    Step 1: research all the different types of roses
    Step 2: pick the best one
    Step 3: find out how many thorns are on the best one on average
    """