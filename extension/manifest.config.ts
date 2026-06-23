import { defineManifest } from "@crxjs/vite-plugin"

const apiUrl = (process.env.VITE_API_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
)

const hostPermissions = Array.from(
  new Set([
    `${apiUrl}/*`,
    "http://localhost:8000/*",
    "http://127.0.0.1:8000/*",
    "http://localhost/*",
    "http://127.0.0.1/*",
  ]),
)

export default defineManifest({
  manifest_version: 3,
  name: "RAG Chat Assistant",
  version: "0.1.0",
  description: "Viewer chat widget for the RAG multitenant assistant",
  permissions: ["storage"],
  host_permissions: hostPermissions,
  content_scripts: [
    {
      matches: ["<all_urls>"],
      js: ["src/content/content-script.ts"],
      run_at: "document_idle",
    },
  ],
  web_accessible_resources: [
    {
      resources: ["panel.html"],
      matches: ["<all_urls>"],
    },
  ],
})
