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

```powershell
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

```powershell
copy worker_client\worker_config.example.yaml worker_client\worker_config.yaml
python -m worker_client.cli register --config worker_client\worker_config.yaml
python -m worker_client.cli start --config worker_client\worker_config.yaml
```

The registration step stores `worker_state.json` locally. Do not commit it. Do not paste the worker secret into docs, issues, screenshots, or logs.

## Worker Console Checklist

Web Console:

```powershell
cd worker_console
npm.cmd run dev
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

```powershell
cd worker_console_desktop
npm.cmd run tauri dev
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

```powershell
python scripts\validate_real_client_worker_e2e.py `
  --server-url http://localhost:8000 `
  --workspace-id demo-workspace `
  --user-id demo-user `
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
## Phase 35A 调试扩展

完成真实客户机 E2E 后，可以继续调用 Browser Runtime Observability API 排查执行过程：

1. `GET /api/v1/browser-runtime/sessions/{session_id}/events`
2. `GET /api/v1/browser-runtime/sessions/{session_id}/snapshots`
3. `POST /api/v1/browser-runtime/sessions/{session_id}/replay`
4. `GET /api/v1/browser-runtime/replays/{replay_id}/export`

这些接口只生成 Timeline、Snapshot Storage 和 metadata-only replay；不会重新执行浏览器动作，也不是 live stream / VNC / noVNC / DevTools remote control。

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
## Phase 38 验证补充

真实客户机 Worker E2E 验证可增加 Conversation run 场景：创建 conversation 后发送“请打开 https://example.com 并截图”，检查 `route_name=browser`、`selected_tool=browser_tool`、`events_created`、`result_metadata`，以及事件 `route_selected`、`tool_execution_started`、`tool_execution_completed`。若客户机不在线，必须标记为 SKIPPED 或清晰失败，不允许伪造成功。

## Phase 41 验证补充

真实客户机完成 Playbook 或 Conversation 后，可验证 Output Library：`GET /api/v1/output-artifacts`、`POST /api/v1/output-artifacts/from-playbook-run/{run_id}`、`POST /api/v1/output-artifacts/from-message/{message_id}`、`GET /api/v1/output-artifacts/{artifact_id}/export?format=markdown`。截图 artifact 只引用路径，不复制大截图文件；当前不接 S3 / MinIO，也不是完整 DAM。
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

Real client worker E2E validation is unchanged by Workflow Graph Runtime. Graph planner and Replay Foundation metadata may reference browser/runtime artifacts through `producing_node_key`, `replay_source`, and `graph_lineage`, but this does not add remote desktop streaming, ComfyUI, real OpenClaw, or social platform automation.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47：真实客户机 E2E 关系

Workflow Template Registry & Versioning 运行在 AI Server 侧。真实客户机 Worker 的 E2E 验证流程不变；模板可以选择 Browser Graph 模板触发远程 Browser Runtime，但仍必须遵守 approval/risk gate。当前仍不做 TikTok / YouTube / X、登录、验证码、代理、指纹、真实 OpenClaw 或 ComfyUI。
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

## Phase 50?Desktop Console Runtime UX & Client Packaging Readiness

Phase 50 ?? Desktop Console Runtime UX & Client Packaging Readiness?Tauri icon resource ??????`worker_console_desktop/src-tauri/icons/icon.ico` ??????????`bundle.icon` ?? `["icons/icon.ico"]`?

Start Runtime diagnostics ??????????`starting`?`started`?`failed`?`unavailable`?`port_conflict`?`missing_config`?`server_environment_warning`?Desktop Console ??? local worker diagnostics??? `/local/status`?`/local/health`?runtime port?`server_url`?`worker_base_url`?last attempted action?last error detail?last successful sync?

???/??????????????????? Worker Runtime????????????????????? worker???????? worker?????? E2E ???????? Desktop Console?

????? packaging readiness?not final installer?no code signing?no auto updater?no MSI/EXE release packaging??? not ComfyUI?

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

?????Phase 51 ?????????????????????????????????? release readiness???????????????????????????????? code signing?auto updater?MSI/EXE?DMG/notarization ? Kubernetes/Helm?

Keywords: Phase 51; Release Packaging & Deployment Bundle Foundation; release/manifest.json; release/version.json; server deployment bundle; frontend production build bundle; desktop release readiness; aiops.release.env.template; validate_release_packaging.py; Windows / Mac startup scripts; not a formal production release; no code signing; no auto updater; no MSI/EXE; no DMG/notarization; no Kubernetes/Helm.
<!-- PHASE51_SYNC:END -->
