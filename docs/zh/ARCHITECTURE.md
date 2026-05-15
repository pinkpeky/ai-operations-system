# 架构说明

## Phase 28 OpenClaw Worker Adapter Foundation

Phase 28 在 Browser Worker 协议之上新增 mock OpenClaw 适配层：

```text
API Server / openclaw_tool
-> OpenClawService
-> BrowserWorkerSelector capability=openclaw
-> OpenClawWorkerClient
-> worker_client /openclaw/* mock runtime
-> MockOpenClawProvider
-> openclaw_action_logs + browser_security_audit_logs
```

服务端 `app/openclaw/` 负责 OpenClaw schemas、`OpenClawWorkerClient`、repository 和 service；客户机 `worker_client/openclaw/` 负责 `BaseOpenClawProvider`、`MockOpenClawProvider`、`OpenClawRuntime` 与 worker runtime routes。内置 `openclaw_tool` 复用同一服务路径，并记录 `tool_call_logs`。

边界：当前只是 placeholder foundation，不调用真实 OpenClaw，不做社媒平台自动化、登录、Cookie 注入、代理池、指纹绕过或验证码自动化。

## Phase 20 Real Browser Worker Service

Phase 20 在 Phase 19 Remote Browser Worker Foundation 之上新增真实独立 Worker 服务。当前浏览器远程执行链路为：

```text
API Server
-> RemoteBrowserProvider
-> BrowserWorkerClient
-> http://browser-worker:9100
-> worker/main.py
-> worker/browser_worker/playwright_runtime.py
-> Playwright Chromium
-> worker/screenshots/{workspace_id}/{remote_session_id}/{filename}.png
```

`browser-worker` 是独立 FastAPI 服务，Docker Compose 中单独运行并暴露 `9100`。它提供 `GET /health`、`POST /sessions`、`POST /actions`、`POST /sessions/{session_id}/close`。API Server 仍通过 `POST /api/v1/browser-workers/register` 注册 `base_url=http://browser-worker:9100`，然后由 `BrowserService` 通过 remote provider 调度动作。

安全边界：只支持 `example.com`、本地测试页面和静态文件页面；不支持 TikTok / YouTube / X、登录、Cookie 注入、代理池、指纹绕过、验证码、OCR、视觉 AI、OpenClaw 或 autonomous browser agent。

更新日期：2026-05-12

本文描述 `E:\ai-operations-system` 当前真实架构。当前状态：Phase 1 到 Phase 15 已完成。

## 总体架构

```text
HTTP API
 -> FastAPI routes
 -> Workspace Context Middleware
 -> Service / Repository / Provider layers
 -> PostgreSQL / Redis / Qdrant / Ollama
```

核心边界：

- Scheduler 只负责任务扫描、状态流转和入队。
- TaskExecutor 负责从 Redis Queue 取任务、分发 handler、写执行结果、事件和日志。
- LLM Client、Embedding、Reranker、RAG、Tool、Memory、Multi-Agent 都是独立层，不直接塞进 Scheduler。
- 所有业务查询必须按 `workspace_id` 隔离。

## Project Structure

```text
app/
  api/            FastAPI route registration and endpoint modules.
  agents/         LLM client, BaseAgent, ContentAgent.
  core/           Settings, logging, errors, workspace context.
  db/             PostgreSQL, Redis, Qdrant connection helpers.
  file_pipeline/  File parsers, text cleaning, upload ingestion service.
  memory/         Conversation sessions, messages, Agent Memory, MemoryService.
  middleware/     Workspace context middleware.
  multi_agent/    AgentRegistry, MultiAgentService, run/message/handoff repository.
  planning/       SimplePlannerAgent, PlanningService, plan/step/review repository.
  rag/            Embedding, chunking, vector store, retrieval, hybrid search, Agentic RAG.
  reranker/       Reranker provider layer.
  repositories/   Database access layer.
  schemas/        Pydantic schemas.
  services/       Prompt manager, queues, lifecycle, eval, scheduler.
  tools/          BaseTool, ToolRegistry, builtin tools.
  workers/        TaskExecutor and handlers.
```

## 数据库结构

已完成核心表：

- Task：`tasks`、`task_events`、`task_logs`。
- Knowledge：`documents`、`document_chunks`、`collections_metadata`。
- Workspace：`users`、`workspaces`、`workspace_members`、`api_keys`。
- Eval：`rag_eval_runs`、`rag_eval_items`。
- Tool：`tool_call_logs`。
- Memory：`conversation_sessions`、`conversation_messages`、`agent_memories`、`memory_operation_logs`。
- Multi-Agent：`agent_runs`、`agent_messages`、`agent_handoffs`。

## RAG 架构

Ingest：

```text
Text / File
 -> parse / clean
 -> chunk
 -> embedding
 -> Qdrant upsert
 -> documents / document_chunks / collections_metadata
```

Search：

```text
Query
 -> Dense Vector Search
 -> Keyword Search
 -> Hybrid Merge
 -> Reranker
 -> TopN Context
 -> Prompt Assembly
 -> LLM
```

当前 search 支持 `search_mode=dense|keyword|hybrid`，并返回 `dense_score`、`keyword_score`、`hybrid_score`、`similarity_score`、`raw_score`。

## Workspace Isolation

`X-Workspace-Id` 由 middleware 写入 `request.state`，然后传入 repository/service。以下资源必须按 workspace 过滤：

- documents / document_chunks。
- RAG search / keyword search。
- tasks / task_events / task_logs。
- tool_call_logs。
- conversation_sessions / conversation_messages / agent_memories。
- agent_runs / agent_messages / agent_handoffs。

未提供 `X-Workspace-Id` 时，业务 API 必须返回清晰错误，不允许查全库。

## File Upload Pipeline

```text
multipart upload
 -> save temp file
 -> compute file_hash
 -> duplicate check by file_hash + workspace_id
 -> parser
 -> clean text
 -> DocumentLifecycle ingest
 -> embedding + Qdrant + DB records
 -> temp cleanup
```

当前支持：PDF、DOCX、TXT、MD、CSV。

当前不支持：PPTX、XLSX、OCR、图片解析。

## Task Reliability & Observability

```text
Task API / Scheduler / TaskExecutor
 -> tasks.status
 -> task_events
 -> task_logs
 -> duration_ms
 -> GET /api/v1/observability/summary
```

任务状态：`pending`、`running`、`retry`、`failed`、`completed`、`cancelled`、`timeout`。

Scheduler 只做最小 timeout 状态适配，不改变核心扫描/入队职责。

## Tool Calling Foundation

```text
Agent / Tool API
 -> ToolRegistry
 -> BaseTool.validate_input
 -> builtin tool execute
 -> workspace-scoped service/repository
 -> tool_call_logs
```

当前 builtin tools：

- `rag_search_tool`
- `file_search_tool`
- `create_task_tool`
- `get_task_status_tool`
- `current_runtime_tool`

当前只支持手动工具调用，不做 autonomous planner、ReAct 或 LLM-native function calling。

## Memory Foundation

```text
Agent / Agentic RAG / Memory API
 -> MemoryService
 -> conversation_sessions / conversation_messages
 -> PostgreSQL text search over agent_memories
 -> prompt memory context
 -> memory_trace
```

当前 Memory 是基础层，不包含 vector memory、graph memory、personality memory 或 autonomous memory planning。

## Phase 15 Multi-Agent Foundation 架构

```text
API
 -> AgentRegistry
 -> MultiAgentService
 -> agent_runs
 -> content_planner
 -> rag_agent
 -> content_agent
 -> review_agent
 -> agent_messages
 -> agent_handoffs
 -> run output with agents_involved + handoff_trace
```

核心目录：

- `app/multi_agent/services/`：`AgentRegistry` 与 `MultiAgentService`。
- `app/multi_agent/repositories/`：`AgentRunRepository`。
- `app/api/routes/multi_agent.py`：run、chain、message、handoff API。
- `app/schemas/multi_agent.py`：请求与响应 schema。

AgentRegistry 当前注册：

- `content_planner`：确定性 mock planner。
- `rag_agent`：封装 `AgenticRAGOrchestrator`。
- `content_agent`：封装 `ContentAgent`。
- `review_agent`：确定性 mock review agent。
- `runtime_agent`：通过 `current_runtime_tool` 读取运行配置。
- `tool_agent`：调用现有 `ToolRegistry` builtin tools。

固定 Agent Chain：

```text
content_planner -> rag_agent -> content_agent -> review_agent
```

Memory 集成：

- `agent_runs.session_id` 记录 conversation session。
- `rag_agent` 和 `content_agent` 可复用 Phase 14 Memory Foundation。
- 输出包含 `agents_involved`、messages、handoffs 和 `handoff_trace`。

当前限制：

- 不支持 autonomous planner。
- 不支持动态 handoff policy。
- 不支持 ReAct。
- 不支持 Browser Agent、OpenClaw、Playwright、Selenium。

## Phase 16 Agent Planning Foundation 架构

Phase 16 在 AgentRegistry 和 ToolRegistry 之上新增有界 Planning 层，把固定链路升级为可持久化、可观测的 plan/step/review 执行流，但不做 autonomous AGI planner、tree-of-thought、recursive planning、无限 Agent loop 或 ReAct。

```text
User goal
 -> SimplePlannerAgent
 -> plans
 -> plan_steps
 -> PlanningService.execute_plan
 -> AgentRegistry or ToolRegistry
 -> step output / duration_ms / error
 -> plan_reviews
 -> final plan status + memory_trace
```

核心目录：

- `app/planning/services/`：`SimplePlannerAgent` 与 `PlanningService`。
- `app/planning/repositories/`：`PlanRepository`。
- `app/api/routes/planning.py`：plan、execute、cancel、steps、reviews API。
- `app/schemas/planning.py`：Planning 请求与响应 schema。

核心表：

- `plans`
- `plan_steps`
- `plan_reviews`

Plan 状态：

- `pending`
- `planning`
- `executing`
- `completed`
- `failed`
- `cancelled`

PlanStep 状态：

- `pending`
- `running`
- `completed`
- `failed`
- `skipped`

Planning 集成：

- Agent step 通过 `AgentRegistry` 执行。
- Tool step 通过 `ToolRegistry` 执行。
- Memory 通过 `session_id` 和 `memory_trace` 接入。

当前限制：

- 仅 rule-based planner。
- 不支持 autonomous AGI planner。
- 不支持 tree-of-thought。
- 不支持 recursive planning。
- 不支持无限 Agent loop。
- 不支持 ReAct。
- 不支持 Browser Agent / OpenClaw / Playwright / Selenium。

## Browser Automation Adapter Foundation

Phase 17 新增 Browser Adapter 基础层，但不做真实浏览器执行。

流程：

```text
Browser API / browser_tool / Planning tool step
 -> BrowserService
 -> BrowserProvider
 -> MockBrowserProvider
 -> browser_sessions / browser_actions / browser_action_logs
```

核心模块：

- `app/browser/providers/base.py`：`BrowserProvider` 接口。
- `app/browser/providers/mock_browser_provider.py`：稳定 mock provider。
- `app/browser/providers/playwright_browser_provider.py`：placeholder only。
- `app/browser/services/browser_service.py`：session/action 执行与可观测记录。
- `app/browser/repositories/browser_repository.py`：workspace-scoped 持久化。
- `app/tools/builtin/browser_tool.py`：安全的手动 browser tool。
- `app/api/routes/browser.py`：Browser API。

核心表：

- `browser_sessions`
- `browser_actions`
- `browser_action_logs`

当前边界：

- 默认 `BROWSER_PROVIDER=mock`。
- `MockBrowserProvider` 不启动真实浏览器。
- `PlaywrightBrowserProvider` 仅 placeholder，不安装也不调用 Playwright。
- Planning 可以执行 `tool_name=browser_tool`，但不做 autonomous browser planning。
- 不做 Browser Agent、OpenClaw、Selenium、OCR、视觉 AI、真实登录流程或平台自动化。

## Playwright Local Provider Integration

Phase 18 在 Browser Adapter 抽象之上新增真实本地 Chromium 执行能力，但仍是受限基础执行，不是 Browser Agent。

```text
Browser API / browser_tool
 -> BrowserService
 -> BrowserProvider switch
 -> PlaywrightLocalProvider
 -> headless Chromium
 -> browser_actions: selector / target_url / screenshot_path / page_title
 -> screenshots/{workspace_id}/{session_id}/{filename}.png
 -> browser_action_logs
```

核心模块：

- `app/browser/providers/playwright_provider.py`：`PlaywrightLocalProvider`，provider name 为 `playwright_local`。
- `app/browser/services/browser_service.py`：根据 `BROWSER_PROVIDER` 在 `mock` 与 `playwright_local` 间切换。
- `app/api/routes/browser.py`：新增 `GET /api/v1/browser/screenshot/{session_id}/{filename}`。
- `app/tools/builtin/browser_tool.py`：支持 `navigate`、`click`、`type_text`、`screenshot`、`get_page_content`。

运行时字段：

- `browser_sessions.browser_id`
- `browser_sessions.page_id`
- `browser_sessions.provider_session_metadata`
- `browser_actions.selector`
- `browser_actions.target_url`
- `browser_actions.screenshot_path`
- `browser_actions.page_title`

安全边界：

- 默认 `BROWSER_PROVIDER=mock`。
- `BROWSER_PROVIDER=playwright_local` 只允许 `example.com`、本地测试页面、静态 `file://` 页面。
- 不做社媒自动化、自动登录、Cookie 注入、指纹绕过、代理池、验证码自动化、OCR、视觉 AI、autonomous browser planning、Browser Worker 或真实平台自动化。

## Remote Browser Worker Foundation

Phase 19 建立 Remote Browser Worker 基础协议，让 AI Server 未来可以把浏览器动作分发到独立 Worker 机器。本阶段只实现协议、client、provider、worker 注册心跳和同项目 mock runtime。

```text
AI Server
 -> RemoteBrowserProvider
 -> BrowserWorkerClient
 -> Browser Worker API
 -> Worker Runtime Mock
```

核心模块：

- `app/browser/remote/client/browser_worker_client.py`：`BrowserWorkerClient`。
- `app/browser/providers/remote_browser_provider.py`：`RemoteBrowserProvider`。
- `app/browser/remote/services/browser_worker_repository.py`：worker/session/action 映射持久化。
- `app/browser/remote/services/browser_worker_service.py`：注册、心跳、列表服务。
- `app/api/routes/browser_workers.py`：worker 管理 API 与 mock runtime API。

数据库表：

- `browser_workers`
- `browser_worker_sessions`
- `browser_worker_actions`

Remote Action Dispatch Flow：

```text
BrowserService creates browser_actions
 -> RemoteBrowserProvider reads provider_session_metadata
 -> BrowserWorkerClient POST /actions
 -> browser_worker_actions stores remote_action_id / response_payload
 -> BrowserService completes browser_actions
 -> browser_action_logs records worker_id / worker_name / remote_action_id
```

边界：

- 当前 worker runtime 是 mock，不启动真实浏览器。
- 不部署真实外部 worker。
- 不做 TikTok / YouTube / X、登录、自动发布、Cookie 注入、指纹绕过、代理池、验证码或 autonomous browser agent。
## Phase 21 Browser Worker Reliability

Browser Worker Reliability 位于 `RemoteBrowserProvider` 与 `BrowserWorkerClient` 周围，目标是让后续多 Worker、Chrome Profile、账号环境隔离可以建立在可恢复的基础上。

核心组件：

- `BrowserWorkerHealthService`：检查 `last_seen` / `last_heartbeat_at`，把 stale worker 标记为 `offline`，记录 `error_message`。
- `BrowserWorkerSelector`：按 `workspace_id`、`status=online`、capability、`active_sessions < max_sessions` 过滤，并选择 least loaded worker。
- `BrowserSessionCleanupService`：关闭 stale sessions，worker offline/error 后将关联 session 标记为 failed，并写 browser logs。
- `ScreenshotCleanupService`：按 workspace 和 age 清理 `screenshots` 与 `worker/screenshots`，默认 dry-run。

Worker selection flow:

```text
create browser session
-> RemoteBrowserProvider
-> BrowserWorkerSelector
-> online + capability + capacity
-> least loaded worker
-> BrowserWorkerClient
-> browser-worker
```

Action retry flow:

```text
browser action
-> BrowserWorkerClient
-> timeout / retry / backoff
-> retry_logs
-> browser_worker_actions.retry_count / max_retries
```

本阶段仍不包含真实平台自动化、登录、Cookie、代理、指纹、验证码、OCR、视觉 AI 或 autonomous browser planning。

## Phase 22 Persistent Browser Profile Foundation

Phase 22 在 Browser Worker 栈周围新增持久化浏览器 Profile 元数据和锁管理，为后续账号环境隔离、人工接管和长期 session 做准备，但仍保持当前安全边界。

核心组件：

- `browser_profiles`：记录 `profile_name`、`profile_type`、`provider`、`profile_path`、`status`、`locked_by_session_id`、`locked_at`、`last_used_at`。
- `BrowserProfileService`：在 workspace isolation 下创建、列出、读取、锁定、释放、标记损坏和逻辑删除 profile。
- `browser_sessions.profile_id`、`browser_sessions.profile_path`、`browser_sessions.persistent_context_enabled`：把 session 绑定到 profile-backed runtime。
- `worker/browser_worker/playwright_runtime.py`：仅在 session 显式请求持久化 profile 时使用 Playwright `launch_persistent_context`。

Profile Lock / Release Flow：

```text
POST /api/v1/browser/profiles
-> BrowserProfileService.create_profile
-> POST /api/v1/browser/sessions with profile_id + use_persistent_profile=true
-> BrowserProfileService.lock_profile
-> BrowserService passes profile metadata to RemoteBrowserProvider
-> browser-worker launches persistent context
-> POST /api/v1/browser/sessions/{session_id}/close
-> BrowserProfileService.release_profile
```

Persistent Context Flow：

```text
browser_sessions.profile_id
-> provider_session_metadata.profile_id/profile_path/use_persistent_profile
-> BrowserWorkerClient /sessions
-> worker/browser_worker/playwright_runtime.py
-> launch_persistent_context
-> worker/profiles/{workspace_id}/{profile_id}
```

本阶段不实现登录、Cookie 注入、浏览器指纹配置、代理池、验证码处理、社媒平台自动化或 autonomous browser planning。

## Phase 23 Browser Profile Health & Recovery

Phase 23 在 Phase 22 的 Persistent Browser Profile 之上增加健康状态、恢复、备份、清理和 usage log。它的目标是让长期浏览器 profile 在异常 session、offline worker、路径损坏或过期文件存在时可以被观察和恢复。

核心数据：

- `browser_profiles.health_status`：`healthy`、`warning`、`corrupted`、`stale`、`deleted`。
- `browser_profiles.last_health_check_at`、`last_error`、`usage_count`、`corrupted_at`、`backup_path`、`last_backup_at`。
- `browser_profile_usage_logs`：记录 profile 生命周期操作，便于审计和排障。

服务分层：

```text
Browser Profile APIs
-> BrowserProfileHealthService
   -> check_profile_health / recover_stale_locks / summarize_profiles
-> BrowserProfileBackupService
   -> create_backup / list_backups / restore_backup
-> BrowserProfileCleanupService
   -> cleanup_deleted_profiles / cleanup_corrupted_profiles / cleanup_unused_profiles
-> browser_profile_usage_logs
```

Stale Lock Recovery Flow：

```text
locked browser_profile
-> check locked_at timeout
-> check locking browser_session status
-> check worker session and worker status
-> release locked_by_session_id
-> set profile status=available
-> set health_status=stale
-> write browser_profile_usage_logs action=recovery
```

Profile Backup Flow：

```text
POST /api/v1/browser/profiles/{profile_id}/backup
-> validate profile_path under BROWSER_PROFILE_ROOT
-> zip profile directory
-> worker/profile_backups/{workspace_id}/{profile_id}
-> update backup_path / last_backup_at
-> enforce BROWSER_PROFILE_MAX_BACKUPS
-> write usage log action=backup
```

Profile Cleanup Flow：

```text
POST /api/v1/browser/profiles/cleanup
-> select deleted / corrupted / unused profiles in current workspace
-> dry-run by default
-> remove profile directory only when inside profile root
-> write usage log action=cleanup
```

新增配置：`BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS`、`BROWSER_PROFILE_BACKUP_ENABLED`、`BROWSER_PROFILE_MAX_BACKUPS`、`BROWSER_PROFILE_UNUSED_DAYS`、`BROWSER_PROFILE_BACKUP_ROOT`。

安全边界不变：不做账号登录、Cookie 注入、代理池、指纹绕过、验证码、真实平台自动化、TikTok / YouTube / X 自动化或 autonomous browser planning。

## Phase 24 Human-in-the-loop Browser Control

Phase 24 在 Browser Session / Worker / Tool 之间建立人工接管控制层。它不是 VNC/noVNC/DevTools 远程 UI，而是一个后端协议与状态机：自动化可以暂停，人工处理外部步骤，然后恢复自动化。

核心数据：

- `browser_human_control_sessions`：记录接管 session、profile、worker、状态、申请人、批准人、过期时间。
- `browser_human_control_events`：记录 requested / approved / started / completed / cancelled / expired / timeout / note。
- `browser_sessions.human_control_status`、`human_control_session_id`、`paused_at`、`resumed_at`：把普通 browser session 与 human control 状态关联。

Pause / Resume Flow：

```text
POST /api/v1/browser/human-control/request
-> BrowserHumanControlService.request_control
-> browser_sessions.status=paused
-> browser_human_control_events requested
-> automation actions blocked by active-session guard
-> approve/start
-> worker /human-control/start metadata
-> complete
-> browser_sessions.status=active
-> resumed_at
-> browser_human_control_events completed
```

Tool Integration：

```text
browser_tool action_type=request_human_control
-> BrowserHumanControlService.request_control

browser_tool action_type=complete_human_control
-> BrowserHumanControlService.complete_control
```

本阶段不实现 VNC、noVNC、Chrome DevTools 远程 UI、平台登录、验证码处理、社媒自动化、代理池、Cookie 注入或指纹绕过。
## Phase 25 Browser Worker UI Access Placeholder

Phase 25 为未来人工远程接管浏览器 UI 建立占位访问层。当前只实现后端协议、token hash、placeholder URL 和能力声明，不提供真实远程桌面或浏览器实时画面。

核心数据：

- `browser_ui_access_sessions`：记录 `browser_session_id`、`human_control_session_id`、`worker_id`、`access_token_hash`、`remote_control_url`、`live_view_url`、`devtools_url`、状态、过期时间和 metadata。
- `BrowserUIAccessService`：负责 create / get / revoke / expire / generate token / validate token。
- `BROWSER_UI_ACCESS_TIMEOUT_SECONDS`：控制 access session 与 token 过期时间。

Token Flow：

```text
POST /api/v1/browser/ui-access
-> 生成明文 token
-> 数据库保存 access_token_hash
-> 明文 token 只返回一次
-> /validate?token=TOKEN 校验
-> revoke 或 expire
```

Human Control Integration：

```text
human control status=active
-> BrowserUIAccessService.create_access_session
-> 生成 placeholder URL
-> browser_tool create_ui_access / revoke_ui_access
```

Worker 能力声明：

```text
GET /ui-access/capabilities
-> vnc=false
-> novnc=false
-> devtools=false
-> placeholder=true
```

当前 URL 只是 placeholder：

- `remote_control_url`: `http://localhost:8000/ui/browser-control/{access_session_id}`
- `live_view_url`: `http://localhost:8000/ui/browser-live/{access_session_id}`
- `devtools_url`: `null`

Phase 25 不实现 VNC、noVNC、Chrome DevTools 远程 UI、实时浏览器画面、自动登录、Cookie 注入、代理池、指纹绕过、验证码自动化、TikTok / YouTube / X 或真实平台自动化。

## Phase 26 Browser Worker Security & Access Control

Phase 26 在 Browser Worker、UI Access、Browser Profile 和 Browser Action 之间补齐基础安全边界。它是后端安全基础设施，不是完整身份系统，也不是社媒平台账号安全实现。

### Worker Secret / Signed Request

```text
POST /api/v1/browser-workers/register
 -> 生成 worker_secret
 -> 明文只返回一次
 -> 数据库存 worker_secret_hash
 -> BrowserWorkerClient.sign_request
 -> X-Worker-Signature / X-Worker-Timestamp / X-Worker-Nonce
 -> browser-worker verify_signature
```

`BrowserWorkerAuthService` 负责 secret 生成、hash、校验、request signing 和 signature verification。`browser_workers` 新增 `worker_secret_hash`、`api_key_hash`、`last_auth_at`、`auth_status`、`allowed_actions`、`allowed_domains`。

### UI Access Scope

`browser_ui_access_sessions` 新增 `scopes`、`one_time`、`used_at`、`revoked_reason`、`client_ip`、`user_agent`。`validate` 时会检查 token、过期时间、scope 和 one-time 状态，并写入安全审计日志。

### Browser Action Policy

`BrowserActionPolicyService` 统一校验：

- action type 是否支持。
- navigate 目标是否在 `BROWSER_ALLOWED_DOMAINS` 内。
- profile/session 是否属于当前 workspace。
- worker 是否允许该 action。
- worker capability 是否满足 action。
- UI access scope 是否允许。

默认策略为 `BROWSER_ALLOW_EXTERNAL_DOMAINS=False`，只允许 `example.com`、`localhost`、`127.0.0.1`。

### Security Audit

`BrowserSecurityAuditLog` / `browser_security_audit_logs` 记录 worker 注册、worker auth success/failed、UI token created/validated/revoked/expired、action blocked by policy 和 profile access denied。

Phase 26 不实现 TikTok / YouTube / X 自动化、自动登录、Cookie 注入、代理池、指纹绕过、验证码处理、真实平台自动化或完整 RBAC/JWT/OAuth。

## Phase 27 Customer Machine Worker Bootstrap

Phase 27 新增 `worker_client` 客户机启动包，让 Windows、Mac 或真实客户机可以注册到 AI Server，并暴露与 Docker `browser-worker` 服务相同的 Browser Worker 协议。

```text
customer machine
 -> worker_client/worker_config.yaml
 -> python -m worker_client.cli register
 -> AI Server /api/v1/browser-workers/register
 -> worker_client/worker_state.json
 -> python -m worker_client.cli serve
 -> local worker runtime
 -> python -m worker_client.cli heartbeat
 -> AI Server heartbeat flow / signed request
```

核心模块：

- `worker_client/config.py`：读取 YAML、支持 env override、管理本地 `worker_state.json`、输出时隐藏 secret。
- `worker_client/registration.py`：调用 `POST /api/v1/browser-workers/register` 的 registration flow。
- `worker_client/heartbeat.py`：调用 `POST /api/v1/browser-workers/{worker_id}/heartbeat` 的 heartbeat flow，发送 `X-Worker-Secret` 和 Phase 26 签名请求头。
- `worker_client/runtime.py`：启动兼容 `/health`、`/sessions`、`/actions`、`/sessions/{session_id}/close`、`/ui-access/capabilities` 的 local worker runtime。
- `worker_client/cli.py`：提供 `python -m worker_client.cli register`、`heartbeat`、`serve`、`start`。
- `worker_client/worker_config.example.yaml`：安全示例配置，复制为本地 `worker_config.yaml` 后使用。

安全边界：

- `worker_config.yaml` 与 `worker_state.json` 只保存在客户机本地，并已加入 `.gitignore`。
- 明文 `worker_secret` 只由服务端返回一次，之后仅保存在客户机 `worker_state.json`。
- Phase 27 不接 OpenClaw，不做账号登录、Cookie 注入、代理池、指纹绕过、验证码处理、社媒平台自动化或托管式 Worker 集群。

## Phase 29 Worker Runtime Manager Architecture

`worker_client/runtime_manager.py` is the local control layer for customer-machine workers. It coordinates runtime lifecycle, heartbeat thread, runtime health, and `runtime_state`. Local state is written through `worker_client/status.py` to `worker_client/runtime_state/status.json`; local logs are written through `worker_client/logging.py` to `worker_client/logs/worker.log` with secret redaction. `worker_client/local_api_client.py` is the future Worker Console Foundation client.

Local management API exposed by `worker_client/runtime.py`: `GET /local/status`, `GET /local/health`, `POST /local/runtime/start`, `POST /local/runtime/stop`, `POST /local/runtime/restart`, `POST /local/heartbeat/start`, `POST /local/heartbeat/stop`, `GET /local/logs`.

`Desktop Runtime Placeholder` lives in `worker_client/desktop/`; Phase 29 has no GUI, no Electron, no Tauri, no PySide, no system tray, and no exe/dmg packaging.

## Phase 30 Worker Console GUI Foundation

`worker_console` is an independent local Web GUI project built with Vite, React, TypeScript, and Tailwind. It is not served by the central API container. Operators run it locally during worker-machine operation.

Architecture:

```text
Worker Console Web UI
↓
worker_console/src/api/localWorkerClient.ts
↓
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
↓
worker_client.runtime /local/* API
↓
Worker Runtime Manager
```

Pages: Dashboard, Runtime Control, Logs, Connection Info. Current boundary: no system tray, no auto update, no Electron, no Tauri, no PySide, no exe / dmg.
## Phase 31：Worker Console Desktop 架构

`worker_console_desktop` 是 Tauri 桌面壳基础，运行在客户机本地，调用 `http://127.0.0.1:9100` 上的 `worker_client` Local API。

流程：

```text
Tauri Window
↓
React Worker Console UI
↓
worker_console_desktop/src/api/localWorkerClient.ts
↓
worker_client local API
↓
runtime_manager / status / logging
```

当前桌面端只负责显示状态、日志和发起 runtime/heartbeat 控制请求；不包含系统托盘、开机自启、自动更新、正式安装包或真实平台自动化。

## Phase 32：System Tray Desktop Runtime 架构

Phase 32 后，桌面 Runtime 架构为：

```text
Tauri System Tray
↓
tray-control event
↓
React Desktop Console
↓
localWorkerClient.ts
↓
worker_client Local API
↓
runtime_manager / heartbeat / status / logging
```

窗口关闭事件被 Tauri 拦截，`minimize_to_tray=true` 时执行隐藏窗口，不退出进程。Tray Runtime Control 只通过本地 HTTP API 控制 runtime / heartbeat，不执行 shell，不执行远程命令。

Desktop Status Sync 定时调用 `GET /local/status` 和 `GET /local/health`，并通过 Tauri command 更新托盘 tooltip。

## Phase 33 Conversation Runtime Architecture

Flow:

```text
user message
-> ConversationService
-> MemoryService lightweight lookup
-> PlanningService plan placeholder
-> ToolRegistry / ContentAgent / OpenClaw mock routing
-> assistant response
-> conversation_events polling timeline
```

Core files:

- `app/models/conversation.py`
- `app/schemas/conversation.py`
- `app/conversation/repositories/conversation_repository.py`
- `app/conversation/services/conversation_service.py`
- `app/api/routes/conversations.py`
- `worker_console/src/api/conversationClient.ts`
- `worker_console_desktop/src/api/conversationClient.ts`

Conversation Runtime does not replace Memory Foundation. It reuses `conversation_messages` by adding nullable `thread_id`; Phase 14 Memory session messages continue to use nullable-compatible `session_id`.

## Phase 34 Remote Browser Runtime Architecture

Remote Browser Runtime Foundation adds a real dispatch path from AI Server to customer-machine Worker:

```text
AI Server
-> BrowserRuntimeSessionService
-> RemoteBrowserProvider
-> BrowserWorkerSelector
-> BrowserWorkerClient
-> worker_client/browser_runtime
-> Playwright Chromium
-> storage/browser_screenshots
```

Core files:

- `app/models/browser_runtime.py` for `browser_runtime_sessions`
- `app/browser/services/browser_runtime_session_service.py`
- `app/browser/providers/remote_provider.py`
- `worker_client/browser_runtime/runtime.py`
- `worker_client/browser_runtime/session_manager.py`
- `worker_client/browser_runtime/playwright_provider.py`
- `worker_client/browser_runtime/schemas.py`

Worker Runtime API:

- `/browser/session/create`
- `/browser/session/{session_id}/navigate`
- `/browser/session/{session_id}/screenshot`
- `/browser/session/{session_id}/page`
- `/browser/session/{session_id}/close`

The runtime supports basic Chromium create / navigate / screenshot / page content / close. It does not support stealth browser, proxy rotation, cookie injection, login cloning, captcha bypass, remote desktop streaming, or DevTools remote control.

## Phase 35B Real Client Worker E2E Validation Architecture

Phase 35B adds validation capability rather than new runtime execution primitives.

```text
validate_real_client_worker_e2e.py
-> API health
-> worker health summary
-> available workers
-> expected_worker_name online check
-> browser runtime create / navigate / screenshot / page / close
-> JSON summary
```

If `expected_worker_name` is unavailable, the validator returns `SKIPPED` and does not call browser runtime action APIs. This preserves the distinction between validation readiness and a real customer-machine E2E result.

## Phase 35A：Browser Runtime Observability & Replay

```text
BrowserRuntimeSessionService
 -> BrowserRuntimeObservabilityService
 -> browser_runtime_events
 -> browser_runtime_snapshots
 -> browser_runtime_replays
 -> storage/browser_runtime_snapshots/{workspace_id}/{session_id}
 -> Worker Console Timeline / Snapshots / Replay metadata
```

Timeline Event Flow：

- create session -> `session_created`
- navigate -> `navigate_started` / `navigate_completed` / `action_failed`
- screenshot -> `screenshot_started` / `screenshot_completed`
- get page -> `page_snapshot_captured`
- close -> `session_closed`
- replay -> `replay_requested`

Snapshot Storage 保存 page HTML、page TXT、error JSON、replay JSON；截图继续保存到 `storage/browser_screenshots`。Replay Metadata Flow 只导出可读 metadata，不重新执行浏览器动作。Failure Debug 会记录 action_type、target/url、worker_id、error、duration_ms、last known url、last page title。

边界：Phase 35A 不是 live stream，不是 VNC/noVNC，不是 DevTools remote control，不做 replay 重新执行，也不做真实平台自动化。

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
## Phase 38：Conversation Tool Execution Bridge 架构补充

已完成：`ConversationToolRouter` 负责 Routing Rules，将用户消息映射到 Browser Bridge、OpenClaw mock bridge、RAG bridge、Content bridge、Planning bridge 或 fallback。`ConversationService.run_conversation_turn` 负责写入 `route_selected`、`tool_execution_started`、`tool_execution_completed`、`agent_execution_started`、`planning_execution_started`、`bridge_fallback`、`bridge_error` 等事件，并返回 `route_name`、`selected_tool`、`events_created`、`success`、`summary`、`result_metadata`。

边界：当前不是 autonomous agent，不是 WebSocket，不是 SSE，不做真实平台发布，不做真实 OpenClaw，不做 ComfyUI。

## Phase 39：Conversation Approval Flow 架构补充

Phase 39 在 Conversation Runtime 与 Tool Execution Bridge 之间加入审核门禁：

```text
user message
-> ConversationToolRouter
-> ConversationRiskPolicy
-> conversation_approvals
-> pending approvals panel
-> approve / reject / cancel
-> execute_after_approval
-> Tool Execution Gate
-> Tool / Agent / Planning
-> conversation_events
```

核心组件：

- `ConversationRiskPolicy`：根据 route/tool/action 计算 `risk_level`。
- `ConversationApprovalService`：管理 `approval_status` 状态流转。
- `conversation_approvals`：保存 `proposed_action` 与 `proposed_payload`，避免未审核动作直接执行。
- Tool Execution Gate：`auto_safe` 只自动执行 low risk；`review_first` 全部先创建 approval；`execute_after_approval` 只执行 approved approval。
- Frontend：Admin Dashboard、Worker Console、Worker Console Desktop 都展示 pending approvals panel。

边界：当前不是完整权限系统，not a full permission system；不是 WebSocket/SSE；不做真实平台发布、登录、验证码、代理、指纹绕过、真实 OpenClaw 或 ComfyUI。
## Phase 40：Conversation Playbook Architecture

Conversation Runtime 现在包含三层：

1. `ConversationToolRouter`：临时一句话 rule-based route。
2. `ConversationApprovalService` / `ConversationRiskPolicy`：执行前审核与风险门禁。
3. `ConversationPlaybookService` / `ConversationPlaybookExecutor`：标准化模板执行。

Playbook Run Flow：

`conversation_playbooks` -> `conversation_playbook_runs` -> step executor -> existing Tool / Agent / Planning bridge -> approval gate when needed -> `conversation_events` timeline -> assistant message。

Step details 不单独建表，当前存放在 `conversation_playbook_runs.output_payload.steps`，字段包含 `step_index`、`step_type`、`status`、`input`、`output`、`error`、`duration_ms`。

当前不是完整 workflow builder，也不是 autonomous agent；它只是 Playbook Foundation。

## Phase 41 Output Library Architecture

Output Library 位于 Conversation / Playbook / Tool 执行之后：

```text
Conversation / Playbook / Tool / Browser Runtime
-> OutputArtifactService
-> output_artifacts
-> storage/output_artifacts/{workspace_id}/{artifact_id}/
-> Admin Dashboard / Worker Console / Desktop preview and export
```

`output_artifacts` 按 workspace 隔离，可关联 `thread_id` 和 `playbook_run_id`。截图、HTML snapshot 等文件型 artifact 只保存 `file_path` 和 metadata，不复制大文件；`content_draft`、`rag_answer`、`report`、`plan` 等文本型 artifact 可保存 bounded content。

Playbook artifact generation：
- `content_generation` -> `content_draft`
- `browser_screenshot_report` -> `screenshot` + `report`
- `rag_answer` -> `rag_answer`
- `trend_research_draft` -> `report` + `content_draft`
- `openclaw_mock_device_check` -> `json`

当前不是完整素材管理系统，not a full DAM；不接 S3 / MinIO，也不做真实发布资产管理。
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
## Phase 46 Architecture: Workflow Graph Runtime

Phase 46 adds `workflow_graphs`, `workflow_graph_nodes`, `workflow_graph_edges`, `workflow_replays`, `WorkflowExecutionPlanner`, and `SafeConditionEvaluator` above the Phase 45 Workflow State layer. Graph runtime supports Conditional Execution, dependency resolution, Retry/Fallback Path planning, and Replay Foundation metadata while preserving boundaries: not a visual DAG builder, not distributed orchestration engine, and not ComfyUI.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47：Workflow Template Registry & Versioning

架构新增 `workflow_templates`、`workflow_template_versions`、`workflow_template_runs`，通过 `WorkflowTemplateRegistryService` 和 `WorkflowTemplateCompatibilityService` 将 Workflow Graph Runtime 沉淀为可复用模板。内置模板包括 `browser_screenshot_report_graph`、`content_generation_graph`、`rag_answer_graph`、`approval_then_browser_graph`、`openclaw_mock_inspect_graph`、`task_retry_demo_graph`。模板运行会关联 `workflow_template_id`、`workflow_template_version_id`、`workflow_template_run_id`，并继续遵守 approval / risk gate。

边界：当前不是可视化 DAG builder，不接 ComfyUI，不做真实平台自动化。
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
