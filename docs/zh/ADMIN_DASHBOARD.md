# Admin Dashboard Foundation

Phase 36 已完成：`admin_dashboard` 是服务器端 Admin Dashboard Foundation，用于在浏览器中查看 AI Server、Browser Worker、Browser Runtime、Timeline、Snapshots、Replay metadata、Tasks、Conversation、OpenClaw mock、Audit Logs、RAG / Documents 等核心运行状态。

## 当前定位

- 已完成：read-only monitoring foundation。
- 已完成：独立 Vite + React + TypeScript + Tailwind 前端项目。
- 已完成：通过 `X-Workspace-Id` 和 `X-User-Id` header 访问现有 AI Server API。
- 已完成：Settings 页面把 `aiServerUrl`、`workspaceId`、`userId` 保存到 localStorage。
- 实验性：Browser Runtime 页面可以创建 metadata-only replay，用于调试，不重新执行浏览器动作。
- 规划中：生产级运营后台、登录 UI、权限 UI、发布业务流、复杂编辑。

当前明确没有：no login UI、no permission UI、no publishing business flow、no real social platform control、no production-grade operations backend。

## 目录

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

## Runtime 配置

```env
VITE_AI_SERVER_API=http://localhost:8000
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

默认访问：

```text
http://localhost:8000
```

开发启动：

```powershell
cd admin_dashboard
npm install
npm run dev
```

静态构建：

```powershell
cd admin_dashboard
npm run build
```

## 页面列表

| Page | 状态 | 说明 |
| --- | --- | --- |
| Overview | 已完成 | API health、Worker online/offline、Browser runtime session count、Task summary、Conversation count、OpenClaw mock status、Recent errors |
| Workers | 已完成 | browser worker inventory、available workers、health summary；只读，不做 rotate secret / revoke |
| Browser Runtime | 已完成 | sessions、events timeline、snapshots、metadata-only replay |
| Conversations | 已完成 | threads、messages、events；标记为 foundation |
| Tasks | 已完成 | task list、events、logs、payload summary；只读，不做 retry/cancel |
| OpenClaw | 已完成 | health、capabilities、mock status；未接真实 OpenClaw |
| Audit Logs | 已完成 | browser security audit logs，支持 event_type / success / target_type 基础过滤 |
| RAG / Documents | 已完成 | embedding health、documents、collections、simple hybrid search form |
| Settings | 已完成 | AI Server URL、Workspace ID、User ID、Refresh interval |

## API Client

`admin_dashboard/src/api/client.ts` 提供：

- `workersApi`
- `browserRuntimeApi`
- `conversationsApi`
- `tasksApi`
- `openclawApi`
- `auditApi`
- `ragApi`

所有请求默认包含：

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

## Auto Refresh

- Overview：10 秒刷新。
- Workers：10 秒刷新。
- Browser Runtime：10 秒刷新。
- Logs / Events / Snapshots：手动刷新或选择详情时刷新。
- API error 不会让整个页面崩溃，页面会显示 unavailable 或错误信息。

## 边界

Admin Dashboard Foundation 不实现：

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
## Phase 38：Conversation Tool Bridge 前端集成

Admin Dashboard Conversation 页面已显示 route selected、selected tool、tool status、result summary、event timeline 和 full metadata panel。事件包括 `route_selected`、`tool_execution_started`、`tool_execution_completed`、`agent_execution_started`、`planning_execution_started`、`bridge_fallback`、`bridge_error`。当前仍是 polling，不是 WebSocket，不是 SSE，不是完整 ChatGPT UI，也不是 autonomous agent。

## Phase 39：Conversation Approval Panel

Admin Dashboard Conversations 页面已支持 Approval Flow Foundation：

- pending approvals panel
- proposed action preview
- proposed payload JSON
- risk badge
- approve / reject / cancel buttons
- execute approved action button
- approval events timeline

相关 API：`GET /api/v1/conversations/{thread_id}/approvals`、`POST /api/v1/conversation-approvals/{approval_id}/approve`、`/reject`、`/cancel`、`/execute`。当前是审核门禁基础，不是完整权限系统，not a full permission system；不做真实平台发布、真实 OpenClaw、登录、验证码、代理、指纹绕过或社媒自动化。
## Phase 40：Playbooks 页面与 Conversation Playbook UI

Admin Dashboard 新增 `Playbooks` 页面，并在 `Conversations` 页面增加：

- Playbook selector
- Playbook list / description
- Run playbook button
- Playbook Runs
- Step Timeline
- Approval-aware execution controls

## Phase 41：Output Library

Admin Dashboard 新增 Output Library 页面：
- artifact list
- artifact detail
- artifact type badge
- source type
- related thread
- related Playbook Run
- preview content
- Export markdown / json / txt
- filter by `artifact_type` / `source_type`

Conversation 页面同步显示 generated artifacts，并且 assistant message 支持 Save as Artifact。Playbook Run 完成后自动生成的 artifacts 会出现在 Output Library。

当前边界：Output Library 不是完整素材管理系统（not a full DAM），不接 S3 / MinIO，不做真实平台发布资产管理。

可查看内置模板：`browser_search_summary`、`browser_screenshot_report`、`rag_answer`、`content_generation`、`trend_research_draft`、`openclaw_mock_device_check`。

当前只提供基础运行和监控入口，不提供复杂可视化 workflow editor，不做真实社媒发布，不绕过 Phase 39 approval gate。
## Phase 42: Task Orchestration & Background Execution

  Task Orchestration foundation?`task_runs`?`task_run_events`?`TaskOrchestratorService`?`BackgroundTaskExecutor`?`TaskRetryPolicy`?Conversation / Playbook   `execution_mode=background`   `/api/v1/task-runs`   queued?running?waiting_approval?retrying?completed?failed?cancelled?expired   timeline?`scheduled_at`   scheduled run?retry   exponential backoff?approval resume   Phase 39 Approval Gate?Output Library artifacts   `task_run_id`   artifact linkage?

  in-process queue  Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue  OpenClaw?ComfyUI
## Phase 43: Task Scheduler Persistence & Worker Recovery

 Task Scheduler Persistence?`task_scheduler_state`?`task_runs` ? Task Lease  `TaskRecoveryService`?Scheduler Health API?manual recovery API?Failed Diagnostics  scheduler health

Task Lease?running task run   `lease_owner`?`lease_token`?`lease_expires_at`?`heartbeat_at`?expired lease ? stale heartbeat   scan ? manual recover

Recovery rules?running + expired lease ? stale heartbeat -> retrying  retry budget ? failed?pending scheduled due -> queued?retrying delay elapsed -> queued?waiting_approval  completed/cancelled/expired

Admin Dashboard   Scheduler Health?lease status?recoverable badge?diagnostics panel?scheduled due indicator?manual recover?Worker Console ? Worker Console Desktop   Task recovery

  in-process scheduler foundation  Celery  Kubernetes  production HA distributed queue?
## Phase 43: Scheduler Health ? Task Recovery

Admin Dashboard   Scheduler Health ? Task Runs   scheduler status?heartbeat?last scan?active task count?recovered task count?Task Lease  recoverable badge?scheduled due indicator?Failed Diagnostics ? manual recover  production HA queue?

<!-- PHASE44_ADMIN:START -->
## Phase 44 Artifact Explorer

Admin Dashboard   Artifact Explorer   Output Library records  artifact_role?artifact_stage?retention_policy?exportable?root/parent artifact IDs?lineage graph metadata?export actions?package actions?archived indicator?retention badge?bundle download metadata  Phase 44 Output Artifact Pipeline APIs  DAM  production object storage platform?
<!-- PHASE44_ADMIN:END -->

<!-- PHASE44_SYNC:START -->
## Phase 44: Output Artifact Pipeline & Export System

Phase 44 ? Phase 41 Output Library ? Phase 42/43 task runtime   Output Artifact Pipeline  Artifact lineage?relationship graph retention policy preview  Artifact Explorer



- `output_artifacts`   `parent_artifact_id`?`root_artifact_id`?`source_task_run_id`?`source_playbook_run_id`?`source_conversation_id`?`source_runtime_session_id`?`artifact_role`?`artifact_stage`?`generated_by`?`exportable`?`retention_policy`?`expires_at`?
- `artifact_relationships`   relationship graph   `derived_from`?`packaged_into`?`summarized_from`?`exported_from`?`replay_of`?
- `ArtifactExportService`   `export_markdown`?`export_html`?`export_json`?`export_bundle_zip`?`export_report_package`  browser runtime ? playbook?
- `ArtifactPackagingService`   `package_playbook_run`?`package_task_run`?`package_browser_runtime_session`?`package_conversation`  package artifact ? `bundle.zip` metadata?
- `ArtifactRetentionService`   retention policy?expiration scan?cleanup preview?soft archive   preview
- API   `GET /api/v1/output-artifacts/{artifact_id}/lineage`?`GET /api/v1/output-artifacts/{artifact_id}/relationships`?`POST /api/v1/output-artifacts/{artifact_id}/export`?`POST /api/v1/output-artifacts/{artifact_id}/package`?`POST /api/v1/output-artifacts/cleanup/preview`?
- Storage roots   `storage/output_artifacts`?`storage/output_packages`?`storage/output_exports`?
- Admin Dashboard   Artifact Explorer?lineage graph panel?export actions?package actions?retention badge?archived indicator?bundle metadata preview?
- Worker Console / Desktop   export?package?lineage summary?retention status



-   DAM
-   production object storage platform?
-   S3 / MinIO / CDN?
- Export   Browser Runtime?Playbook?Conversation?OpenClaw ? Task action?
-   TikTok / YouTube / X automation  OpenClaw ? ComfyUI?
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

<!-- PHASE47_SYNC:START -->
## Phase 47：Workflow Template Library

Admin Dashboard 新增 Workflow Templates / Template Library 页面，用于查看和运行 Workflow Template Registry & Versioning：

- 显示 `workflow_templates`、`workflow_template_versions`、`workflow_template_runs`。
- 展示 `template_key`、`current_version`、`latest_version`、`risk_level`、`validation_status`、`compatibility`。
- 支持查看 built-in templates：`browser_screenshot_report_graph`、`content_generation_graph`、`rag_answer_graph`、`approval_then_browser_graph`、`openclaw_mock_inspect_graph`、`task_retry_demo_graph`。
- 支持 Validation result、Compatibility result、Import / Export JSON、Run template、Template runs。
- Output Library / Task Runs / Agent Memory Snapshot detail 可显示 `workflow_template_id`、`workflow_template_version_id`、`workflow_template_run_id`。

当前 Template Library 是注册、版本和运行入口，不是可视化 DAG builder，不是 drag/drop workflow editor，不接 ComfyUI，也不做真实平台自动化。
<!-- PHASE47_SYNC:END -->

<!-- PHASE48_SYNC:START -->
## Phase 48: Workflow Template Marketplace & Governance Foundation

Status: completed.

Phase 48 ? Phase 47 Workflow Template Registry & Versioning   Marketplace foundation  public marketplace  SaaS marketplace  DAG editor  ComfyUI?

Completed scope:

-   `workflow_template_reviews`  review queue?`review_status`?`risk_assessment`?`compatibility_report`?approve / reject / request changes?
-   `workflow_template_promotions`  activate?rollback?deprecate?archive ? `promotion_type`  reason?
-   `workflow_template_audit_logs`  audit trail?actor?previous_state?new_state?metadata?
-   `workflow_template_compatibility_matrix`  runtime capability   `browser_runtime`?`approval_gate`?`task_scheduler`?`artifact_pipeline`?`workflow_graph_runtime`?`openclaw_mock`?`rag_pipeline`
-   `WorkflowTemplateGovernanceService`  `submit_for_review`?`approve_review`?`reject_review`?`request_changes`?`activate_template_version`?`rollback_template_version`?`deprecate_template`?`archive_template`?`list_review_queue`?`list_governance_events`?
- Template lifecycle?draft -> review -> approved -> active -> deprecated -> archived?review   activate?active version  deprecated  archived  rollback
- Marketplace foundation ? `workflow_templates`   `featured`?`verified`?`recommended`?`usage_count`?`success_rate`?`average_runtime_ms`?`average_step_count`  governance badges?risk badge?verified badge?featured templates?recommended templates?
- Output Artifact lineage   `source_template_review_id` ? `governance_state`?Workflow Runs   template governance state ? compatibility snapshot?
- Admin Dashboard   Template Governance   Review Queue?Approval / Reject / Request Changes?Template Lifecycle View?Audit Log View?Marketplace View?Compatibility Matrix View?Rollback UI?
- Worker Console ? Worker Console Desktop ? Template Library   governance status?template verification status ? compatibility summary?

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

Phase 50   Desktop Console Runtime UX & Client Packaging Readiness?Tauri icon resource  `worker_console_desktop/src-tauri/icons/icon.ico`  `bundle.icon`   `["icons/icon.ico"]`?

Start Runtime diagnostics  `starting`?`started`?`failed`?`unavailable`?`port_conflict`?`missing_config`?`server_environment_warning`?Desktop Console   local worker diagnostics  `/local/status`?`/local/health`?runtime port?`server_url`?`worker_base_url`?last attempted action?last error detail?last successful sync?

 /  Worker Runtime  worker  worker  E2E   Desktop Console?

  packaging readiness?not final installer?no code signing?no auto updater?no MSI/EXE release packaging  not ComfyUI?

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

 Phase 51   release readiness  code signing?auto updater?MSI/EXE?DMG/notarization ? Kubernetes/Helm?

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
