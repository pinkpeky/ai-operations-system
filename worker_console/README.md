# AI Ops Worker Console

Status: Phase 62I Workstation/Customer Client Frontend UX Alignment.

This is an independent local Web GUI for the customer-machine Worker Client. It connects to the local Worker API by default:

```text
http://127.0.0.1:9100
```

## Current Scope

- Phase 62I operator home for customer-machine/workstation users.
- Chinese/English language switching for the top-level workstation flow.
- Simple status cards for local connection, runtime, heartbeat, and recovery state.
- Shortcuts for conversation runs, playbooks, approval queue, Output Library, task recovery, and local logs.
- Setup/recovery guidance and explicit server-vs-customer-machine boundary messaging.
- Dashboard for worker status.
- Runtime Control buttons for runtime and heartbeat actions.
- Logs panel backed by `GET /local/logs`.
- Connection Info panel.
- TypeScript local API client in `src/api/localWorkerClient.ts`.

Phase 62I does not add live ComfyUI calls, OpenClaw execution, platform publishing, real account control, captcha/proxy/fingerprint bypass, installer signing, or auto-update.

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
