# 开发指南

## Phase 28 ????

?? OpenClaw Worker Adapter Foundation ???????????? docs ???

- `worker_client/openclaw/` ????? OpenClaw phase ????? mock-only?
- `OpenClawWorkerClient` ??????? Browser Worker ? `base_url` ??????? Workspace Isolation?
- `openclaw_tool` ?????? `tool_call_logs`?OpenClaw action ?????? `openclaw_action_logs` ? `browser_security_audit_logs`?
- ?? OpenClaw runtime routes ????????? `API_REFERENCE.md`?
- ??????? TikTok / YouTube / X ?????????Cookie ???????????????????????????

???????

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Phase 20 开发规则

`worker/` 是独立 Browser Worker 服务，和 `app/` API Server 共享同一个仓库但运行在独立容器中。修改远程浏览器链路时必须同时检查：

- `worker/main.py`
- `worker/browser_worker/playwright_runtime.py`
- `app/browser/remote/client/browser_worker_client.py`
- `app/browser/providers/remote_browser_provider.py`
- `docker-compose.yml`
- `docs/CURRENT_RUNTIME.md`

固定验证顺序：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Phase 27 开发规则

涉及 Customer Machine Worker Bootstrap 时，必须保持代码、测试和 docs 同步：

- `worker_client/worker_config.example.yaml` 是唯一允许提交的客户机配置模板。
- 本地 `worker_client/worker_config.yaml` 与 `worker_client/worker_state.json` 必须继续被 Git 忽略。
- `worker_state.json` 可以保存明文 `worker_secret`，但绝不能写日志、打印、写入 docs 或提交。
- `registration flow` 必须继续调用 `POST /api/v1/browser-workers/register`。
- `heartbeat flow` 必须继续调用 `POST /api/v1/browser-workers/{worker_id}/heartbeat`，并携带 `X-Worker-Secret` 与 Phase 26 签名请求头。
- `local worker runtime` 必须继续与 Docker `browser-worker` 服务协议兼容。
- 修改 CLI 行为时，必须同步 `python -m worker_client.cli register`、`heartbeat`、`serve`、`start` 的文档。
- Phase 27 范围内禁止加入 OpenClaw 真实接入、TikTok / YouTube / X 自动化、登录自动化、Cookie 注入、代理池、指纹绕过、验证码处理或真实平台自动化。

固定验证流程：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Phase 26 开发规则

涉及 Browser Worker Security & Access Control 时，必须保持安全基础层与现有 Browser/Worker/Profile/UI Access 边界一致：

- `BrowserWorkerAuthService` 是 worker secret、hash、签名和验签的唯一入口。
- 明文 `worker_secret` 只能在 register / rotate 响应中返回一次，数据库只能保存 `worker_secret_hash`。
- Worker signed request 必须使用 `X-Worker-Signature`、`X-Worker-Timestamp`、`X-Worker-Nonce` 和 body hash。
- `BROWSER_WORKER_AUTH_STRICT=false` 只用于本地开发和 smoke test；生产化前应配置共享 secret 并开启 strict。
- `BrowserActionPolicyService` 是 action type、domain、profile access、worker capability、UI Access Scope 的统一校验入口。
- 默认不得放开 `BROWSER_ALLOW_EXTERNAL_DOMAINS=false`；新增域名必须显式进入 `BROWSER_ALLOWED_DOMAINS`。
- `browser_security_audit_logs` 必须记录 worker auth、UI token、policy block 和 profile access 安全事件。
- `browser_ui_access_sessions.scopes`、`one_time`、`used_at`、`revoked_reason`、`client_ip`、`user_agent` 改动必须同步更新 API schema、测试和 docs。
- 禁止加入真实平台登录、Cookie 注入、代理池、指纹绕过、验证码自动化、TikTok / YouTube / X 自动化或完整 RBAC/JWT/OAuth。

固定验证流程：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

不得把社媒自动化、登录、Cookie 注入、代理池、指纹绕过、验证码、OCR、视觉 AI、OpenClaw 或 autonomous browser agent 写入 Phase 20 代码或文档。

更新日期：2026-05-12

本文是中文主开发指南。当前状态：Phase 1 到 Phase 15 已完成。

## 固定交付流程

每个 Phase 完成后必须执行：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

只有 docs verifier 输出 `SUMMARY: PASS` 后，docs 才视为与 runtime 同步。

## Docs-as-Code 规则

新增或修改功能时必须同步：

- `docs/PROJECT_OVERVIEW.md`
- `docs/CURRENT_RUNTIME.md`
- `docs/zh/*`
- `docs/en/*`
- `docs/Aiops Project Documentation Update Request For Codex.docx`
- `scripts/verify_docs_runtime.py`

API 文档必须包含 method、path、request JSON 或 form fields、response JSON、required headers、workspace requirements、debug fields、production/experimental/planned 状态。

禁止把未实现能力写成已完成，例如 Browser Agent、Playwright、OpenClaw、ReAct、autonomous planner、真实 BM25、vector memory、graph memory。

## 测试策略

- 单元测试不依赖真实外部模型。
- LocalProvider / LocalEmbeddingProvider 使用 mock HTTP client。
- File parser 测试使用小 fixture 或 fake reader。
- Workspace isolation 必须覆盖不同 workspace 无法互查。
- Docs verifier 必须作为测试的一部分。

## 不应在当前阶段实现

- Browser Agent / OpenClaw / Playwright / Selenium。
- 外部平台 API。
- autonomous planner / ReAct。
- Elasticsearch / OpenSearch / 真实 BM25。
- vector memory / graph memory。
- 完整 RBAC / JWT / OAuth。
- 前端 Dashboard。
- Scheduler 核心逻辑大改。
- TaskExecutor 核心逻辑大改。

## Task Reliability 开发规则

- 新增任务状态必须同步 `TaskStatus`、API_REFERENCE 和 docs verifier。
- TaskExecutor 执行开始、成功、失败、retry、cancelled skip、timeout 必须写入 `task_events`。
- 关键执行记录必须写入 `task_logs`。
- 终态任务应尽量写入 `completed_at` 与 `duration_ms`。
- `cancel`、`retry`、events、logs、summary API 必须要求 `X-Workspace-Id`。
- Scheduler 只负责扫描、状态流转和入队，只允许最小 timeout/cancelled 适配。

## Tool Calling 开发规则

- 所有工具必须继承 `BaseTool`。
- 必须定义 `name`、`description`、`input_schema`、`output_schema`、`execute()`。
- 访问业务数据时必须使用 `ToolExecutionContext.workspace_id`。
- 工具执行应通过 `ToolRegistry.execute_tool()`，以便写入 `tool_call_logs`。
- 新增工具必须同步 zh/en API_REFERENCE 和 docs verifier。
- 当前 Tool Calling 不包含 autonomous planner、ReAct、Browser Agent 或外部 API。

## Memory 开发规则

- `conversation_sessions`、`conversation_messages`、`agent_memories`、`memory_operation_logs` 是当前 canonical tables。
- 所有 memory 相关数据必须带 `workspace_id`。
- message `role` 只允许 `system`、`user`、`assistant`、`tool`。
- `memory_type` 只允许 `short_term`、`long_term`、`task_memory`、`retrieval_memory`。
- 当前 memory retrieval 只做 PostgreSQL 文本检索。
- `BaseAgent` 集成 memory 必须走 `MemoryExecutionContext`、`load_memory()`、`save_memory()`。
- Agentic RAG debug 必须保留 `session_id`、`recent_messages_count`、`retrieved_memories_count`、`memory_trace`。

## Multi-Agent 开发规则

Phase 15 之后，Multi-Agent 相关变更必须遵守：

- `agent_runs`、`agent_messages`、`agent_handoffs` 是当前 canonical Multi-Agent tables。
- 所有 Multi-Agent 记录必须按 `workspace_id` 隔离。
- `AgentRegistry` 是当前 agent 注册唯一入口。
- 当前注册 Agent：`content_planner`、`rag_agent`、`content_agent`、`review_agent`、`runtime_agent`、`tool_agent`。
- 当前唯一固定链路是 `content_planning`：`content_planner -> rag_agent -> content_agent -> review_agent`。
- `ToolAgent` 必须调用已有 `ToolRegistry`，不允许绕过 tool logging 或 workspace isolation。
- Memory 集成应传递 `session_id`，并复用 Phase 14 Memory Foundation。
- 新增 Multi-Agent API 必须同步 zh/en API_REFERENCE、PROJECT_STATUS 和 `scripts/verify_docs_runtime.py`。
- 不允许把 Browser Agent、OpenClaw、Playwright、Selenium、外部平台 API、autonomous planning、ReAct 写入本基础层。

推荐测试：

- AgentRegistry 注册和禁用。
- run 创建、列表、详情按 workspace 隔离。
- handoff 创建和 message trace。
- 固定 chain 执行。
- Multi-Agent API 带 `X-Workspace-Id` 的完整流程。

## Planning 开发规则

Phase 16 之后，Planning 相关变更必须遵守：

- `plans`、`plan_steps`、`plan_reviews` 是当前 canonical Planning tables。
- 所有 Planning 记录必须按 `workspace_id` 隔离。
- `SimplePlannerAgent` 当前是 rule-based 且有界的 planner，不允许把 autonomous AGI planning、tree-of-thought、recursive planning、无限 Agent loop 或 ReAct 写成已完成。
- Plan step 只能指定 `agent_name` 或 `tool_name` 其中之一，不能同时指定。
- Agent step 必须通过 `AgentRegistry` / `MultiAgentService`。
- Tool step 必须通过 `ToolRegistry`，以保留 tool isolation 与 tool logs。
- 每个 step 必须记录 status、duration、output 和 error。
- Planning API 必须继续要求 `X-Workspace-Id`。
- Planning memory integration 仅限 `session_id` 和 `memory_trace`，不允许写成 graph memory 或高级长期记忆规划。
- 新增 Planning API 必须同步 zh/en API_REFERENCE、PROJECT_STATUS 和 `scripts/verify_docs_runtime.py`。
- 不允许在 Planning Foundation 中接 Browser Agent、OpenClaw、Playwright、Selenium、外部平台 API、autonomous planner 或 ReAct。

推荐测试：

- SimplePlannerAgent 输出稳定性。
- plan 创建、列表、详情按 workspace 隔离。
- plan execution 和 review 创建。
- step retry / skip。
- Planning API 完整流程。

## Browser Adapter 开发规则

Phase 17 之后，Browser Adapter 相关变更必须遵守：

- 默认保持 `BROWSER_PROVIDER=mock`。
- `MockBrowserProvider` 不能启动真实浏览器。
- `PlaywrightBrowserProvider` 在后续真实浏览器阶段前只能保持 placeholder。
- Browser 数据必须通过 `browser_sessions`、`browser_actions`、`browser_action_logs` 按 `workspace_id` 隔离。
- 每个 browser action 必须记录 `duration_ms`、success/error、provider、action_type 和日志。
- `browser_tool` 必须通过 `BrowserService` 和 `ToolRegistry`，保留 `tool_call_logs`。
- Planning 可以使用 `tool_name=browser_tool`，但不允许实现 autonomous browser planning、ReAct、browser loop、OCR、视觉 AI、OpenClaw、Playwright 执行、Selenium 或平台自动化。

推荐测试：

- Provider placeholder 行为。
- BrowserService session/action/log 持久化。
- Browser API workspace isolation。
- `browser_tool` 执行与 `tool_call_logs`。
- `tool_name=browser_tool` 的 Planning step 执行。

## Playwright Local Provider 开发规则

Phase 18 之后允许在 `PlaywrightLocalProvider` 内做本地 Chromium 基础执行，但必须遵守：

- 默认仍保持 `BROWSER_PROVIDER=mock`。
- 真实执行只通过 `BROWSER_PROVIDER=playwright_local` 显式启用。
- 只安装 Playwright Chromium，不安装完整浏览器矩阵。
- 只允许 `example.com`、本地测试页面、静态 `file://` 页面。
- `screenshot` 必须写入 `screenshots/{workspace_id}/{session_id}/{filename}.png`，并在 `browser_actions.screenshot_path` 中记录。
- 每个 action 必须记录 `selector`、`target_url`、`page_title`、`duration_ms`、success/error 和 `browser_action_logs`。
- 禁止实现 TikTok / YouTube / X、登录、Cookie 注入、指纹绕过、代理池、验证码自动化、OCR、视觉 AI、autonomous browser planning、Browser Worker 或真实平台自动化。

Phase 18 固定验证：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Remote Browser Worker 开发规则

Phase 19 之后，Remote Browser Worker 相关变更必须遵守：

- 默认仍保持 `BROWSER_PROVIDER=mock`。
- `BROWSER_PROVIDER=remote` 只代表协议分发，不代表真实外部 worker 已部署。
- Worker 管理 API 必须按 `X-Workspace-Id` 隔离。
- `BrowserWorkerClient` 必须返回结构化 success/error，不允许把 HTTP 异常直接泄露到业务层。
- `RemoteBrowserProvider` 必须通过 `BrowserService` 使用，不能绕过 `browser_actions` 和 `browser_action_logs`。
- remote action 必须记录 `worker_id`、`worker_name`、`remote_session_id`、`remote_action_id`、latency、success/error。
- 禁止在本阶段实现 TikTok / YouTube / X、账号登录、自动发布、Cookie 注入、指纹绕过、代理池、验证码或 autonomous browser agent。

Phase 19 固定验证：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```
## Phase 21 开发规则

涉及 Browser Worker Reliability 时必须保持以下边界：

- 只改 Worker health、capacity、selection、session cleanup、action retry、screenshot cleanup。
- 不修改 Scheduler 核心逻辑。
- 不修改 TaskExecutor 核心逻辑。
- 不修改 Workspace Isolation 核心逻辑。
- 不修改 Hybrid Search 主逻辑。
- 不加入 TikTok / YouTube / X、登录、Cookie、代理、指纹、验证码、OCR、视觉 AI 或 autonomous browser planning。

固定自测流程：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

新增或调整 Browser Worker API 时，必须同步：

- `docs/PROJECT_OVERVIEW.md`
- `docs/CURRENT_RUNTIME.md`
- `docs/zh/API_REFERENCE.md`
- `docs/en/API_REFERENCE.md`
- `scripts/verify_docs_runtime.py`

## Phase 22 开发规则

涉及 Persistent Browser Profile Foundation 时必须保持以下边界：

- `browser_profiles` 是 profile 生命周期元数据的 canonical table。

## Phase 23 开发规则

涉及 Browser Profile Health & Recovery 时必须同步维护代码、迁移、测试和 docs：

- `browser_profiles` 的 health 字段必须通过 `BrowserProfileHealthService`、`BrowserProfileBackupService` 或 `BrowserProfileCleanupService` 更新，不要在业务代码里散落写状态。
- `browser_profile_usage_logs` 是 profile lock/release、session_start/session_close、backup/restore、recovery、cleanup 的审计来源。
- profile path 校验必须限制在 `BROWSER_PROFILE_ROOT` 下，backup path 必须限制在 `BROWSER_PROFILE_BACKUP_ROOT` 下。
- cleanup API 默认 dry-run；新增清理逻辑必须先支持预览，再允许删除。
- stale lock recovery 只能释放当前 workspace 的 profile，不得跨 workspace 操作。
- 每次修改必须运行 `python -m pytest`、`docker compose up --build -d`、`python scripts/verify_docs_runtime.py`。

禁止在 Phase 23 范围内加入账号登录、Cookie 注入、代理池、指纹绕过、验证码、真实平台自动化或 autonomous browser planning。
- 所有 profile 操作必须按 `workspace_id` 隔离。
- 同一个 profile 同一时间只能被一个 active session 使用，通过 `locked_by_session_id` 保证。
- `lock_profile` 和 `release_profile` 在存在 session 上下文时必须写入 browser logs。
- `POST /api/v1/browser/sessions` 只有在显式提供 `profile_id` 且 `use_persistent_profile=true` 时才允许启用 profile。
- worker runtime 只有在 profile-backed session 下才允许使用 `launch_persistent_context`。
- profile 文件必须保存在 `worker/profiles/{workspace_id}/{profile_id}` 下。
- 关闭 profile-backed session 必须 release lock 并更新 `last_used_at`。
- 禁止加入登录自动化、Cookie 注入、指纹绕过、代理池、验证码处理、社媒平台自动化或 autonomous browser planning。

固定验证流程：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```
## Phase 24 开发规则

涉及 Human-in-the-loop Browser Control 时，必须把实现范围限制在后端状态管理和 worker metadata-level 信号：

- `browser_human_control_sessions` 和 `browser_human_control_events` 是人工接管审计的 canonical tables。
- 状态流转必须通过 `BrowserHumanControlService`，不要在业务代码中散落写 pause/resume 状态。
- 每次状态流转必须写 event：`requested`、`approved`、`started`、`completed`、`cancelled`、`expired`、`timeout`、`note`。
- request control 必须 pause browser session，并保留 profile lock 与 worker session。
- complete 或 cancel control 后，如果关联 session 仍存在，必须恢复 browser session。
- paused 期间普通 browser action 必须被拒绝。
- `browser_tool` 的 human-control action 必须调用 service，并保留 `tool_call_logs`。
- worker `/human-control/*` 只允许 metadata-level 接口。
- 禁止加入 VNC、noVNC、DevTools 真实远程 UI、自动登录、Cookie 注入、代理池、指纹绕过、验证码自动化、TikTok / YouTube / X 自动化或真实平台自动化。

固定验证流程：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```
## Phase 25 开发规则

涉及 Browser Worker UI Access Placeholder 时，必须把范围限制在后端占位访问层：

- `browser_ui_access_sessions` 是 UI access placeholder 的 canonical table。
- 数据库只能保存 `access_token_hash`，不能持久化明文 access token。
- 明文 `access_token` 只能从 `POST /api/v1/browser/ui-access` 返回一次。
- `remote_control_url` 和 `live_view_url` 必须明确标注为 placeholder URL。
- `devtools_url` 在未来真正实现 DevTools UI 之前保持 `null`。
- worker `/ui-access/capabilities` 必须返回 `vnc=false`、`novnc=false`、`devtools=false`、`placeholder=true`。
- `browser_tool` 的 UI access action 必须调用 `BrowserUIAccessService`，并保留 `tool_call_logs`。
- 禁止加入 VNC、noVNC、Chrome DevTools 远程 UI、实时浏览器画面、自动登录、Cookie 注入、代理池、指纹绕过、验证码自动化、TikTok / YouTube / X 自动化或真实平台自动化。

固定验证流程：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Phase 29 Development Notes

When changing Worker Client runtime behavior, update these together: `worker_client/runtime_manager.py`, `worker_client/status.py`, `worker_client/logging.py`, `worker_client/runtime.py`, `worker_client/local_api_client.py`, packaging scripts, and docs. Run `python -m pytest`, `docker compose up --build -d`, and `python scripts/verify_docs_runtime.py`.

Do not log `worker_secret`. Do not commit `worker_client/runtime_state/status.json`, `worker_client/logs/worker.log`, `worker_client/worker_config.yaml`, or `worker_client/worker_state.json`.

Phase 29 remains Worker Console Foundation only: no GUI, no Electron/Tauri/PySide, no system tray, and no exe/dmg packaging.

## Phase 30 Worker Console Development Guide

When changing `worker_console`, run `npm install` when dependencies change, then `npm run build`. Keep `worker_console/src/api/localWorkerClient.ts`, docs, and `scripts/verify_docs_runtime.py` synchronized. Do not add Electron, Tauri, PySide, system tray, auto update, exe / dmg packaging, or platform automation in Phase 30.
## Phase 31：Worker Console Desktop 开发规则

桌面壳位于 `worker_console_desktop`，使用 Tauri + React + Vite + TypeScript + Tailwind。新增桌面端能力时必须保持 Local API 契约稳定，优先复用 `worker_console_desktop/src/api/localWorkerClient.ts`。

固定验证流程：

```powershell
cd worker_console_desktop
npm install
npm run build
cd ..
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

当前不允许加入正式安装包、exe / dmg、system tray、autostart、auto update 或真实平台自动化能力。相关能力只能作为规划中路线写入 docs，不能写成已完成。

## Phase 32：System Tray 开发规则

Phase 32 已允许在 Tauri 中实现 System Tray、Minimize To Tray 和本地 Runtime 控制，但仍禁止：

- formal installer
- exe / dmg 正式发布
- 真正开机自启
- auto-update
- arbitrary shell
- remote shell
- 远程命令执行

托盘菜单只能通过 `tray-control` 事件通知前端，再由前端调用 `localWorkerClient.ts` 的本地 HTTP API。不要在 Rust 或 TypeScript 中加入 `std::process`、shell plugin、process plugin 或任意命令执行逻辑。

## Phase 33?Conversation Runtime Foundation

???????

????`conversation_threads`?`conversation_events`??? `conversation_messages.thread_id`?`ConversationService`?`run_conversation_turn`?Conversation APIs?Worker Console Chat Panel Foundation?Event Timeline?polling event feed?

???????`message_received`?`planning_started`?`plan_created`?`agent_started`?`tool_called`?`worker_action_started`?`worker_action_completed`?`assistant_response`?`error`?

??????? Conversation Runtime Foundation???? WebSocket/SSE????? OpenClaw??? ComfyUI??? TikTok / YouTube / X??????Cookie ????????????????????????

## Phase 34 Remote Browser Runtime Development Notes

Remote browser runtime development must keep the dispatch boundary clear:

- API orchestration belongs in `BrowserRuntimeSessionService`.
- Remote worker calls belong in `app/browser/providers/remote_provider.py` and `BrowserWorkerClient`.
- Customer-machine execution belongs in `worker_client/browser_runtime`.
- Do not add platform automation, stealth behavior, proxy logic, cookie injection, or captcha bypass.
- Do not bypass workspace isolation when querying `browser_runtime_sessions`.
- Do not store screenshot base64 in database metadata; store files under `storage/browser_screenshots` and keep metadata paths.

Required verification after changes:

```powershell
python -m pytest
python scripts/verify_docs_runtime.py
```

For real customer-machine runtime checks, install Chromium with:

```powershell
playwright install chromium
```

## Phase 35B Real Client Worker E2E Development Rule

When changing `scripts/validate_real_client_worker_e2e.py`, preserve these rules:

- Missing `expected_worker_name` returns `SKIPPED`, not PASS.
- Browser actions are executed only after the expected worker is online and available.
- JSON output must include checks, warnings, summary, and exit code.
- `BROWSER_PROVIDER=remote` mismatch is a WARNING only.
- Never fabricate a real customer-machine E2E result.

Required tests:

```powershell
python -m pytest tests\test_real_client_worker_e2e_script.py tests\test_real_client_worker_e2e_docs.py
```

## Phase 35A 开发规则：Browser Runtime Observability

新增或修改 Browser Runtime 动作时，必须同步维护：

- `BrowserRuntimeObservabilityService`
- `browser_runtime_events`
- `browser_runtime_snapshots`
- `browser_runtime_replays`
- `docs/zh/API_REFERENCE.md`
- `docs/en/API_REFERENCE.md`
- Worker Console Timeline / Snapshots / Replay metadata 面板

固定自测流程：

```powershell
python -m pytest
cd worker_console
npm install
npm run build
cd ..\worker_console_desktop
npm install
npm run build
cd ..
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

边界：Replay 只能是 metadata-only replay，不能重新执行浏览器动作；不得加入 live stream、VNC/noVNC、DevTools remote control 或真实平台自动化。

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
## Phase 38 开发规则补充

新增 Conversation bridge 能力时必须先扩展 `ConversationToolRouter` 的 Routing Rules，再在 `ConversationService` 中实现受控 bridge。所有执行必须写入 `route_selected`、`tool_execution_started` / `tool_execution_completed` / `tool_execution_failed` 或对应 agent / planning event，并把完整结果放入 `result_metadata`。不得把本阶段描述为 autonomous agent、WebSocket、SSE 或真实平台发布。

## Phase 39 开发规则

新增可能触发 Tool / Browser / OpenClaw / Task 的 Conversation route 时，必须同步更新 `ConversationRiskPolicy`。medium/high risk 不允许绕过 `ConversationApprovalService` 和 Tool Execution Gate。

固定检查：

- 是否创建 `conversation_approvals` 或明确说明 low risk 自动执行。
- 是否写入 approval events。
- 是否保证 rejected / cancelled / expired / executed approval 不可执行。
- 是否更新 Admin Dashboard、Worker Console、Worker Console Desktop 的 pending approvals panel。
- 是否更新 docs 和 `scripts/verify_docs_runtime.py`。

禁止把 Phase 39 描述为完整权限系统、真实平台发布或 autonomous agent。
## Phase 40 开发规则：Playbooks

新增 Playbook 时必须同步：

- `app/conversation/playbook_definitions.py`
- `ConversationPlaybookService`
- API_REFERENCE
- Admin Dashboard / Worker Console Playbook UI
- pytest
- `python scripts/verify_docs_runtime.py`

Playbook step 不允许绕过 `ConversationRiskPolicy` 和 `ConversationApprovalService`。如果新增高风险 step，只能创建 approval，不得直接执行。

## Phase 41 开发规则

新增 Conversation / Playbook / Tool 产物时，优先通过 `OutputArtifactService` 写入 `output_artifacts`，不要把超大 raw payload 直接塞进 `content`。文件型 artifact 保存路径和 metadata；文本型 artifact 可保存 bounded content。每个 Phase 完成后必须同步 Output Library API、前端页面、pytest、前端 build、Docker smoke 和 docs verifier。
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
## Phase 46 Development Notes

Workflow Graph Runtime development centers on `WorkflowExecutionPlanner`, `SafeConditionEvaluator`, `WorkflowGraphService`, and `WorkflowStateService`. Tests should cover graph validation, Conditional Execution, Retry/Fallback Path planning, Replay Foundation metadata, `current_node_key`, `planned_next_nodes`, `skipped_nodes`, `producing_node_key`, and `graph_lineage`. Do not use Python eval for conditions; do not build a visual DAG builder or distributed orchestration engine.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47：开发说明

新增开发入口：`app/workflow/template_definitions.py` 定义 built-in templates，`app/workflow/template_registry.py` 实现 `WorkflowTemplateRegistryService` 与 `WorkflowTemplateCompatibilityService`，`app/schemas/workflow_template.py` 定义 API schema，`app/api/routes/workflow_templates.py` 暴露 `/api/v1/workflow-templates` 与 `/api/v1/workflow-template-runs`。三端前端新增 `workflowTemplateClient.ts`。

开发边界：版本不可覆盖，`template_key` 必须 workspace 唯一，validate_template 必须复用 planner validation，不允许绕过 approval/risk gate；当前不是可视化 DAG builder，不接 ComfyUI。
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

