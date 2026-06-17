import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import electron from "vite-plugin-electron";
import { resolve } from "path";

export default defineConfig({
  plugins: [
    react(),
    electron([
      {
        entry: "main.ts",
        vite: {
          build: {
            outDir: "dist-electron",
            rollupOptions: { external: ["electron"] },
          },
        },
      },
      {
        entry: "preload.ts",
        vite: {
          build: {
            outDir: "dist-electron",
            rollupOptions: { external: ["electron"] },
          },
        },
      },
    ]),
  ],
  root: resolve(__dirname),
  build: {
    outDir: "dist",
  },
  server: {
    port: 5173,
  },
});
