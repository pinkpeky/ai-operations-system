# AI Ops Worker Console

Status: Phase 30 Worker Console GUI Foundation.

This is an independent local Web GUI for the customer-machine Worker Client. It connects to the local Worker API by default:

```text
http://127.0.0.1:9100
```

## Current Scope

- Dashboard for worker status.
- Runtime Control buttons for runtime and heartbeat actions.
- Logs panel backed by `GET /local/logs`.
- Connection Info panel.
- TypeScript local API client in `src/api/localWorkerClient.ts`.

## Run Locally

```bash
cd worker_console
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Build

```bash
npm run build
```

## Configuration

Copy `.env.example` to `.env` when needed:

```env
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

## Future Packaging Placeholder

Future phases may add:

- Tauri
- Electron
- PySide
- system tray
- auto start
- exe / dmg packaging

Not implemented in Phase 30:

- system tray
- exe / dmg
- auto update
- Tauri / Electron / PySide runtime
- TikTok / YouTube / X automation
- login automation
- proxy pools
- fingerprint bypass
- captcha automation
- real platform automation
