# RAG Chat Browser Extension

Viewer-only chat widget for Chrome and Edge. A floating button appears at the bottom-right of every webpage; clicking it opens a panel where users can sign in, pick a customer, and chat with the RAG assistant.

## Prerequisites

- Node.js 18+ and npm
- Backend API running (default: `http://localhost:8000`)
- A **viewer**-role user account (create via the web app Admin page)

## Configuration

Copy the example env file and set your API URL:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API base URL (no trailing slash). Baked into the build and used for `host_permissions`. |

## Development

**Important:** For loading the extension in Chrome/Edge, always use a **production build** of `extension/dist`. Do not load the folder after `npm run dev` unless the Vite dev server is still running — dev output points `panel.html` at source files and the chat panel will fail with a blank/broken page.

From the repository root:

```bash
npm install
npm run build:extension
```

Load the unpacked extension from `extension/dist` (see below). Use `npm run dev:extension` only when actively developing the extension UI with hot reload.

Or from this directory:

```bash
npm run build
```

Load the unpacked extension:

1. Build or use dev output from `extension/dist`
2. Open `chrome://extensions` (Chrome) or `edge://extensions` (Edge)
3. Enable **Developer mode**
4. Click **Load unpacked** and select `extension/dist`

Visit any website — the chat bubble should appear in the bottom-right corner.

## Production build

```bash
# From repository root
npm run build:extension

# Or from extension/
npm run build
```

The built extension is in `extension/dist/`. Zip that folder to submit to the [Chrome Web Store](https://developer.chrome.com/docs/webstore/publish) or [Edge Add-ons](https://learn.microsoft.com/en-us/microsoft-edge/extensions-chromium/publish/publish-extension).

Set `VITE_API_URL` to your production API host before building:

```bash
VITE_API_URL=https://api.yourdomain.com npm run build
```

## Architecture

- **Content script** (`src/content/content-script.ts`) — injects the floating button and iframe shell on all pages
- **Panel app** (`panel.html` + `src/panel/`) — React UI with inline login, customer picker, and chat
- **Shared package** (`packages/shared`) — API client, auth, customer context, and chat hooks used by both this extension and the web frontend

The panel runs inside an extension iframe (`chrome-extension://…`) so API calls use `host_permissions` and are not blocked by page CORS.

## Permissions

| Permission | Why |
|------------|-----|
| `storage` | Persist JWT and selected customer |
| `host_permissions` (API URL) | Call backend login and chat endpoints |
| `<all_urls>` content script | Show the widget on any site |

## Store submission checklist

- [ ] Set production `VITE_API_URL` and rebuild
- [ ] Add extension icons (`public/icons/` — 16, 48, 128 px PNG) and reference them in `manifest.config.ts`
- [ ] Prepare privacy policy (extension stores JWT locally; no data sent to third parties except your API)
- [ ] Document that users need viewer accounts provisioned by an administrator
- [ ] Zip `extension/dist/` for upload

## Troubleshooting

**Login stuck on "Signing in..."** — Usually the extension cannot reach the API.

1. Check the **API:** line at the bottom of the login form shows the URL the extension calls (should be `http://localhost:8000` when using Docker locally).
2. Confirm the backend is up: open `http://localhost:8000/api/v1/utils/health-check/` in your browser.
3. Rebuild with the correct API URL:

```bash
# extension/.env
VITE_API_URL=http://localhost:8000
npm run build:extension
```

4. Reload the extension in Edge.

The `auth.py` / "message channel closed" console errors are usually from Edge password manager or another extension — they are unrelated to login and can be ignored.

**"Webpage might be having issues" / blank panel** — You loaded a **dev build** instead of a production build. The broken `panel.html` looks like this:

```html
<script type="module" src="/src/panel/main.tsx"></script>
```

Fix:

```bash
npm run build:extension
```

Then in `edge://extensions` or `chrome://extensions`, click **Reload** on the extension. Confirm `extension/dist/panel.html` references `./assets/panel-….js`, not `/src/panel/main.tsx`.

**Widget does not appear** — Reload the extension and refresh the page. Check the browser console for content-script errors.

**Login fails** — Confirm the backend is reachable at `VITE_API_URL` and the user has a valid account.

**Chat returns empty answers** — Ensure documents are uploaded for the selected customer via the web app (moderator/admin).

**Panel is blank** — Rebuild with `npm run build` and reload the extension. Check the panel iframe console via DevTools → inspect the iframe.
