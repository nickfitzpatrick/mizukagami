import { useEffect, useState } from "react";
import { fetchNotes } from "../api";
import type { NoteMeta } from "../types";
import "./Sidebar.css";

interface Props {
  selectedId: string | null;
  onSelectNote: (id: string) => void;
  onNewNote: () => void;
  onOpenChat: () => void;
  onOpenSettings: () => void;
  refreshKey: number;
  activeView: string;
}

export default function Sidebar({
  selectedId, onSelectNote, onNewNote, onOpenChat, onOpenSettings, refreshKey, activeView,
}: Props) {
  const [notes, setNotes] = useState<NoteMeta[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchNotes()
      .then(setNotes)
      .catch((e) => setError(String(e)));
  }, [refreshKey]);

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-logo">水鏡</span>
        <span className="sidebar-title">Mizukagami</span>
      </div>

      <nav className="sidebar-nav">
        <button
          className={`nav-item ${activeView === "chat" ? "active" : ""}`}
          onClick={onOpenChat}
        >
          <span className="nav-icon">⌁</span> Chat
        </button>
        <button
          className={`nav-item ${activeView === "settings" ? "active" : ""}`}
          onClick={onOpenSettings}
        >
          <span className="nav-icon">⚙</span> Settings
        </button>
      </nav>

      <div className="sidebar-section-header">
        <span>Notes</span>
        <button className="new-note-btn" onClick={onNewNote} title="New note">+</button>
      </div>

      <div className="note-list">
        {error && <div className="sidebar-error">{error}</div>}
        {notes.length === 0 && !error && (
          <div className="sidebar-empty">No notes yet</div>
        )}
        {notes.map((n) => (
          <button
            key={n.id}
            className={`note-item ${selectedId === n.id ? "active" : ""}`}
            onClick={() => onSelectNote(n.id)}
          >
            <span className="note-item-title">{n.title || n.id}</span>
            {n.tags?.length > 0 && (
              <span className="note-item-tags">{n.tags.join(" ")}</span>
            )}
          </button>
        ))}
      </div>
    </aside>
  );
}
