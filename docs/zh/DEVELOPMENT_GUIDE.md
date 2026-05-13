# 开发指南

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
