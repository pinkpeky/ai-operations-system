# Worker Console Desktop App Foundation

`worker_console_desktop` is the Phase 31 Tauri desktop shell for the AI Ops Worker Console. It reuses the same local Worker API contract as the web console and defaults to:

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

## Scope

Implemented:

- Tauri project skeleton
- React + Vite + TypeScript + Tailwind frontend
- Local Worker status dashboard
- Runtime and heartbeat control buttons
- Local Worker logs view
- Worker API unreachable state
- Tauri config and Rust shell placeholders

Not implemented in this phase:

- formal exe / dmg installer
- system tray
- autostart
- auto update
- real platform automation
- TikTok / YouTube / X automation
- login, cookie injection, proxy pool, fingerprint bypass, or captcha handling

## Development

```powershell
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

If the current machine does not have Rust or the Tauri platform dependencies, use `npm run build` to validate the frontend and inspect `src-tauri/tauri.conf.json` for configuration readiness.

## Manual Runtime Check

Start the local Worker first:

```powershell
python -m worker_client.cli start
```

Then run the desktop console:

```powershell
cd worker_console_desktop
npm run tauri dev
```

The desktop window calls:

- `GET /local/status`
- `GET /local/health`
- `GET /local/logs`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`
