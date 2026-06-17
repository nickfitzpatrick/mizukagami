"""Agent memory: durable facts the agent chose to keep (spec §4, tier 2).

A small JSON list, distinct from the note corpus and from conversation
state. Injected into the system prompt each run so the agent carries
preferences/facts across sessions.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

MEMORY_FILE = Path(__file__).resolve().parent.parent / "memory" / "agent_memory.json"


def load_facts() -> list[dict]:
    if not MEMORY_FILE.exists():
        return []
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def add_fact(fact: str) -> bool:
    MEMORY_FILE.parent.mkdir(exist_ok=True)
    facts = load_facts()
    facts.append({"fact": fact, "added": datetime.now().replace(microsecond=0).isoformat()})
    MEMORY_FILE.write_text(json.dumps(facts, indent=2), encoding="utf-8")
    return True


def format_for_prompt() -> str:
    facts = load_facts()
    if not facts:
        return ""
    lines = "\n".join(f"- {f['fact']}" for f in facts)
    return f"\n\nThings you remember about the user:\n{lines}"
