import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server for the Task 3 dashboard frontend. Talks to the Flask API
// (dashboard/backend/app.py) via VITE_API_BASE_URL, defaulting to
// localhost:5001 for local development (see dashboard/README.md).
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    allowedHosts: true,
  },
});
