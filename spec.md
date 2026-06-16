# PIA — Personal Intelligent Application

A local-first "second brain" desktop agent. You write notes; it retrieves the *right* notes at the right time and reasons over them. Built on the Anthropic Claude Agent SDK to demonstrate agent-harness design, well-scoped tools, persistent memory, and retrieval (keyword → embeddings) — the systems concepts that matter for AI Engineering / AI Product roles.

**Status:** spec v0.1 (2026-06-16). Pre-build.
**Owner:** Nick
**Product name (working):** PIA. Alt names to consider later: "Recall", "Marginalia", "Cortex".

---

## 1. Why this project exists

Two goals, ranked:

1. **Learning.** Understand, by building, what an *agent harness* is (the loop + system prompt + scoped tools), how to give an agent *persistent memory*, and how to get *the right context at the right time* (retrieval). These are the load-bearing concepts in applied AI engineering today.
2. **Portfolio.** Produce a defensible, demoable artifact for AI Product / ML PM / AI Implementation applications. The interview narrative is the deliverable as much as the code.

Non-goals (explicitly out of scope for now): multi-user, cloud sync, mobile, account systems, fine-tuning.

### The interview narrative (write the code to earn these sentences)

- "I built the agent on the Claude Agent SDK and scoped its tools deliberately so the model operates inside a small, safe action space instead of free-form file access."
- "I shipped keyword retrieval first, built an eval set, measured where it failed on semantically-related notes, then rebuilt retrieval with embeddings + vector search and measured the lift."
- "I gave the agent persistent memory separate from conversation context, and made the human/agent boundary explicit: human-triggered now, background-capable by design."
- "It's a desktop app (Electron shell + Python agent backend), so it embeds in my actual workflow rather than living in a browser tab."

---

## 2. Concepts in plain language (so the spec is self-documenting)

- **Agent harness.** The scaffolding around the model: the loop that lets it call tools and see results, the system prompt that defines its job and constraints, and the set of tools it's allowed to use. The Agent SDK provides the loop; *we* design the prompt and tools. Good harness design = tools scoped tightly enough that the model rarely does the wrong thing.
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
│  │  Agent harness (claude-agent-sdk)         │ │
│  │   query() + ClaudeAgentOptions            │ │
│  │   system prompt + allowed_tools           │ │
│  │   custom tools via @tool / in-proc MCP    │ │
│  └──────────┬───────────────────────────────┘ │
│             │ calls scoped tools                │
│  ┌──────────▼───────────────────────────────┐ │
│  │  Note store  (markdown files + index)     │ │
│  │  Retrieval  (stage1 keyword → stage2 vec) │ │
│  │  Agent memory  (durable facts JSON)       │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

**Why this split:** the hard AI work is pure Python (your preference, and where the SDK lives). Electron is the desktop shell (the "this is a product" signal, and the right home for background/tray behavior later). They talk over `localhost` only — nothing leaves the machine except the Claude API calls themselves.

**Model layer is abstracted.** All model calls go through one module (`backend/llm.py`). v1 uses the Claude API via the Agent SDK. The friend's open-weight idea (Ollama/Mistral) becomes a *later, optional* swap behind this interface — a portfolio talking point, not a v1 dependency.

---

## 4. The agent harness (the core)

### System prompt (sketch, refined during build)
Defines PIA as a note-retrieval-and-reasoning assistant. Key instructions: always retrieve before answering factual questions about the user's notes; cite which notes it used; never fabricate note content; ask before overwriting an existing note; keep answers concise. Embeds the agent-memory facts at the top each run.

### Scoped tools (custom, via `@tool` + `create_sdk_mcp_server`)
Deliberately small. The agent gets *these and nothing else* (no raw `Bash`/`Write`):

| Tool | Signature (conceptual) | Purpose |
|------|------------------------|---------|
| `search_notes` | `(query: str, k: int=5) -> list[hit]` | Retrieval entry point. Stage 1 keyword; stage 2 vector. Returns note ids + snippets + scores. |
| `read_note` | `(note_id: str) -> str` | Return full text of one note. |
| `write_note` | `(title: str, body: str) -> note_id` | Create a new note. |
| `update_note` | `(note_id: str, body: str) -> ok` | Edit existing note (agent must confirm via system-prompt rule). |
| `list_notes` | `(limit: int=20) -> list[meta]` | Browse recent notes (titles/dates), no bodies. |
| `remember` | `(fact: str) -> ok` | Append a durable fact to agent memory. |

Tools are exposed as an in-process MCP server; referenced in `allowed_tools` as `mcp__pia__search_notes`, etc. **No built-in file/shell tools are allowed** — that's the scoping point.

### Loop & streaming
Backend calls `query(prompt=..., options=ClaudeAgentOptions(system_prompt=..., allowed_tools=[...], mcp_servers={"pia": server}))` and streams messages to the Electron UI. A `PreToolUse` hook logs every tool call to an audit log (good demo: "here's exactly what the agent did and why").

### Memory model (three tiers, kept distinct on purpose)
1. **Notes** — the corpus. Markdown files on disk. The thing being retrieved.
2. **Agent memory** — durable facts/preferences the agent chose to keep (`remember` tool), small JSON, injected into the system prompt each run.
3. **Session** — short-term conversation context, handled by the SDK (`resume`/session id). Ephemeral by comparison.

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
| Agent | `claude-agent-sdk` (Python) | Provides the loop, tool execution, hooks, sessions, in-process custom tools. Industry-current. |
| Backend | FastAPI + uvicorn | Async, streams cleanly to Electron, minimal. |
| Model access | Claude API via SDK (abstracted in `llm.py`) | v1 simplest path; open-weight swap later behind the interface. |
| Retrieval s1 | keyword (stdlib / SQLite) | Zero infra. |
| Retrieval s2 | embeddings + local vector store (SQLite-vec or similar) | Local-first, no service dependency. |
| Desktop shell | Electron + React + Vite | Desktop product feel; tray/background path for later; full aesthetic control. |
| Storage | markdown files + JSON + SQLite | Local-first, inspectable, git-friendly. |
| Packaging | electron-builder (later) | Distributable demo. |

**Cost note (verify before building):** as of 2026-06-15, Agent SDK usage on Claude subscription plans draws from a separate monthly Agent SDK credit (Pro $20 / Max tiers higher). For development, a pay-as-you-go API key is the cleanest. Confirm current pricing at build time.

---

## 8. Milestones (iterative; each ends shippable)

**M0 — Spec + scaffold.** This doc + repo skeleton + git init. *(in progress)*

**M1 — Agent works in the terminal (keyword).**
- `notes/` with sample notes. `search_notes`/`read_note`/`write_note`/`list_notes` (keyword).
- Agent harness in Python; talk to it via a CLI. No UI, no FastAPI yet.
- Exit criteria: ask a question, agent retrieves a note and answers citing it; write a note via the agent.

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
- Audit-log viewer (shows tool calls), README with architecture diagram + eval results, short demo GIF/video, writeup.
- *Stretch:* background/scheduled mode (tray app that digests new notes); optional open-weight model swap behind `llm.py`.

---

## 9. Open decisions (resolve as we hit them)

- Embedding model: hosted vs. local (decide at M3).
- Vector store: SQLite-vec vs. alternative (decide at M3, verify current options).
- Chunking strategy for long notes (decide at M3).
- Electron aesthetic direction (decide at M4 — bring references).
- Whether to add tags/links as retrieval signals (post-M3, optional).

## 10. Risks

- **Scope creep via UI.** Mitigation: M1–M3 prove the AI before any pixels (backend-first).
- **Electron/Python two-language overhead.** Mitigation: keep the boundary tiny (HTTP, a few endpoints); Python owns all logic.
- **Eval set too small to be meaningful.** Mitigation: keep it honest about n; it's a learning instrument, not a benchmark claim.
- **API cost during dev.** Mitigation: small model for tool-loop iterations; cache where possible.
```
