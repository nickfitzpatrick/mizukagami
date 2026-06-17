"""Unit tests for keyword retrieval and notes store (hermetic, no model)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import retrieval  # noqa: E402


def test_search_finds_relevant_note():
    hits = retrieval.search("RouteMorph explainability", k=5)
    ids = [h["note_id"] for h in hits]
    assert "2026-06-16-routemorph-explainability" in ids


def test_search_ranks_by_score():
    hits = retrieval.search("Geopogo accessibility ADA", k=5)
    assert hits, "expected at least one hit"
    scores = [h["score"] for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_empty_query_returns_nothing():
    assert retrieval.search("   ", k=5) == []


def test_no_match_returns_empty():
    assert retrieval.search("zzzqqq nonexistent xyzzy", k=5) == []
