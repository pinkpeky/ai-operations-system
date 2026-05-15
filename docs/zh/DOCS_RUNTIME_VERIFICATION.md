# Docs Runtime Verification

## Phase 20 校验范围

`scripts/verify_docs_runtime.py` 现在会检查 Phase 20 相关文档与 runtime：

- `BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100` 是否写入 `CURRENT_RUNTIME.md` 与 `docker-compose.yml`。
- API Reference 是否记录 `Real Browser Worker Service`、`browser-worker`、`worker/main.py`、`worker/browser_worker/playwright_runtime.py`、`WORKER_TIMEOUT_SECONDS`、`WORKER_SCREENSHOT_DIR`。
- `PROJECT_OVERVIEW.md` 是否记录 Phase 20、API Server -> Worker 链路、Playwright Chromium 和 `worker/screenshots`。
- `PROJECT_STATUS.md` 是否把 Phase 20 标记为已完成。

运行：

```powershell
python scripts/verify_docs_runtime.py
```

## Phase 27 校验范围

`scripts/verify_docs_runtime.py` 现在会校验 Customer Machine Worker Bootstrap：

- 必须存在 `worker_client/main.py`、`worker_client/config.py`、`worker_client/registration.py`、`worker_client/heartbeat.py`、`worker_client/runtime.py`、`worker_client/cli.py`、`worker_client/worker_config.example.yaml`。
- `API_REFERENCE.md` 必须记录 `worker_client`、`worker_config.example.yaml`、`worker_config.yaml`、`worker_state.json`、`python -m worker_client.cli register`、`python -m worker_client.cli heartbeat`、`python -m worker_client.cli serve`、`python -m worker_client.cli start`、`registration flow`、`heartbeat flow`、`local worker runtime`。
- `PROJECT_OVERVIEW.md` 必须记录 Phase 27、Customer Machine Worker Bootstrap、customer machine、registration flow、heartbeat flow、local worker runtime。
- zh/en `PROJECT_STATUS.md` 必须声明 Phase 27 已完成。

如果 Phase 27 CLI、配置结构、本地 runtime 协议或 Worker Client 安全行为发生变化，必须先更新 docs，再运行：

```powershell
python scripts/verify_docs_runtime.py
```

期望结果：`SUMMARY: PASS`。

更新日期：2026-05-12

本文说明如何验证 docs 与当前 runtime 是否一致。

## 目标

Docs Runtime Verification 用于防止：

- API 已新增但 API_REFERENCE 未更新。
- config 默认值改变但 CURRENT_RUNTIME 未更新。
- docker-compose 环境变量与 config 不一致。
- Phase 状态写错。
- docs 写入当前代码不存在的功能。

## 运行方式

在项目根目录执行：

```powershell
python scripts/verify_docs_runtime.py
```

Phase 17 之后，docs verifier 还会检查 Browser Adapter 是否漂移：

- `app/core/config.py`、`docker-compose.yml`、`docs/CURRENT_RUNTIME.md` 中的 `BROWSER_PROVIDER`。
- OpenAPI 和 API Reference 中的 Browser API。
- `browser_sessions`、`browser_actions`、`browser_action_logs`。
- `BrowserProvider`、`MockBrowserProvider`、`PlaywrightBrowserProvider`、`browser_tool`。

当 `BROWSER_PROVIDER=mock` 时，docs 不允许把真实 Playwright / Selenium / OpenClaw 执行写成已完成。

Phase 18 之后，docs verifier 还会检查 Playwright Local Provider 是否漂移：

- `CURRENT_RUNTIME.md` 与 `docker-compose.yml` 必须记录 `BROWSER_TIMEOUT_SECONDS`、`BROWSER_HEADLESS`、`BROWSER_TYPE`、`BROWSER_VIEWPORT_WIDTH`、`BROWSER_VIEWPORT_HEIGHT`、`BROWSER_SCREENSHOT_DIR`。
- OpenAPI 和 API Reference 必须记录 `GET /api/v1/browser/screenshot/{session_id}/{filename}`。
- API Reference 必须记录 `PlaywrightLocalProvider`、`playwright_local`、`browser_id`、`page_id`、`provider_session_metadata`、`selector`、`target_url`、`screenshot_path`、`page_title`、`get_page_content`。
- `PROJECT_OVERVIEW.md` 必须记录 Phase 18、Playwright Local Provider Integration、Screenshot System 和安全边界。

Docs 仍然必须明确：Phase 18 不是 Browser Agent，不做 TikTok / YouTube / X，不做登录自动化、Cookie 注入、指纹绕过、OCR、视觉 AI 或 Browser Worker。

Phase 19 之后，docs verifier 还会检查 Remote Browser Worker 是否漂移：

- `CURRENT_RUNTIME.md` 与 `docker-compose.yml` 必须记录 `BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS`、`BROWSER_WORKER_RETRY_COUNT`。
- OpenAPI 和 API Reference 必须记录 `/api/v1/browser-workers/register`、`/api/v1/browser-workers/{worker_id}/heartbeat`、`/api/v1/browser-workers`。
- OpenAPI 和 API Reference 必须记录 mock runtime：`/api/v1/browser-worker-runtime/health`、`/api/v1/browser-worker-runtime/sessions`、`/api/v1/browser-worker-runtime/actions`、`/api/v1/browser-worker-runtime/sessions/{session_id}/close`。
- API Reference 必须记录 `RemoteBrowserProvider`、`BrowserWorkerClient`、`browser_workers`、`browser_worker_sessions`、`browser_worker_actions`、`remote_session_id`、`remote_action_id`。
- `PROJECT_OVERVIEW.md` 必须记录 Phase 19、Remote Browser Worker Foundation、Worker Registration、Worker Heartbeat、Worker Runtime Mock。

Docs 仍然必须明确：Phase 19 不包含真实外部 worker 部署，不做 TikTok / YouTube / X、账号登录、指纹绕过、代理池或验证码。

通过时应输出：

```text
SUMMARY: PASS
```

## 输出级别

- `PASS`：检查通过。
- `WARNING`：需要人工确认。
- `ERROR`：必须修复，脚本以非 0 状态退出。

## 当前检查范围

脚本读取：

- `app/core/config.py`
- `docker-compose.yml`
- FastAPI OpenAPI schema
- `docs/CURRENT_RUNTIME.md`
- `docs/PROJECT_OVERVIEW.md`
- `docs/zh/API_REFERENCE.md`
- `docs/en/API_REFERENCE.md`
- `docs/zh/PROJECT_STATUS.md`
- `docs/en/PROJECT_STATUS.md`

脚本检查：

- provider 默认值。
- search 默认值。
- embedding dimension。
- upload 配置。
- required API paths。
- `search_mode`、`dense_top_k`、`keyword_top_k`、`final_top_k`、`duplicate_strategy`。
- Phase 12 Task Reliability：`task_events`、`task_logs`、`duration_ms`、cancel、retry、events、logs、observability summary。
- Phase 13 Tool Calling：`/tools`、`/tools/{tool_name}`、`/tools/{tool_name}/execute`、`/tool-calls`、`tool_call_logs`、`tool_name`、`tool_input`、`tool_output`。
- Phase 14 Memory：`/memory/sessions`、`/memory/sessions/{session_id}`、`/memory/messages`、`/memory/messages/{session_id}`、`/memory/memories`、`/memory/memories/{memory_id}`、`conversation_sessions`、`conversation_messages`、`agent_memories`、`memory_trace`、`recent_messages_count`、`retrieved_memories_count`。
- Phase 15 Multi-Agent：`/agents/registry`、`/multi-agent/runs`、`/multi-agent/runs/{run_id}`、`/multi-agent/runs/{run_id}/execute-chain`、`/multi-agent/runs/{run_id}/messages`、`/multi-agent/runs/{run_id}/handoffs`、`agent_runs`、`agent_messages`、`agent_handoffs`、`AgentRegistry`、`agents_involved`、`handoff_trace`。
- Phase 16 Planning：`/plans`、`/plans/{plan_id}`、`/plans/{plan_id}/execute`、`/plans/{plan_id}/cancel`、`/plans/{plan_id}/steps`、`/plans/{plan_id}/reviews`、`plans`、`plan_steps`、`plan_reviews`、`SimplePlannerAgent`、`PlanStep`、`PlanReview`、`memory_trace`。

## Docs Sync 规则

新增 API 时：

1. 更新 route。
2. 更新 schema。
3. 更新 tests。
4. 更新 zh/en API_REFERENCE。
5. 更新 `scripts/verify_docs_runtime.py`。
6. 运行 verifier。

新增配置时：

1. 更新 `app/core/config.py`。
2. 更新 `.env.example`。
3. 更新 `docker-compose.yml`。
4. 更新 `docs/CURRENT_RUNTIME.md`。
5. 更新 zh/en DEPLOYMENT。
6. 运行 verifier。

新增 Phase 时：

1. 更新 `docs/PROJECT_OVERVIEW.md`。
2. 更新 zh/en PROJECT_STATUS。
3. 更新 zh/en ARCHITECTURE。
4. 更新 zh/en API_REFERENCE。
5. 更新 zh/en DEPLOYMENT。
6. 更新 zh/en DEVELOPMENT_GUIDE。
7. 更新 Word 文档。
8. 运行 pytest、Docker smoke test、docs verifier。

## 与测试的关系

`tests/test_docs_runtime_verification.py` 会调用：

```powershell
python scripts/verify_docs_runtime.py
```

因此 docs 漂移会导致 pytest 失败。

## 边界

该脚本是轻量级一致性检查，不替代：

- 完整 API 契约测试。
- 数据库 migration 验证。
- Docker smoke test。
- 安全审计。
- 性能测试。

它的职责是让 docs 不落后于 runtime。
## Phase 21 校验范围

`scripts/verify_docs_runtime.py` 现在会校验 Browser Worker Reliability：

- `CURRENT_RUNTIME.md` 必须记录 worker health、session cleanup、action retry、screenshot retention 配置。
- OpenAPI 必须包含 worker health summary、available workers、mark offline、cleanup sessions、worker sessions、screenshot cleanup。
- `API_REFERENCE.md` 必须记录 `BrowserWorkerHealthService`、`BrowserWorkerSelector`、`BrowserSessionCleanupService`、`ScreenshotCleanupService`、capacity 字段和 retry 字段。
- `PROJECT_STATUS.md` 必须声明 Phase 21 已完成。

如果 Phase 21 相关 API 或配置发生变化，必须先更新 docs，再运行：

```powershell
python scripts/verify_docs_runtime.py
```

## Phase 22 校验范围

`scripts/verify_docs_runtime.py` 现在会校验 Persistent Browser Profile Foundation：

- `CURRENT_RUNTIME.md` 必须记录 `BROWSER_PROFILE_ROOT`。
- OpenAPI 必须包含 browser profile APIs 和 `POST /api/v1/browser/sessions/{session_id}/close`。
- `API_REFERENCE.md` 必须记录 `BrowserProfileService`、`browser_profiles`、`profile_id`、`profile_path`、`persistent_context_enabled`、`locked_by_session_id`、`locked_at`、`last_used_at`、`launch_persistent_context`、`BROWSER_PROFILE_ROOT`、`WORKER_PROFILE_DIR`。
- `PROJECT_OVERVIEW.md` 必须记录 Phase 22、Profile Lock / Profile Release、worker-side persistent context 和 `worker/profiles`。
- `PROJECT_STATUS.md` 必须声明 Phase 22 已完成。

如果 Phase 22 API、schema 字段或 profile runtime 配置发生变化，必须先更新 docs，再运行：

## Phase 23 校验范围

`scripts/verify_docs_runtime.py` 现在会校验 Browser Profile Health & Recovery：

- `config.py`、`.env.example`、`docker-compose.yml` 必须记录 `BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS`、`BROWSER_PROFILE_BACKUP_ENABLED`、`BROWSER_PROFILE_MAX_BACKUPS`、`BROWSER_PROFILE_UNUSED_DAYS`、`BROWSER_PROFILE_BACKUP_ROOT`。
- OpenAPI 必须存在 `GET /api/v1/browser/profiles/health/summary`、`POST /api/v1/browser/profiles/{profile_id}/health-check`、`POST /api/v1/browser/profiles/recover-stale-locks`、`POST /api/v1/browser/profiles/{profile_id}/backup`、`GET /api/v1/browser/profiles/{profile_id}/backups`、`POST /api/v1/browser/profiles/{profile_id}/restore`、`POST /api/v1/browser/profiles/cleanup`、`GET /api/v1/browser/profiles/{profile_id}/usage-logs`。
- `API_REFERENCE.md` 必须记录 `BrowserProfileHealthService`、`BrowserProfileBackupService`、`BrowserProfileCleanupService`、`browser_profile_usage_logs`、`health_status`、`last_health_check_at`、`last_error`、`usage_count`、`corrupted_at`、`backup_path`、`last_backup_at`、`recover-stale-locks`、`health/summary`。
- `PROJECT_OVERVIEW.md` 必须记录 Phase 23、profile health、stale lock recovery、profile backup、profile cleanup。
- `PROJECT_STATUS.md` 必须声明 Phase 23 已完成。

如果 Phase 23 API、schema 字段、migration 或运行配置发生变化，必须先更新 docs，再运行：

```powershell
python scripts/verify_docs_runtime.py
```

```powershell
python scripts/verify_docs_runtime.py
```
## Phase 24 校验范围

`scripts/verify_docs_runtime.py` 现在会校验 Human-in-the-loop Browser Control：

- `config.py`、`.env.example`、`docker-compose.yml` 必须记录 `BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS`。
- OpenAPI 必须存在 `/api/v1/browser/human-control/request`、`/api/v1/browser/human-control`、`/api/v1/browser/human-control/{control_session_id}`、approve/start/complete/cancel/events，以及 worker runtime metadata-level `/human-control/*` 路由。
- `API_REFERENCE.md` 必须记录 `BrowserHumanControlService`、`browser_human_control_sessions`、`browser_human_control_events`、`human_control_status`、`human_control_session_id`、`paused_at`、`resumed_at`、`request_human_control`、`complete_human_control`。
- `PROJECT_OVERVIEW.md` 必须记录 Phase 24、Human-in-the-loop Browser Control、session paused/resumed 行为和 worker metadata-level 边界。
- `PROJECT_STATUS.md` 必须声明 Phase 24 已完成。

如果 Phase 24 API、schema 字段、migration 或运行配置发生变化，必须先更新 docs，再运行：

```powershell
python scripts/verify_docs_runtime.py
```

## Phase 25 校验范围

`scripts/verify_docs_runtime.py` 现在会校验 Browser Worker UI Access Placeholder：

- `config.py`、`.env.example`、`docker-compose.yml` 必须记录 `BROWSER_UI_ACCESS_TIMEOUT_SECONDS`。
- OpenAPI 必须存在 `/api/v1/browser/ui-access`、`/api/v1/browser/ui-access/expire`、`/api/v1/browser/ui-access/{access_session_id}`、revoke、validate，以及 `/api/v1/browser-worker-runtime/ui-access/capabilities`。
- `API_REFERENCE.md` 必须记录 `BrowserUIAccessService`、`browser_ui_access_sessions`、`access_token_hash`、`remote_control_url`、`live_view_url`、`devtools_url`、`create_ui_access`、`revoke_ui_access`。
- `PROJECT_OVERVIEW.md` 必须记录 Phase 25、Browser Worker UI Access Placeholder、access token hash、placeholder URL，并明确当前不支持真实 VNC/noVNC/DevTools UI。
- `PROJECT_STATUS.md` 必须声明 Phase 25 已完成。

如果 Phase 25 API、schema 字段、migration 或运行配置发生变化，必须先更新 docs，再运行：

```powershell
python scripts/verify_docs_runtime.py
```

## Phase 26 校验范围

`scripts/verify_docs_runtime.py` 现在会校验 Browser Worker Security & Access Control：

- `CURRENT_RUNTIME.md` 必须记录 `BROWSER_WORKER_AUTH_ENABLED`、`BROWSER_WORKER_AUTH_STRICT`、`BROWSER_ALLOWED_DOMAINS`、`BROWSER_BLOCKED_DOMAINS`、`BROWSER_ALLOW_EXTERNAL_DOMAINS`。
- OpenAPI 必须包含 `POST /api/v1/browser-workers/{worker_id}/rotate-secret`、`POST /api/v1/browser-workers/{worker_id}/revoke`、`GET /api/v1/browser/security/audit-logs`、`POST /api/v1/browser/security/policy/check`。
- `API_REFERENCE.md` 必须记录 `BrowserWorkerAuthService`、`worker_secret_hash`、`X-Worker-Signature`、`UI Access Scope`、`BrowserActionPolicyService` 和 `browser_security_audit_logs`。
- `PROJECT_OVERVIEW.md` 必须记录 Phase 26、Browser Worker Security & Access Control、signed worker request、UI Access Scope 和 Browser Action Policy。
- `PROJECT_STATUS.md` 必须声明 Phase 26 已完成。

如果 Phase 26 API、schema 字段、migration 或运行配置发生变化，必须先更新 docs，再运行：

```powershell
python scripts/verify_docs_runtime.py
```

## Phase 29 Worker Client Runtime Verification

Docs verification now also checks Worker Console Foundation files: `worker_client/runtime_manager.py`, `worker_client/status.py`, `worker_client/logging.py`, `worker_client/local_api_client.py`, `packaging/windows_start_worker.ps1`, `packaging/mac_start_worker.sh`, and Worker Client install docs.

After any Worker Client runtime change, run:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

The local runtime API is documented as local-only: `GET /local/status`, `GET /local/health`, `POST /local/runtime/start`, `POST /local/runtime/stop`, `POST /local/runtime/restart`, `POST /local/heartbeat/start`, `POST /local/heartbeat/stop`, `GET /local/logs`.

## Phase 30 Worker Console Docs Verification

Docs verifier checks `worker_console`, `worker_console/src/api/localWorkerClient.ts`, `VITE_LOCAL_WORKER_API`, `http://127.0.0.1:9100`, Worker Console GUI Foundation docs, and the explicit no system tray / no exe / dmg boundary.
## Phase 31 校验补充

Docs Runtime Verification 现在覆盖 Worker Console Desktop App Foundation。校验项包括：

- `worker_console_desktop/package.json`
- `worker_console_desktop/src/api/localWorkerClient.ts`
- `worker_console_desktop/src-tauri/tauri.conf.json`
- `VITE_LOCAL_WORKER_API=http://127.0.0.1:9100`
- `npm run tauri dev`
- `Worker Console Desktop App Foundation`

Phase 31 完成后仍必须执行：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

当前桌面端只是 Tauri 基础壳：没有正式安装包、no exe / dmg、no system tray、no auto update。

## Phase 32 校验补充

Docs Runtime Verification 现在覆盖 Worker Console System Tray & Desktop Runtime Foundation。校验项包括：

- `worker_console_desktop/src-tauri/src/main.rs`
- `worker_console_desktop/src-tauri/desktop-runtime.json`
- `worker_console_desktop/src/settings.ts`
- `worker_console_desktop/src/desktopBridge.ts`
- `worker_console_desktop/settings.example.json`
- `worker_console_desktop/autostart/README.md`
- `System Tray`
- `Minimize To Tray`
- `Tray Runtime Control`
- `Desktop Status Sync`
- `AutoStart Placeholder`

仍必须区分已完成与未完成：当前没有 formal installer、没有 auto-update、没有真正开机自启。

## Phase 33?Conversation Runtime Foundation

???????

????`conversation_threads`?`conversation_events`??? `conversation_messages.thread_id`?`ConversationService`?`run_conversation_turn`?Conversation APIs?Worker Console Chat Panel Foundation?Event Timeline?polling event feed?

???????`message_received`?`planning_started`?`plan_created`?`agent_started`?`tool_called`?`worker_action_started`?`worker_action_completed`?`assistant_response`?`error`?

??????? Conversation Runtime Foundation???? WebSocket/SSE????? OpenClaw??? ComfyUI??? TikTok / YouTube / X??????Cookie ????????????????????????

## Phase 34 Docs Runtime Verification

The verifier now checks that Phase 34 Remote Browser Runtime Foundation is reflected in runtime docs:

- `browser_runtime_sessions`
- `BrowserRuntimeSessionService`
- `app/browser/providers/remote_provider.py`
- `worker_client/browser_runtime`
- `/browser/session/create`
- `/browser/session/{session_id}/navigate`
- `/browser/session/{session_id}/screenshot`
- `/browser/session/{session_id}/page`
- `/browser/session/{session_id}/close`
- `storage/browser_screenshots`
- `BROWSER_RUNTIME_SCREENSHOT_DIR`
- `Browser Sessions Panel`
- `playwright install chromium`

Run:

```powershell
python scripts/verify_docs_runtime.py
```

The expected result is `SUMMARY: PASS`.

## Phase 35B Docs Runtime Verification

The verifier now requires:

- `scripts/validate_real_client_worker_e2e.py`
- `docs/zh/REAL_CLIENT_WORKER_E2E.md`
- `docs/en/REAL_CLIENT_WORKER_E2E.md`
- `Real Client Worker E2E Validation Plan`
- `expected_worker_name`
- `SKIPPED`
- `real client worker not online`
- `do not expose port 9100 to the public internet`
- `Tailscale`
- `VPN`

This keeps docs honest: Phase 35B prepares validation ability and does not claim a real customer-machine E2E pass until the customer machine is actually online.

## Phase 35A 校验项

Docs Runtime Verification 现在检查 Browser Runtime Observability & Replay 是否与 runtime 一致，包括：

- `BrowserRuntimeObservabilityService`
- `browser_runtime_events`
- `browser_runtime_snapshots`
- `browser_runtime_replays`
- `BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots`
- events / snapshots / replay / replay export API
- API_REFERENCE 中的 metadata-only replay、Snapshot Storage、Timeline Event Flow、Failure Debug 说明

运行：

```powershell
python scripts/verify_docs_runtime.py
```

必须返回 `SUMMARY: PASS`。Replay 当前不是 live stream，不是 VNC/noVNC，不是 DevTools remote control，也不会重新执行浏览器动作。

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
## Phase 38 Docs Runtime Verification 补充

`scripts/verify_docs_runtime.py` 现在检查 `app/conversation/tool_router.py`、`Conversation Runtime Tool Execution Bridge`、`ConversationToolRouter`、`route_selected`、`tool_execution_started`、`route_name`、`selected_tool`、`events_created`、`success`、`summary`、`result_metadata` 以及 not autonomous agent / not WebSocket / not SSE 边界说明。

Phase 39 后，verifier 还检查 `app/conversation/risk_policy.py`、`app/conversation/services/approval_service.py`、`app/api/routes/conversation_approvals.py`、`conversation_approvals`、`ConversationApprovalService`、`ConversationRiskPolicy`、`review_first`、`auto_safe`、`execute_after_approval`、approval events、pending approvals panel 与 not a full permission system 边界说明。
## Phase 40 Docs Runtime Verification

Verifier 检查项新增：

- `app/conversation/services/playbook_service.py`
- `app/conversation/playbook_definitions.py`
- `app/api/routes/conversation_playbooks.py`
- OpenAPI Playbook routes
- `conversation_playbooks`
- `conversation_playbook_runs`
- `playbook_name`
- `playbook_run_id`
- `playbook_step_started`
- `playbook_waiting_approval`
- `playbook_completed`

如果新增或删除 Playbook API，必须同步 `scripts/verify_docs_runtime.py`。

## Phase 41 验证补充

Docs verifier 现在检查 Output Library：`output_artifacts`、`OutputArtifactService`、`/api/v1/output-artifacts`、artifact events、Save as Artifact、Export markdown、S3 / MinIO 边界和 not a full DAM 声明。新增或删除 Output Artifact API、字段或前端入口时，必须同步 `scripts/verify_docs_runtime.py`。
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
## Phase 46 Docs Verification

Docs verifier now checks Workflow Graph Runtime terms and routes: `workflow_graphs`, `workflow_graph_nodes`, `workflow_graph_edges`, `workflow_replays`, `WorkflowExecutionPlanner`, `SafeConditionEvaluator`, Conditional Execution, Retry/Fallback Path, Replay Foundation, `current_node_key`, `planned_next_nodes`, `skipped_nodes`, `producing_node_key`, `graph_lineage`, and the boundaries not a visual DAG builder, not distributed orchestration engine, and not ComfyUI.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47：Docs Runtime Verification

`scripts/verify_docs_runtime.py` 已加入 Phase 47 检查项：必需文件、OpenAPI 路由、API_REFERENCE 字段、PROJECT_OVERVIEW、PROJECT_STATUS 均需覆盖 Workflow Template Registry & Versioning、`workflow_templates`、`workflow_template_versions`、`workflow_template_runs`、`WorkflowTemplateRegistryService`、`WorkflowTemplateCompatibilityService`、Template Library、Import / Export 和 built-in templates。

执行：`python scripts/verify_docs_runtime.py`，期望 `SUMMARY: PASS`。
<!-- PHASE47_SYNC:END -->
