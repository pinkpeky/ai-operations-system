# Phase 70P Browser Worker Heartbeat Supervision

Phase 70P closes the runtime gap found during Phase 70O deployment: the Browser Worker process can be online on port 9100 while the API marks the registered worker offline because heartbeat is not running. Production readiness depends on both the local runtime and the API worker registry staying fresh.

## What Changed

- `deployment/windows/start_browser_worker_aiops.ps1` now starts a heartbeat loop through `Start-WorkerHeartbeatLoop` after confirming the worker runtime is healthy.
- The script also starts heartbeat when an existing 9100 runtime is already responding, which covers the current Docker-backed worker path.
- Added `-SkipHeartbeat` for maintenance cases where an operator intentionally wants runtime startup only.
- Heartbeat stdout/stderr are written to:
  - `storage/logs/browser_worker_heartbeat_stdout.log`
  - `storage/logs/browser_worker_heartbeat_stderr.log`
- `deployment/windows/register_browser_worker_aiops_task.ps1` now describes the scheduled task as starting both the Browser Worker and heartbeat loop.
- `worker_client.heartbeat.heartbeat_loop` writes and refreshes `heartbeat_running=true` while the loop is active and clears it on graceful exit.
- `docker-compose.yml` mounts `worker_client/runtime_state` and `worker_client/worker_state.json` into `browser-worker` so Docker `/local/status` reads the same supervised heartbeat state as the host startup script.

## Operational Contract

The startup task is now responsible for two things:

- keep `worker.main:app` reachable on port 9100;
- keep the registered `production-workspace` worker fresh through `POST /api/v1/browser-workers/{worker_id}/heartbeat`.

This means a server reboot or a Docker/browser-worker restart should not leave `BrowserWorkerSelector` with only a stale offline worker record.

## Boundaries

Phase 70P does not create a real OpenClaw provider, does not publish, does not run Playwright actions automatically, does not store new secrets, does not bypass worker signing, does not control social accounts, does not submit ComfyUI prompts, and does not change the operator approval model.

## Verification

- `tests/test_browser_worker_production_scripts.py` verifies the Windows startup scripts supervise heartbeat.
- `tests/test_worker_client_heartbeat.py` verifies `heartbeat_loop` marks local status as running while active.
- Live runtime verification after this phase showed the registered `aiops-production-browser-worker` returning to `online`, while OpenClaw provider readiness correctly remained `real_publish_provider_not_configured` because the provider is still mock.
