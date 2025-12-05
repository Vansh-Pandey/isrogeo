import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    watch: {
      usePolling: true,
      interval: 250,
      ignored: ["**/node_modules/**", "**/.git/**", "**/dist/**"],
    },
    host: true,
  },
});
