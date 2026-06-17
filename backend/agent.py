"""The agent harness: LangGraph ReAct loop + scoped tools + system prompt.

Heart of the project (spec §4). Model-agnostic: the model comes from llm.py
and can be Ollama or Claude. M1 drives this from cli.py; M2 wraps it in
FastAPI (app.py).

Reference shape (verify against installed langgraph/langchain):

    from langgraph.prebuilt import create_react_agent
    from llm import get_chat_model
    from tools.note_tools import TOOLS   # list of @tool functions

    SYSTEM_PROMPT = '''You are Mizukagami, a personal note assistant.
    Always use search_notes to retrieve relevant notes before answering
    questions about the user's notes. Cite which notes you used by id.
    Never invent note content. Ask before overwriting a note. Be concise.'''

    def build_agent(agent_memory_facts=None):
        model = get_chat_model()
        prompt = SYSTEM_PROMPT + format_memory(agent_memory_facts or [])
        return create_react_agent(model, TOOLS, prompt=prompt)

    # stream:
    #   agent = build_agent()
    #   for chunk in agent.stream({"messages": [("user", prompt)]}):
    #       ...

Stretch: replace create_react_agent with a hand-built StateGraph to show
node/edge-level understanding of the loop.
"""
