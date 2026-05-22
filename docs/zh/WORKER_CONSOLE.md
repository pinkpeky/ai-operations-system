# Worker Console GUI Foundation

状态：已完成，Phase 30。

`worker_console` 是客户机 Worker 的本地 Web GUI Foundation。它是独立 Vite + React + TypeScript + Tailwind 前端项目，默认连接本地 Worker API：

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

## 当前页面

Dashboard：

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

Runtime Control：

- Start Runtime
- Stop Runtime
- Restart Runtime
- Start Heartbeat
- Stop Heartbeat

Logs：

- 调用 `GET /local/logs`
- 支持 refresh
- 高亮 error / failed / exception / traceback 行

Connection Info：

- `server_url`
- `worker_base_url`
- `runtime_port`
- `openclaw_enabled`
- `browser_enabled`

## Local API Client

前端 client 文件：

```text
worker_console/src/api/localWorkerClient.ts
```

支持：

- `getStatus`
- `getHealth`
- `getLogs`
- `startRuntime`
- `stopRuntime`
- `restartRuntime`
- `startHeartbeat`
- `stopHeartbeat`

## 启动方式

```powershell
python -m worker_client.cli start
cd worker_console
npm install
npm run dev
```

打开：

```text
http://localhost:5173
```

如果本地 Worker API 不可用，页面显示：

- `Worker API unreachable`
- `请确认 worker_client 是否启动`
- `请确认端口是否为 9100`

## 当前边界

当前只是本地 Web GUI Foundation，不是桌面应用。当前没有 system tray，没有自动更新，没有 Electron，没有 Tauri，没有 PySide，没有 no exe / dmg 打包。未来可接 Tauri / Electron / PySide / system tray / auto start / exe / dmg。

不包含 TikTok / YouTube / X 自动化、账号登录、Cookie 注入、代理池、指纹绕过、验证码自动化或真实平台自动化。

Boundary marker: no system tray, no auto update, no Electron, no Tauri, no PySide, no exe / dmg.

## Phase 31：Worker Console Desktop App Foundation

状态：已完成，Phase 31。

`worker_console_desktop` 是当前 Worker Console 的 Tauri 桌面壳基础。它复用 Phase 30 的本地 Worker API 契约，默认连接：

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

### 桌面壳能力

- 打开 Tauri 窗口。
- 显示 Worker status、Runtime status、Heartbeat status、Connection Info 和 Logs。
- 调用 `GET /local/status`、`GET /local/health`、`GET /local/logs`。
- 调用 `POST /local/runtime/start`、`POST /local/runtime/stop`、`POST /local/runtime/restart`。
- 调用 `POST /local/heartbeat/start`、`POST /local/heartbeat/stop`。
- 本地 Worker API 不可达时显示：`Worker API unreachable`、`Worker Runtime 未启动`、`请先启动 worker_client`、`packaging 脚本启动`。

### 开发启动

```powershell
python -m worker_client.cli start
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

### 当前边界

当前只是 Worker Console Desktop App Foundation。没有正式安装包，没有 no exe / dmg，没有系统托盘，没有 no system tray，没有开机自启，没有自动更新，没有 no auto update。未来可在此基础上继续增加 tray / autostart / installer。

本阶段仍不包含 TikTok / YouTube / X 自动化、账号登录、Cookie 注入、代理池、指纹绕过、验证码自动化或真实平台自动化。

## Phase 32：Worker Console System Tray & Desktop Runtime Foundation

状态：已完成，Phase 32。

`worker_console_desktop` 现在从桌面壳基础升级为桌面 Runtime 基础，新增 Tauri System Tray、Minimize To Tray、Tray Runtime Control 和 Desktop Status Sync。

### System Tray

托盘菜单包含：

- Show Console
- Hide Window
- Start Runtime
- Stop Runtime
- Restart Runtime
- Start Heartbeat
- Stop Heartbeat
- Refresh Status
- Quit

Show Console 会显示窗口，Hide Window 会隐藏窗口，Quit 才真正退出程序。

### Minimize To Tray

默认配置：

```json
{
  "minimize_to_tray": true
}
```

配置文件：`worker_console_desktop/src-tauri/desktop-runtime.json`。点击窗口关闭按钮时默认隐藏到托盘，不退出进程。

### Tray Runtime Control

托盘菜单不会执行 shell 命令，也不会执行远程命令。托盘动作会发送给前端，由前端调用本地 Worker API：

- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`

### Desktop Status Sync

桌面端定时调用：

- `GET /local/status`
- `GET /local/health`

托盘 tooltip 显示 `worker_name`、`current_status`、`runtime_running`、`heartbeat_running`。UI 显示 connected、reconnecting、disconnected、online、offline、error，以及 last successful sync 和 last error。

### AutoStart Placeholder

新增占位目录：`worker_console_desktop/autostart/`。当前只是 AutoStart Placeholder，说明未来可支持 Windows registry startup、macOS LaunchAgent 和 start on login。本阶段没有真正开机自启。

### 当前边界

当前没有正式 installer，没有正式安装包，没有 exe / dmg，没有真正开机自启，没有 auto-update / 自动更新，没有远程 shell，没有任意命令执行。仍不包含 TikTok / YouTube / X 自动化、账号登录、Cookie 注入、代理池、指纹绕过、验证码自动化或真实平台自动化。

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

```powershell
cd worker_console
npm.cmd run dev
```

Open `http://localhost:5173` and check:

- `registered=true`
- `runtime_running=true`
- `heartbeat_running=true`
- `current_status=online`
- logs include heartbeat success
- Browser Sessions Panel can refresh sessions

Desktop Console:

```powershell
cd worker_console_desktop
npm.cmd run tauri dev
```

If Rust/MSVC is not ready, mark `desktop native validation pending` and do not report native desktop validation as passed.

## Phase 35A Browser Runtime Timeline / Snapshots / Replay

Worker Console Web 和 Worker Console Desktop 的 Browser Sessions Panel 已增强：

- Timeline：调用 `GET /api/v1/browser-runtime/sessions/{session_id}/events`
- Screenshot history：从 `browser_runtime_snapshots` 读取 `snapshot_type=screenshot`
- Page snapshots：从 `browser_runtime_snapshots` 读取 `snapshot_type=page`
- Replay metadata：调用 `POST /api/v1/browser-runtime/sessions/{session_id}/replay`
- Replay export：调用 `GET /api/v1/browser-runtime/replays/{replay_id}/export`
- Refresh events / Refresh snapshots：polling 查询，不是 live stream

当前 Replay 是 metadata-only replay，不重新执行浏览器动作。当前没有 VNC、noVNC、DevTools remote control、live browser stream，也不做 TikTok / YouTube / X、登录、Cookie 注入、代理池、指纹绕过、验证码或真实平台自动化。

## Phase 36：Server Admin Dashboard Foundation

`admin_dashboard` 已加入 docs SSOT。它是 read-only monitoring foundation，用于查看 Overview、Workers、Browser Runtime、Conversations、Tasks、OpenClaw、Audit Logs、RAG / Documents、Settings。运行配置为 `VITE_AI_SERVER_API=http://localhost:8000`、`VITE_WORKSPACE_ID=demo-workspace`、`VITE_USER_ID=demo-user`，API client 位于 `admin_dashboard/src/api/client.ts`，包含 `workersApi`、`browserRuntimeApi`、`conversationsApi`、`tasksApi`、`openclawApi`、`auditApi`、`ragApi`。当前 no login UI、no permission UI、no publishing business flow、no real social platform control、no production-grade operations backend。

## Phase 37：Conversation Runtime Frontend Integration

状态：已完成，Phase 37。

Phase 37 将 Conversation Runtime 接入 Server Admin Dashboard、Worker Console Web 与 Worker Console Desktop。当前能力是 Conversation frontend integration 和基础对话入口，不是完整 ChatGPT UI，也不是 WebSocket / SSE streaming。

已完成：

- Admin Dashboard Conversation page：`admin_dashboard` 的 Conversations 页面支持 create thread、thread list、thread detail、message list、event timeline、send message、run conversation、refresh messages、refresh events。
- Admin Dashboard client：新增 `admin_dashboard/src/api/conversationClient.ts`，支持 `createThread`、`listThreads`、`getThread`、`sendMessage`、`listMessages`、`listEvents`、`runConversation`。
- Worker Console Chat Panel：`worker_console` 支持 AI Server URL、Workspace ID、User ID 配置，支持 create thread、send and run、Polling Event Timeline、AI Server connected / disconnected / unreachable 状态。
- Desktop Chat Panel：`worker_console_desktop` 同步 Chat Panel 基础能力；Tauri native validation 仍取决于客户机 Rust/MSVC 环境。
- Polling Event Timeline：前端通过 `GET /api/v1/conversations/{thread_id}/events` 手动刷新或 5 秒 polling，展示 `event_type`、`message`、`created_at`、`payload JSON`。
- Frontend config：`VITE_AI_SERVER_API=http://localhost:8000`，`VITE_WORKSPACE_ID=demo-workspace`，`VITE_USER_ID=demo-user`。
- Development CORS：后端通过 `CORS_ALLOWED_ORIGINS` 允许 `http://localhost:5173`、`http://127.0.0.1:5173`、`http://localhost:5180`、`http://127.0.0.1:5180`、`tauri://localhost` 等开发来源。

边界：当前不是 WebSocket，not WebSocket；当前不是 SSE，not SSE；当前不是完整 ChatGPT UI，not a full ChatGPT UI；不做 TikTok / YouTube / X 自动化，不做登录、Cookie 注入、代理池、指纹绕过、验证码自动化、真实平台自动化、真实 OpenClaw 或 ComfyUI。
## Phase 38：Worker Console Chat Panel Bridge

Worker Console 和 Worker Console Desktop 的 Chat Panel 已展示 `route_name`、`selected_tool`、run status、result summary、`result_metadata` 和 event payload。Browser Bridge、OpenClaw mock bridge、RAG bridge、Content bridge、Planning bridge 均通过 Conversation Runtime polling 事件展示。当前不是 WebSocket，不是 SSE，不做真实平台自动化。

## Phase 39：Conversation Approval Panel

Worker Console Web 和 Worker Console Desktop 的 Chat Panel 已新增 pending approvals panel。面板展示 proposed action preview、proposed payload JSON、risk badge、approval_status，以及 approve / reject / cancel / execute approved action 控制。

Chat Panel 默认使用 `review_first` 运行用户消息，让 Browser / OpenClaw 类动作先进入审批队列再执行。前端调用 `GET /api/v1/conversations/{thread_id}/approvals` 以及 `/api/v1/conversation-approvals/{approval_id}` 的 approve / reject / cancel / execute API。

当前边界：不是完整权限系统，not a full permission system；不是 WebSocket/SSE；不做真实平台发布、真实 OpenClaw、登录、验证码、代理或指纹绕过。
## Phase 40：Worker Console Playbook Entry

Worker Console Web 和 Desktop Chat Panel 增加 Playbook selector、Run playbook、Playbook runs 和 Step timeline 展示。

该入口主要用于客户机侧快速触发标准化 Conversation Playbook，但仍然：

- 使用 polling，不是 WebSocket/SSE。
- 保留 pending approvals panel。
- medium/high risk step 必须审批后执行。
- 不实现完整 workflow builder。
- 不做真实平台发布、登录、验证码、代理、指纹或真实 OpenClaw。

## Phase 41：Worker Console Output Library

Worker Console Web 和 Desktop Chat Panel 增加 Output Library 基础展示：

- generated artifacts list
- assistant message 的 Save as Artifact
- artifact type / source type badge
- related `playbook_run_id`
- Export markdown

该能力用于查看 Playbook / Conversation 生成的 `content_draft`、`report`、`rag_answer`、`screenshot`、`html_snapshot`、`plan`、`json` 等产物。当前只是 Output Library Foundation，不是完整 DAM，不接 S3 / MinIO，也不做真实平台发布资产管理。
## Phase 42: Task Orchestration & Background Execution

  Task Orchestration foundation, `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, `TaskRetryPolicy`, Conversation / Playbook  `execution_mode=background`  `/api/v1/task-runs`  queued, running, waiting_approval, retrying, completed, failed, cancelled, expired  timeline, `scheduled_at`  scheduled run, retry  exponential backoff, approval resume  Phase 39 Approval Gate, Output Library artifacts  `task_run_id`  artifact linkage.

  in-process queue  Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue  OpenClaw, ComfyUI
## Phase 43: Task Scheduler Persistence & Worker Recovery

 Task Scheduler Persistence, `task_scheduler_state`, `task_runs`, Task Lease  `TaskRecoveryService`, Scheduler Health API, manual recovery API, Failed Diagnostics  scheduler health

Task Lease, running task run  `lease_owner`, `lease_token`, `lease_expires_at`, `heartbeat_at`, expired lease, stale heartbeat  scan, manual recover

Recovery rules, running + expired lease, stale heartbeat -> retrying  retry budget, failed, pending scheduled due -> queued, retrying delay elapsed -> queued, waiting_approval  completed/cancelled/expired

Admin Dashboard  Scheduler Health, lease status, recoverable badge, diagnostics panel, scheduled due indicator, manual recover, Worker Console, Worker Console Desktop  Task recovery

  in-process scheduler foundation  Celery  Kubernetes  production HA distributed queue?
## Phase 43  Task Recovery

Worker Console Web, Worker Console Desktop  scheduler, task recovery  scheduler health, recovered count, lease expiry, recoverable state, suggested action, manual recover  shell  scheduler console.

<!-- PHASE44_CONSOLE:START -->
## Phase 44 Output Library Controls

Worker Console, Worker Console Desktop  Output Library  export, package, lineage summary, retention status  DAM CDN
<!-- PHASE44_CONSOLE:END -->

<!-- PHASE44_SYNC:START -->
## Phase 44: Output Artifact Pipeline & Export System

Phase 44, Phase 41 Output Library, Phase 42/43 task runtime  Output Artifact Pipeline  Artifact lineage, relationship graph retention policy preview  Artifact Explorer



- `output_artifacts`  `parent_artifact_id`, `root_artifact_id`, `source_task_run_id`, `source_playbook_run_id`, `source_conversation_id`, `source_runtime_session_id`, `artifact_role`, `artifact_stage`, `generated_by`, `exportable`, `retention_policy`, `expires_at`.
- `artifact_relationships`  relationship graph  `derived_from`, `packaged_into`, `summarized_from`, `exported_from`, `replay_of`.
- `ArtifactExportService`  `export_markdown`, `export_html`, `export_json`, `export_bundle_zip`, `export_report_package`  browser runtime, playbook.
- `ArtifactPackagingService`  `package_playbook_run`, `package_task_run`, `package_browser_runtime_session`, `package_conversation`  package artifact, `bundle.zip` metadata.
- `ArtifactRetentionService`  retention policy, expiration scan, cleanup preview, soft archive  preview
- API  `GET /api/v1/output-artifacts/{artifact_id}/lineage`, `GET /api/v1/output-artifacts/{artifact_id}/relationships`, `POST /api/v1/output-artifacts/{artifact_id}/export`, `POST /api/v1/output-artifacts/{artifact_id}/package`, `POST /api/v1/output-artifacts/cleanup/preview`.
- Storage roots  `storage/output_artifacts`, `storage/output_packages`, `storage/output_exports`.
- Admin Dashboard  Artifact Explorer, lineage graph panel, export actions, package actions, retention badge, archived indicator, bundle metadata preview.
- Worker Console / Desktop  export, package, lineage summary, retention status



-   DAM
-   production object storage platform?
-   S3 / MinIO / CDN?
- Export  Browser Runtime, Playbook, Conversation, OpenClaw, Task action.
-  TikTok / YouTube / X automation  OpenClaw, ComfyUI.
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
## Phase 47：Worker Console Template Library

Worker Console Web 和 Worker Console Desktop 新增简化 Template Library：

- 通过 `worker_console/src/api/workflowTemplateClient.ts` 与 `worker_console_desktop/src/api/workflowTemplateClient.ts` 调用 AI Server。
- 支持 list templates、select template、run template、view template run status。
- 可显示内置模板 `browser_screenshot_report_graph`、`content_generation_graph`、`rag_answer_graph`、`approval_then_browser_graph`、`openclaw_mock_inspect_graph`、`task_retry_demo_graph`。
- 可显示 `workflow_template_id`、`workflow_template_version_id`、`workflow_template_run_id`、`validation_status` 和 `compatibility` 摘要。

当前只是模板入口和运行状态视图，不是可视化 DAG builder，不是 drag/drop workflow editor，不接 ComfyUI，不做真实平台自动化。
<!-- PHASE47_SYNC:END -->

<!-- PHASE48_SYNC:START -->
## Phase 48: Workflow Template Marketplace & Governance Foundation

Status: completed.

Phase 48, Phase 47 Workflow Template Registry & Versioning  Marketplace foundation  public marketplace  SaaS marketplace  DAG editor  ComfyUI.

Completed scope:

-  `workflow_template_reviews`  review queue, `review_status`, `risk_assessment`, `compatibility_report`, approve / reject / request changes.
-  `workflow_template_promotions`  activate, rollback, deprecate, archive, `promotion_type`  reason.
-  `workflow_template_audit_logs`  audit trail, actor, previous_state, new_state, metadata.
-  `workflow_template_compatibility_matrix`  runtime capability  `browser_runtime`, `approval_gate`, `task_scheduler`, `artifact_pipeline`, `workflow_graph_runtime`, `openclaw_mock`, `rag_pipeline`
-  `WorkflowTemplateGovernanceService`  `submit_for_review`, `approve_review`, `reject_review`, `request_changes`, `activate_template_version`, `rollback_template_version`, `deprecate_template`, `archive_template`, `list_review_queue`, `list_governance_events`.
- Template lifecycle, draft -> review -> approved -> active -> deprecated -> archived, review  activate, active version  deprecated  archived  rollback
- Marketplace foundation, `workflow_templates`  `featured`, `verified`, `recommended`, `usage_count`, `success_rate`, `average_runtime_ms`, `average_step_count`  governance badges, risk badge, verified badge, featured templates, recommended templates.
- Output Artifact lineage  `source_template_review_id`, `governance_state`, Workflow Runs  template governance state, compatibility snapshot.
- Admin Dashboard  Template Governance  Review Queue, Approval / Reject / Request Changes, Template Lifecycle View, Audit Log View, Marketplace View, Compatibility Matrix View, Rollback UI.
- Worker Console, Worker Console Desktop, Template Library  governance status, template verification status, compatibility summary.

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

## Phase 49：Workflow Run Observability & Replay Center

已完成 Workflow Run Observability & Replay Center foundation：新增 `workflow_execution_traces`、`workflow_runtime_diagnostics`、`workflow_replay_sessions`，并接入 `WorkflowExecutionTraceService` 与 `WorkflowDiagnosticsService`。系统现在可以记录 node_started / node_completed / node_failed / planner_decision / retry_triggered / fallback_triggered / approval_wait / approval_resume / replay_started / replay_completed，形成 Execution Trace、Runtime Summary、Failure Hotspots、Replay Center 与 metadata_only / dry_run replay session。

新增 API：`GET /api/v1/workflow-runs/{workflow_run_id}/traces`、`GET /api/v1/workflow-runs/{workflow_run_id}/diagnostics`、`GET /api/v1/workflow-runs/{workflow_run_id}/analytics`、`POST /api/v1/workflow-runs/{workflow_run_id}/replay-sessions`、`GET /api/v1/workflow-runs/{workflow_run_id}/runtime-summary`、`GET /api/v1/workflow-replay-sessions`、`GET /api/v1/workflow-replay-sessions/{replay_session_id}`。

前端更新 Admin Dashboard 的 Replay Center / Workflow Observability 页面，展示 Execution Trace Timeline、Node Inspection Panel、Retry/Fallback Visualization、Diagnostics Panel、Runtime Summary、Replay Session View、Failure Hotspots 与 Approval Wait Visualization。Worker Console / Desktop 显示简化 trace timeline、replay session status、diagnostics summary、retry/fallback counters。

边界：当前不是 distributed tracing platform，不是 OpenTelemetry stack，不是 WebSocket/SSE realtime，不是 deterministic replay engine，不是 visual DAG editor，不接 ComfyUI，不做真实社媒发布，不做 Kubernetes orchestration。

Keywords: not distributed tracing platform; not deterministic replay engine; not ComfyUI.

## Phase 50: Desktop Console Runtime UX & Client Packaging Readiness

Phase 50  Desktop Console Runtime UX & Client Packaging Readiness, Tauri icon resource  `worker_console_desktop/src-tauri/icons/icon.ico`  `bundle.icon`  `["icons/icon.ico"]`.

Start Runtime diagnostics  `starting`, `started`, `failed`, `unavailable`, `port_conflict`, `missing_config`, `server_environment_warning`, Desktop Console  local worker diagnostics  `/local/status`, `/local/health`, runtime port, `server_url`, `worker_base_url`, last attempted action, last error detail, last successful sync.

 /  Worker Runtime  worker  worker  E2E   Desktop Console?

  packaging readiness, not final installer, no code signing, no auto updater, no MSI/EXE release packaging  not ComfyUI.

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

Phase 62I 面向客户机/工作站使用人员同步前端操作入口。`worker_console` 和 `worker_console_desktop` 现在提供更简洁的操作首页，集中展示本机连接、Worker runtime、heartbeat 和 recovery 状态。

操作流程：

- 先确认本机 Worker API 是否可达。
- 在客户机控制台启动本机 runtime 或 heartbeat。
- 直接跳转到 conversation、playbook、approvals、outputs、task runs 和 logs。
- 前端界面支持 Chinese/English language switching。
- 首屏展示 setup、help、recovery 以及 server-vs-customer-machine boundary guidance。

边界：Phase 62I 只是 frontend/readiness slice，不会调用 ComfyUI，不会执行 OpenClaw，不会发布到真实平台，不会控制真实账号，不会签名 installer，不会启用 auto-update，不会绕过 captcha，不会使用 proxy pools，不会绕过 fingerprints，不会解析 secrets，也不会绕过 approval。

## Phase 62K Customer Console Codex-like UX Simplification

Status: in progress on `codex/phase-62k-customer-console-codex-ux`.

Phase 62K 根据客户机真实界面反馈继续简化 `worker_console` 和 `worker_console_desktop`。默认首屏从密集维护面板改为更接近 Codex 的命令式操作入口：左侧显示本机状态，中央显示下一步和对话输入，高级维护与诊断默认折叠。

操作入口：

- 在左侧状态栏查看本机 Worker API、runtime、heartbeat 和 recovery 状态。
- 按中央下一步提示先恢复连接或启动 runtime/heartbeat。
- 在首屏对话输入框直接提交客户机任务。
- 通过快捷入口进入剧本、审批、产物、任务和日志。
- 仅在维护时展开 advanced diagnostics。

边界：Phase 62K 只是前端 UX 简化；不会调用 ComfyUI、不会执行 OpenClaw、不会发布真实平台、不会控制真实账号、不会签名安装包、不会启用自动更新、不会绕过 captcha/proxy/fingerprint、不会解析 secret，也不会绕过审批。

## Phase 62L Customer Console Task Workbench

Status: in progress on `codex/phase-62l-client-task-workbench`.

Phase 62L 在 Codex-like 客户机界面上继续增加任务工作台，让 `worker_console` 和 `worker_console_desktop` 更适合普通使用人员按下一步操作。

Operator workflow:

- 在首屏工作台输入运营目标。
- 当存在待审批、运行中任务、失败/可恢复任务时，先看 suggested next action。
- 不打开维护面板也能看到 pending approvals、active tasks、failed/recoverable tasks 和 artifacts 数量。
- Playbooks、templates、approvals、messages/events、outputs、workflow state、task recovery 保持为可展开详情。
- Advanced maintenance and diagnostics 继续放在独立折叠区。

边界：Phase 62L 只是前端 UX 简化；不会调用 ComfyUI、不会执行 OpenClaw、不会发布真实平台、不会控制真实账号、不会签名安装包、不会启用自动更新、不会绕过 captcha/proxy/fingerprint、不会解析 secret，也不会绕过审批。

## Phase 62M Customer Console Goal Templates

Status: in progress on `codex/phase-62m-client-goal-templates`.

Phase 62M 在 `worker_console` 和 `worker_console_desktop` 的客户机任务工作台里增加标准目标模板。

Operator workflow:

- 选择发布内容、RAG 证据、素材简报或页面报告模板。
- 模板会自动填入运营目标。
- 模板会自动选择推荐 playbook。
- 继续通过现有审批受控的立即运行或后台排队动作执行。
- 高级维护和诊断仍然放在独立折叠区。

边界：Phase 62M 只是前端 UX 简化；不会调用 ComfyUI、不会执行 OpenClaw、不会发布真实平台、不会控制真实账号、不会签名安装包、不会启用自动更新、不会绕过 captcha/proxy/fingerprint、不会解析 secret，也不会绕过审批。

## Phase 62N Customer Console Goal Plan Preview

Status: in progress on `codex/phase-62n-client-goal-plan-preview`.

Phase 62N 在 `worker_console` 和 `worker_console_desktop` 里为当前选中的客户机目标模板增加紧凑计划预览。

Operator workflow:

- 选择目标模板。
- 运行前先查看计划步骤。
- 确认审批边界和预期产物。
- 继续使用现有立即运行或后台运行入口。
- 高级维护和诊断仍然放在独立折叠区。

边界：Phase 62N 只是前端 UX 简化；不会调用 ComfyUI、不会执行 OpenClaw、不会发布真实平台、不会控制真实账号、不会签名安装包、不会启用自动更新、不会绕过 captcha/proxy/fingerprint、不会解析 secret，也不会绕过审批。

## Phase 62O Customer Console Goal Status Tracker

Status: in progress on `codex/phase-62o-client-goal-status-tracker`, draft PR #81.

Phase 62O adds a compact goal status tracker to `worker_console` and `worker_console_desktop` for customer-machine operators.

Operator workflow:

- Choose a goal template and review the plan preview.
- Check prepare, approval, execution, recovery, and output status from one tracker.
- See current run status, thread id, task id, pending approvals, active tasks, failed/recoverable tasks, and artifacts.
- Continue with existing run-now, background, approval, and recovery actions.
- Keep advanced maintenance and diagnostics behind a separate disclosure.

Boundary: Phase 62O is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Phase 62P Customer Console Simple Operator Mode

Status: active branch `codex/phase-62p-client-simple-operator-mode`, draft PR #82.

Phase 62P 继续简化 `worker_console` 和 `worker_console_desktop`。默认任务页只突出一个目标输入框、常用任务按钮、可视化当前进度卡片，以及折叠后的审批、剧本、产物、工作流、任务和诊断维护区。

Phase 62P 同时新增独立的 knowledge base upload/edit page（知识库修改与上传分页）。该页是可视化操作页，不展示代码或 JSON。它支持：

- 上传知识文件到已有 RAG ingest / file upload API
- 新增或更新文字资料
- 设置知识分组和重复资料处理方式
- 查看上传队列卡片
- 查看资料卡片并快速进入修改
- 刷新当前知识资料列表

Boundary: Phase 62P is frontend-only. It does not call ComfyUI, execute OpenClaw, publish to real platforms, control real accounts, sign installers, enable auto-update, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, or bypass approval.

## Docs Stabilization Sprint

This document is now indexed by `docs/PHASE_INDEX.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/SYSTEM_BOUNDARIES.md`, `docs/DOC_RENDER_QA.md`, and `docs/ARCHITECTURE_TIMELINE.md`.

The canonical project recovery state is: `main` remains the Phase 42 stable baseline, the active docs branch is `codex/docs-stabilization-sprint`, and Phase 43-52 remain open PRs layered on top of the Phase 42 baseline. Current non-goals remain: no ComfyUI integration, no real social media publishing, no captcha bypass, no proxy pool, no Kubernetes/Helm/Terraform, no HA orchestration, and no production installer/signing.
