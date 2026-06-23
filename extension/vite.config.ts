import react from "@vitejs/plugin-react-swc"
import { crx } from "@crxjs/vite-plugin"
import path from "node:path"
import { defineConfig } from "vite"
import manifest from "./manifest.config"

export default defineConfig({
  base: "./",
  plugins: [react(), crx({ manifest })],
  build: {
    rollupOptions: {
      input: {
        panel: path.resolve(__dirname, "panel.html"),
      },
    },
  },
})
