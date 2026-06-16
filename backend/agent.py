"""The agent harness: system prompt + scoped tools + the Agent SDK loop.

This is the heart of the project (spec §4). At M1 it is driven by cli.py;
at M2 it is wrapped by FastAPI in app.py.

Reference shape (verify against installed claude-agent-sdk):

    from claude_agent_sdk import query, ClaudeAgentOptions
    from tools.note_tools import server  # in-process MCP with scoped tools

    SYSTEM_PROMPT = '''You are PIA, a personal note assistant.
    Always retrieve relevant notes (search_notes) before answering questions
    about the user's notes. Cite which notes you used. Never invent note
    content. Ask before overwriting a note. Be concise.'''

    async def run(prompt, agent_memory_facts):
        options = ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT + format_memory(agent_memory_facts),
            allowed_tools=[
                "mcp__pia__search_notes", "mcp__pia__read_note",
                "mcp__pia__write_note", "mcp__pia__update_note",
                "mcp__pia__list_notes", "mcp__pia__remember",
            ],  # note: NO built-in Bash/Write/Read — scoping is the point
            mcp_servers={"pia": server},
        )
        async for message in query(prompt=prompt, options=options):
            yield message
"""
