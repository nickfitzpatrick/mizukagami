"""Retrieval: given a query, return the notes worth showing the agent.

Staged plan (spec §5):
  Stage 1 (M1): keyword token matching over note bodies.
  Stage 2 (M3): embeddings + vector nearest-neighbor.

The public function `search(query, k)` keeps the SAME signature across both
stages — only the implementation changes. That clean seam is the point.
"""


def search(query: str, k: int = 5):
    """Return up to k hits: [{note_id, snippet, score}, ...]."""
    # M1: keyword implementation goes here.
    # M3: swap internals to embed(query) + nearest-vector lookup.
    raise NotImplementedError("M1: implement keyword search")
