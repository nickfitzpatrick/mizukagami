import "./Settings.css";

export default function Settings() {
  return (
    <div className="settings">
      <h2 className="settings-heading">Settings</h2>

      <section className="settings-section">
        <h3>Model provider</h3>
        <p>
          Set <code>MIZUKAGAMI_MODEL_PROVIDER</code> in <code>PIA/.env</code> before
          starting the backend:
        </p>
        <div className="settings-code">
          <div><code>MIZUKAGAMI_MODEL_PROVIDER=ollama</code> &mdash; local Ollama (default, free)</div>
          <div><code>MIZUKAGAMI_MODEL_PROVIDER=anthropic</code> &mdash; Claude API (set <code>ANTHROPIC_API_KEY</code> too)</div>
        </div>
        <p className="settings-note">
          Restart the backend after changing. The same LangGraph agent runs against either provider.
        </p>
      </section>

      <section className="settings-section">
        <h3>Backend</h3>
        <p>FastAPI is running at <code>http://localhost:8000</code>.</p>
        <p className="settings-note">
          If the sidebar shows no notes or chat returns an error, check that the backend is up:
        </p>
        <div className="settings-code">
          <code>cd PIA/backend && source .venv/bin/activate && uvicorn app:app --port 8000</code>
        </div>
      </section>

      <section className="settings-section">
        <h3>Notes location</h3>
        <p>
          Notes are stored as markdown files in <code>PIA/notes/</code>. They are the
          source of truth and can be edited directly in any text editor.
        </p>
      </section>
    </div>
  );
}
