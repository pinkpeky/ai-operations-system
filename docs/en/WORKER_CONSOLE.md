# Worker Console GUI Foundation

Status: completed, Phase 30.

`worker_console` is the local Web GUI Foundation for customer-machine Workers. It is an independent Vite + React + TypeScript + Tailwind frontend project and connects to the local Worker API by default:

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

## Current Pages

Dashboard:

- `worker_name`
- `worker_id`
- `workspace_id`
- `server_url`
- `registered`
- `runtime_running`
- `heartbeat_running`
- `current_status`
- `last_heartbeat_at`
- `last_error`

Runtime Control:

- Start Runtime
- Stop Runtime
- Restart Runtime
- Start Heartbeat
- Stop Heartbeat

Logs:

- calls `GET /local/logs`
- supports refresh
- highlights error / failed / exception / traceback lines

Connection Info:

- `server_url`
- `worker_base_url`
- `runtime_port`
- `openclaw_enabled`
- `browser_enabled`

## Local API Client

Frontend client file:

```text
worker_console/src/api/localWorkerClient.ts
```

Supported methods:

- `getStatus`
- `getHealth`
- `getLogs`
- `startRuntime`
- `stopRuntime`
- `restartRuntime`
- `startHeartbeat`
- `stopHeartbeat`

## Run

```bash
python -m worker_client.cli start
cd worker_console
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

If the local Worker API is unavailable, the page shows:

- `Worker API unreachable`
- `请确认 worker_client 是否启动`
- `请确认端口是否为 9100`

## Current Boundary

This is a local Web GUI Foundation, not a desktop application. There is no system tray, no auto update, no Electron, no Tauri, no PySide, and no exe / dmg packaging. Future phases may add Tauri / Electron / PySide / system tray / auto start / exe / dmg.

It does not include TikTok / YouTube / X automation, account login, cookie injection, proxy pools, fingerprint bypass, captcha automation, or real platform automation.

Boundary marker: no system tray, no auto update, no Electron, no Tauri, no PySide, no exe / dmg.

## Phase 31: Worker Console Desktop App Foundation

Status: completed, Phase 31.

`worker_console_desktop` is the Tauri desktop shell foundation for the Worker Console. It reuses the Phase 30 local Worker API contract and defaults to:

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

### Desktop Shell Capabilities

- Opens a Tauri desktop window.
- Displays Worker status, Runtime status, Heartbeat status, Connection Info, and Logs.
- Calls `GET /local/status`, `GET /local/health`, and `GET /local/logs`.
- Calls `POST /local/runtime/start`, `POST /local/runtime/stop`, and `POST /local/runtime/restart`.
- Calls `POST /local/heartbeat/start` and `POST /local/heartbeat/stop`.
- If the local Worker API is unavailable, the UI shows `Worker API unreachable`, `Worker Runtime 未启动`, `请先启动 worker_client`, and `packaging 脚本启动`.

### Development

```bash
python -m worker_client.cli start
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

### Current Boundary

This is only the Worker Console Desktop App Foundation. There is no formal installer, no exe / dmg, no system tray, no autostart, and no auto update. Future phases may add tray / autostart / installer support.

It still does not include TikTok / YouTube / X automation, account login, cookie injection, proxy pools, fingerprint bypass, captcha automation, or real platform automation.
