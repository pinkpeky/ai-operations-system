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

## Phase 32: Worker Console System Tray & Desktop Runtime Foundation

Status: completed, Phase 32.

`worker_console_desktop` now moves from a desktop shell foundation to a desktop runtime foundation with Tauri System Tray, Minimize To Tray, Tray Runtime Control, and Desktop Status Sync.

### System Tray

Tray menu entries:

- Show Console
- Hide Window
- Start Runtime
- Stop Runtime
- Restart Runtime
- Start Heartbeat
- Stop Heartbeat
- Refresh Status
- Quit

Show Console displays the window, Hide Window hides the window, and Quit is the only action that exits the process.

### Minimize To Tray

Default configuration:

```json
{
  "minimize_to_tray": true
}
```

Configuration file: `worker_console_desktop/src-tauri/desktop-runtime.json`. Closing the window hides it to the tray by default instead of exiting the app.

### Tray Runtime Control

Tray actions do not execute shell commands and do not perform remote command execution. Tray actions emit frontend events and the frontend calls the local Worker API:

- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`

### Desktop Status Sync

The desktop app periodically calls:

- `GET /local/status`
- `GET /local/health`

The tray tooltip shows `worker_name`, `current_status`, `runtime_running`, and `heartbeat_running`. The UI shows connected, reconnecting, disconnected, online, offline, error, last successful sync, and last error.

### AutoStart Placeholder

Placeholder docs live under `worker_console_desktop/autostart/`. They describe future Windows registry startup, macOS LaunchAgent, and start on login support. This phase does not register real autostart behavior.

### Current Boundary

There is no formal installer, no exe / dmg release, no real autostart registration, no auto-update, no remote shell, and no arbitrary command execution. The system still does not include TikTok / YouTube / X automation, account login, cookie injection, proxy pools, fingerprint bypass, captcha automation, or real platform automation.

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

## Phase 34 Browser Sessions Panel

Worker Console Web and Worker Console Desktop now include a Browser Sessions Panel for Remote Browser Runtime Foundation.

The panel shows:

- active sessions
- worker id
- browser
- status
- created_at
- current_url

Supported actions:

- refresh active sessions
- close a runtime session through `POST /api/v1/browser-runtime/sessions/{session_id}/close`

Client files:

- `worker_console/src/api/browserRuntimeClient.ts`
- `worker_console_desktop/src/api/browserRuntimeClient.ts`

This is not live streaming, not VNC, not noVNC, not DevTools remote UI, and not a browser-control visual stream.

## Phase 35B Worker Console Validation Checklist

Web Console:

```bash
cd worker_console
npm run dev
```

Open `http://localhost:5173` and check:

- `registered=true`
- `runtime_running=true`
- `heartbeat_running=true`
- `current_status=online`
- logs include heartbeat success
- Browser Sessions Panel can refresh sessions

Desktop Console:

```bash
cd worker_console_desktop
npm run tauri dev
```

If Rust/MSVC is not ready, mark `desktop native validation pending` and do not report native desktop validation as passed.

## Phase 35A Browser Runtime Timeline / Snapshots / Replay

Worker Console Web and Worker Console Desktop Browser Sessions Panel now includes:

- Timeline: calls `GET /api/v1/browser-runtime/sessions/{session_id}/events`
- Screenshot history: reads `snapshot_type=screenshot` from `browser_runtime_snapshots`
- Page snapshots: reads `snapshot_type=page` from `browser_runtime_snapshots`
- Replay metadata: calls `POST /api/v1/browser-runtime/sessions/{session_id}/replay`
- Replay export: calls `GET /api/v1/browser-runtime/replays/{replay_id}/export`
- Refresh events / Refresh snapshots: polling only, not live stream

Replay is metadata-only replay and does not re-run browser actions. There is no VNC, noVNC, DevTools remote control, live browser stream, TikTok / YouTube / X, login automation, cookie injection, proxy pool, fingerprint bypass, captcha automation, or real platform automation.

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
## Phase 38: Worker Console Chat Panel Bridge

Worker Console and Worker Console Desktop Chat Panels now display `route_name`, `selected_tool`, run status, result summary, `result_metadata`, and event payload. Browser Bridge, OpenClaw mock bridge, RAG bridge, Content bridge, and Planning bridge are shown through Conversation Runtime polling events. This is not WebSocket, not SSE, and not real platform automation.

## Phase 39: Conversation Approval Panel

Worker Console Web and Worker Console Desktop now show a pending approvals panel in the Chat Panel. The panel displays proposed action preview, proposed payload JSON, risk badge, approval_status, and approve / reject / cancel / execute approved action controls.

The Chat Panel uses `review_first` by default for user-triggered runs so Browser/OpenClaw style actions are visible before execution. It calls `GET /api/v1/conversations/{thread_id}/approvals` and the `/api/v1/conversation-approvals/{approval_id}` approve / reject / cancel / execute endpoints.

Current boundaries: not a full permission system, not WebSocket/SSE, no real platform publishing, no real OpenClaw, no login, no captcha, no proxy, and no fingerprint bypass.
## Phase 40: Worker Console Playbook Entry

Worker Console Web and Desktop Chat Panel now include a Playbook selector, Run playbook action, Playbook runs list, and Step timeline display.

This entrypoint is for customer-machine operators to trigger standardized Conversation Playbooks, while still keeping these limits:

- Polling only, not WebSocket/SSE.
- Pending approvals panel remains active.
- Medium/high risk steps require approval before execution.
- No full workflow builder.
- No real social publishing, login, captcha, proxy, fingerprint handling, or real OpenClaw execution.

## Phase 41: Worker Console Output Library

Worker Console Web and Desktop Chat Panel now include Output Library foundation views:

- generated artifacts list
- Save as Artifact for assistant messages
- artifact type / source type badges
- related `playbook_run_id`
- Export markdown

This lets operators inspect reusable `content_draft`, `report`, `rag_answer`, `screenshot`, `html_snapshot`, `plan`, and `json` outputs from Playbook / Conversation runs. It is an Output Library Foundation, not a full DAM, has no S3 / MinIO integration, and is not production publishing asset management.
## Phase 42: Task Orchestration & Background Execution

This phase adds the Task Orchestration foundation: `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, and `TaskRetryPolicy`. Conversation / Playbook runs can use `execution_mode=background`, then `/api/v1/task-runs` exposes queued, running, waiting_approval, retrying, completed, failed, cancelled, expired state plus timeline events. `scheduled_at` supports scheduled runs; retry uses exponential backoff; approval resume continues to enforce the Phase 39 Approval Gate; Output Library artifacts are linked by `task_run_id`.

Boundary: this is an in-process queue, not Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue. It does not implement real publishing, real OpenClaw, ComfyUI, CAPTCHA handling, proxies, or fingerprint bypass.
## Phase 43: Task Scheduler Persistence & Worker Recovery (Completed)

Completed: Task Scheduler Persistence, `task_scheduler_state`, Task Lease fields on `task_runs`, `TaskRecoveryService`, Scheduler Health API, manual recovery API, Failed Diagnostics, and frontend scheduler health panels.

Task Lease: running task runs receive `lease_owner`, `lease_token`, `lease_expires_at`, and `heartbeat_at`. Expired lease and stale heartbeat are recoverable through scan or manual recover.

Recovery rules: running + expired lease or stale heartbeat -> retrying if retry budget remains, otherwise failed; pending scheduled due -> queued; retrying delay elapsed -> queued; waiting_approval is not auto-executed; completed/cancelled/expired are not recovered.

Admin Dashboard now shows Scheduler Health, lease status, recoverable badge, diagnostics panel, scheduled due indicator, and manual recover. Worker Console and Worker Console Desktop show simplified Task recovery state.

Boundary: this remains an in-process scheduler foundation, not Celery, not Kubernetes, and not production HA distributed queue.
## Phase 43: Simplified Task Recovery Status

Worker Console Web and Worker Console Desktop show simplified scheduler and task recovery status: scheduler health, recovered count, lease expiry, recoverable state, suggested action, and manual recover. The console still does not run arbitrary shell commands and is not a production scheduler console.

<!-- PHASE44_CONSOLE:START -->
## Phase 44 Output Library Controls

Worker Console and Worker Console Desktop now show simplified Output Library controls for export, package, lineage summary, and retention status. They do not implement a full DAM, object storage platform, CDN, or real publishing workflow.
<!-- PHASE44_CONSOLE:END -->

<!-- PHASE44_SYNC:START -->
## Phase 44: Output Artifact Pipeline & Export System

Phase 44 adds the Output Artifact Pipeline & Export System on top of the Phase 41 Output Library and Phase 42/43 task runtime. It adds Artifact lineage, relationship graph tracking with `artifact_relationships`, export/package services, retention policy preview, and frontend Artifact Explorer controls.

Completed in this phase:

- `output_artifacts` now records `parent_artifact_id`, `root_artifact_id`, `source_task_run_id`, `source_playbook_run_id`, `source_conversation_id`, `source_runtime_session_id`, `artifact_role`, `artifact_stage`, `generated_by`, `exportable`, `retention_policy`, and `expires_at`.
- `artifact_relationships` records relationship graph edges such as `derived_from`, `packaged_into`, `summarized_from`, `exported_from`, and `replay_of`.
- `ArtifactExportService` supports `export_markdown`, `export_html`, `export_json`, `export_bundle_zip`, and `export_report_package` without re-running browser runtime or playbook execution.
- `ArtifactPackagingService` supports `package_playbook_run`, `package_task_run`, `package_browser_runtime_session`, and `package_conversation` to create package artifacts and `bundle.zip` metadata.
- `ArtifactRetentionService` supports retention policy, expiration scan, cleanup preview, and soft archive foundations. Current cleanup preview does not delete physical files.
- API additions include `GET /api/v1/output-artifacts/{artifact_id}/lineage`, `GET /api/v1/output-artifacts/{artifact_id}/relationships`, `POST /api/v1/output-artifacts/{artifact_id}/export`, `POST /api/v1/output-artifacts/{artifact_id}/package`, and `POST /api/v1/output-artifacts/cleanup/preview`.
- Storage roots now include `storage/output_artifacts`, `storage/output_packages`, and `storage/output_exports`.
- Admin Dashboard adds Artifact Explorer, lineage graph panel, export actions, package actions, retention badge, archived indicator, and bundle metadata preview.
- Worker Console and Worker Console Desktop expose simplified export, package, lineage summary, and retention status controls.

Boundaries:

- This is not a full DAM system.
- This is not a production object storage platform.
- There is no production S3 / MinIO / CDN integration.
- Export never re-executes Browser Runtime, Playbook, Conversation, OpenClaw, or Task actions.
- There is still no TikTok / YouTube / X automation, no automatic login, no captcha automation, no proxy pool, no fingerprint bypass, no real OpenClaw, and no ComfyUI.
<!-- PHASE44_SYNC:END -->

<!-- PHASE45_CONSOLE:START -->
## Phase 45 Worker Console: Workflow State Panel

Worker Console Web and Worker Console Desktop now show a simplified Workflow State panel with recent workflow runs, current step, checkpoint count, Agent Memory Snapshots summary, linked `workflow_run_id`, and Pause / Resume actions. Conversation, Task, and Output Library panels surface workflow references for operator context.

This is not a full workflow builder and not ComfyUI.
<!-- PHASE45_CONSOLE:END -->

<!-- PHASE45_SYNC:START -->
## Phase 45: Workflow State & Agent Memory Foundation

Status: completed.

Phase 45 adds recoverable Workflow State and Agent Memory Snapshots across Conversation, Playbook, Task, and Artifact runtime. It is a foundation for long multi-step automation, not a full workflow builder and not ComfyUI.

Completed scope:

- `workflow_runs` stores workflow status, source links, `conversation_thread_id`, `playbook_run_id`, `task_run_id`, `current_step`, variables, context, checkpoints, pause/resume/failure timestamps, and metadata.
- `workflow_steps` stores ordered step execution with `step_index`, `step_name`, `step_type`, status, input/output payloads, error, duration, and metadata.
- `workflow_checkpoints` stores immutable checkpoint records with auto/manual/approval/failure/resume checkpoint types plus state, variables, and context snapshots.
- `agent_memory_snapshots` stores durable memory snapshots for `conversation_summary`, `task_context`, `tool_result`, `decision`, `approval_context`, and `artifact_summary`.
- `WorkflowStateService` supports create workflow, list/get workflow, variables/context update, start/complete/fail step, pause workflow, resume workflow, complete workflow, fail workflow, create/restore checkpoint, create memory snapshot, and list memory snapshots.
- Conversation events now include `workflow_run_created`, `workflow_step_started`, `workflow_step_completed`, `workflow_checkpoint_created`, `workflow_paused`, `workflow_resumed`, and `memory_snapshot_created`.
- Playbook and Task execution now optionally link to `workflow_run_id`; each playbook step can create a `workflow_step`; waiting approval moves workflow status to `waiting_approval`; completion/failure creates final/failure checkpoints.
- Output Artifact lineage now supports `workflow_run_id`, `workflow_step_id`, `checkpoint_id`, and `memory_snapshot_id` so artifacts can be traced back to workflow state.
- Admin Dashboard adds Workflow Runs with step timeline, variables viewer, context viewer, checkpoints list, Agent Memory Snapshots, and Pause / Resume controls.
- Worker Console and Worker Console Desktop show simplified Workflow State, current step, checkpoint count, memory summary, and linked workflow ids.

API coverage:

- `GET /api/v1/workflow-runs`
- `GET /api/v1/workflow-runs/{workflow_run_id}`
- `GET /api/v1/workflow-runs/{workflow_run_id}/steps`
- `GET /api/v1/workflow-runs/{workflow_run_id}/checkpoints`
- `POST /api/v1/workflow-runs/{workflow_run_id}/pause`
- `POST /api/v1/workflow-runs/{workflow_run_id}/resume`
- `POST /api/v1/workflow-runs/{workflow_run_id}/checkpoints`
- `GET /api/v1/workflow-runs/{workflow_run_id}/memory-snapshots`
- `POST /api/v1/workflow-runs/{workflow_run_id}/memory-snapshots`
- `GET /api/v1/agent-memory-snapshots`

Boundaries: this is not a full workflow builder, not ComfyUI, not WebSocket/SSE streaming, not real OpenClaw, not real social-platform publishing, and not TikTok / YouTube / X automation. It does not add automatic login, CAPTCHA automation, proxy pools, or fingerprint bypass.
<!-- PHASE45_SYNC:END -->
