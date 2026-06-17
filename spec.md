# Mizukagami — a local-first AI second brain

Mizukagami (水鏡, "water mirror") is a local-first "second brain" desktop agent. You write notes; it retrieves the *right* notes at the right time and reasons over them. Built on **LangGraph** with a model-agnostic core (local **Ollama** model and the **Claude API**, interchangeable) to demonstrate agent-harness design, well-scoped tools, persistent memory, and retrieval (keyword → embeddings) — the systems concepts that matter for AI Engineering / AI Product roles.

> Portfolio tagline (lead with this; the name alone won't tell a recruiter what it is): **"Mizukagami — a local-first AI second brain that retrieves and reasons over your notes."**

**Status:** spec v0.2 (2026-06-16). Pre-build. (v0.1 targeted the Claude Agent SDK; revised to LangGraph + Ollama for model-agnosticism, deeper harness learning, and lower dev cost — see §4.)
**Owner:** Nick
**Repo folder:** `AI_Projects/PIA/` (product name Mizukagami).

---

## 1. Why this project exists

Two goals, ranked:

1. **Learning.** Understand, by building, what an *agent harness* is (the loop + system prompt + scoped tools), how to give an agent *persistent memory*, and how to get *the right context at the right time* (retrieval). These are the load-bearing concepts in applied AI engineering today.
2. **Portfolio.** Produce a defensible, demoable artifact for AI Product / ML PM / AI Implementation applications. The interview narrative is the deliverable as much as the code.

Non-goals (explicitly out of scope for now): multi-user, cloud sync, mobile, account systems, fine-tuning.

### The interview narrative (write the code to earn these sentences)

- "I built the agent loop on LangGraph and scoped its tools deliberately so the model operates inside a small, safe action space instead of free-form file access."
- "I made the model layer pluggable: the same graph runs against a local Ollama model or the Claude API, so I iterate for free locally and switch to a frontier model for quality. The open-weight piece is a real feature, not a footnote."
- "I shipped keyword retrieval first, built an eval set, measured where it failed on semantically-related notes, then rebuilt retrieval with embeddings + vector search and measured the lift."
- "I gave the agent persistent memory separate from conversation context, and made the human/agent boundary explicit: human-triggered now, background-capable by design."
- "It's a desktop app (Electron shell + Python agent backend), so it embeds in my actual workflow rather than living in a browser tab."

---

## 2. Concepts in plain language (so the spec is self-documenting)

- **Agent harness.** The scaffolding around the model: the loop that lets it call tools and see results, the system prompt that defines its job and constraints, and the set of tools it's allowed to use. With LangGraph we assemble the loop ourselves from a prebuilt ReAct agent (or a hand-built graph), which means we see and control the harness internals rather than having them hidden. Good harness design = tools scoped tightly enough that the model rarely does the wrong thing.
- **Model-agnostic core.** The agent talks to a *model interface*, not a specific vendor. LangGraph lets us pass either a local `ChatOllama` model or a `ChatAnthropic` (Claude API) model into the same graph, interchangeably. We develop against local Ollama (free, private) and switch to Claude for quality. This is the "open-weight model" goal, realized as a runtime choice.
- **Tool scoping.** Instead of handing the agent raw file access, we expose a small set of purpose-built tools (`search_notes`, `read_note`, `write_note`, `list_notes`). Narrow tools make agent behavior predictable, auditable, and safe. This is the single most-cited "good practice" signal in the project.
- **Retrieval.** Given a user question, find the notes worth putting in front of the model.
  - *Keyword (stage 1):* match words. Simple, no infra, misses synonyms/paraphrase.
  - *Embeddings (stage 2):* convert each note and the query into vectors capturing *meaning*; return the nearest. Catches semantic matches keyword search misses. "Embeddings + vector search" is the resume phrase.
- **Persistent memory.** Storage that outlives a single conversation: (a) the notes themselves, (b) a small agent "memory" of durable facts/preferences. Distinct from the SDK *session* (short-term conversation context).
- **The shape of software is changing.** Where the agent runs in your workflow: foreground (you ask), background (it watches/maintains), or scheduled (it digests). v1 is foreground; the architecture leaves a clean seam for background triggers.

---

## 3. Architecture

```
┌─────────────────────────────────────────────┐
│  Electron desktop app  (TypeScript/React)     │  ← product shell, your aesthetic
│  - chat surface, note browser, settings       │
└───────────────┬───────────────────────────────┘
                │  local HTTP / WebSocket (localhost only)
┌───────────────▼───────────────────────────────┐
│  FastAPI backend  (Python)                     │  ← the AI engineering
│  - /chat  (runs the agent loop, streams)       │
│  - /notes (CRUD passthrough)                   │
│  ┌──────────────────────────────────────────┐ │
│  │  Agent harness (LangGraph)                │ │
│  │   create_react_agent(model, tools, prompt)│ │
│  │   model = ChatOllama | ChatAnthropic      │ │
│  │   tools = scoped @tool functions          │ │
│  └──────────┬───────────────────────────────┘ │
│             │ calls scoped tools                │
│  ┌──────────▼───────────────────────────────┐ │
│  │  Note store  (markdown files + index)     │ │
│  │  Retrieval  (stage1 keyword → stage2 vec) │ │
│  │  Agent memory  (durable facts JSON)       │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
          │ model calls (one of:)
          ▼
   ┌─────────────┐     ┌──────────────────┐
   │ Ollama      │     │ Claude API       │
   │ (local, $0) │ or  │ (frontier qual.) │
   └─────────────┘     └──────────────────┘
```

**Why this split:** the hard AI work is pure Python (your preference, and where LangGraph lives). Electron is the desktop shell (the "this is a product" signal, and the right home for background/tray behavior later). They talk over `localhost` only — nothing leaves the machine except, optionally, the Claude API calls.

**Model layer is pluggable, not just abstracted.** `backend/llm.py` returns a LangChain chat model — `ChatOllama` for local/free/private dev, or `ChatAnthropic` for frontier quality — selected by config/env. The *same graph* runs against either. The open-weight goal is therefore a first-class runtime choice from M1, not a deferred swap. Mistral, Llama, etc. are just different Ollama model tags.

---

## 4. The agent harness (the core)

### System prompt (sketch, refined during build)
Defines Mizukagami as a note-retrieval-and-reasoning assistant. Key instructions: always retrieve before answering factual questions about the user's notes; cite which notes it used; never fabricate note content; ask before overwriting an existing note; keep answers concise. Embeds the agent-memory facts at the top each run. In LangGraph this is passed as the `prompt` arg to `create_react_agent` (or the system message in a hand-built graph).

### Scoped tools (LangChain/LangGraph `@tool` decorator)
Deliberately small. The agent gets *these and nothing else* (no shell, no raw file write):

| Tool | Signature (conceptual) | Purpose |
|------|------------------------|---------|
| `search_notes` | `(query: str, k: int=5) -> list[hit]` | Retrieval entry point. Stage 1 keyword; stage 2 vector. Returns note ids + snippets + scores. |
| `read_note` | `(note_id: str) -> str` | Return full text of one note. |
| `write_note` | `(title: str, body: str) -> note_id` | Create a new note. |
| `update_note` | `(note_id: str, body: str) -> ok` | Edit existing note (agent must confirm via system-prompt rule). |
| `list_notes` | `(limit: int=20) -> list[meta]` | Browse recent notes (titles/dates), no bodies. |
| `remember` | `(fact: str) -> ok` | Append a durable fact to agent memory. |

Tools are plain Python functions wrapped in LangChain's `@tool` decorator and passed as the `tools` list to the agent. The agent has **no other tools** — no shell, no filesystem, no web. That closed action space *is* the scoping point, and it's enforced by simply not giving it anything else.

### Loop & streaming
M1 uses LangGraph's prebuilt `create_react_agent(model, tools, prompt)` for the ReAct loop (model is `ChatOllama` or `ChatAnthropic`). Stream via the graph's `.stream()` / `.astream()` to the CLI (M1) and later to the Electron UI over the FastAPI `/chat` endpoint (M2). Tool calls are logged to an audit log for the "here's exactly what the agent did and why" demo. *Stretch:* replace the prebuilt agent with a hand-built `StateGraph` to show you understand the loop at the node/edge level — a strong depth signal if time allows.

### Memory model (three tiers, kept distinct on purpose)
1. **Notes** — the corpus. Markdown files on disk. The thing being retrieved.
2. **Agent memory** — durable facts/preferences the agent chose to keep (`remember` tool), small JSON, injected into the system prompt each run.
3. **Conversation state** — short-term context within a session, held in LangGraph state (and optionally persisted via a LangGraph checkpointer). Ephemeral by comparison.

Articulating these three as separate tiers is itself an interview talking point.

---

## 5. Retrieval — the staged plan

**Stage 1 — keyword.** `search_notes` does case-insensitive token matching across note bodies (simple inverted index or even ripgrep-style scan for a small corpus). Ship the whole app end-to-end on this. Goal: working agent, fast.

**Stage 2 — embeddings.** Replace the guts of `search_notes`:
- On note write/update, compute an embedding for the note (chunk if long) and store the vector.
- On query, embed the query, return nearest vectors by cosine similarity.
- Storage: start with a single local file / SQLite + a vector extension, or a small local vector store. No external service.
- **The tool signature does not change** — only its implementation. Clean seam, and a clean before/after for the writeup.

**Embedding model choice:** decide at stage 2. Options to weigh then: a hosted embedding API (simplest) vs. a local embedding model (on-brand with the open-weight thesis, no per-call cost, more setup). Defer the decision; note it here.

### Evaluation harness (do this — it's the senior-track signal)
A small `eval/` set: ~15–25 questions, each labeled with the note(s) that *should* be retrieved. Metrics: recall@k and a simple "did it surface the right note" hit rate. Run it against stage 1 and stage 2; the delta is the headline result for the portfolio. Keep it dead simple — a JSON of {question, expected_note_ids} and a script that scores `search_notes` output.

---

## 6. Data model

**Note (markdown file + frontmatter):**
```
---
id: 2026-06-16-routemorph-explainability
title: RouteMorph explainability approach
created: 2026-06-16T10:00:00
updated: 2026-06-16T10:00:00
tags: [routemorph, xai]
---
<body markdown>
```
- One file per note under `notes/`. Human-readable, git-friendly, editable outside the app.
- Index (`index/`): for stage 1, an optional keyword index; for stage 2, the vector store. Rebuildable from the notes folder (notes are source of truth).

**Agent memory (`memory/agent_memory.json`):** list of short fact strings + timestamps.

---

## 7. Tech stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Agent framework | LangGraph (`langgraph`, `langchain`) | Model-agnostic; you assemble the loop (learning); 2026 production standard; widest resume recognition. |
| Models | `langchain-ollama` (ChatOllama) + `langchain-anthropic` (ChatAnthropic) | Same graph runs local (free/private) or Claude (frontier). Open-weight goal is native. |
| Local inference | Ollama | Runs open-weight models (Llama/Mistral/etc.) locally at $0/call. See hardware caveat below. |
| Backend | FastAPI + uvicorn | Async, streams cleanly to Electron, minimal. |
| Retrieval s1 | keyword (stdlib / SQLite) | Zero infra. |
| Retrieval s2 | embeddings + local vector store (SQLite-vec or similar) | Local-first, no service dependency. Embeddings can also be Ollama-served. |
| Desktop shell | Electron + React + Vite | Desktop product feel; tray/background path for later; full aesthetic control. |
| Storage | markdown files + JSON + SQLite | Local-first, inspectable, git-friendly. |
| Version control / CI | Git + GitHub + GitHub Actions | See §11. |
| Packaging | electron-builder (later) | Distributable demo. |

**Cost:** LangGraph is free OSS. Ollama inference is $0/call (local). The Claude API is pay-as-you-go and only hit when you select the Claude model — so dev iteration can be entirely free. This is *cheaper* than a Claude-only path where every loop iteration is billed.

**Hardware caveat (the one real constraint):** Ollama runs models on your machine. A small model (~3B–8B, e.g. Llama 3.x 8B) runs on a typical laptop; larger models want more RAM/GPU. If local inference is too slow on your hardware, point the same graph at the Claude API — you lose only the "free local" perk, nothing architectural. Verify your machine's RAM/GPU before committing to a local model size at M1.

---

## 8. Milestones (iterative; each ends shippable)

**M0 — Spec + scaffold.** This doc + repo skeleton + git init. *(in progress)*

**M1 — Agent works in the terminal (keyword), model-agnostic from day one.**
- `notes/` with sample notes. `search_notes`/`read_note`/`write_note`/`list_notes` (keyword), as LangChain `@tool` functions.
- LangGraph `create_react_agent`; `llm.py` returns ChatOllama or ChatAnthropic by env. Talk to it via a CLI. No UI, no FastAPI yet.
- Exit criteria: ask a question, agent retrieves a note and answers citing it; write a note via the agent; same run works against both a local Ollama model and Claude by flipping one env var.

**M2 — Backend + eval set.**
- Wrap the agent in FastAPI (`/chat` streaming, `/notes` CRUD). `remember` tool + agent memory.
- Build `eval/` set; run it; record stage-1 recall@k baseline.
- Exit criteria: hit the API with curl and get a streamed, cited answer; baseline eval numbers committed.

**M3 — Embeddings retrieval.**
- Swap `search_notes` internals to embeddings + local vector store; index on write.
- Re-run eval; record stage-2 numbers; write the before/after up in `docs/`.
- Exit criteria: measurable retrieval improvement on the eval set, documented.

**M4 — Electron UI (your aesthetic).**
- Electron shell, chat surface, note browser, settings. Talks to FastAPI over localhost.
- Exit criteria: end-to-end desktop app you actually use.

**M5 — Polish + portfolio.**
- Audit-log viewer (shows tool calls), README with architecture diagram + eval results, short demo GIF/video, writeup. Model-comparison note: how the local vs. Claude model differed in quality on the same tasks (good content).
- *Stretch:* background/scheduled mode (tray app that digests new notes); hand-built `StateGraph` to replace the prebuilt ReAct agent.

---

## 9. Open decisions (resolve as we hit them)

- Local model + size at M1 (depends on your hardware — check RAM/GPU first).
- Embedding model: Ollama-served vs. hosted (decide at M3).
- Vector store: SQLite-vec vs. alternative (decide at M3, verify current options).
- Chunking strategy for long notes (decide at M3).
- Electron aesthetic direction (decide at M4 — bring references).
- Whether to add tags/links as retrieval signals (post-M3, optional).

## 10. Risks

- **Scope creep via UI.** Mitigation: M1–M3 prove the AI before any pixels (backend-first).
- **Electron/Python two-language overhead.** Mitigation: keep the boundary tiny (HTTP, a few endpoints); Python owns all logic.
- **Eval set too small to be meaningful.** Mitigation: keep it honest about n; it's a learning instrument, not a benchmark claim.
- **Local model quality.** Small Ollama models may handle tool-calling worse than Claude. Mitigation: model-agnostic core means you fall back to Claude for quality; the *difference* is itself portfolio content.

---

## 11. Version control & GitHub (portfolio surface)

The repo *is* the portfolio artifact. Priorities, highest signal-per-effort first:

1. **Polished public README (the thing recruiters actually see).** One-line description + tagline, architecture diagram, the **eval before/after numbers**, a short demo GIF, and a "what I learned" section. A reviewer spends ~30 seconds on the repo page; this is where it's won.
2. **GitHub Actions CI running the eval harness + tests on push.** Most portfolio projects have no tests and no CI; a green "passing" check is a strong, cheap AI-engineering signal and makes the eval harness continuously enforced. Workflow at `.github/workflows/eval.yml`. (CI runs keyword-stage eval and unit tests; it does *not* call paid model APIs or Ollama — keep CI hermetic.)
3. **Frequent, meaningful commits (one per milestone / sub-step).** Less about impressing anyone, more about rebuilding Git muscle memory and keeping a readable history. Convention: `M1: implement keyword search_notes tool`, `M3: swap retrieval to embeddings`, etc.

**Conventions** (in `CONTRIBUTING.md`): imperative commit subjects prefixed with the milestone; never commit secrets (`.env` is gitignored); never commit generated indexes or `agent_memory.json`.

**Pushing to GitHub (you do this — I can't auth to your account):**
```bash
# after creating an empty repo named "mizukagami" on github.com
cd PIA
git remote add origin git@github.com:<you>/mizukagami.git
git branch -M main
git push -u origin main
```
Deferred: GitHub connector (lets future sessions read issues/PRs/commits). Not needed for the portfolio; add later if useful.
