"""Model access layer.

Single chokepoint for all model interaction so the underlying model is
swappable (Claude API now; open-weight model later) without touching the
agent or tools. See spec §3, §7.
"""

# M1: thin — the Agent SDK's query() handles model calls directly.
# This module exists so that when we add embeddings (M3) or swap to an
# open-weight model, there is one place to change.

DEFAULT_MODEL = "claude-sonnet-4-6"  # verify current model string at build time


def get_model() -> str:
    """Return the model id to use for the agent loop."""
    return DEFAULT_MODEL


# M3: add embed(text) here, backed by hosted or local embedding model.
# def embed(text: str) -> list[float]:
#     raise NotImplementedError("Implement at M3 (embeddings retrieval).")
