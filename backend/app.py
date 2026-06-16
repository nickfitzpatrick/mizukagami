"""M2 entry point: FastAPI wrapper around the agent + note CRUD.

Endpoints (spec §3):
  POST /chat    -> stream agent messages (runs the harness)
  GET/POST/PUT  /notes  -> note CRUD passthrough to notes_store
Binds to localhost only; the Electron shell (M4) is the client.

Run: uvicorn app:app --reload --port 8000
"""

# from fastapi import FastAPI
# app = FastAPI(title="PIA backend")
#
# @app.post("/chat")
# async def chat(...): ...
