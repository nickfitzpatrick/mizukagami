import type { NoteMeta, NoteDetail, ChatEvent } from "./types";

const BASE = "http://localhost:8000";

export async function fetchNotes(limit = 20): Promise<NoteMeta[]> {
  const res = await fetch(`${BASE}/notes?limit=${limit}`);
  if (!res.ok) throw new Error(`GET /notes failed: ${res.status}`);
  return res.json();
}

export async function fetchNote(id: string): Promise<NoteDetail> {
  const res = await fetch(`${BASE}/notes/${id}`);
  if (!res.ok) throw new Error(`GET /notes/${id} failed: ${res.status}`);
  return res.json();
}

export async function createNote(title: string, body: string): Promise<{ id: string }> {
  const res = await fetch(`${BASE}/notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, body }),
  });
  if (!res.ok) throw new Error(`POST /notes failed: ${res.status}`);
  return res.json();
}

export async function updateNote(id: string, body: string): Promise<void> {
  const res = await fetch(`${BASE}/notes/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ body }),
  });
  if (!res.ok) throw new Error(`PUT /notes/${id} failed: ${res.status}`);
}

/** Stream chat events. Calls onEvent for each parsed SSE chunk until "done". */
export async function streamChat(
  message: string,
  onEvent: (e: ChatEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    signal,
  });
  if (!res.ok) throw new Error(`POST /chat failed: ${res.status}`);

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buf = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop() ?? "";
    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith("data:")) continue;
      try {
        const event = JSON.parse(line.slice(5).trim()) as ChatEvent;
        onEvent(event);
        if (event.type === "done") return;
      } catch {
        // malformed chunk, skip
      }
    }
  }
}
