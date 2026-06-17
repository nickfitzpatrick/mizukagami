import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Chat from "./components/Chat";
import NoteDetail from "./components/NoteDetail";
import Settings from "./components/Settings";
import "./App.css";

type MainView = "chat" | "note" | "settings";

export default function App() {
  const [view, setView] = useState<MainView>("chat");
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);
  const [refreshSidebar, setRefreshSidebar] = useState(0);

  function openNote(id: string) {
    setSelectedNoteId(id);
    setView("note");
  }

  function onNoteSaved() {
    setRefreshSidebar((n) => n + 1);
    setView("note");
  }

  return (
    <div className="app-shell">
      {/* macOS traffic-light drag region */}
      <div className="titlebar-drag" />

      <Sidebar
        selectedId={selectedNoteId}
        onSelectNote={openNote}
        onNewNote={() => { setSelectedNoteId(null); setView("note"); }}
        onOpenChat={() => setView("chat")}
        onOpenSettings={() => setView("settings")}
        refreshKey={refreshSidebar}
        activeView={view}
      />

      <main className="main-panel">
        {view === "chat" && <Chat />}
        {view === "note" && (
          <NoteDetail
            noteId={selectedNoteId}
            onSaved={onNoteSaved}
          />
        )}
        {view === "settings" && <Settings />}
      </main>
    </div>
  );
}
