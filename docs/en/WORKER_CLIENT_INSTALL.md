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
## Phase 42: Task Orchestration & Background Execution

This phase adds the Task Orchestration foundation: `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, and `TaskRetryPolicy`. Conversation / Playbook runs can use `execution_mode=background`, then `/api/v1/task-runs` exposes queued, running, waiting_approval, retrying, completed, failed, cancelled, expired state plus timeline events. `scheduled_at` supports scheduled runs; retry uses exponential backoff; approval resume continues to enforce the Phase 39 Approval Gate; Output Library artifacts are linked by `task_run_id`.

Boundary: this is an in-process queue, not Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue. It does not implement real publishing, real OpenClaw, ComfyUI, CAPTCHA handling, proxies, or fingerprint bypass.
## Phase 43: Task Scheduler Persistence & Worker Recovery (Completed)

Completed: Task Scheduler Persistence, `task_scheduler_state`, Task Lease fields on `task_runs`, `TaskRecoveryService`, Scheduler Health API, manual recovery API, Failed Diagnostics, and frontend scheduler health panels.

Task Lease: running task runs receive `lease_owner`, `lease_token`, `lease_expires_at`, and `heartbeat_at`. Expired lease and stale heartbeat are recoverable through scan or manual recover.

Recovery rules: running + expired lease or stale heartbeat -> retrying if retry budget remains, otherwise failed; pending scheduled due -> queued; retrying delay elapsed -> queued; waiting_approval is not auto-executed; completed/cancelled/expired are not recovered.

Admin Dashboard now shows Scheduler Health, lease status, recoverable badge, diagnostics panel, scheduled due indicator, and manual recover. Worker Console and Worker Console Desktop show simplified Task recovery state.

Boundary: this remains an in-process scheduler foundation, not Celery, not Kubernetes, and not production HA distributed queue.

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
## Phase 46 Note

Worker client installation is unchanged. Workflow Graph Runtime and Conditional Execution run on the AI Server and UI surfaces; customer machines continue to expose the same worker runtime APIs. Phase 46 does not add ComfyUI, a distributed orchestration engine, or platform automation.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47 Note

Worker client installation is unchanged. Workflow Template Registry & Versioning lives on AI Server and the frontend consoles; customer machines continue exposing browser runtime / worker runtime APIs. Template Library can select templates such as `browser_screenshot_report_graph`, but it does not change customer-machine security boundaries and does not connect ComfyUI, TikTok / YouTube / X, or real platform automation.
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
