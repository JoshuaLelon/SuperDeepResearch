# Documentation

This folder contains:

- **Diagrams** explaining major system flows, sequences, and states.  
- Additional technical references that help illustrate how queries flow from the user into the system and how results move back out.

## Subdirectories

- `diagrams/`:
  - `state.md`  
    Mermaid diagram showing high-level state transitions in the pipeline.
  - `sequence.md`  
    Sequence diagram showing how data flows between user, MCP server, plan tool, orchestration, etc.
  - `flow.md`  
    Flow diagram offering a visual representation of the end-to-end process.

## Generating or Viewing Diagrams

Multiple approaches:

- Open `*.md` with a Mermaid-compatible viewer or use an online Mermaid renderer.
- Copy diagram content into a local or web-based Mermaid preview tool.

## Further References

- [mcp_server/README.md](../mcp_server/README.md) to understand how the server lifecycle and tools fit together.
- [../README.md](../README.md) for an overall project overview.