# Worker Client 安装与本地 Runtime 管理

状态：已完成，Phase 29。

本文说明客户机 Worker 的本地安装、注册、启动、状态、日志和 Worker Console Foundation。当前没有 GUI、系统托盘、Electron、Tauri、PySide、exe/dmg 打包或真实平台自动化。

## 当前能力

- `Worker Runtime Manager`：`worker_client/runtime_manager.py`
- 本地状态：`worker_client/status.py`
- 状态文件：`worker_client/runtime_state/status.json`
- 本地日志：`worker_client/logging.py`
- 日志文件：`worker_client/logs/worker.log`
- Local API client：`worker_client/local_api_client.py`
- Packaging Scripts：`packaging/windows_start_worker.ps1`、`packaging/mac_start_worker.sh`
- Desktop Runtime Placeholder：`worker_client/desktop/README.md`

## Windows

```powershell
copy worker_client\worker_config.example.yaml worker_client\worker_config.yaml
.\packaging\windows_install_requirements.ps1
.\packaging\windows_register_worker.ps1
.\packaging\windows_start_worker.ps1
```

停止：

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

停止：

```bash
bash packaging/mac_stop_worker.sh
```

## 本地管理 API

默认监听：

```text
http://127.0.0.1:9100
```

接口：

- `GET /local/status`
- `GET /local/health`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`
- `GET /local/logs`

## 安全说明

- `worker_client/worker_state.json` 保存明文 `worker_secret`，只存在客户机本地，已加入 `.gitignore`。
- `worker_client/runtime_state/status.json` 不包含 `worker_secret`。
- `worker_client/logs/worker.log` 会做基础 secret 脱敏。
- 不要把 `worker_config.yaml`、`worker_state.json`、runtime state 或 logs 提交到 Git。

## 当前边界

当前只是 Worker Console Foundation，不是 Worker Console GUI。未实现 GUI、系统托盘、Electron、Tauri、PySide、exe/dmg、TikTok / YouTube / X 自动化、自动登录、Cookie 注入、指纹绕过、代理池或验证码自动化。
## Phase 31：桌面控制台入口

Phase 31 新增 `worker_console_desktop`，作为 Tauri 桌面壳基础。安装并启动 `worker_client` 后，可以用桌面控制台连接本地 Local API：

```powershell
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

默认连接：

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

当前仍没有正式安装包、no exe / dmg、no system tray、no auto update；这只是 Worker Console Desktop App Foundation。

## Phase 32：托盘运行说明

Phase 32 后，桌面端支持 System Tray 和 Minimize To Tray。启动方式不变：

```powershell
python -m worker_client.cli start
cd worker_console_desktop
npm run tauri dev
```

托盘菜单可以控制 Start Runtime、Stop Runtime、Restart Runtime、Start Heartbeat、Stop Heartbeat 和 Refresh Status。它只调用本地 Worker API，不执行 shell 命令。

当前仍没有正式 installer、没有 auto-update、没有真正开机自启。

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

```powershell
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

```powershell
python -m worker_client.cli register --config worker_client\worker_config.yaml
python -m worker_client.cli start --config worker_client\worker_config.yaml
```

Then validate from AI Server:

```powershell
python scripts\validate_real_client_worker_e2e.py `
  --server-url http://localhost:8000 `
  --workspace-id demo-workspace `
  --user-id demo-user `
  --expected-worker-name customer-machine-worker-1
```

If the worker is not online, the script returns `SKIPPED` and `real client worker not online`. This is the correct result when the real customer machine is unavailable.

Do not expose port 9100 to the public internet; use Tailscale, VPN, or LAN.

## Phase 35A 说明：Runtime 可观测性

客户机 Worker 不需要新增真实平台能力。AI Server 会在 Browser Runtime 动作后记录 Timeline、Snapshots 和 Replay metadata。

客户机仍需满足 Phase 34 要求：

```powershell
playwright install chromium
```

Phase 35A 不会要求客户机提供 live stream、VNC/noVNC、DevTools remote control，也不会重新执行 replay。不要把 9100 端口暴露到公网；推荐 Tailscale、VPN 或可信局域网。

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
## Phase 38 对 worker_client 的影响

Phase 38 不改变 worker_client 安装流程。Conversation Runtime 通过 Browser Bridge 调用 `browser_tool` 时，仍依赖已注册且在线的 Browser Worker / worker_client runtime。若 worker 不在线，Conversation run 会通过 `tool_execution_failed` / `bridge_fallback` 返回清晰错误，不会伪造执行成功。

## Phase 41 对 worker_client 的影响

Phase 41 不改变 worker_client 安装流程。Output Library 在 AI Server 侧保存 artifacts；worker_client 仍只负责 Browser Runtime / Playwright 执行和结果回传。截图文件仍由既有 screenshot storage 管理，Output Library 只保存引用路径。
## Phase 42?Task Orchestration & Background Execution

????? Task Orchestration foundation?`task_runs`?`task_run_events`?`TaskOrchestratorService`?`BackgroundTaskExecutor`?`TaskRetryPolicy`?Conversation / Playbook ??? `execution_mode=background` ??????? `/api/v1/task-runs` ?? queued?running?waiting_approval?retrying?completed?failed?cancelled?expired ??? timeline?`scheduled_at` ?? scheduled run?retry ?? exponential backoff?approval resume ???? Phase 39 Approval Gate?Output Library artifacts ?? `task_run_id` ?? artifact linkage?

???????? in-process queue??? Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue???????????? OpenClaw?ComfyUI?????????????
## Phase 43?Task Scheduler Persistence & Worker Recovery?????

????Task Scheduler Persistence?`task_scheduler_state`?`task_runs` ? Task Lease ???`TaskRecoveryService`?Scheduler Health API?manual recovery API?Failed Diagnostics????? scheduler health ???

Task Lease?running task run ??? `lease_owner`?`lease_token`?`lease_expires_at`?`heartbeat_at`?expired lease ? stale heartbeat ??? scan ? manual recover ???

Recovery rules?running + expired lease ? stale heartbeat -> retrying????? retry budget ? failed?pending scheduled due -> queued?retrying delay elapsed -> queued?waiting_approval ??????completed/cancelled/expired ????

Admin Dashboard ?? Scheduler Health?lease status?recoverable badge?diagnostics panel?scheduled due indicator?manual recover?Worker Console ? Worker Console Desktop ???? Task recovery ???

??????? in-process scheduler foundation??? Celery??? Kubernetes???? production HA distributed queue?

<!-- PHASE44_SYNC:START -->
## Phase 44?Output Artifact Pipeline & Export System

Phase 44 ? Phase 41 Output Library ? Phase 42/43 task runtime ?????? Output Artifact Pipeline????? Artifact lineage?relationship graph???????retention policy preview????? Artifact Explorer ?????

???????

- `output_artifacts` ?? `parent_artifact_id`?`root_artifact_id`?`source_task_run_id`?`source_playbook_run_id`?`source_conversation_id`?`source_runtime_session_id`?`artifact_role`?`artifact_stage`?`generated_by`?`exportable`?`retention_policy`?`expires_at`?
- `artifact_relationships` ?? relationship graph ???? `derived_from`?`packaged_into`?`summarized_from`?`exported_from`?`replay_of`?
- `ArtifactExportService` ?? `export_markdown`?`export_html`?`export_json`?`export_bundle_zip`?`export_report_package`??????? browser runtime ? playbook?
- `ArtifactPackagingService` ?? `package_playbook_run`?`package_task_run`?`package_browser_runtime_session`?`package_conversation`??? package artifact ? `bundle.zip` metadata?
- `ArtifactRetentionService` ?? retention policy?expiration scan?cleanup preview?soft archive ????? preview ????????
- API ?? `GET /api/v1/output-artifacts/{artifact_id}/lineage`?`GET /api/v1/output-artifacts/{artifact_id}/relationships`?`POST /api/v1/output-artifacts/{artifact_id}/export`?`POST /api/v1/output-artifacts/{artifact_id}/package`?`POST /api/v1/output-artifacts/cleanup/preview`?
- Storage roots ?? `storage/output_artifacts`?`storage/output_packages`?`storage/output_exports`?
- Admin Dashboard ?? Artifact Explorer?lineage graph panel?export actions?package actions?retention badge?archived indicator?bundle metadata preview?
- Worker Console / Desktop ???? export?package?lineage summary?retention status ???

???

- ?????? DAM ???
- ???? production object storage platform?
- ??????? S3 / MinIO / CDN?
- Export ?????? Browser Runtime?Playbook?Conversation?OpenClaw ? Task action?
- ????? TikTok / YouTube / X automation???????????????????????? OpenClaw ? ComfyUI?
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

Worker client 安装方式不变。Workflow Template Registry & Versioning 位于 AI Server 和前端控制台侧；客户机继续提供 browser runtime / worker runtime API。Template Library 可选择 `browser_screenshot_report_graph` 等模板，但不会改变客户机安全边界，也不接 ComfyUI、TikTok / YouTube / X 或真实平台自动化。
<!-- PHASE47_SYNC:END -->

<!-- PHASE48_SYNC:START -->
## Phase 48?Workflow Template Marketplace & Governance Foundation

Status: completed.

Phase 48 ? Phase 47 Workflow Template Registry & Versioning ??????????? Marketplace foundation???????????????? public marketplace????????????? SaaS marketplace?????? DAG editor???? ComfyUI?

Completed scope:

- ?? `workflow_template_reviews`??? review queue?`review_status`?`risk_assessment`?`compatibility_report`?approve / reject / request changes?
- ?? `workflow_template_promotions`??? activate?rollback?deprecate?archive ? `promotion_type`??????????? reason?
- ?? `workflow_template_audit_logs`????? audit trail?actor?previous_state?new_state?metadata?
- ?? `workflow_template_compatibility_matrix`?? runtime capability ?? `browser_runtime`?`approval_gate`?`task_scheduler`?`artifact_pipeline`?`workflow_graph_runtime`?`openclaw_mock`?`rag_pipeline` ??????
- ?? `WorkflowTemplateGovernanceService`??? `submit_for_review`?`approve_review`?`reject_review`?`request_changes`?`activate_template_version`?`rollback_template_version`?`deprecate_template`?`archive_template`?`list_review_queue`?`list_governance_events`?
- Template lifecycle?draft -> review -> approved -> active -> deprecated -> archived?review ????? activate?active version ?????deprecated ???????archived ??????rollback ???????
- Marketplace foundation ? `workflow_templates` ??? `featured`?`verified`?`recommended`?`usage_count`?`success_rate`?`average_runtime_ms`?`average_step_count`???? governance badges?risk badge?verified badge?featured templates?recommended templates?
- Output Artifact lineage ?? `source_template_review_id` ? `governance_state`?Workflow Runs ??? template governance state ? compatibility snapshot?
- Admin Dashboard ?? Template Governance ????? Review Queue?Approval / Reject / Request Changes?Template Lifecycle View?Audit Log View?Marketplace View?Compatibility Matrix View?Rollback UI?
- Worker Console ? Worker Console Desktop ? Template Library ??? governance status?template verification status ? compatibility summary?

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

