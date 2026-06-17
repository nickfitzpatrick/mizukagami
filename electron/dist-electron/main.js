"use strict";
const electron = require("electron");
const path = require("path");
const child_process = require("child_process");
const fs = require("fs");
const isDev = !electron.app.isPackaged;
let backend = null;
function startBackend() {
  var _a;
  const venvPython = path.join(__dirname, "..", "..", "backend", ".venv", "bin", "python");
  const backendDir = path.join(__dirname, "..", "..", "backend");
  const python = fs.existsSync(venvPython) ? venvPython : "python3";
  backend = child_process.spawn(
    python,
    ["-m", "uvicorn", "app:app", "--port", "8000", "--no-access-log"],
    { cwd: backendDir, stdio: "pipe" }
  );
  (_a = backend.stderr) == null ? void 0 : _a.on("data", (d) => {
    if (isDev) process.stderr.write(`[backend] ${d}`);
  });
}
function createWindow() {
  const win = new electron.BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    titleBarStyle: "hiddenInset",
    backgroundColor: "#0d1117",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  if (isDev) {
    win.loadURL("http://localhost:5173");
  } else {
    win.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  }
}
electron.app.whenReady().then(() => {
  startBackend();
  setTimeout(createWindow, 1200);
  electron.app.on("activate", () => {
    if (electron.BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});
electron.app.on("window-all-closed", () => {
  backend == null ? void 0 : backend.kill();
  if (process.platform !== "darwin") electron.app.quit();
});
electron.app.on("before-quit", () => {
  backend == null ? void 0 : backend.kill();
});
