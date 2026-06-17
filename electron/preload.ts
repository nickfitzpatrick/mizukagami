// Minimal preload: contextBridge not needed since all API calls go over HTTP
// to localhost:8000 from the renderer. Kept as placeholder for future IPC.
import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("mizukagami", {
  version: process.env.npm_package_version ?? "0.1.0",
});
