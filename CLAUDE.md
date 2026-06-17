# Mizukagami — project context for AI assistants

Read this first when working on this repo. It captures state and decisions
not obvious from the code alone.

## What this is
Mizukagami (水鏡, "water mirror") — a local-first AI "second brain": a desktop
agent that retrieves and reasons over the user's markdown notes. Nick's first
AI-engineering portfolio project (targeting AI Product / ML PM / AI
Implementation roles). GitHub: github.com/nickfitzpatrick/mizukagami.

## Architecture (and why)
- **LangGraph** agent harness — chosen over the Claude Agent SDK for
  model-agnosticism, deeper "build the loop yourself" learning, and lower dev
  cost. Uses the current `langchain.agents.create_agent` API (NOT the
  deprecated `langgraph.prebuilt.create_react_agent`).
- **Model-agnostic core** (`backend/llm.py`): same graph runs on local
  **Ollama** (`ChatOllama`) or **Claude** (`ChatAnthropic`), switched by
  `MIZUKAGAMI_MODEL_PROVIDER` env (`ollama` default, or `anthropic`).
- **Scoped tools only** (`backend/tools/note_tools.py`): search_notes,
  read_note, write_note, update_note, list_notes, remember. No shell, no raw
  filesystem, no web. That closed action space is the point.
- **Notes** = markdown + frontmatter under `notes/`, source of truth.
  Retrieval index is rebuildable from them.
- **Three memory tiers**: notes (corpus) / agent memory
  (`memory/agent_memory.json`, durable facts) / conversation state (LangGraph).
- **Retrieval is staged**: M1 keyword (done) → M3 embeddings+vector. The
  `retrieval.search(query, k)` signature is stable across stages; only the
  implementation changes. An eval harness measures the lift.

## Status
- **M0** done: spec + scaffold.
- **M1** done: keyword agent, CLI, model-agnostic, verified on local Llama
  3.1 8B (Nick's M5 Mac, 16GB RAM).
- **M2** done: FastAPI backend (`backend/app.py`) — streaming `POST /chat`
  (SSE), `GET /notes`, `GET /notes/{id}`, `POST /notes`. Corpus grown to 13
  notes (Nick's real domains). Eval grown to 18 items with direct/paraphrase
  split, scored at hit_rate@1.
- **Next: M3** — swap `retrieval.search` internals to embeddings + a local
  vector store (Ollama-served embeddings or hosted; SQLite-vec or similar —
  decide at M3). Re-run eval, document before/after. Then M4 (Electron UI),
  M5 (polish/portfolio).

## Keyword baseline to beat (hit_rate@1, n=18)
overall 0.89 · direct 1.00 · paraphrase 0.75. M3's job: lift the paraphrase
number with semantic retrieval.

## Conventions
- **Python 3.12** (3.9 is too old — modern LangChain needs 3.10+).
- Commit per milestone: `M3: swap retrieval to embeddings ...`. Push to
  `origin/main`. CI (`.github/workflows/eval.yml`) runs tests + keyword eval,
  hermetic (no model calls).
- Verify current library APIs by search before coding (training cutoffs lag).
- Apply the **karpathy-guidelines** skill throughout; use **ponytail** as a
  review pass for bloat (but this is a learning/portfolio project — don't
  over-minimize to the point of underselling competence).
- Code runs on Nick's machine, not in the assistant sandbox — deliver code +
  exact run commands; Nick runs and reports back.

## Run it
```bash
cd backend && python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q                 # 9 tests
cd ../eval && python run_eval.py    # keyword eval
# agent CLI:  MIZUKAGAMI_MODEL_PROVIDER=ollama python ../backend/cli.py
# API:        uvicorn app:app --reload --port 8000   (from backend/)
# Ollama:     brew services start ollama && ollama pull llama3.1:8b
```
