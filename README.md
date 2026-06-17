# Mizukagami — a local-first AI second brain

A local-first "second brain" desktop agent that retrieves and reasons over your notes. You write notes; Mizukagami (水鏡, "water mirror") retrieves the *right* ones at the right time and answers, citing what it used.

Built on **LangGraph** with a model-agnostic core: the same agent runs against a local **Ollama** model (free, private) or the **Claude API** (frontier quality), interchangeably.

See [`spec.md`](./spec.md) for the full design, rationale, and milestones.

## Status
M3 complete: retrieval upgraded from keyword to **embeddings** (MiniLM + NumPy cosine) behind an unchanged `search(query, k)` seam, measured against the keyword baseline. Plus (from M1–M2) the LangGraph agent, scoped tools, FastAPI backend (streaming `/chat`, `/notes` CRUD), model-agnostic core (Ollama or Claude), and a 25-item retrieval eval. 12 passing tests.

### Retrieval eval: keyword → embeddings (hit_rate@1, n=25)

| split | keyword | embeddings | delta |
|-------|:-------:|:----------:|:-----:|
| overall (n=25)    | 0.52 | _TBD_ | _TBD_ |
| direct (n=12)     | 1.00 | _TBD_ | _TBD_ |
| paraphrase (n=13) | 0.08 | _TBD_ | _TBD_ |

The headline is the **paraphrase split**: 13 questions reworded to share at most one token with their target note (enforced by [`eval/check_overlap.py`](./eval/check_overlap.py), so the test can't drift easy). Keyword search has nothing to match on there and scores 0.08; embeddings match on meaning. Full writeup and method: [`docs/retrieval-eval.md`](./docs/retrieval-eval.md). (Honest caveat: n=13 is a learning instrument, not a benchmark — the *method* is the point.)

> Embeddings column is `TBD` pending a local re-run (`python eval/run_eval.py --k 1`) — the dev sandbox has no torch. Paste the output into the table and `docs/retrieval-eval.md`.

> Note: folder is `PIA/` (the original "Personal Intelligent Application" working title); product name is **Mizukagami**.

## Why this project
Demonstrates the systems concepts behind applied AI engineering: deliberate **agent-harness** design, **tightly scoped tools**, **persistent memory**, a **model-agnostic** core (open-weight + frontier), and **retrieval** built and *measured* in two stages (keyword → embeddings) with an eval harness.

## Architecture
```
  Electron desktop shell  (M4 — TypeScript/React)
        │  localhost HTTP / SSE
  ┌─────▼─────────────────────────────────────────┐
  │  FastAPI backend  (Python — the AI engineering)│
  │   /chat  (runs agent loop, streams)            │
  │   /notes (CRUD)                                │
  │  ┌──────────────────────────────────────────┐  │
  │  │ LangGraph agent  (create_agent loop)      │  │
  │  │   model = ChatOllama | ChatAnthropic ─────┼──┼──▶ Ollama (local, $0)
  │  │   tools = scoped @tool fns (no shell/fs)  │  │   or Claude API
  │  └────────────────┬─────────────────────────┘  │
  │   ┌───────────────▼──────────────────────────┐ │
  │   │ Notes (markdown, source of truth)         │ │
  │   │ Retrieval: keyword → embeddings (MiniLM)  │ │
  │   │ Agent memory (durable facts JSON)         │ │
  │   └───────────────────────────────────────────┘ │
  └─────────────────────────────────────────────────┘
```
Model layer is pluggable, not just abstracted: the *same graph* runs local or frontier, picked by one env var. Retrieval swapped implementations (keyword → embeddings) behind a fixed signature, so the eval compares both with identical calls.

## Layout
```
backend/    Python: LangGraph agent + retrieval + FastAPI (the AI engineering)
  tools/    Scoped @tool functions the agent is allowed to call
electron/   Desktop shell (TypeScript/React) — added at M4
notes/      The note corpus (markdown, source of truth)
index/      Embedding cache (embeddings.npz, gitignored, rebuilt from notes/)
memory/     Durable agent memory (facts/preferences)
eval/       Retrieval evaluation set + scoring (the senior-track signal)
docs/       Writeups, architecture diagram, eval before/after
.github/    CI: runs tests + retrieval eval (both stages) on push
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
Requires Python 3.10+ (tested through 3.14). The eval's embedding stage pulls
`sentence-transformers` + `torch` and downloads MiniLM (~90MB) on first run.
```bash
cd backend
pip install -r requirements-dev.txt        # app deps + pytest + embeddings
python -m pytest -q                         # 12 tests (keyword + embeddings + API)
cd ../eval && python run_eval.py --k 1     # prints keyword vs embeddings + delta
```
See the before/after table above, or [`docs/retrieval-eval.md`](./docs/retrieval-eval.md) for the full method and caveats.

## Design principles
- Tools are tightly scoped (no shell, no raw filesystem, no web for the agent).
- Model layer is pluggable (`backend/llm.py`): Ollama or Claude, same graph.
- Notes are the source of truth; the index is rebuildable.
- Backend-first: the AI works and is *evaluated* before any UI is built.

## Version control
Git + GitHub, CI via GitHub Actions ([`.github/workflows/eval.yml`](./.github/workflows/eval.yml)). See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for commit conventions. Architecture diagram and eval before/after numbers are above; a demo GIF lands at M5 once the Electron UI exists.
