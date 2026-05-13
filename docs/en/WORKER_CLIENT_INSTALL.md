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
