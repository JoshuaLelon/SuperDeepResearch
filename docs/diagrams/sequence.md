sequenceDiagram
    participant User
    participant MCPServer
    participant PlanTool
    participant Orchestrator
    participant BrowserAutomation
    participant CombineTool
    participant UploadTool

    User->>MCPServer: send query
    MCPServer->>PlanTool: create plan(query)
    PlanTool-->>MCPServer: return plan
    MCPServer->>Orchestrator: orchestrate(plan)
    loop For each product
        Orchestrator->>BrowserAutomation: gatherResearch(planStep)
        BrowserAutomation-->>Orchestrator: return partial report
    end
    Orchestrator-->>MCPServer: all product results
    MCPServer->>CombineTool: combine(all results)
    CombineTool-->>MCPServer: final report + sources
    MCPServer->>UploadTool: upload(sources)
    UploadTool-->>MCPServer: GDrive links
    MCPServer-->>User: final big report + drive links 