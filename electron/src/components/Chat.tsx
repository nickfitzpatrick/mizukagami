import { useEffect, useRef, useState } from "react";
import { streamChat } from "../api";
import type { Message } from "../types";
import "./Chat.css";

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || streaming) return;
    setInput("");

    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setStreaming(true);

    const assistantMsg: Message = { role: "assistant", content: "", toolCalls: [] };
    setMessages((prev) => [...prev, assistantMsg]);

    const ctrl = new AbortController();
    abortRef.current = ctrl;

    try {
      await streamChat(
        text,
        (event) => {
          if (event.type === "tool_call") {
            setMessages((prev) => {
              const msgs = [...prev];
              const last = { ...msgs[msgs.length - 1] };
              last.toolCalls = [...(last.toolCalls ?? []), { name: event.name, args: event.args }];
              msgs[msgs.length - 1] = last;
              return msgs;
            });
          } else if (event.type === "answer") {
            setMessages((prev) => {
              const msgs = [...prev];
              const last = { ...msgs[msgs.length - 1] };
              last.content += event.content;
              msgs[msgs.length - 1] = last;
              return msgs;
            });
          } else if (event.type === "error") {
            setMessages((prev) => {
              const msgs = [...prev];
              const last = { ...msgs[msgs.length - 1] };
              last.content = `Error: ${event.message}`;
              msgs[msgs.length - 1] = last;
              return msgs;
            });
          }
        },
        ctrl.signal
      );
    } catch (e) {
      if ((e as Error).name !== "AbortError") {
        setMessages((prev) => {
          const msgs = [...prev];
          const last = { ...msgs[msgs.length - 1] };
          last.content = `Connection error: ${e}`;
          msgs[msgs.length - 1] = last;
          return msgs;
        });
      }
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }

  function stop() {
    abortRef.current?.abort();
  }

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="chat">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="chat-empty-logo">水鏡</div>
            <p>Ask me about your notes.</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message message-${msg.role}`}>
            {msg.toolCalls && msg.toolCalls.length > 0 && (
              <div className="tool-calls">
                {msg.toolCalls.map((tc, j) => (
                  <div key={j} className="tool-call">
                    <span className="tool-call-name">{tc.name}</span>
                    <span className="tool-call-args">
                      {Object.entries(tc.args)
                        .map(([k, v]) => `${k}=${JSON.stringify(v)}`)
                        .join("  ")}
                    </span>
                  </div>
                ))}
              </div>
            )}
            {msg.content && (
              <div className="message-body">{msg.content}</div>
            )}
            {streaming && i === messages.length - 1 && msg.role === "assistant" && !msg.content && (
              <div className="message-body typing">
                <span />
                <span />
                <span />
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-row">
        <textarea
          className="chat-input"
          placeholder="Ask about your notes... (Enter to send, Shift+Enter for newline)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          rows={1}
          disabled={streaming}
        />
        {streaming ? (
          <button className="send-btn stop-btn" onClick={stop}>Stop</button>
        ) : (
          <button className="send-btn" onClick={send} disabled={!input.trim()}>
            Send
          </button>
        )}
      </div>
    </div>
  );
}
