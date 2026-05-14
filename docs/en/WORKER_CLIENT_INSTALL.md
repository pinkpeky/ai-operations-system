# Worker Client Install and Local Runtime Management

Status: completed, Phase 29.

This guide covers customer-machine Worker installation, registration, startup, status, logs, and the Worker Console Foundation. There is currently no GUI, system tray, Electron, Tauri, PySide, exe/dmg packaging, or real platform automation.

## Current Capabilities

- `Worker Runtime Manager`: `worker_client/runtime_manager.py`
- local status: `worker_client/status.py`
- status file: `worker_client/runtime_state/status.json`
- local logging: `worker_client/logging.py`
- log file: `worker_client/logs/worker.log`
- Local API client: `worker_client/local_api_client.py`
- Packaging Scripts: `packaging/windows_start_worker.ps1`, `packaging/mac_start_worker.sh`
- Desktop Runtime Placeholder: `worker_client/desktop/README.md`

## Windows

```powershell
copy worker_client\worker_config.example.yaml worker_client\worker_config.yaml
.\packaging\windows_install_requirements.ps1
.\packaging\windows_register_worker.ps1
.\packaging\windows_start_worker.ps1
```

Stop:

```powershell
.\packaging\windows_stop_worker.ps1
```

## Mac

```bash
cp worker_client/worker_config.example.yaml worker_client/worker_config.yaml
bash packaging/mac_install_requirements.sh
bash packaging/mac_register_worker.sh
bash packaging/mac_start_worker.sh
```

Stop:

```bash
bash packaging/mac_stop_worker.sh
```

## Local Management API

Default listener:

```text
http://127.0.0.1:9100
```

Endpoints:

- `GET /local/status`
- `GET /local/health`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`
- `GET /local/logs`

## Security Notes

- `worker_client/worker_state.json` stores plaintext `worker_secret` locally on the customer machine and is ignored by Git.
- `worker_client/runtime_state/status.json` does not include `worker_secret`.
- `worker_client/logs/worker.log` performs basic secret redaction.
- Do not commit `worker_config.yaml`, `worker_state.json`, runtime state, or logs.

## Current Boundary

This is Worker Console Foundation, not Worker Console GUI. It does not implement GUI, system tray, Electron, Tauri, PySide, exe/dmg, TikTok / YouTube / X automation, automatic login, cookie injection, fingerprint bypass, proxy pools, or captcha automation.
## Phase 31: Desktop Console Entry Point

Phase 31 adds `worker_console_desktop` as the Tauri desktop shell foundation. After installing and starting `worker_client`, the desktop console can connect to the local Local API:

```bash
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

Default connection:

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

There is still no formal installer, no exe / dmg, no system tray, and no auto update; this is only the Worker Console Desktop App Foundation.

## Phase 32: Tray Runtime Notes

After Phase 32, the desktop app supports System Tray and Minimize To Tray. The startup flow is unchanged:

```bash
python -m worker_client.cli start
cd worker_console_desktop
npm run tauri dev
```

The tray menu can control Start Runtime, Stop Runtime, Restart Runtime, Start Heartbeat, Stop Heartbeat, and Refresh Status. It only calls the local Worker API and does not execute shell commands.

There is still no formal installer, no auto-update, and no real autostart registration.

## Phase 33 Chat Panel Foundation

Worker Console Web and Desktop now include a Chat Panel Foundation:

- input box
- Send button
- Message list
- Event Timeline
- Refresh events
- route display for planning / tool / worker status
- `conversationClient.ts` for AI Server conversation APIs

Configuration:

```text
VITE_AI_SERVER_API=http://localhost:8000/api/v1
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

The Event Timeline uses polling. It is not a ChatGPT-level UI, not WebSocket streaming, and not SSE streaming.

## Phase 34 Worker Browser Runtime Setup

Customer-machine workers can now host the Remote Browser Runtime. Install Playwright Chromium on the customer machine before using real browser runtime actions:

```bash
python -m pip install playwright
playwright install chromium
```

Runtime endpoints exposed by `worker_client.runtime`:

- `POST /browser/session/create`
- `POST /browser/session/{session_id}/navigate`
- `POST /browser/session/{session_id}/screenshot`
- `GET /browser/session/{session_id}/page`
- `POST /browser/session/{session_id}/close`

The runtime implementation lives in `worker_client/browser_runtime`. It supports basic Chromium sessions, screenshots, and page content. It does not implement stealth, proxy, cookie injection, captcha bypass, platform automation, remote desktop streaming, or DevTools remote control.

## Phase 35B Real Client Worker E2E Checklist

After the customer machine is prepared:

```bash
python -m worker_client.cli register --config worker_client/worker_config.yaml
python -m worker_client.cli start --config worker_client/worker_config.yaml
```

Then validate from AI Server:

```bash
python scripts/validate_real_client_worker_e2e.py \
  --server-url http://localhost:8000 \
  --workspace-id demo-workspace \
  --user-id demo-user \
  --expected-worker-name customer-machine-worker-1
```

If the worker is not online, the script returns `SKIPPED` and `real client worker not online`. This is the correct result when the real customer machine is unavailable.

Do not expose port 9100 to the public internet; use Tailscale, VPN, or LAN.

## Phase 35A Note: Runtime Observability

The customer-machine worker does not need new real-platform capability for Phase 35A. The AI Server records Timeline, Snapshots, and Replay metadata after Browser Runtime actions.

The customer machine still needs the Phase 34 Playwright setup:

```powershell
playwright install chromium
```

Phase 35A does not require live stream, VNC/noVNC, DevTools remote control, or replay re-execution. Do not expose port 9100 to the public internet; prefer Tailscale, VPN, or a trusted LAN.

## Phase 36: Server Admin Dashboard Foundation

`admin_dashboard` is now part of the docs SSOT. It is a read-only monitoring foundation for Overview, Workers, Browser Runtime, Conversations, Tasks, OpenClaw, Audit Logs, RAG / Documents, and Settings. Runtime config is `VITE_AI_SERVER_API=http://localhost:8000`, `VITE_WORKSPACE_ID=demo-workspace`, and `VITE_USER_ID=demo-user`. The API client lives at `admin_dashboard/src/api/client.ts` and exports `workersApi`, `browserRuntimeApi`, `conversationsApi`, `tasksApi`, `openclawApi`, `auditApi`, and `ragApi`. Current boundaries: no login UI, no permission UI, no publishing business flow, no real social platform control, no production-grade operations backend.

## Phase 37: Conversation Runtime Frontend Integration

Status: completed, Phase 37.

Phase 37 connects the Conversation Runtime to Server Admin Dashboard, Worker Console Web, and Worker Console Desktop. The current scope is Conversation frontend integration and a basic conversation entrypoint. It is not a full ChatGPT UI and it is not WebSocket / SSE streaming.

Completed:

- Admin Dashboard Conversation page: `admin_dashboard` Conversations supports create thread, thread list, thread detail, message list, event timeline, send message, run conversation, refresh messages, and refresh events.
- Admin Dashboard client: `admin_dashboard/src/api/conversationClient.ts` supports `createThread`, `listThreads`, `getThread`, `sendMessage`, `listMessages`, `listEvents`, and `runConversation`.
- Worker Console Chat Panel: `worker_console` supports AI Server URL, Workspace ID, User ID settings, create thread, send and run, Polling Event Timeline, and AI Server connected / disconnected / unreachable state.
- Desktop Chat Panel: `worker_console_desktop` mirrors the Chat Panel foundation. Tauri native validation still depends on the customer machine Rust/MSVC environment.
- Polling Event Timeline: frontends call `GET /api/v1/conversations/{thread_id}/events` manually or every 5 seconds and show `event_type`, `message`, `created_at`, and `payload JSON`.
- Frontend config: `VITE_AI_SERVER_API=http://localhost:8000`, `VITE_WORKSPACE_ID=demo-workspace`, `VITE_USER_ID=demo-user`.
- Development CORS: backend `CORS_ALLOWED_ORIGINS` allows `http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:5180`, `http://127.0.0.1:5180`, `tauri://localhost`, and related local development origins.

Boundaries: current implementation is not WebSocket, not SSE, and not a full ChatGPT UI. It does not implement TikTok / YouTube / X automation, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, real platform automation, real OpenClaw, or ComfyUI.
## Phase 38 Worker Client Impact

Phase 38 does not change the worker_client installation flow. When Conversation Runtime uses Browser Bridge through `browser_tool`, it still depends on a registered and online Browser Worker / worker_client runtime. If no worker is online, the conversation run returns a clear `tool_execution_failed` / `bridge_fallback` error and does not fake success.

## Phase 41 Worker Client Impact

Phase 41 does not change worker_client installation. Output Library stores artifacts on the AI Server side; worker_client still only handles Browser Runtime / Playwright execution and result return. Screenshot files remain managed by the existing screenshot storage, while Output Library stores path references.
