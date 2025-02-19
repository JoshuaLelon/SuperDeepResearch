# Documentation

This folder contains technical documentation and diagrams explaining the system architecture and workflows.

## Diagrams

### System Architecture

- `diagrams/state.md`  
  Mermaid diagram showing high-level state transitions in the pipeline.
- `diagrams/sequence.md`  
  Sequence diagram showing how data flows between user, MCP server, plan tool, orchestration, etc.
- `diagrams/flow.md`  
  Flow diagram offering a visual representation of the end-to-end process.

### Workflow Diagrams

#### Testing Workflow

```mermaid
graph TD
    A[Start] --> B{Choose Browser Approach}
    B -->|Patchright| C1[Test Patchright]
    B -->|NoDriver| C2[Test NoDriver]
    B -->|Browser-use| C3[Test Browser-use]
    
    C1 --> D{Choose Research Site}
    C2 --> D
    C3 --> D
    
    D -->|Gemini| E1[Configure Auth]
    D -->|Perplexity| E2[No Auth Needed]
    
    E1 --> F[Execute Research]
    E2 --> F
    
    F --> G[Get Results]
    G --> H[End]
```

#### MCP Server Workflow

```mermaid
graph TD
    A[Start Server] --> B[Register Tools]
    B --> C[Wait for Requests]
    
    C --> D{Receive Request}
    D -->|Research Query| E[Parse Parameters]
    
    E --> F{Choose Site}
    F -->|Gemini| G1[Auth Flow]
    F -->|Perplexity| G2[Direct Access]
    
    G1 --> H[Execute Research]
    G2 --> H
    
    H --> I[Return Results]
    I --> C
```

## Generating or Viewing Diagrams

Multiple approaches:
- Open `*.md` with a Mermaid-compatible viewer or use an online Mermaid renderer.
- Copy diagram content into a local or web-based Mermaid preview tool.

## Technical Details

### Research Engine Flow

```mermaid
graph LR
    A[Query] --> B[Research Engine]
    B --> C{Browser Approach}
    C -->|Browser-use| D1[Browser-use Driver]
    C -->|NoDriver| D2[NoDriver Driver]
    C -->|Patchright| D3[Patchright Driver]
    
    D1 --> E{Research Site}
    D2 --> E
    D3 --> E
    
    E -->|Gemini| F1[Gemini Scraper]
    E -->|Perplexity| F2[Perplexity Scraper]
    
    F1 --> G[Results]
    F2 --> G
```

### Authentication Flow

```mermaid
graph TD
    A[Start] --> B{Site Requires Auth?}
    B -->|Yes| C[Load Credentials]
    B -->|No| G[Skip Auth]
    
    C --> D[Navigate to Login]
    D --> E[Enter Credentials]
    E --> F{2FA Enabled?}
    
    F -->|Yes| H[Handle 2FA]
    F -->|No| I[Complete Login]
    
    H --> I
    I --> J[Verify Success]
    G --> J
    
    J --> K[End]
```

## Further References

- [mcp_server/README.md](../mcp_server/README.md) to understand how the server lifecycle and tools fit together.
- [../README.md](../README.md) for an overall project overview.
- [../scripts/README.md](../scripts/README.md) for test script usage.