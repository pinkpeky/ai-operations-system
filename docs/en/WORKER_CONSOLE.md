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

<!-- PHASE46_SYNC:START -->
## Phase 46: Workflow Graph Runtime in Worker Console

Worker Console and Worker Console Desktop now show a simplified graph execution panel:

- `current_node_key`
- `planned_next_nodes`
- `skipped_nodes`
- `retry_state`
- `fallback_state`
- Workflow step `node_key`
- replay metadata request for `workflow_replays`
- Artifact graph lineage summary with `producing_node_key`, `replay_source`, and `graph_lineage`

This is a status and debugging view for Workflow Graph Runtime & Conditional Execution. It is not a visual DAG builder, not a drag/drop workflow editor, not distributed orchestration engine, and not ComfyUI.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47: Worker Console Template Library

Worker Console Web and Worker Console Desktop add a simplified Template Library:

- `worker_console/src/api/workflowTemplateClient.ts` and `worker_console_desktop/src/api/workflowTemplateClient.ts` call AI Server template APIs.
- Supports list templates, select template, run template, and view template run status.
- Shows built-in templates: `browser_screenshot_report_graph`, `content_generation_graph`, `rag_answer_graph`, `approval_then_browser_graph`, `openclaw_mock_inspect_graph`, and `task_retry_demo_graph`.
- Shows `workflow_template_id`, `workflow_template_version_id`, `workflow_template_run_id`, `validation_status`, and `compatibility` summaries.

This is a template entry and run-status view only. It is not a visual DAG builder, not a drag/drop workflow editor, not ComfyUI, and not real platform automation.
<!-- PHASE47_SYNC:END -->

<!-- PHASE48_SYNC:START -->
## Phase 48: Workflow Template Marketplace & Governance Foundation

Status: completed.

Phase 48 adds an internal Workflow Template Marketplace & Governance foundation on top of Phase 47 Workflow Template Registry & Versioning. It is an internal template library and governance layer, not public marketplace, not a paid marketplace, not multi-tenant SaaS marketplace, not a visual DAG editor, and not ComfyUI.

Completed scope:

- Added `workflow_template_reviews` for review queue, `review_status`, `risk_assessment`, `compatibility_report`, approve / reject / request changes.
- Added `workflow_template_promotions` to record activate, rollback, deprecate, and archive lifecycle events with `promotion_type`, source version, target version, and reason.
- Added `workflow_template_audit_logs` for governance audit trail, actor, previous_state, new_state, and metadata.
- Added `workflow_template_compatibility_matrix` for runtime capabilities: `browser_runtime`, `approval_gate`, `task_scheduler`, `artifact_pipeline`, `workflow_graph_runtime`, `openclaw_mock`, and `rag_pipeline`.
- Added `WorkflowTemplateGovernanceService` with `submit_for_review`, `approve_review`, `reject_review`, `request_changes`, `activate_template_version`, `rollback_template_version`, `deprecate_template`, `archive_template`, `list_review_queue`, and `list_governance_events`.
- Template lifecycle is draft -> review -> approved -> active -> deprecated -> archived. Activation requires approved review; only one active version is default; deprecated templates are not default-runnable; archived templates cannot run; rollback does not delete old versions.
- Marketplace foundation records `featured`, `verified`, `recommended`, `usage_count`, `success_rate`, `average_runtime_ms`, and `average_step_count` on `workflow_templates`, then exposes governance badges, risk badge, verified badge, featured templates, and recommended templates.
- Output Artifact lineage adds `source_template_review_id` and `governance_state`; Workflow Runs can record template governance state and compatibility snapshot.
- Admin Dashboard adds Template Governance with Review Queue, Approval / Reject / Request Changes, Template Lifecycle View, Audit Log View, Marketplace View, Compatibility Matrix View, and Rollback UI.
- Worker Console and Worker Console Desktop show governance status, template verification status, and compatibility summary in Template Library.

API coverage:

- `GET /api/v1/workflow-template-reviews`
- `POST /api/v1/workflow-template-reviews`
- `POST /api/v1/workflow-template-reviews/{review_id}/approve`
- `POST /api/v1/workflow-template-reviews/{review_id}/reject`
- `POST /api/v1/workflow-template-reviews/{review_id}/request-changes`
- `POST /api/v1/workflow-templates/{template_id}/rollback/{version_id}`
- `POST /api/v1/workflow-templates/{template_id}/deprecate`
- `POST /api/v1/workflow-templates/{template_id}/archive`
- `GET /api/v1/workflow-template-audit-logs`
- `GET /api/v1/workflow-template-marketplace`
- `GET /api/v1/workflow-template-compatibility-matrix`

Boundaries: Phase 48 is not public marketplace, not a visual DAG builder, not a distributed orchestration platform, not ComfyUI, not TikTok / YouTube / X automation, not real platform publishing, not automatic login, not CAPTCHA automation, not proxy pool, and not fingerprint bypass.
<!-- PHASE48_SYNC:END -->

## Phase 49: Workflow Run Observability & Replay Center

Completed the Workflow Run Observability & Replay Center foundation: added `workflow_execution_traces`, `workflow_runtime_diagnostics`, `workflow_replay_sessions`, and integrated `WorkflowExecutionTraceService` plus `WorkflowDiagnosticsService`. The runtime now records node_started / node_completed / node_failed / planner_decision / retry_triggered / fallback_triggered / approval_wait / approval_resume / replay_started / replay_completed for Execution Trace, Runtime Summary, Failure Hotspots, Replay Center, and metadata_only / dry_run replay sessions.

New APIs: `GET /api/v1/workflow-runs/{workflow_run_id}/traces`, `GET /api/v1/workflow-runs/{workflow_run_id}/diagnostics`, `GET /api/v1/workflow-runs/{workflow_run_id}/analytics`, `POST /api/v1/workflow-runs/{workflow_run_id}/replay-sessions`, `GET /api/v1/workflow-runs/{workflow_run_id}/runtime-summary`, `GET /api/v1/workflow-replay-sessions`, and `GET /api/v1/workflow-replay-sessions/{replay_session_id}`.

Admin Dashboard now includes Replay Center / Workflow Observability views for Execution Trace Timeline, Node Inspection Panel, Retry/Fallback Visualization, Diagnostics Panel, Runtime Summary, Replay Session View, Failure Hotspots, and Approval Wait Visualization. Worker Console / Desktop show a simplified trace timeline, replay session status, diagnostics summary, and retry/fallback counters.

Boundaries: this is not a distributed tracing platform, not an OpenTelemetry stack, not WebSocket/SSE realtime, not a deterministic replay engine, not a visual DAG editor, does not connect ComfyUI, does not perform real social publishing, and does not implement Kubernetes orchestration.

Keywords: not distributed tracing platform; not deterministic replay engine; not ComfyUI.

## Phase 50: Desktop Console Runtime UX & Client Packaging Readiness

Phase 50 adds Desktop Console Runtime UX & Client Packaging Readiness. The Tauri icon resource is now explicit: `worker_console_desktop/src-tauri/icons/icon.ico` is a valid local placeholder icon and `bundle.icon` points to `["icons/icon.ico"]`.

Start Runtime diagnostics now surface clear states: `starting`, `started`, `failed`, `unavailable`, `port_conflict`, `missing_config`, and `server_environment_warning`. The Desktop Console shows local worker diagnostics for `/local/status`, `/local/health`, runtime port, `server_url`, `worker_base_url`, last attempted action, last error detail, and last successful sync.

Server/client boundary: Desktop Console controls the worker runtime on this local machine. If running on the server host, Start Runtime starts a server-local worker, not a remote customer machine. For real client E2E, run this app on the customer machine.

This phase is packaging readiness only: not final installer, no code signing, no auto updater, no MSI/EXE release packaging, and not ComfyUI.

Keywords: Desktop Console Runtime UX & Client Packaging Readiness; Tauri icon resource; icons/icon.ico; bundle.icon; Start Runtime diagnostics; missing_config; port_conflict; server_environment_warning; local worker diagnostics; customer machine; not final installer; no code signing; no auto updater.
<!-- PHASE51_SYNC:START -->
## Phase 51: Release Packaging & Deployment Bundle Foundation

Status: completed.

Phase 51 adds the Release Packaging & Deployment Bundle Foundation. It introduces a `release/` directory with `release/manifest.json`, `release/version.json`, `release/env/aiops.release.env.template`, server deployment bundle scripts, frontend production build bundle scripts, desktop release readiness scripts, Windows / Mac startup scripts, and `release/scripts/validate_release_packaging.py`.

Packaging architecture:

- Server deployment bundle: `release/scripts/build_server_bundle.ps1` and `release/scripts/build_server_bundle.sh` collect API server, worker, worker_client, Alembic, Docker, docs runtime metadata, and env template sources under ignored `release/build/server`.
- Frontend production build bundle: `release/scripts/build_frontend_bundles.ps1` and `release/scripts/build_frontend_bundles.sh` run production builds for Admin Dashboard, Worker Console, and Worker Console Desktop frontend assets, then copy `dist` output under ignored `release/build/frontends`.
- Desktop release readiness: `release/scripts/check_desktop_release_readiness.ps1` and `.sh` verify Tauri config, `icons/icon.ico`, package metadata, and Cargo/toolchain presence without producing a signed installer.
- Version metadata: `release/version.json` records Phase 51 package metadata and component readiness.
- Release manifest: `release/manifest.json` is the packaging SSOT for components, outputs, startup scripts, validation script, and forbidden runtime artifacts.
- Validation: `release/scripts/validate_release_packaging.py` checks required files, manifest JSON, version JSON, desktop icon config, boundaries, and forbidden artifact declarations.

Boundaries: Phase 51 is not a formal production release, no code signing, no auto updater, no MSI/EXE formal installer, no DMG/notarization, no Kubernetes/Helm packaging, no ComfyUI, and no real social platform publishing.

 Phase 51  release readiness  code signing, auto updater, MSI/EXE, DMG/notarization, Kubernetes/Helm.

Keywords: Phase 51; Release Packaging & Deployment Bundle Foundation; release/manifest.json; release/version.json; server deployment bundle; frontend production build bundle; desktop release readiness; aiops.release.env.template; validate_release_packaging.py; Windows / Mac startup scripts; not a formal production release; no code signing; no auto updater; no MSI/EXE; no DMG/notarization; no Kubernetes/Helm.
<!-- PHASE51_SYNC:END -->
<!-- PHASE52_SYNC:START -->
## Phase 52: Deployment Profiles & Environment Bootstrap

Status: completed.

Phase 52 adds Deployment Profiles & Environment Bootstrap on top of Phase 51 release packaging. It introduces `deployment/` with profile-based configuration for `local-dev`, `server-docker`, `client-worker`, `desktop-client`, `staging`, and `production-like`. Each profile contains `profile.json`, `env.template`, `ports.json`, `services.json`, `healthchecks.json`, and `README.md`.

Completed scope:

- `deployment/scripts/generate_env.py` generates `.env.generated` or a specified output from a profile `env.template`, supports override JSON, validates required keys, and refuses to overwrite existing env files without `--force`.
- `deployment/scripts/check_dependencies.py` checks Python, Docker, Docker Compose, Node/npm, Git, Playwright/client worker advisories, Rust/cargo, MSVC/link.exe on Windows, Tauri icon readiness, and WebView2 advisory by profile.
- `deployment/scripts/check_ports.py` checks API 8000, Admin Dashboard 5180, Worker Console 5173, Desktop Console 5174, Worker Runtime 9100, PostgreSQL 5432, Redis 6379, and Qdrant 6333 from each profile `ports.json`; it reports process hints and never kills processes.
- `deployment/scripts/verify_environment.py` verifies `server-docker`, `client-worker`, and `desktop-client` health: docker compose ps, API health, browser-worker health, workflow routes smoke, task-runs smoke, output-artifacts smoke, local worker status/health, Tauri config/icon, and frontend build presence where applicable.
- Added Windows / Mac startup scripts under `deployment/windows/` and `deployment/mac/` for server Docker, Admin Dashboard, Worker Console, Desktop Console, client worker, and profile verification.
- Release integration updates `release/manifest.json`, `release/version.json`, `release/README.md`, and `release/scripts/validate_release_packaging.py` to include deployment profiles, bootstrap scripts, dependency checks, port checks, and profile verification.
- Admin Dashboard, Worker Console, and Worker Console Desktop Settings / Help now show recommended profile, AI Server URL, Workspace ID, User ID, Local Worker API, server/client/desktop role differences, and profile bootstrap docs link.

Boundaries: Phase 52 is not Kubernetes/Helm/Terraform, not Ansible, not production HA, not code signing, not an auto updater, not a formal installer, not ComfyUI, and not real social platform publishing.

Keywords: Phase 52; Deployment Profiles & Environment Bootstrap; local-dev; server-docker; client-worker; desktop-client; staging; production-like; generate_env.py; check_dependencies.py; check_ports.py; verify_environment.py; env generation; dependency checks; port checks; health verification; profile bootstrap docs; Kubernetes/Helm/Terraform.
<!-- PHASE52_SYNC:END -->

## Phase 62I Workstation/Customer Client Frontend UX Alignment

Status: in progress on `codex/phase-62i-workstation-client-ux`.

Phase 62I aligns the customer-machine frontends for workstation operators and server maintenance handoff. `worker_console` and `worker_console_desktop` now expose a simplified operator home with local connection, Worker runtime, heartbeat, and recovery status cards.

Operator workflow:

- Confirm the local Worker API is reachable.
- Start local runtime or heartbeat from the customer-machine console.
- Jump directly to conversation, playbook, approvals, outputs, task runs, and logs.
- Use Chinese/English language switching for workstation and maintenance operators.
- Read setup, help, recovery, and server-vs-customer-machine boundary guidance in the first screen.

Boundary: Phase 62I is a frontend/readiness slice. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62K Customer Console Codex-like UX Simplification

Status: in progress on `codex/phase-62k-customer-console-codex-ux`.

Phase 62K simplifies the customer-machine frontends after live operator feedback. `worker_console` and `worker_console_desktop` now open with a Codex-like command surface instead of a dense maintenance dashboard.

Operator workflow:

- Read local Worker API, runtime, heartbeat, and recovery state in a left status rail.
- Follow one clear next-step prompt before using advanced tools.
- Use the first-screen conversation input to send and run a customer-machine task.
- Keep playbooks, approvals, outputs, tasks, and logs reachable through shortcuts.
- Open advanced maintenance and diagnostics only when needed.

Boundary: Phase 62K is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62L Customer Console Task Workbench

Status: in progress on `codex/phase-62l-client-task-workbench`.

Phase 62L builds on the Codex-like customer-machine surface by adding a focused task workbench to `worker_console` and `worker_console_desktop`.

Operator workflow:

- Enter an operating goal in the first workbench input.
- Follow the suggested next action when approvals, active tasks, or failed/recoverable tasks exist.
- See pending approval count, active task count, failed/recoverable task count, and artifact count without opening maintenance panels.
- Keep playbooks, templates, approvals, messages/events, outputs, workflow state, and task recovery available as expandable detail sections.
- Keep advanced maintenance and diagnostics behind a separate disclosure.

Boundary: Phase 62L is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62M Customer Console Goal Templates

Status: in progress on `codex/phase-62m-client-goal-templates`.

Phase 62M adds standard goal templates to the first customer-machine task workbench in `worker_console` and `worker_console_desktop`.

Operator workflow:

- Choose a launch content, RAG evidence, asset brief, or page report template.
- Let the template prefill the operating goal.
- Let the template select the recommended playbook.
- Run now or queue in the background through the existing approval-gated actions.
- Keep advanced maintenance and diagnostics behind a separate disclosure.

Boundary: Phase 62M is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62N Customer Console Goal Plan Preview

Status: in progress on `codex/phase-62n-client-goal-plan-preview`.

Phase 62N adds a compact plan preview to the selected customer-machine goal template in `worker_console` and `worker_console_desktop`.

Operator workflow:

- Choose a goal template.
- Review the planned steps before running.
- Confirm the approval boundary and expected output.
- Continue with the existing run-now or background actions.
- Keep advanced maintenance and diagnostics behind a separate disclosure.

Boundary: Phase 62N is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62O Customer Console Goal Status Tracker

Status: in progress on `codex/phase-62o-client-goal-status-tracker`, draft PR #81.

Phase 62O adds a compact goal status tracker to the selected customer-machine goal in `worker_console` and `worker_console_desktop`.

Operator workflow:

- Choose a goal template and review the plan preview.
- Check prepare, approval, execution, recovery, and output status from one tracker.
- See current run status, thread id, task id, pending approvals, active tasks, failed/recoverable tasks, and artifacts.
- Continue with existing run-now, background, approval, and recovery actions.
- Keep advanced maintenance and diagnostics behind a separate disclosure.

Boundary: Phase 62O is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62P Customer Console Simple Operator Mode

Status: active branch `codex/phase-62p-client-simple-operator-mode`, draft PR #82.

Phase 62P simplifies `worker_console` and `worker_console_desktop` again after customer-machine feedback. The default task page now emphasizes one goal input, common task chips, a visual current-progress card, and collapsed maintenance details for approvals, playbooks, outputs, workflows, tasks, and diagnostics.

Phase 62P also adds a separate knowledge base upload/edit page. The knowledge base upload/edit page is visual and does not display code or JSON. It supports:

- file upload to the existing RAG ingest/file upload APIs
- text material add/update
- collection and duplicate handling controls
- upload queue cards
- document cards with edit shortcuts
- refresh controls for the current knowledge material

Boundary: Phase 62P is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62Q Customer Console Knowledge Upload Readiness

Status: active branch `codex/phase-62q-knowledge-upload-readiness`, draft PR #83.

Phase 62Q improves the separate visual knowledge base upload/edit page in `worker_console` and `worker_console_desktop`. It keeps the page operator-facing and does not display code or JSON.

Operator workflow:

- Check knowledge upload readiness before selecting files.
- Confirm connection, collection, queue, and library status from visual cards.
- See supported file rules for PDF, DOCX, TXT, MD, and CSV.
- Block unsupported files and files larger than 20 MB before upload.
- Retry failed uploadable files, remove queue items, and clear completed files.
- Follow the next-step card to choose files, wait for upload, recover failures, or use the knowledge library.

Boundary: Phase 62Q is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62R Customer Console Knowledge Activity Timeline

Status: active branch `codex/phase-62r-knowledge-activity-timeline`, draft PR #84.

Phase 62R improves the separate visual knowledge base upload/edit page in `worker_console` and `worker_console_desktop` with a knowledge activity timeline. It keeps the page operator-facing and does not display code or JSON.

Operator workflow:

- Select files and see a recent activity record for the selected batch.
- Upload files and see success/failure counts in the activity timeline.
- Save text material and see a plain activity record with collection context.
- Refresh the library and see whether the refresh succeeded or failed.
- Remove queue files or clear completed items and keep those actions visible.
- Clear activity when the operator no longer needs the local timeline.

Boundary: Phase 62R is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62S Customer Console Knowledge Document Details

Status: active branch `codex/phase-62s-knowledge-document-details`, draft PR #85.

Phase 62S improves the separate visual knowledge base upload/edit page in `worker_console` and `worker_console_desktop` with knowledge document details. It keeps the page operator-facing and does not display code or JSON.

Operator workflow:

- Review the document processing overview for total material, search-ready material, items needing review, and the currently selected material.
- Select a document card to view plain details without opening diagnostics.
- Confirm source id, collection, status, chunk count, created time, and updated time from the details panel.
- Use the selected document for update so the edit form is prefilled with the document identity.
- Keep upload readiness and recent activity visible while inspecting document readiness.

Boundary: Phase 62S is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62T Customer Console Knowledge Search Validation

Status: active branch `codex/phase-62t-knowledge-search-validation`, draft PR #86.

Phase 62T improves the separate visual knowledge base upload/edit page in `worker_console` and `worker_console_desktop` with knowledge search validation. It lets customer-machine operators confirm that uploaded or edited material can be retrieved without reading code or JSON.

Operator workflow:

- Enter a validation question for the current knowledge collection.
- Choose hybrid, semantic, or keyword search.
- Run validation through the existing RAG search endpoint.
- Review matched snippets, source labels, chunk indexes, and score summaries as visual cards.
- Use empty-result guidance to decide whether to adjust the query, check the collection, or upload material again.
- Keep validation attempts in the recent activity timeline.

Boundary: Phase 62T is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62U Customer Console Knowledge Ingestion Status Loop

Status: active branch `codex/phase-62u-knowledge-ingestion-status`, draft PR #87.

Phase 62U improves the separate visual knowledge base upload/edit page in `worker_console` and `worker_console_desktop` with a knowledge ingestion status loop. It lets customer-machine operators understand what happened after upload or text update without reading code or JSON.

Operator workflow:

- See queued, uploading, processing, search-ready, and needs-review counts.
- Follow a simple selected -> upload -> chunk/index -> search validation pipeline.
- Review latest upload results with source IDs, document IDs, chunk counts, duplicate-skip notes, and failure reasons.
- Refresh document status or retry recoverable failed uploads from the same visual panel.
- Inspect selected-document ingestion status and error messages in the details panel.

Boundary: Phase 62U is frontend-only. It uses existing file upload, document list, text ingest, reingest, and RAG search APIs. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62V Customer Console Knowledge Validation Guidance

Status: active branch `codex/phase-62v-knowledge-validation-guidance`, draft PR #88.

Phase 62V improves the separate visual knowledge base upload/edit page in `worker_console` and `worker_console_desktop` with knowledge validation guidance. It helps customer-machine operators validate selected or newly uploaded material without inventing search terms and without reading code or JSON.

Operator workflow:

- Use suggested validation questions for core content, risks and limits, and execution notes.
- Validate the currently selected material or the latest upload from compact target cards.
- Fill a validation question with one click, or run the suggested question immediately.
- Keep validation results in the same visual search result cards and activity flow.
- Keep the knowledge page focused on upload, ingestion, validation, and document readiness.

Boundary: Phase 62V is frontend-only. It uses existing file upload, document list, text ingest, reingest, and RAG search APIs. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62W Customer Console Knowledge Validation Outcomes

Status: active branch `codex/phase-62w-knowledge-validation-outcomes`.

Phase 62W improves the separate visual knowledge base upload/edit page in `worker_console` and `worker_console_desktop` with knowledge validation outcomes. It turns validation hits into a clear operator decision without showing code or JSON.

Operator workflow:

- Run validation from a suggested question or manual question.
- See whether the material is ready for operations, needs more evidence, or needs human review.
- Check evidence count, material context, and validation mode in compact outcome stats.
- Retry validation when evidence is missing or mark the material ready when the validation result is usable.
- Keep outcome decisions in the local activity timeline.

Boundary: Phase 62W is frontend-only. It uses existing file upload, document list, text ingest, reingest, and RAG search APIs. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62X Customer Console Product Operation Desk

Branch: `codex/phase-62x-client-operation-desk`

Phase 62X moves `worker_console` and `worker_console_desktop` toward the actual customer-machine operation loop with a product operation desk. The first task surface now highlights product/campaign topic input, current process, execution result, interrupt/continue controls, deliverables, and knowledge upload access.

Operator-facing loop:
- Product or campaign topic
- System task planning
- Knowledge base use
- Content production for copy, video, data analysis, and operating direction
- Human approval
- OpenClaw/Playwright client execution positioning
- Result recording
- Data observation
- Data analysis and content improvement

Boundary: Phase 62X is frontend-only. It does not execute OpenClaw, run Playwright, publish to social media, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval. It only makes the customer-machine product operation desk easier for ordinary operators to understand before real guarded execution adapters are enabled.

## Phase 63A Customer Console Loop Protocol Binding

Branch: `codex/phase-63a-client-loop-protocol-binding`

Phase 63A binds `worker_console` and `worker_console_desktop` to the commercial operation loop protocol. The customer-machine task page can create an operation from the current goal, refresh `GET /api/v1/commercial-operations/{operation_id}/operation-loop`, show the shared operation-loop status, and fall back to local task state when no server loop is available.

Operator-visible behavior:

- Start from one operation goal and create the loop without reading JSON.
- See the current loop stage, next action, deliverables, and knowledge upload access.
- Refresh the real `operation-loop` status while keeping interrupt, continue, output, and knowledge controls in one concise surface.

Boundary: Phase 63A is API-bound UI only. It does not execute OpenClaw, run Playwright, publish to social media, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63B Customer Console First Draft Bootstrap

Branch: `codex/phase-63b-client-first-draft-bootstrap`

Phase 63B adds the first draft bootstrap to `worker_console` and `worker_console_desktop`. From the same customer-machine operation desk, an operator can prepare the first reviewable output after creating or selecting an operation loop.

The action performs a guarded record-only sequence:

- Regenerate the commercial operation plan.
- Create the first content draft from the current goal.
- Mark the draft ready for human review.
- Create a human approval gate for that first draft.
- Refresh `operation-loop` so the stage and next action update.

Boundary: Phase 63B is first draft and approval bootstrap only. It does not execute OpenClaw, run Playwright, publish to social media, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63C Customer Console Approval and Execution Prep

Branch: `codex/phase-63c-client-approval-execution-prep`

Phase 63C adds the next usable customer-machine loop step to `worker_console` and `worker_console_desktop`. From the same product operation desk, an operator can approve or reject the pending commercial approval gate after the first draft is prepared.

The approval-and-prep action performs a guarded record-only sequence:

- Approve the pending commercial operation approval gate.
- Approve the linked content draft.
- Create, review, approve, and package a deliverable from the approved draft.
- Create a metadata-only `openclaw` execution prep request for `customer_machine_playwright`.
- Mark that execution request ready for pre-run review without executing it.

The reject action rejects the commercial approval gate and the linked content draft so the operator can revise and prepare a new version.

Boundary: Phase 63C is approval and execution prep only. It creates metadata-only execution prep records. It does not execute OpenClaw, run Playwright, publish to social media, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63D Customer Console Execution Run Review

Branch: `codex/phase-63d-client-execution-run-review`

Phase 63D adds the next customer-machine loop step to `worker_console` and `worker_console_desktop`. After Phase 63C creates the metadata-only execution prep request, an operator can review that prep request and create a recoverable execution run record from the same product operation desk.

The execution-run review action performs a guarded record-only sequence:

- Find the latest execution prep request.
- Move it through ready, approved, and prepared states when needed.
- Create a metadata-only execution run record for `customer_machine_playwright`.
- Keep the run queued until the operator explicitly marks it started.

The run controls let the operator mark a queued run started, record a running run as failed, and retry a failed run. These controls make interruption and recovery visible without starting real OpenClaw or Playwright automation.

Boundary: Phase 63D is execution run review and recovery tracking only. It creates metadata-only execution run records. It does not execute OpenClaw, run Playwright, publish to social media, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63E Customer Console Result Feedback Loop

Branch: `codex/phase-63e-client-result-feedback-loop`

Phase 63E adds the minimum usable closed loop to `worker_console` and `worker_console_desktop`. After a customer-machine execution run exists, the operator can record the outcome and create the next improvement signal from the same product operation desk.

The result feedback action performs a guarded record-only sequence:

- Reuse a succeeded/failed/cancelled execution run, or start and complete a queued/running metadata-only run.
- Create, mark ready, and approve a commercial result record.
- Create, mark ready, and approve a monitoring observation with manual metric placeholders.
- Create, mark ready, and approve an optimization decision for the next content iteration.

The first deliverable product loop is therefore visible end to end: topic, task planning, knowledge/material use, content draft, human approval, execution prep, execution run, result record, data observation, and next improvement decision.

Boundary: Phase 63E is result feedback and next-iteration planning only. It creates metadata-only result, observation, and optimization records. It does not execute OpenClaw, run Playwright, publish to social media, ingest platform analytics, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63F Customer Console Next-Cycle Content Drafts

Branch: `codex/phase-63f-next-cycle-content-drafts`

Phase 63F connects the approved improvement decision back into content production for `worker_console` and `worker_console_desktop`. After Phase 63E completes the result, observation, and optimization records, the operator can generate the next-cycle content draft from the same product operation desk.

The next-cycle draft action performs a guarded record-only sequence:

- Require an approved optimization decision.
- Create or reuse a next-cycle content draft linked to that decision.
- Mark the draft ready for human review.
- Create or reuse a human approval gate for the next-cycle draft.
- Refresh `operation-loop` so the operator can continue into approval and execution prep again.

This makes the first usable closed loop repeatable: topic, planning, knowledge/material use, first content draft, approval, execution prep, execution run, result, observation, optimization decision, and next-cycle content draft.

Boundary: Phase 63F is next-cycle content draft and approval bootstrap only. It creates metadata-only content draft and approval records from approved optimization decisions. It does not execute OpenClaw, run Playwright, publish to social media, ingest platform analytics, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63G Customer Console Next-Cycle Execution Prep

Branch: `codex/phase-63g-next-cycle-execution-prep`

Phase 63G connects the next-cycle approval gate back into execution preparation for `worker_console` and `worker_console_desktop`. After Phase 63F creates a next-cycle content draft and human approval gate, the same customer-machine approval button can recognize that next-cycle gate and prepare the second execution pass.

The next-cycle execution prep action performs a guarded record-only sequence:

- Prefer pending approvals created from the next-cycle content draft.
- Approve or reject them with next-cycle wording.
- Approve the linked next-cycle content draft.
- Package a next-cycle deliverable with the approved optimization decision linkage.
- Create a metadata-only execution prep request for the second iteration.

This keeps the repeatable closed loop usable without adding a new complex page: the operator can move from result feedback to next draft, next approval, and next execution prep from the same product operation desk.

Boundary: Phase 63G is next-cycle execution prep only. It creates metadata-only deliverable and execution prep records from approved next-cycle drafts. It does not execute OpenClaw, run Playwright, publish to social media, ingest platform analytics, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63H Customer Console Next-Cycle Execution Run Review

Branch: `codex/phase-63h-next-cycle-execution-run-review`

Phase 63H connects next-cycle execution prep back into execution run tracking for `worker_console` and `worker_console_desktop`. After Phase 63G creates a next-cycle metadata-only execution prep request, the same review-and-queue action can prefer that request and create the second execution run record.

The next-cycle execution run review action performs a guarded record-only sequence:

- Prefer next-cycle execution prep requests when reviewing runnable requests.
- Move draft/ready/approved requests through the existing review path.
- Create a metadata-only next-cycle execution run record.
- Keep the run queued until the operator explicitly starts it.
- Reuse the existing start, failure, retry, result, observation, and improvement controls.

This keeps the repeatable closed loop moving through the same simple task desk without a new page or a separate second-round workflow.

Boundary: Phase 63H is next-cycle execution run review only. It creates metadata-only execution run records from next-cycle execution prep requests. It does not execute OpenClaw, run Playwright, publish to social media, ingest platform analytics, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63I Customer Console Next-Cycle Result Feedback Loop

Branch: `codex/phase-63i-next-cycle-result-feedback-loop`

Phase 63I connects next-cycle execution runs back into result feedback for `worker_console` and `worker_console_desktop`. After Phase 63H creates a metadata-only next-cycle execution run, the same result-and-improve action can prefer that run and create the second result, observation, and optimization records.

The next-cycle result feedback action performs a guarded record-only sequence:

- Prefer next-cycle execution runs when recording result feedback.
- Start and complete queued metadata-only next-cycle runs when needed.
- Create or reuse the result record for the next-cycle run.
- Create or reuse the manual monitoring observation for that result.
- Create or reuse an approved optimization decision for another iteration.
- Preserve `previous_optimization_decision_id` and `next_iteration` lineage for the next draft.

This keeps the repeatable closed loop usable without adding a complex page: the operator can move from next execution run to next result, next observation, next improvement, and another content draft from the same product operation desk.

Boundary: Phase 63I is next-cycle result feedback only. It creates metadata-only result, observation, and optimization records from next-cycle execution runs. It does not execute OpenClaw, run Playwright, publish to social media, ingest platform analytics, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63J Customer Console Client Runtime Preflight

Branch: `codex/phase-63j-client-runtime-preflight`

Phase 63J connects queued/retrying execution runs to customer-machine runtime readiness for `worker_console` and `worker_console_desktop`. After Phase 63D or Phase 63H creates a metadata-only execution run, the same product operation desk can run a client runtime preflight before any operator start.

The client runtime preflight action performs a guarded record-only sequence:

- Prefer queued/retrying next-cycle execution runs when available.
- Read the local Worker API status and health from the customer machine.
- Check worker registration, runtime, heartbeat, OpenClaw capability, browser capability, localhost-only health, and approval requirement.
- Patch the execution run with a metadata-only `client_runtime_preflight` payload.
- Mark the preflight as `ready` or `blocked` without starting OpenClaw or Playwright.
- Preserve cycle and optimization lineage for later run/result records.

This gives ordinary operators a simple Run preflight step before future real adapter work arrives, while maintainers can inspect the recorded readiness and recovery reason.

Boundary: Phase 63J is client runtime preflight only. It patches queued/retrying execution runs with local readiness metadata. It does not execute OpenClaw, run Playwright, publish to social media, ingest platform analytics, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63K Customer Console Guarded Adapter Dispatch Handoff

Branch: `codex/phase-63k-guarded-adapter-dispatch-handoff`

Phase 63K connects client runtime preflight readiness to a guarded adapter dispatch handoff for `worker_console` and `worker_console_desktop`. After Phase 63J records a ready or blocked preflight on a queued/retrying execution run, the same product operation desk can prepare the handoff record before any operator start.

The guarded adapter dispatch handoff action performs a guarded record-only sequence:

- Prefer queued/retrying next-cycle execution runs with ready client runtime preflight.
- Fall back to queued/retrying runs and record a blocked handoff when preflight is missing.
- Patch the execution run with a metadata-only `guarded_adapter_dispatch_handoff` payload.
- Record explicit disabled flags for OpenClaw, Playwright, publishing, and account control.
- Preserve cycle, previous source, preflight status, and optimization lineage.
- Keep the run waiting for explicit operator start.

This gives ordinary operators a simple Prepare handoff step between preflight and start, while maintainers can inspect why a handoff is ready or blocked before future real adapters arrive.

Boundary: Phase 63K is guarded adapter dispatch handoff only. It patches queued/retrying execution runs with local handoff metadata. It does not execute OpenClaw, run Playwright, publish to social media, ingest platform analytics, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63L-63N Customer Console Execution and Approval Loop

Branch: `codex/phase-63l-63n-execution-approval-loop`

Phase 63L-63N moves the customer-machine loop from guarded handoff into a safer first execution pass for `worker_console` and `worker_console_desktop`. The product operation desk now has a guarded adapter dry-run action after preflight and handoff, a visual client execution queue for queued/running/failed/succeeded records, and a commercial approval center that lets operators approve or reject specific operation approvals without raw JSON.

The guarded adapter dry-run action records `guarded_adapter_dry_run` metadata, starts the existing metadata-only execution run, marks it succeeded with a dry-run result payload, and keeps all external-action flags disabled. The client execution queue shows status, target, retry count, and readiness in simple cards. The commercial approval center keeps approval decisions visible and separate from the general conversation approval queue.

Boundary: Phase 63L-63N is a guarded adapter dry-run, client execution queue, and commercial approval center only. It does not execute live OpenClaw, run Playwright, publish to social media, ingest platform analytics, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63O-63Q Customer Console Publish Result Observation Loop

Branch: `codex/phase-63o-63q-publish-result-observation-loop`

Phase 63O-63Q moves the customer-machine loop from dry-run execution into a visible publish/result/data path for `worker_console` and `worker_console_desktop`. The product operation desk now has a publish result loop panel with guarded publish handoff, manual publish result, and manual metric observation steps.

The guarded publish handoff records `guarded_publish_handoff` from a succeeded dry-run. The result step records `manual_publish_result` with manual link, screenshot, and execution-log placeholders. The data step records `manual_publish_metrics` so operators can continue toward the next improvement pass without raw JSON.

Boundary: Phase 63O-63Q is publish handoff, manual publish result, and manual metric observation only. It does not execute live OpenClaw, run Playwright, publish to social media, ingest platform analytics, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63R-63T Customer Console Publish Metric Improvement Loop

Branch: `codex/phase-63r-63t-publish-metric-improvement-loop`

Phase 63R-63T moves the customer-machine loop from manual metric observation into improvement and next-content preparation for `worker_console` and `worker_console_desktop`. The product operation desk now has a fourth publish loop step for manual publish metric improvement and a publish metric next-cycle draft action.

The improvement action records `manual_publish_improvement` from an approved `manual_publish_metrics` observation. The draft action prefers that improvement decision and creates `publish_metric_next_cycle_draft` content for another human approval pass. This keeps the closed loop simple: record data, analyze it, prepare the improved draft, then continue approval and execution.

Boundary: Phase 63R-63T is manual publish metric improvement and publish metric next-cycle draft preparation only. It does not execute live OpenClaw, run Playwright, publish to social media, ingest platform analytics, auto-optimize, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63U-63W Customer Console Improved Draft Re-execution Loop

Branch: `codex/phase-63u-63w-improved-draft-reexecution-loop`

Phase 63U-63W moves the customer-machine loop from improved content back into execution preparation for `worker_console` and `worker_console_desktop`. The product operation desk now recognizes publish metric next-cycle approvals, uses improved draft re-execution labels, and prioritizes publish metric re-execution prep when queueing the next run.

The re-execution path records `publish_metric_reexecution_prep` execution requests and `publish_metric_reexecution_run_review` execution runs. This keeps the closed loop simple: approve the improved draft, prepare the customer-machine re-execution record, queue the run, then continue preflight, handoff, dry-run, and result tracking.

Boundary: Phase 63U-63W is improved draft re-execution and publish metric re-execution prep only. It does not execute live OpenClaw, run Playwright, publish to social media, ingest platform analytics, auto-optimize, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 63X-64B Customer Console Closed Loop Delivery Pass

Branch: `codex/phase-63x-64b-client-closed-loop-delivery`

Phase 63X-64B adds a client closed-loop delivery pass to `worker_console` and `worker_console_desktop`. The product operation desk now gives operators one clear action that advances the safe sequence across client runtime preflight, OpenClaw/Playwright handoff, guarded dry-run, publish result capture, manual metric observation, improvement analysis, and next draft generation.

The operator-facing steps are intentionally compact: client execution prep, publish result capture, operating data observation, improvement analysis, and next draft generation. This turns the previous five-step continuation into one big usable step while preserving each underlying record for server maintenance and audit.

Boundary: Phase 63X-64B is client closed-loop delivery orchestration only. It does not execute live OpenClaw, run Playwright, publish to social media, ingest platform analytics, auto-optimize, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 64C Commercial Agent/Skill Orchestration

Branch: `codex/phase-64c-commercial-agent-skill-orchestration`

Phase 64C Commercial Agent/Skill Orchestration connects the customer-machine consoles to the new metadata-only `agent-skill-orchestration` API. `worker_console` and `worker_console_desktop` now fetch `/api/v1/commercial-operations/{operation_id}/agent-skill-orchestration`, refresh `/agent-skill-orchestration/refresh`, and show a compact Agent/Skill panel with the `commercial_operation_agent`, next skill, owner agent, tool, next action, and boundary.

The server `admin_dashboard` also shows the same Agent/Skill orchestration for maintainers, so customer-machine operators and server maintainers can read the same closed-loop routing state without seeing code or raw JSON.

Boundary: Phase 64C is Agent/Skill orchestration display only. It does not execute live OpenClaw, run Playwright, publish to social media, ingest platform analytics, auto-optimize, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, bypass approval, or rebuild client packages.

## Phase 64D Server/Client Frontend Operability Optimization

Branch: `codex/phase-64d-frontend-operability-optimization`

Phase 64D improves the customer-machine first screen without changing runtime behavior. `worker_console` and `worker_console_desktop` now keep the common commercial operations actions visible in a short action strip: create loop, upload knowledge, prepare first draft, approve and prepare execution, and advance the full loop. Advanced execution/recovery controls remain available but are folded behind an "Advanced execution and recovery" details panel.

The server `admin_dashboard` also adds a maintenance cockpit so maintainers can see AI Server connection, customer-machine frontend status, selected operation, and Agent/Skill next action before opening long records.

Boundary: Phase 64D is frontend display and operator ergonomics only. It does not execute live OpenClaw, run Playwright, publish to social media, ingest platform analytics, auto-optimize, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, bypass approval, mutate runtime configuration, or rebuild client packages.

## Docs Stabilization Sprint

This document is now indexed by `docs/PHASE_INDEX.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/SYSTEM_BOUNDARIES.md`, `docs/DOC_RENDER_QA.md`, and `docs/ARCHITECTURE_TIMELINE.md`.

The canonical project recovery state is: `main` remains the Phase 42 stable baseline, the active docs branch is `codex/docs-stabilization-sprint`, and Phase 43-52 remain open PRs layered on top of the Phase 42 baseline. Current non-goals remain: no ComfyUI integration, no real social media publishing, no captcha bypass, no proxy pool, no Kubernetes/Helm/Terraform, no HA orchestration, and no production installer/signing.
