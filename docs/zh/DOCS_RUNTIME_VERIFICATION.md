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
