# Admin Dashboard Foundation

Phase 36 is completed. `admin_dashboard` is the Server Admin Dashboard Foundation for inspecting AI Server, Browser Workers, Browser Runtime, Timeline, Snapshots, Replay metadata, Tasks, Conversation Runtime, OpenClaw mock, Audit Logs, and RAG / Documents state from a browser.

## Current Scope

- Completed: read-only monitoring foundation.
- Completed: standalone Vite + React + TypeScript + Tailwind frontend project.
- Completed: calls existing AI Server APIs with `X-Workspace-Id` and `X-User-Id` headers.
- Completed: Settings page stores `aiServerUrl`, `workspaceId`, and `userId` in localStorage.
- Experimental: Browser Runtime page can create metadata-only replay for debugging. It does not re-execute browser actions.
- Planned: production-grade operations backend, login UI, permission UI, publishing business flow, and complex editing workflows.

Current explicit boundaries: no login UI, no permission UI, no publishing business flow, no real social platform control, no production-grade operations backend.

## Project Structure

```text
admin_dashboard/
├── package.json
├── .env.example
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── src/main.tsx
├── src/styles.css
└── src/api/client.ts
```

## Runtime Configuration

```env
VITE_AI_SERVER_API=http://localhost:8000
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

Default AI Server:

```text
http://localhost:8000
```

Development:

```powershell
cd admin_dashboard
npm install
npm run dev
```

Static build:

```powershell
cd admin_dashboard
npm run build
```

## Pages

| Page | Status | Description |
| --- | --- | --- |
| Overview | Completed | API health, worker online/offline, Browser Runtime session count, Task summary, Conversation count, OpenClaw mock status, recent errors |
| Workers | Completed | Browser worker inventory, available workers, health summary; read-only, no rotate secret / revoke actions |
| Browser Runtime | Completed | Sessions, events timeline, snapshots, metadata-only replay |
| Conversations | Completed | Threads, messages, events; explicitly marked as foundation |
| Tasks | Completed | Task list, events, logs, payload summary; read-only, no retry/cancel actions |
| OpenClaw | Completed | Health, capabilities, mock status; no real OpenClaw |
| Audit Logs | Completed | Browser security audit logs with basic event_type / success / target_type filters |
| RAG / Documents | Completed | Embedding health, documents, collections, simple hybrid search form |
| Settings | Completed | AI Server URL, Workspace ID, User ID, refresh interval |

## API Client

`admin_dashboard/src/api/client.ts` exports:

- `workersApi`
- `browserRuntimeApi`
- `conversationsApi`
- `tasksApi`
- `openclawApi`
- `auditApi`
- `ragApi`

Every request includes:

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

## Auto Refresh

- Overview: every 10 seconds.
- Workers: every 10 seconds.
- Browser Runtime: every 10 seconds.
- Logs / Events / Snapshots: manual refresh or detail selection.
- API failures are rendered as unavailable/error states and should not crash the entire page.

## Boundaries

Admin Dashboard Foundation does not implement:

- no login UI
- no permission UI
- no publishing business flow
- no real social platform control
- no production-grade operations backend
- no TikTok / YouTube / X automation
- no auto login
- no cookie injection
- no proxy pool
- no fingerprint bypass
- no captcha automation

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
## Phase 38: Conversation Tool Bridge Frontend Integration

The Admin Dashboard Conversation page now displays route selected, selected tool, tool status, result summary, event timeline, and full metadata panel. Events include `route_selected`, `tool_execution_started`, `tool_execution_completed`, `agent_execution_started`, `planning_execution_started`, `bridge_fallback`, and `bridge_error`. It remains polling only, not WebSocket, not SSE, not a full ChatGPT UI, and not autonomous agent.

## Phase 39: Conversation Approval Panel

The Admin Dashboard Conversations page now includes the Approval Flow Foundation:

- pending approvals panel
- proposed action preview
- proposed payload JSON
- risk badge
- approve / reject / cancel buttons
- execute approved action button
- approval events timeline

Related APIs: `GET /api/v1/conversations/{thread_id}/approvals`, `POST /api/v1/conversation-approvals/{approval_id}/approve`, `/reject`, `/cancel`, and `/execute`. This is an execution review gate, not a full permission system. It does not implement real platform publishing, real OpenClaw, login, captcha, proxy, fingerprint bypass, or social automation.
## Phase 40: Playbooks Page and Conversation Playbook UI

Admin Dashboard adds a `Playbooks` page and extends the `Conversations` page with:

- Playbook selector
- Playbook list / description
- Run playbook button
- Playbook Runs
- Step Timeline
- Approval-aware execution controls

## Phase 41: Output Library

Admin Dashboard now includes an Output Library page:
- artifact list
- artifact detail
- artifact type badge
- source type
- related thread
- related Playbook Run
- preview content
- Export markdown / json / txt
- filter by `artifact_type` / `source_type`

Conversation pages show generated artifacts, and assistant messages expose Save as Artifact. Artifacts generated after Playbook Run completion appear in Output Library.

Boundary: Output Library is not a full DAM, has no S3 / MinIO integration, and is not production publishing asset management.

Built-ins visible in the UI: `browser_search_summary`, `browser_screenshot_report`, `rag_answer`, `content_generation`, `trend_research_draft`, and `openclaw_mock_device_check`.

This is a basic run/monitoring entrypoint. It is not a visual workflow editor, does not publish to real social platforms, and does not bypass the Phase 39 approval gate.
## Phase 42: Task Orchestration & Background Execution

This phase adds the Task Orchestration foundation: `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, and `TaskRetryPolicy`. Conversation / Playbook runs can use `execution_mode=background`, then `/api/v1/task-runs` exposes queued, running, waiting_approval, retrying, completed, failed, cancelled, expired state plus timeline events. `scheduled_at` supports scheduled runs; retry uses exponential backoff; approval resume continues to enforce the Phase 39 Approval Gate; Output Library artifacts are linked by `task_run_id`.

Boundary: this is an in-process queue, not Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue. It does not implement real publishing, real OpenClaw, ComfyUI, CAPTCHA handling, proxies, or fingerprint bypass.
## Phase 43: Task Scheduler Persistence & Worker Recovery (Completed)

Completed: Task Scheduler Persistence, `task_scheduler_state`, Task Lease fields on `task_runs`, `TaskRecoveryService`, Scheduler Health API, manual recovery API, Failed Diagnostics, and frontend scheduler health panels.

Task Lease: running task runs receive `lease_owner`, `lease_token`, `lease_expires_at`, and `heartbeat_at`. Expired lease and stale heartbeat are recoverable through scan or manual recover.

Recovery rules: running + expired lease or stale heartbeat -> retrying if retry budget remains, otherwise failed; pending scheduled due -> queued; retrying delay elapsed -> queued; waiting_approval is not auto-executed; completed/cancelled/expired are not recovered.

Admin Dashboard now shows Scheduler Health, lease status, recoverable badge, diagnostics panel, scheduled due indicator, and manual recover. Worker Console and Worker Console Desktop show simplified Task recovery state.

Boundary: this remains an in-process scheduler foundation, not Celery, not Kubernetes, and not production HA distributed queue.
## Phase 43: Scheduler Health and Task Recovery

Admin Dashboard now includes Scheduler Health in Overview and Task Runs. Operators can inspect scheduler status, heartbeat, last scan, active task count, recovered task count, Task Lease fields, recoverable badge, scheduled due indicator, Failed Diagnostics, and manual recover. This is a monitoring and recovery foundation, not a full operations console and not a production HA queue.

<!-- PHASE44_ADMIN:START -->
## Phase 44 Artifact Explorer

Admin Dashboard now includes an Artifact Explorer foundation for Output Library records. It shows artifact_role, artifact_stage, retention_policy, exportable, root/parent artifact IDs, lineage graph metadata, export actions, package actions, archived indicator, retention badge, and bundle download metadata. It calls the Phase 44 Output Artifact Pipeline APIs and remains a monitoring/admin foundation, not a full DAM and not a production object storage platform.
<!-- PHASE44_ADMIN:END -->

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

<!-- PHASE45_ADMIN:START -->
## Phase 45 Admin Dashboard: Workflow State

Admin Dashboard now includes Workflow Runs. The page lists workflows, opens a workflow detail panel, shows the workflow step timeline, variables viewer, context viewer, checkpoints list, Agent Memory Snapshots, linked Output Artifacts, and Pause / Resume buttons. Task Runs and Output Library details display linked `workflow_run_id` and workflow lineage fields.

This is a Workflow State viewer and recovery foundation, not a full workflow editor, not a permission UI, and not ComfyUI.
<!-- PHASE45_ADMIN:END -->

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
## Phase 46: Workflow Graph Runtime Admin Dashboard

Admin Dashboard now includes Workflow Graphs for Workflow Graph Runtime & Conditional Execution:

- graph summary for `workflow_graphs`
- node list from `workflow_graph_nodes`
- edge list from `workflow_graph_edges`
- planner result from `WorkflowExecutionPlanner`
- conditional routing result
- Retry/Fallback Path display
- replay panel for `workflow_replays`
- Workflow detail fields: `current_node_key`, `planned_next_nodes`, `skipped_nodes`, `retry_state`, and `fallback_state`
- Artifact detail fields: `producing_node_key`, `replay_source`, and `graph_lineage`

Boundaries: this Admin Dashboard view is not a visual DAG builder, not drag/drop workflow editing, not distributed orchestration engine, and not ComfyUI.
<!-- PHASE46_SYNC:END -->
