"""Retrieval: given a query, return the notes worth showing the agent.

Staged plan (spec §5):
  Stage 1 (M1, THIS FILE): keyword token-overlap scoring over note bodies.
  Stage 2 (M3): embeddings + vector nearest-neighbor.

The public function `search(query, k)` keeps the SAME signature across both
stages — only the implementation changes. That clean seam is the point, and
it lets the eval harness compare stage 1 vs stage 2 with identical calls.
"""

from __future__ import annotations

import re

import notes_store

_TOKEN = re.compile(r"[a-z0-9]+")
# Tiny stopword list so common words don't dominate scoring.
_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "are",
    "was", "were", "it", "its", "this", "that", "with", "as", "by", "be", "at",
    "how", "what", "why", "does", "do", "can", "i", "my", "you", "your",
}


def _tokens(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]


def _snippet(body: str, query_tokens: set[str], width: int = 160) -> str:
    """Return a short window of body around the first query-token hit."""
    low = body.lower()
    pos = -1
    for qt in query_tokens:
        i = low.find(qt)
        if i != -1 and (pos == -1 or i < pos):
            pos = i
    if pos == -1:
        snip = body[:width]
    else:
        start = max(0, pos - width // 3)
        snip = body[start : start + width]
    return " ".join(snip.split())


def search(query: str, k: int = 5) -> list[dict]:
    """Return up to k hits: [{note_id, title, snippet, score}], best first.

    Stage-1 keyword scoring: score = (# distinct query tokens found in the
    note's title+body), title matches weighted higher. Notes with score 0
    are dropped.
    """
    q_tokens = set(_tokens(query))
    if not q_tokens:
        return []

    hits = []
    for note in notes_store.iter_notes():
        title_tokens = set(_tokens(note["title"]))
        body_tokens = set(_tokens(note["body"]))
        title_overlap = q_tokens & title_tokens
        body_overlap = q_tokens & body_tokens
        score = 2 * len(title_overlap) + len(body_overlap - title_overlap)
        if score == 0:
            continue
        hits.append(
            {
                "note_id": note["id"],
                "title": note["title"],
                "snippet": _snippet(note["body"], q_tokens),
                "score": score,
            }
        )

    hits.sort(key=lambda h: h["score"], reverse=True)
    return hits[:k]
