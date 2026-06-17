import { app, BrowserWindow } from "electron";
import { join } from "path";
import { spawn, ChildProcess } from "child_process";
import { existsSync } from "fs";

const isDev = !app.isPackaged;
let backend: ChildProcess | null = null;

function startBackend() {
  // Find venv python relative to the electron dir (one level up in PIA/)
  const venvPython = join(__dirname, "..", "..", "backend", ".venv", "bin", "python");
  const backendDir = join(__dirname, "..", "..", "backend");
  const python = existsSync(venvPython) ? venvPython : "python3";

  backend = spawn(
    python,
    ["-m", "uvicorn", "app:app", "--port", "8000", "--no-access-log"],
    { cwd: backendDir, stdio: "pipe" }
  );

  backend.stderr?.on("data", (d) => {
    if (isDev) process.stderr.write(`[backend] ${d}`);
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    titleBarStyle: "hiddenInset",
    backgroundColor: "#0d1117",
    webPreferences: {
      preload: join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev) {
    win.loadURL("http://localhost:5173");
  } else {
    win.loadFile(join(__dirname, "..", "dist", "index.html"));
  }
}

app.whenReady().then(() => {
  startBackend();
  // Small delay so backend has time to bind port before renderer starts fetching
  setTimeout(createWindow, 1200);

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  backend?.kill();
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", () => {
  backend?.kill();
});
