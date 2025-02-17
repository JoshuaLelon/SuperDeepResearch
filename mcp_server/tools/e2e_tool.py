"""
e2e_tool.py

End-to-end tool: accepts a query, produces final combined report.
"""

import asyncio
# from typing import Dict, Any
from .plan_tool import generate_plan
# from .orchestrator import orchestrate
# from .combine_tool import combine_results
# from .upload_tool import upload_to_drive
from .single_research import gemini_deep_research

def full_research_pipeline(query: str) -> str:
    """
    Generates a plan, orchestrates research, combines results, optionally uploads sources.
    """
    plan = generate_plan(query)
    partial = asyncio.run(gemini_deep_research(plan=plan))
    # partials = orchestrate(plan)
    # combined = combine_results(partials)

    # drive_info = None
    # if do_upload:
    #     drive_info = upload_to_drive(combined["sources"])

    # return {
    #     "report": combined["report"],
    #     "sources": combined["sources"],
    #     "driveInfo": drive_info
    # } 
    return partial

    