"""The agent's scoped toolset, defined with the Agent SDK @tool decorator.

Each tool is a thin wrapper over notes_store / retrieval. Keeping them
small and purpose-built is the tool-scoping practice (spec §4).

Reference API (verify exact import paths against installed claude-agent-sdk):
    from claude_agent_sdk import tool, create_sdk_mcp_server

    @tool("search_notes", "Search the user's notes", {"query": str, "k": int})
    async def search_notes(args):
        hits = retrieval.search(args["query"], args.get("k", 5))
        return {"content": [{"type": "text", "text": render(hits)}]}

    server = create_sdk_mcp_server(name="pia", version="0.1.0",
                                   tools=[search_notes, read_note, ...])
"""

# Implement the six tools from spec §4 at M1/M2:
#   search_notes, read_note, write_note, update_note, list_notes, remember
