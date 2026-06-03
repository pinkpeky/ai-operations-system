# Phase 68W Production Worker Registration Alignment

## Purpose

Phase 68W turns the Phase 68V standalone worker compatibility layer into a formal production registration path.

Before this phase, the live `worker.main:app` process could expose `/local/status` and `/local/metric-dispatch-scheduler`, but it still reported fallback values:

- `worker_name=browser-worker-compat`
- `workspace_id=demo-workspace`
- `registered=false`

That meant the customer-machine local console could see the local worker, but the API selector could not reliably choose this machine for remote browser/OpenClaw handoff work.

## Changes

- `worker.main` now resolves signed request verification secrets from `worker_client/worker_state.json` first, then from explicit worker config, then from `BROWSER_WORKER_SECRET`.
- `deployment/windows/register_browser_worker_with_api.ps1` now persists the returned one-time `worker_secret` to `worker_client/worker_state.json` without printing the secret.
- `deployment/windows/verify_browser_worker_aiops.ps1` now prefers the local worker state secret, so verification matches the registered worker record.
- `deployment/windows/start_browser_worker_aiops.ps1` no longer kills arbitrary port owners on `-Force`; it only stops Python `worker.main:app` processes and warns or fails for Docker/WSL port owners.
- The single-server production workspace baseline is `production-workspace`, matching `deployment/profiles/production-server/healthchecks.json`.

## Live Server Runbook

Use host-managed `worker.main:app` as the customer-machine worker when the same physical server also runs Docker backing services.

Keep Docker backing services running:

```powershell
docker compose up -d postgres redis qdrant api
```

Do not run the Docker `browser-worker` container in this host-worker mode:

```powershell
docker stop aiops-browser-worker
```

Create `worker_client/worker_config.yaml` outside Git:

```yaml
server_url: http://127.0.0.1:8000
worker_name: aiops-production-browser-worker
worker_type: playwright
workspace_id: production-workspace
worker_secret: null
worker_base_url: http://host.docker.internal:9100
runtime_host: 0.0.0.0
runtime_port: 9100
state_path: worker_client/worker_state.json
heartbeat_interval_seconds: 30
auth_enabled: true
auth_strict: true
```

Register and persist state:

```powershell
.\.venv\Scripts\python.exe -m worker_client.cli --config worker_client\worker_config.yaml register --force
```

Restart the host worker after config/state exists:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\start_browser_worker_aiops.ps1 -Force
```

Send one heartbeat:

```powershell
.\.venv\Scripts\python.exe -m worker_client.cli --config worker_client\worker_config.yaml heartbeat --once
```

Verify API registration:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/browser-workers/health/summary" `
  -Headers @{ "X-Workspace-Id" = "production-workspace" }
```

Verify the local worker:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\verify_browser_worker_aiops.ps1
Invoke-RestMethod http://127.0.0.1:9100/local/status
```

Because the API currently runs in Docker, `worker_base_url` must be reachable from the API container. Use `http://host.docker.internal:9100` for the API registry; use `http://127.0.0.1:9100` only for direct host-side smoke checks.

Expected local status after registration:

- `worker_name=aiops-production-browser-worker`
- `workspace_id=production-workspace`
- `registered=true`
- `runtime_running=true`
- `heartbeat_running` may be false unless the local heartbeat loop is running continuously.

## Boundary

Phase 68W does not publish to social platforms, log in to accounts, scrape analytics, run OpenClaw actions, mutate ComfyUI workflows, submit ComfyUI prompts, bypass approval, or install a Windows service.

It only aligns the already-running customer-machine worker with the API registry and makes the secret/auth path reproducible.
