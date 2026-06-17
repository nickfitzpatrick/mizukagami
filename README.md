# Mizukagami — a local-first AI second brain

A local-first "second brain" desktop agent that retrieves and reasons over your notes. You write notes; Mizukagami (水鏡, "water mirror") retrieves the *right* ones at the right time and answers, citing what it used.

Built on **LangGraph** with a model-agnostic core: the same agent runs against a local **Ollama** model (free, private) or the **Claude API** (frontier quality), interchangeably.

See [`spec.md`](./spec.md) for the full design, rationale, and milestones.

## Status
M2 complete: keyword agent + FastAPI backend (streaming `/chat`, `/notes` CRUD), model-agnostic (Ollama or Claude), 18-item retrieval eval, 9 passing tests.

Keyword-stage retrieval baseline (hit_rate@1, n=18): overall 0.89, direct 1.00, paraphrase 0.75. The paraphrase gap is what M3 embeddings will close.

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

### Backend API (M2)
```bash
cd backend && source .venv/bin/activate
uvicorn app:app --reload --port 8000
```
Endpoints (localhost only):
- `POST /chat` `{"message": "..."}` — streams Server-Sent Events: `tool_call`, `answer`, `done`.
- `GET /notes?limit=20` — recent note metadata.
- `GET /notes/{id}` — one note's body.
- `POST /notes` `{"title","body"}` — create a note.

Quick check:
```bash
curl -N -X POST localhost:8000/chat -H 'content-type: application/json' \
  -d '{"message":"what did I note about RouteMorph explainability?"}'
curl localhost:8000/notes
```

### Tests & eval
Requires Python 3.10+ (3.12 recommended). Tests need the dev deps:
```bash
cd backend
pip install -r requirements-dev.txt        # app deps + pytest
python -m pytest -q                         # 9 tests (retrieval + API)
cd ../eval && python run_eval.py           # keyword-stage retrieval metrics (hit_rate@1)
```
Current keyword-stage baseline (hit_rate@1, n=18): overall 0.89, direct 1.00,
paraphrase 0.75 — the baseline M3 embeddings will be measured against.

## Design principles
- Tools are tightly scoped (no shell, no raw filesystem, no web for the agent).
- Model layer is pluggable (`backend/llm.py`): Ollama or Claude, same graph.
- Notes are the source of truth; the index is rebuildable.
- Backend-first: the AI works and is *evaluated* before any UI is built.

## Version control
Git + GitHub, CI via GitHub Actions ([`.github/workflows/eval.yml`](./.github/workflows/eval.yml)). See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for commit conventions. README will carry the architecture diagram, eval before/after numbers, and a demo GIF at M5 — that's the portfolio surface.
