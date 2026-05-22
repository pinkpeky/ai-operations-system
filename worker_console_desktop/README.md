# Worker Console Desktop App Foundation

`worker_console_desktop` is the Phase 62I customer-machine desktop shell for the AI Ops Worker Console. It reuses the same local Worker API contract as the web console and defaults to:

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

## Scope

Implemented:

- Phase 62I operator home for customer-machine/workstation users
- Chinese/English language switching for the top-level workstation flow
- Simple status cards for local connection, runtime, heartbeat, and recovery state
- Shortcuts for conversation runs, playbooks, approval queue, Output Library, task recovery, and local logs
- Setup/recovery guidance and explicit server-vs-customer-machine boundary messaging
- Tauri project skeleton
- Tauri system tray with Show Console, Hide Window, Start Runtime, Stop Runtime, Restart Runtime, Start Heartbeat, Stop Heartbeat, Refresh Status, and Quit
- Minimize To Tray: closing the window hides it; Quit exits the app
- Tray tooltip status sync from `GET /local/status` and `GET /local/health`
- React + Vite + TypeScript + Tailwind frontend
- Local Worker status dashboard
- Runtime and heartbeat control buttons
- Local Worker logs view
- Worker API unreachable state
- Desktop settings in `src/settings.ts` and `settings.example.json`
- AutoStart Placeholder docs under `autostart/`
- Tauri config and Rust shell placeholders

Not implemented in this phase:

- formal exe / dmg installer
- autostart
- auto update
- real platform automation
- TikTok / YouTube / X automation
- login, cookie injection, proxy pool, fingerprint bypass, or captcha handling
- live ComfyUI calls, OpenClaw execution, platform publishing, real account control, installer signing, or auto-update

## Development

```powershell
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

If the current machine does not have Rust or the Tauri platform dependencies, use `npm run build` to validate the frontend and inspect `src-tauri/tauri.conf.json` for configuration readiness.

## Settings

Example:

```json
{
  "localWorkerApi": "http://127.0.0.1:9100",
  "minimizeToTray": true,
  "refreshIntervalMs": 5000
}
```

Copy `settings.example.json` to `public/settings.json` in local development if you want runtime settings to override `.env` values.

## Tray Runtime Control

Tray menu actions emit local frontend events and the React app calls the Worker Client Local API:

- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`

No tray action executes arbitrary shell commands or remote commands.

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
