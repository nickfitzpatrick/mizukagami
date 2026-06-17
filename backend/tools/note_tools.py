"""The agent's scoped toolset, defined with LangChain's @tool decorator.

Each tool is a thin wrapper over notes_store / retrieval / memory_store.
Keeping them small and purpose-built is the tool-scoping practice (spec §4).
The agent is given exactly TOOLS and nothing else — no shell, no raw
filesystem, no web. Tools return strings (what the model reads).
"""

from __future__ import annotations

from langchain_core.tools import tool

import memory_store
import notes_store
import retrieval


@tool
def search_notes(query: str, k: int = 5) -> str:
    """Search the user's notes and return the most relevant ones.

    Use this BEFORE answering any question about the user's notes. Returns
    note ids, titles, and snippets. Read a full note with read_note.
    """
    hits = retrieval.search(query, k)
    if not hits:
        return "No matching notes found."
    lines = [
        f"[{h['note_id']}] {h['title']} (score {h['score']})\n    {h['snippet']}"
        for h in hits
    ]
    return "\n".join(lines)


@tool
def read_note(note_id: str) -> str:
    """Return the full text of one note, given its id."""
    try:
        return notes_store.read_note(note_id)
    except FileNotFoundError:
        return f"No note with id {note_id!r}."


@tool
def write_note(title: str, body: str) -> str:
    """Create a new note with the given title and body. Returns the new id."""
    note_id = notes_store.write_note(title, body)
    return f"Created note {note_id!r}."


@tool
def update_note(note_id: str, body: str) -> str:
    """Replace the body of an existing note. Confirm with the user before
    overwriting unless they clearly asked for the change."""
    try:
        notes_store.update_note(note_id, body)
        return f"Updated note {note_id!r}."
    except FileNotFoundError:
        return f"No note with id {note_id!r}."


@tool
def list_notes(limit: int = 20) -> str:
    """List recent notes (id, title, updated date). No bodies."""
    metas = notes_store.list_notes(limit)
    if not metas:
        return "No notes yet."
    return "\n".join(f"[{m['id']}] {m['title']} (updated {m['updated']})" for m in metas)


@tool
def remember(fact: str) -> str:
    """Store a durable fact or preference about the user for future sessions."""
    memory_store.add_fact(fact)
    return "Noted."


TOOLS = [search_notes, read_note, write_note, update_note, list_notes, remember]
