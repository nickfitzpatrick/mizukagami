# Mizukagami — a local-first AI second brain

A local-first "second brain" desktop agent that retrieves and reasons over your notes. You write notes; Mizukagami (水鏡, "water mirror") retrieves the *right* ones at the right time and answers, citing what it used.

Built on **LangGraph** with a model-agnostic core: the same agent runs against a local **Ollama** model (free, private) or the **Claude API** (frontier quality), interchangeably.

See [`spec.md`](./spec.md) for the full design, rationale, and milestones.

## Status
M1 complete: working keyword agent you can talk to in the terminal, model-agnostic (Ollama or Claude). Tests + retrieval eval pass.

> Note: folder is `PIA/` (the original "Personal Intelligent Application" working title); product name is **Mizukagami**.

## Why this project
Demonstrates the systems concepts behind applied AI engineering: deliberate **agent-harness** design, **tightly scoped tools**, **persistent memory**, a **model-agnostic** core (open-weight + frontier), and **retrieval** built and *measured* in two stages (keyword → embeddings) with an eval harness.

## Layout
```
backend/    Python: LangGraph agent + retrieval + FastAPI (the AI engineering)
  tools/    Scoped @tool functions the agent is allowed to call
electron/   Desktop shell (TypeScript/React) — added at M4
notes/      The note corpus (markdown, source of truth)
index/      Retrieval index / vector store (rebuildable from notes/)
memory/     Durable agent memory (facts/preferences)
eval/       Retrieval evaluation set + scoring (the senior-track signal)
docs/       Writeups, architecture diagram, eval before/after
.github/    CI: runs tests + keyword-stage eval on push
```

## Quickstart (M1)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env        # then edit

# Option A — local & free (needs Ollama running + a model pulled):
ollama pull llama3.1:8b          # ~5GB; wants ~8GB+ free RAM
MIZUKAGAMI_MODEL_PROVIDER=ollama python cli.py

# Option B — frontier quality (Claude API):
#   put ANTHROPIC_API_KEY in .env, then:
MIZUKAGAMI_MODEL_PROVIDER=anthropic python cli.py
```
Try: `what did I note about RouteMorph's explainability?` — the agent should
call `search_notes`, then answer citing the note id.

### Tests & eval
```bash
cd backend && python -m pytest -q          # unit tests
cd ../eval && python run_eval.py           # keyword-stage retrieval metrics
```
Current keyword-stage baseline (n=3): hit_rate@5 = 1.00, recall@5 = 1.00.
This number is the baseline the M3 embeddings work will be compared against.

## Design principles
- Tools are tightly scoped (no shell, no raw filesystem, no web for the agent).
- Model layer is pluggable (`backend/llm.py`): Ollama or Claude, same graph.
- Notes are the source of truth; the index is rebuildable.
- Backend-first: the AI works and is *evaluated* before any UI is built.

## Version control
Git + GitHub, CI via GitHub Actions ([`.github/workflows/eval.yml`](./.github/workflows/eval.yml)). See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for commit conventions. README will carry the architecture diagram, eval before/after numbers, and a demo GIF at M5 — that's the portfolio surface.
