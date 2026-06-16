# PIA — Personal Intelligent Application

A local-first "second brain" desktop agent built on the Claude Agent SDK. You write notes; PIA retrieves the *right* ones at the right time and reasons over them.

See [`spec.md`](./spec.md) for the full design, rationale, and milestones.

## Status
Pre-build. M0 (spec + scaffold) complete.

## Layout
```
backend/    Python: FastAPI + the agent harness + retrieval (the AI engineering)
  tools/    Scoped custom tools the agent is allowed to call
electron/   Desktop shell (TypeScript/React) — added at M4
notes/      The note corpus (markdown, source of truth)
index/      Retrieval index / vector store (rebuildable from notes/)
memory/     Durable agent memory (facts/preferences)
eval/       Retrieval evaluation set + scoring (the senior-track signal)
docs/       Writeups, architecture diagram, eval before/after
```

## Quickstart (M1, once implemented)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...      # see spec §7 cost note
python cli.py                     # talk to the agent in the terminal
```

## Design principles
- Tools are tightly scoped (no raw file/shell access for the agent).
- Notes are the source of truth; the index is rebuildable.
- Model access is abstracted (`backend/llm.py`) so the model is swappable.
- Backend-first: the AI works and is evaluated before any UI is built.
