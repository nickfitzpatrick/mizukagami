"""The agent's scoped toolset, defined with LangChain's @tool decorator.

Each tool is a thin wrapper over notes_store / retrieval. Keeping them
small and purpose-built is the tool-scoping practice (spec §4). The agent
is given THIS LIST AND NOTHING ELSE — no shell, no filesystem, no web.

Reference shape (verify against installed langchain):

    from langchain_core.tools import tool
    import retrieval, notes_store

    @tool
    def search_notes(query: str, k: int = 5) -> str:
        '''Search the user's notes for the most relevant ones.'''
        hits = retrieval.search(query, k)
        return render(hits)   # note ids + snippets + scores as text

    # ... read_note, write_note, update_note, list_notes, remember

    TOOLS = [search_notes, read_note, write_note, update_note,
             list_notes, remember]
"""

# Implement the six tools from spec §4 at M1/M2 and export TOOLS.
TOOLS: list = []  # populated at M1
