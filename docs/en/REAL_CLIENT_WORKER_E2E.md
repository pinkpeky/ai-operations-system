# Real Client Worker E2E Validation

Status: completed validation plan and script. Real customer-machine E2E success must be executed later when the customer machine is online. Do not fabricate or backfill a passing real-client result.

## Goal

Validate the final Phase 34 chain:

```text
AI Server
-> RemoteBrowserProvider
-> BrowserWorkerSelector
-> real customer-machine worker_client
-> local browser_runtime
-> local Playwright Chromium
-> screenshot / page content / status returned to AI Server
```

## Customer Machine Preparation

Required:

- Python 3.11+
- project source or packaged `worker_client`
- Playwright
- Chromium browser runtime

Install:

```bash
python -m pip install -r requirements.txt
python -m pip install playwright
playwright install chromium
```

Optional for Worker Console Desktop native validation:

- Node.js
- Rust
- MSVC Build Tools on Windows

If Rust/MSVC is not ready, mark desktop native validation pending. Do not pretend `npm run tauri dev` passed.

## worker_config.yaml Example

```yaml
server_url: http://AI_SERVER_HOST:8000
worker_name: customer-machine-worker-1
worker_type: playwright
workspace_id: demo-workspace
worker_secret: null
heartbeat_interval_seconds: 30
runtime_host: 127.0.0.1
runtime_port: 9100
capabilities:
  browser: chromium
  browser_runtime: true
  screenshot: true
  page_content: true
  persistent_profile: false
```

Security note: do not expose port 9100 to the public internet. Prefer Tailscale, VPN, or a trusted LAN. The worker runtime should listen on localhost unless there is an explicit private-network deployment reason.

## Worker Registration And Startup

```bash
cp worker_client/worker_config.example.yaml worker_client/worker_config.yaml
python -m worker_client.cli register --config worker_client/worker_config.yaml
python -m worker_client.cli start --config worker_client/worker_config.yaml
```

The registration step stores `worker_state.json` locally. Do not commit it. Do not paste the worker secret into docs, issues, screenshots, or logs.

## Worker Console Checklist

Web Console:

```bash
cd worker_console
npm run dev
```

Open:

```text
http://localhost:5173
```

Check:

- `registered=true`
- `runtime_running=true`
- `heartbeat_running=true`
- `current_status=online`
- logs show heartbeat success
- Browser Sessions Panel can refresh active sessions

Desktop Console:

```bash
cd worker_console_desktop
npm run tauri dev
```

If Rust/MSVC is not installed or still being validated, record: `desktop native validation pending`.

## Swagger Validation Flow

Headers:

```text
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Steps:

1. `GET /api/v1/health`
2. `GET /api/v1/browser-workers/health/summary`
3. `GET /api/v1/browser-workers/available`
4. `POST /api/v1/browser-runtime/sessions`
5. `POST /api/v1/browser-runtime/sessions/{session_id}/navigate`
6. `POST /api/v1/browser-runtime/sessions/{session_id}/screenshot`
7. `GET /api/v1/browser-runtime/sessions/{session_id}/page`
8. `POST /api/v1/browser-runtime/sessions/{session_id}/close`

Create session:

```json
{
  "browser": "chromium",
  "metadata": {
    "phase": "35B",
    "source": "swagger"
  }
}
```

Navigate:

```json
{
  "url": "https://example.com"
}
```

Screenshot:

```json
{
  "full_page": true,
  "screenshot_name": "real-client-worker-e2e-example"
}
```

## E2E Script Validation

Run:

```bash
python scripts/validate_real_client_worker_e2e.py \
  --server-url http://localhost:8000 \
  --workspace-id demo-workspace \
  --user-id demo-user \
  --expected-worker-name customer-machine-worker-1
```

Exit codes:

- `0`: PASS
- `1`: FAIL
- `2`: SKIPPED / client unavailable

If `expected_worker_name` is not online, the script returns `SKIPPED` with reason `real client worker not online` and does not execute browser actions.

## Server Configuration Checks

The script inspects:

- `BROWSER_PROVIDER`
- `BROWSER_WORKER_AUTH_ENABLED`
- `BROWSER_ALLOWED_DOMAINS` includes `example.com`
- browser runtime OpenAPI routes exist
- `storage/browser_screenshots` / `BROWSER_RUNTIME_SCREENSHOT_DIR`

If `BROWSER_PROVIDER` is not `remote`, the script emits a WARNING rather than failing. The Phase 34 browser runtime API can still be validated directly, but old browser action API paths may continue using the mock provider.

## Common Troubleshooting

- Worker not listed: verify `worker_config.yaml`, registration, workspace id, and heartbeat loop.
- Worker listed but not available: check `max_sessions`, `active_sessions`, `status`, and `capabilities.browser_runtime`.
- Browser action fails: run `playwright install chromium` on the customer machine.
- Screenshot missing: check `storage/browser_screenshots` on AI Server and local worker logs.
- Connection refused: do not open port 9100 publicly; use Tailscale, VPN, or LAN routing.

## Boundaries

Current Phase 35B is only a validation plan and script. It does not implement TikTok / YouTube / X automation, login automation, cookie injection, proxy pools, fingerprint bypass, captcha automation, real platform automation, OpenClaw real device, or ComfyUI.
## Phase 35A Debug Extension

After a real client E2E run, use the Browser Runtime Observability APIs to inspect execution:

1. `GET /api/v1/browser-runtime/sessions/{session_id}/events`
2. `GET /api/v1/browser-runtime/sessions/{session_id}/snapshots`
3. `POST /api/v1/browser-runtime/sessions/{session_id}/replay`
4. `GET /api/v1/browser-runtime/replays/{replay_id}/export`

These endpoints create Timeline, Snapshot Storage, and metadata-only replay. They do not re-run browser actions and are not live stream, VNC, noVNC, or DevTools remote control.

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
## Phase 38 Validation Addendum

Real client worker E2E validation can add a Conversation run scenario: create a conversation, send “open https://example.com and take a screenshot”, then check `route_name=browser`, `selected_tool=browser_tool`, `events_created`, `result_metadata`, and events `route_selected`, `tool_execution_started`, and `tool_execution_completed`. If the client worker is offline, mark the run SKIPPED or clearly failed. Do not fake success.

## Phase 41 Validation Addendum

After a real client Playbook or Conversation run completes, validate Output Library with `GET /api/v1/output-artifacts`, `POST /api/v1/output-artifacts/from-playbook-run/{run_id}`, `POST /api/v1/output-artifacts/from-message/{message_id}`, and `GET /api/v1/output-artifacts/{artifact_id}/export?format=markdown`. Screenshot artifacts keep path references and do not copy large files. There is no S3 / MinIO integration and this is not a full DAM.
## Phase 42: Task Orchestration & Background Execution

This phase adds the Task Orchestration foundation: `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, and `TaskRetryPolicy`. Conversation / Playbook runs can use `execution_mode=background`, then `/api/v1/task-runs` exposes queued, running, waiting_approval, retrying, completed, failed, cancelled, expired state plus timeline events. `scheduled_at` supports scheduled runs; retry uses exponential backoff; approval resume continues to enforce the Phase 39 Approval Gate; Output Library artifacts are linked by `task_run_id`.

Boundary: this is an in-process queue, not Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue. It does not implement real publishing, real OpenClaw, ComfyUI, CAPTCHA handling, proxies, or fingerprint bypass.
## Phase 43: Task Scheduler Persistence & Worker Recovery (Completed)

Completed: Task Scheduler Persistence, `task_scheduler_state`, Task Lease fields on `task_runs`, `TaskRecoveryService`, Scheduler Health API, manual recovery API, Failed Diagnostics, and frontend scheduler health panels.

Task Lease: running task runs receive `lease_owner`, `lease_token`, `lease_expires_at`, and `heartbeat_at`. Expired lease and stale heartbeat are recoverable through scan or manual recover.

Recovery rules: running + expired lease or stale heartbeat -> retrying if retry budget remains, otherwise failed; pending scheduled due -> queued; retrying delay elapsed -> queued; waiting_approval is not auto-executed; completed/cancelled/expired are not recovered.

Admin Dashboard now shows Scheduler Health, lease status, recoverable badge, diagnostics panel, scheduled due indicator, and manual recover. Worker Console and Worker Console Desktop show simplified Task recovery state.

Boundary: this remains an in-process scheduler foundation, not Celery, not Kubernetes, and not production HA distributed queue.
