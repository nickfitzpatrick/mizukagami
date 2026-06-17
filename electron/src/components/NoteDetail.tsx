import { useEffect, useState } from "react";
import { fetchNote, createNote, updateNote } from "../api";
import "./NoteDetail.css";

interface Props {
  noteId: string | null;
  onSaved: () => void;
}

export default function NoteDetail({ noteId, onSaved }: Props) {
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!noteId) {
      setTitle("");
      setBody("");
      setStatus(null);
      return;
    }
    fetchNote(noteId)
      .then((n) => {
        setTitle(n.title);
        setBody(n.body);
        setStatus(null);
      })
      .catch((e) => setStatus(`Error: ${e}`));
  }, [noteId]);

  async function handleSave() {
    setSaving(true);
    setStatus(null);
    try {
      if (noteId) {
        await updateNote(noteId, body);
        setStatus("Saved");
      } else {
        await createNote(title || "Untitled", body);
        setStatus("Created");
        onSaved();
      }
    } catch (e) {
      setStatus(`Error: ${e}`);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="note-detail">
      <div className="note-detail-toolbar">
        {!noteId ? (
          <input
            className="note-title-input"
            placeholder="Note title..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        ) : (
          <span className="note-id">{noteId}</span>
        )}
        <div className="toolbar-right">
          {status && <span className="save-status">{status}</span>}
          <button className="save-btn" onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : noteId ? "Save" : "Create"}
          </button>
        </div>
      </div>

      <textarea
        className="note-body"
        placeholder="Write in markdown..."
        value={body}
        onChange={(e) => setBody(e.target.value)}
        spellCheck={false}
      />
    </div>
  );
}
