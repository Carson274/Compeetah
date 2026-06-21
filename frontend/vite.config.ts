import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, the Vite server proxies the API + websocket to the FastAPI backend
// on :8000, so the frontend talks to the same origin in dev and in production.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // listen on the LAN so you can preview from your phone
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true },
      "/ws": { target: "ws://localhost:8000", ws: true },
    },
  },
  build: { outDir: "dist" },
});
