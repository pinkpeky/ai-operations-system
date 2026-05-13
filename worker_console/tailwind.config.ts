import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        console: {
          ink: "#0f172a",
          muted: "#64748b",
          line: "#d8dee8",
          surface: "#ffffff",
          band: "#f6f8fb",
          accent: "#2563eb",
          success: "#15803d",
          warning: "#b45309",
          danger: "#b91c1c",
        },
      },
      boxShadow: {
        panel: "0 1px 2px rgba(15, 23, 42, 0.06)",
      },
    },
  },
  plugins: [],
} satisfies Config;
