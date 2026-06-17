# Contributing / conventions

Solo project, but kept clean because the repo is a portfolio artifact.

## Commits
- Imperative subject, prefixed with the milestone:
  - `M1: implement keyword search_notes tool`
  - `M3: swap retrieval to embeddings + vector store`
  - `docs: add eval before/after to README`
- One commit per meaningful sub-step (rebuilds Git habits + readable history).

## Never commit
- Secrets / `.env` (gitignored).
- Generated indexes (`index/*`) or `memory/agent_memory.json` (gitignored).

## Branches
- `main` is always in a working/shippable state (each milestone ends shippable).
- Use short-lived feature branches for anything risky; merge when green.

## CI
- `.github/workflows/eval.yml` runs unit tests + the keyword-stage eval on push.
- CI is hermetic: it does NOT call paid model APIs or Ollama. Retrieval eval
  (keyword stage) and pure-logic tests only.
