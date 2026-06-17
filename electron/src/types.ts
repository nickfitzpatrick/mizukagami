export interface NoteMeta {
  id: string;
  title: string;
  created: string;
  updated: string;
  tags: string[];
}

export interface NoteDetail extends NoteMeta {
  body: string;
}

// SSE event shapes from /chat
export type ChatEvent =
  | { type: "tool_call"; name: string; args: Record<string, unknown> }
  | { type: "answer"; content: string }
  | { type: "error"; message: string }
  | { type: "done" };

export interface Message {
  role: "user" | "assistant";
  content: string;
  toolCalls?: { name: string; args: Record<string, unknown> }[];
}
