import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5174,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/local-worker": {
        target: "http://127.0.0.1:9100",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/local-worker/, ""),
      },
    },
  },
  preview: {
    host: "127.0.0.1",
    port: 4174,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/local-worker": {
        target: "http://127.0.0.1:9100",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/local-worker/, ""),
      },
    },
  },
});
