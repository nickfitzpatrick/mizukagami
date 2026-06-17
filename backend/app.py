"""M2: FastAPI backend wrapping the agent + note CRUD (spec §3).

localhost-only, single-user. Reuses build_agent() and notes_store directly
— no extra service layer. Streaming uses SSE (one-way token stream), which
is enough here; no WebSockets.

Run (from backend/, venv active):
    uvicorn app:app --reload --port 8000
"""

from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import StreamingResponse  # noqa: E402
from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from pydantic import BaseModel  # noqa: E402

import notes_store  # noqa: E402
from agent import build_agent  # noqa: E402

app = FastAPI(title="Mizukagami backend")


class ChatRequest(BaseModel):
    message: str


class NoteRequest(BaseModel):
    title: str
    body: str


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


def _chat_events(message: str):
    """Yield SSE events as the agent runs: tool calls, then the final answer."""
    agent = build_agent()
    try:
        for step in agent.stream(
            {"messages": [HumanMessage(content=message)]},
            stream_mode="values",
        ):
            msg = step["messages"][-1]
            if isinstance(msg, AIMessage):
                for call in msg.tool_calls or []:
                    yield _sse({"type": "tool_call", "name": call["name"], "args": call["args"]})
                if msg.content:
                    yield _sse({"type": "answer", "content": msg.content})
    except Exception as e:  # surface model/connection errors to the client
        yield _sse({"type": "error", "message": str(e)})
    yield _sse({"type": "done"})


@app.post("/chat")
def chat(req: ChatRequest):
    return StreamingResponse(_chat_events(req.message), media_type="text/event-stream")


@app.get("/notes")
def get_notes(limit: int = 20):
    return notes_store.list_notes(limit)


@app.get("/notes/{note_id}")
def get_note(note_id: str):
    try:
        return {"id": note_id, "body": notes_store.read_note(note_id)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No note with id {note_id!r}")


@app.post("/notes")
def create_note(req: NoteRequest):
    note_id = notes_store.write_note(req.title, req.body)
    return {"id": note_id}
