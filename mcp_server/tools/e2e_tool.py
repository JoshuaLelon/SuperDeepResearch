"""
e2e_tool.py

End-to-end tool: accepts a query, produces final combined report.
"""

from .plan_tool import generate_plan
from .single_research import gemini_deep_research

async def full_research_pipeline(query: str) -> str:
    """
    Generates a plan, orchestrates research, combines results, optionally uploads sources.
    """
    # Generate research plan
    plan = generate_plan(query)
    
    # Run the async research
    result = await gemini_deep_research(plan)
    return result

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

    