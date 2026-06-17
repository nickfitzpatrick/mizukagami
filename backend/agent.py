"""The agent harness: LangGraph ReAct loop + scoped tools + system prompt.

Heart of the project (spec §4). Model-agnostic: the model comes from llm.py
(Ollama or Claude). M1 drives this from cli.py; M2 will wrap it in FastAPI.
"""

from __future__ import annotations

# LangChain v1 exposes the agent factory at langchain.agents.create_agent.
# Older installs had it at langgraph.prebuilt.create_react_agent (now
# deprecated). Support both so the project runs across versions.
try:
    from langchain.agents import create_agent as _create_agent

    def _make_agent(model, tools, system_prompt):
        return _create_agent(model, tools, system_prompt=system_prompt)

except ImportError:  # pragma: no cover - fallback for older installs
    from langgraph.prebuilt import create_react_agent as _create_react_agent

    def _make_agent(model, tools, system_prompt):
        return _create_react_agent(model, tools, prompt=system_prompt)

import memory_store
from llm import get_chat_model
from tools.note_tools import TOOLS

SYSTEM_PROMPT = """You are Mizukagami, a personal note assistant and second brain.

Rules:
- For ANY question about the user's notes, call search_notes FIRST. Do not
  answer from memory or guess.
- After searching, read the most relevant note(s) with read_note before
  answering if you need their full content.
- Always cite which note(s) you used, by their id, e.g. "(from
  2026-06-10-embeddings-vs-keyword)".
- Never invent note content. If nothing relevant is found, say so plainly.
- Ask before overwriting an existing note with update_note, unless the user
  clearly asked for the edit.
- Use the remember tool only for durable facts/preferences about the user.
- Be concise and direct."""


def build_agent():
    """Construct the LangGraph ReAct agent with the active model + scoped tools.

    Agent memory is injected into the system prompt at build time so the
    agent carries durable facts across sessions.
    """
    model = get_chat_model()
    system_prompt = SYSTEM_PROMPT + memory_store.format_for_prompt()
    return _make_agent(model, TOOLS, system_prompt)
