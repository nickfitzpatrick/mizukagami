"""Unit tests for keyword + embeddings retrieval and notes store."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import retrieval  # noqa: E402


@pytest.fixture
def keyword_stage():
    retrieval.set_stage("keyword")
    yield
    retrieval.set_stage("embeddings")


# --- keyword stage (M1) ----------------------------------------------------

def test_keyword_finds_relevant_note(keyword_stage):
    hits = retrieval.search("RouteMorph explainability", k=5)
    ids = [h["note_id"] for h in hits]
    assert "2026-06-16-routemorph-explainability" in ids


def test_keyword_ranks_by_score(keyword_stage):
    hits = retrieval.search("Geopogo accessibility ADA", k=5)
    assert hits, "expected at least one hit"
    scores = [h["score"] for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_keyword_empty_query_returns_nothing(keyword_stage):
    assert retrieval.search("   ", k=5) == []


def test_keyword_no_match_returns_empty(keyword_stage):
    assert retrieval.search("zzzqqq nonexistent xyzzy", k=5) == []


# --- embeddings stage (M3) -------------------------------------------------

def test_embeddings_finds_paraphrased_note():
    # No shared keywords with the target note's vocabulary — keyword search
    # misses this; embeddings should catch it.
    hits = retrieval.search(
        "How do I stop the moss enclosure from staying soggy at the roots?", k=5
    )
    ids = [h["note_id"] for h in hits]
    assert "2026-04-15-vivarium-drainage-layer" in ids


def test_embeddings_ranks_by_cosine():
    hits = retrieval.search("RouteMorph explainability", k=5)
    assert hits
    scores = [h["score"] for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_embeddings_empty_query_returns_nothing():
    assert retrieval.search("   ", k=5) == []
