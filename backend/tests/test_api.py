"""API tests for the FastAPI backend.

Notes endpoints are tested directly (no model). /chat is tested with a fake
tool-capable model injected into llm.get_chat_model, so the agent loop runs
without Ollama or an API key.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402


def _client():
    import app

    return TestClient(app.app)


def test_list_notes():
    r = _client().get("/notes")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_known_note():
    r = _client().get("/notes/2026-06-16-routemorph-explainability")
    assert r.status_code == 200
    assert "RouteMorph" in r.json()["body"]


def test_get_missing_note_404():
    r = _client().get("/notes/does-not-exist")
    assert r.status_code == 404


def test_create_note(tmp_path, monkeypatch):
    # Redirect the notes dir so the test doesn't litter the real corpus.
    import notes_store

    monkeypatch.setattr(notes_store, "NOTES_DIR", tmp_path)
    r = _client().post("/notes", json={"title": "Test Note", "body": "hello"})
    assert r.status_code == 200
    new_id = r.json()["id"]
    assert (tmp_path / f"{new_id}.md").exists()


def test_chat_streams_answer(monkeypatch):
    """/chat should stream SSE events ending in 'done', using a fake model."""
    import llm
    from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
    from langchain_core.messages import AIMessage

    class ToolCapable(GenericFakeChatModel):
        def bind_tools(self, tools, **kw):
            return self

    monkeypatch.setattr(
        llm, "get_chat_model", lambda: ToolCapable(messages=iter([AIMessage(content="hi")]))
    )

    with _client().stream("POST", "/chat", json={"message": "hello"}) as r:
        assert r.status_code == 200
        body = "".join(r.iter_text())
    assert '"type": "done"' in body
