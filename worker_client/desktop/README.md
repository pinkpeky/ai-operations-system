# Worker Console Desktop Placeholder

This directory is a placeholder for the future Worker Console GUI.

Current Phase 29 scope:

- Local Runtime Manager
- Local status API
- Local logs API
- Runtime / heartbeat control API
- Python `WorkerLocalAPIClient`
- Windows / Mac packaging scripts

Not implemented in Phase 29:

- Tauri GUI
- Electron GUI
- PySide GUI
- System tray
- Auto start
- EXE / DMG packaging
- Embedded browser control UI

Future Worker Console GUI can call the local API exposed by `worker_client.runtime`:

- `GET /local/status`
- `GET /local/health`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`
- `GET /local/logs`
