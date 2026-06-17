"""Retrieval: given a query, return the notes worth showing the agent.

Staged plan (spec §5):
  Stage 1 (M1): keyword token-overlap scoring over note bodies.
  Stage 2 (M3, THIS FILE adds it): embeddings + NumPy cosine nearest-neighbor.

The public function `search(query, k)` keeps the SAME signature across both
stages — only the implementation changes. That clean seam is the point, and
it lets the eval harness compare stage 1 vs stage 2 with identical calls.

Stage is selected by `set_stage("keyword" | "embeddings")`; default is
embeddings. The eval harness flips it to score both and report the delta.

Embedding model: all-MiniLM-L6-v2 via sentence-transformers — local, $0/call,
runs in-process so CI stays hermetic (spec §11). Vector store: a NumPy matrix
cached to index/embeddings.npz, keyed by a hash of the corpus so it rebuilds
when notes change. At this corpus size (~13 notes) brute-force cosine is the
whole algorithm; sqlite-vec/FAISS would be YAGNI.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import notes_store

# --- stage selection -------------------------------------------------------

_STAGE = "embeddings"


def set_stage(stage: str) -> None:
    """Pick which retrieval implementation search() uses. For the eval harness."""
    global _STAGE
    if stage not in ("keyword", "embeddings"):
        raise ValueError(f"unknown stage {stage!r}")
    _STAGE = stage


# --- stage 1: keyword ------------------------------------------------------

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


def _keyword_search(query: str, k: int) -> list[dict]:
    """Stage-1 keyword scoring: # distinct query tokens in title+body,
    title matches weighted higher. Score-0 notes dropped."""
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


# --- stage 2: embeddings ---------------------------------------------------

_MODEL_NAME = "all-MiniLM-L6-v2"
_CACHE = Path(__file__).resolve().parent.parent / "index" / "embeddings.npz"

_model = None       # lazy-loaded SentenceTransformer
_index = None       # (note_ids: list[str], titles: list[str], bodies: list[str],
                    #  vectors: np.ndarray, corpus_hash: str)


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def _corpus_hash(notes: list[dict]) -> str:
    """Stable hash of all note ids + content; changes iff the corpus changes."""
    h = hashlib.sha256()
    for note in sorted(notes, key=lambda n: n["id"]):
        h.update(note["id"].encode())
        h.update(b"\0")
        h.update(note["title"].encode())
        h.update(b"\0")
        h.update(note["body"].encode())
        h.update(b"\0")
    return h.hexdigest()


def _embed_text(note: dict) -> str:
    # Title carries strong signal; prepend it. Notes are short, so no chunking.
    # ponytail: no chunking, add when a note exceeds the model's token window.
    return f"{note['title']}\n\n{note['body']}"


def _build_index(notes: list[dict], corpus_hash: str):
    import numpy as np

    model = _get_model()
    texts = [_embed_text(n) for n in notes]
    vectors = model.encode(texts, normalize_embeddings=True)
    vectors = np.asarray(vectors, dtype="float32")
    ids = [n["id"] for n in notes]
    titles = [n["title"] for n in notes]
    bodies = [n["body"] for n in notes]

    _CACHE.parent.mkdir(exist_ok=True)
    np.savez(
        _CACHE,
        ids=np.array(ids, dtype=object),
        titles=np.array(titles, dtype=object),
        bodies=np.array(bodies, dtype=object),
        vectors=vectors,
        corpus_hash=corpus_hash,
    )
    return ids, titles, bodies, vectors, corpus_hash


def _load_index():
    """Return the in-memory index, rebuilding if notes changed since last cache."""
    global _index
    import numpy as np

    notes = notes_store.iter_notes()
    corpus_hash = _corpus_hash(notes)

    if _index is not None and _index[4] == corpus_hash:
        return _index

    if _CACHE.exists():
        data = np.load(_CACHE, allow_pickle=True)
        if str(data["corpus_hash"]) == corpus_hash:
            _index = (
                list(data["ids"]),
                list(data["titles"]),
                list(data["bodies"]),
                data["vectors"],
                corpus_hash,
            )
            return _index

    _index = _build_index(notes, corpus_hash)
    return _index


def _embed_search(query: str, k: int) -> list[dict]:
    import numpy as np

    if not query.strip():
        return []
    ids, titles, bodies, vectors, _ = _load_index()
    if len(ids) == 0:
        return []

    q = _get_model().encode([query], normalize_embeddings=True)
    q = np.asarray(q, dtype="float32")[0]
    # Vectors are unit-normalized, so cosine == dot product.
    sims = vectors @ q

    order = np.argsort(sims)[::-1][:k]
    q_tokens = set(_tokens(query))
    return [
        {
            "note_id": ids[i],
            "title": titles[i],
            "snippet": _snippet(bodies[i], q_tokens),
            "score": round(float(sims[i]), 4),
        }
        for i in order
    ]


# --- public entry point ----------------------------------------------------

def search(query: str, k: int = 5) -> list[dict]:
    """Return up to k hits: [{note_id, title, snippet, score}], best first.

    Dispatches to the keyword or embeddings implementation per the current
    stage. Signature is identical across stages by design (spec §5).
    """
    if _STAGE == "keyword":
        return _keyword_search(query, k)
    return _embed_search(query, k)
