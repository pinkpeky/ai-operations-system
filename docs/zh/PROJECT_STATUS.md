# 项目状态

## Phase 28 OpenClaw Worker Adapter Foundation

状态：已完成。

Phase 28 在客户机 Browser Worker 侧预留 OpenClaw 执行适配层：

- 新增 `worker_client/openclaw/`，包含 `BaseOpenClawProvider`、`MockOpenClawProvider`、`OpenClawRuntime`、OpenClaw action schemas。
- `worker_client runtime` 新增 `GET /openclaw/health`、`GET /openclaw/capabilities`、`POST /openclaw/actions`，当前全部返回 mock。
- 主应用新增 `app/openclaw/`，包含 `OpenClawWorkerClient`、schemas、repository、service。
- 新增 `openclaw_action_logs` 表，用于记录 workspace、worker、action、payload、provider、mock、duration 与 error。
- 新增 API：`GET /api/v1/openclaw/health`、`GET /api/v1/openclaw/capabilities`、`POST /api/v1/openclaw/actions`。
- 新增内置工具 `openclaw_tool`，通过已注册 Browser Worker 调用 mock OpenClaw runtime，并写入 `tool_call_logs`、`openclaw_action_logs`、`browser_security_audit_logs`。
- 新增配置：`OPENCLAW_PROVIDER=mock`、`OPENCLAW_ENABLED=true`、`OPENCLAW_ACTION_TIMEOUT_SECONDS=60`。

边界：Phase 28 只做 OpenClaw Adapter Foundation，不调用真实 OpenClaw，不接 TikTok / YouTube / X，不做账号登录、自动发布、验证码、代理池、指纹绕过或真实平台自动化。

## Phase 27 Customer Machine Worker Bootstrap

状态：已完成。

Phase 27 建立客户机 / Windows / Mac 机器作为 Browser Worker 接入 AI Server 的本地启动基础：

- 新增 `worker_client` 包，包含 `config.py`、`registration.py`、`heartbeat.py`、`runtime.py`、`cli.py` 和 `main.py`。
- 新增 `worker_client/worker_config.example.yaml`，客户机可复制为本地 `worker_config.yaml` 后配置 `server_url`、`workspace_id`、`worker_name`、capabilities、runtime port 和 heartbeat interval。
- 新增 CLI 命令：`python -m worker_client.cli register`、`python -m worker_client.cli heartbeat`、`python -m worker_client.cli serve`、`python -m worker_client.cli start`。
- `registration flow` 调用 `POST /api/v1/browser-workers/register`，一次性接收明文 `worker_secret`，并保存到客户机本地 `worker_state.json`。
- `heartbeat flow` 读取 `worker_state.json`，调用 `POST /api/v1/browser-workers/{worker_id}/heartbeat`，发送 `X-Worker-Secret` 与 Phase 26 signed request headers。
- `local worker runtime` 复用现有 browser-worker 协议，支持 `GET /health`、`POST /sessions`、`POST /actions`、`POST /sessions/{session_id}/close`、`GET /ui-access/capabilities`。
- `worker_config.yaml` 与 `worker_state.json` 已加入 `.gitignore`；`worker_secret` 只允许保存在客户机本地，不写入日志和 docs。

边界：Phase 27 只是 Customer Machine Worker Bootstrap；Phase 28 在此基础上增加 mock OpenClaw Adapter，但仍不调用真实 OpenClaw，不做 TikTok / YouTube / X 自动化、自动登录、Cookie 注入、代理池、指纹绕过、验证码处理或真实平台自动化。

## Phase 26 Browser Worker Security & Access Control

Phase 26 建立 Browser Worker、UI Access、Browser Profile、Browser Action 的基础安全控制层：

- 扩展 `browser_workers`，新增 `worker_secret_hash`、`api_key_hash`、`last_auth_at`、`auth_status`、`allowed_actions`、`allowed_domains`。
- 新增 `BrowserWorkerAuthService`，支持 worker secret 生成、hash、校验、请求签名和签名校验。
- Worker 请求签名使用 `X-Worker-Signature`、`X-Worker-Timestamp`、`X-Worker-Nonce` 和 body hash。
- `browser-worker` 的 `/sessions`、`/actions`、`/sessions/{session_id}/close` 支持签名校验；`/health` 保持无需鉴权。
- 扩展 `browser_ui_access_sessions`，新增 `scopes`、`one_time`、`used_at`、`revoked_reason`、`client_ip`、`user_agent`。
- UI Access Scope 支持 `view`、`control`、`screenshot`、`devtools_placeholder`，token 校验时会检查 scope 和 one-time 状态。
- 新增 `BrowserActionPolicyService`，校验 action type、target domain、profile access、worker capability 和 UI access scope。
- 新增 `BrowserSecurityAuditLog` / `browser_security_audit_logs`，记录 worker auth、UI token、policy block 和 profile access 安全事件。
- 新增 API：`POST /api/v1/browser-workers/{worker_id}/rotate-secret`、`POST /api/v1/browser-workers/{worker_id}/revoke`、`GET /api/v1/browser/security/audit-logs`、`POST /api/v1/browser/security/policy/check`。

边界：Phase 26 是安全基础设施，不实现真实平台账号安全、TikTok / YouTube / X 自动化、自动登录、Cookie 注入、代理池、指纹绕过、验证码处理或完整 RBAC/JWT/OAuth。

## Phase 25 Browser Worker UI Access Placeholder

Phase 25 建立浏览器 UI 接管占位访问层：

- 新增 `browser_ui_access_sessions`。
- 新增 `BrowserUIAccessService`，支持 create / get / revoke / expire / generate_access_token / validate_access_token。
- 数据库只保存 `access_token_hash`，明文 token 只在创建接口返回一次。
- 生成 `remote_control_url`、`live_view_url`、`devtools_url=null`，全部都是 placeholder URL。
- 新增 API：`POST /api/v1/browser/ui-access`、get、revoke、expire、validate。
- browser-worker 新增 `/ui-access/capabilities`，返回 `vnc=false`、`novnc=false`、`devtools=false`、`placeholder=true`。
- `browser_tool` 新增 `create_ui_access` 和 `revoke_ui_access`。

边界：Phase 25 不实现真实 VNC / noVNC / DevTools UI，不做实时浏览器远程画面、平台登录、验证码处理、Cookie 注入、代理池、指纹绕过、TikTok / YouTube / X 或真实平台自动化。

## Phase 24 Human-in-the-loop Browser Control

Phase 24 建立人工接管浏览器控制基础层：

- 新增 `browser_human_control_sessions`，记录 `browser_session_id`、`profile_id`、`worker_id`、`status`、`reason`、`requested_by`、`approved_by`、`started_at`、`completed_at`、`expires_at`。
- 新增 `browser_human_control_events`，记录 `requested`、`approved`、`started`、`completed`、`cancelled`、`expired`、`timeout`、`note` 等事件。
- 扩展 `browser_sessions`：`human_control_status`、`human_control_session_id`、`paused_at`、`resumed_at`。
- 新增 `BrowserHumanControlService`，支持 request / approve / start / complete / cancel / expire / list / get / events。
- 新增 API：`POST /api/v1/browser/human-control/request`、approve、start、complete、cancel、list、get、events。
- `browser_tool` 新增 `request_human_control` 和 `complete_human_control`。
- browser-worker 新增 metadata-level `/human-control/start`、`/human-control/complete`、`/human-control/status/{session_id}`。

边界：Phase 24 不实现 VNC / noVNC / DevTools 真实远程 UI，不做 TikTok / YouTube / X 自动化、自动登录、Cookie 注入、代理池、指纹绕过、验证码自动化或真实平台自动化。

## Phase 23 Browser Profile Health & Recovery

Phase 23 增强 Persistent Browser Profile 的稳定性、恢复能力和生命周期管理：

- 扩展 `browser_profiles`：`health_status`、`last_health_check_at`、`last_error`、`usage_count`、`corrupted_at`、`backup_path`、`last_backup_at`。
- 新增 `browser_profile_usage_logs`，记录 `lock`、`release`、`session_start`、`session_close`、`backup`、`restore`、`recovery`、`cleanup` 等操作。
- 新增 `BrowserProfileHealthService`，支持 health check、warning/corrupted 标记、stale lock recovery、profile path/runtime 校验和 usage count。
- 新增 `BrowserProfileBackupService`，支持 profile backup / restore / list / cleanup，备份路径为 `worker/profile_backups/{workspace_id}/{profile_id}`。
- 新增 `BrowserProfileCleanupService`，支持 deleted / corrupted / unused profiles 的 dry-run 与实际清理。
- 新增 API：`GET /api/v1/browser/profiles/health/summary`、`POST /api/v1/browser/profiles/recover-stale-locks`、`POST /api/v1/browser/profiles/{profile_id}/backup`、`POST /api/v1/browser/profiles/cleanup`、health-check、backups、restore、usage-logs。

边界：Phase 23 不做 TikTok / YouTube / X 自动化、账号登录、Cookie 注入、代理池、指纹绕过、验证码、真实平台自动化或 autonomous browser planning。

## Phase 22 Persistent Browser Profile Foundation

状态：已完成。

Phase 22 新增持久化 Browser Profile 基础层：

- 新增 `browser_profiles` 表，记录 `profile_name`、`profile_type`、`provider`、`profile_path`、`status`、`locked_by_session_id`、`locked_at`、`last_used_at`。
- 新增 `BrowserProfileService`，支持 `create_profile`、`list_profiles`、`get_profile`、`lock_profile`、`release_profile`、`mark_corrupted`、`delete_profile`、`get_available_profile`。
- `browser_sessions` 新增 `profile_id`、`profile_path`、`persistent_context_enabled`。
- `POST /api/v1/browser/sessions` 支持 `profile_id` 与 `use_persistent_profile=true`。
- `POST /api/v1/browser/sessions/{session_id}/close` 会释放 profile lock。
- `browser-worker` 在 profile-backed session 下使用 Playwright `launch_persistent_context`，profile 文件位于 `worker/profiles/{workspace_id}/{profile_id}`。

边界：Phase 22 不做 TikTok / YouTube / X 自动化、账号登录、Cookie 注入、代理池、指纹绕过、验证码、真实平台自动化或 OpenClaw。

## Phase 21 Browser Worker Reliability

状态：已完成。

Phase 21 在 Phase 19/20 的 Remote Browser Worker 与真实 `browser-worker` 服务之上补齐可靠性基础：

- 新增 `BrowserWorkerHealthService`，按 `BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS` 检测 stale worker，并将过期 worker 标记为 `offline`，写入 `error_message`。
- 新增 `BrowserWorkerSelector`，按 `workspace_id`、`status=online`、capability、capacity 过滤，并选择 least loaded worker。
- 扩展 `browser_workers`：`max_sessions`、`active_sessions`、`max_actions_per_minute`、`current_load`、`priority`、`error_message`，`last_heartbeat_at` 作为 `last_seen` 返回。
- 扩展 `browser_worker_actions`：`retry_count`、`max_retries`。
- 新增 `BrowserSessionCleanupService`，支持 stale session 清理、worker offline/error 后关联 session 标记失败，并写 browser logs。
- 新增 `ScreenshotCleanupService`，支持按 workspace 与 age 手动清理截图，默认 `dry_run=true`。
- 新增 API：`GET /api/v1/browser-workers/health/summary`、`GET /api/v1/browser-workers/available`、`POST /api/v1/browser-workers/{worker_id}/mark-offline`、`POST /api/v1/browser-workers/cleanup-sessions`、`GET /api/v1/browser-workers/{worker_id}/sessions`、`POST /api/v1/browser/screenshots/cleanup`。

边界：Phase 21 只做 Worker Reliability，不做 TikTok / YouTube / X 自动化、登录、Cookie 注入、代理池、指纹绕过、验证码、OCR、视觉 AI、OpenClaw、真实平台自动化或 autonomous browser planning。

## Phase 20 Real Browser Worker Service

状态：已完成。

Phase 20 新增真正独立运行的 `browser-worker` 服务：

- `worker/main.py` 暴露 `GET /health`、`POST /sessions`、`POST /actions`、`POST /sessions/{session_id}/close`。
- `worker/browser_worker/playwright_runtime.py` 使用 headless Playwright Chromium。
- Docker Compose 新增 `browser-worker` 服务并暴露 `9100`。
- API Server 调用链路为 `RemoteBrowserProvider -> BrowserWorkerClient -> http://browser-worker:9100`。
- 新增运行配置 `BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100`。
- 截图保存到 `worker/screenshots/{workspace_id}/{remote_session_id}/{filename}.png`。

边界：Phase 20 仍不支持 TikTok / YouTube / X 自动化、登录、Cookie 注入、代理池、指纹绕过、验证码、OCR、视觉 AI、OpenClaw 或 autonomous browser agent。当前是本地 Docker Worker 基础，不是生产级外部 Worker 集群。

更新日期：2026-05-12

本文是中文主开发状态文档，记录 `E:\ai-operations-system` 的真实工程状态。当前状态：Phase 1 到 Phase 28 已完成。

## 总体状态

当前系统已经具备：

- FastAPI、PostgreSQL、Redis、Qdrant、Docker Compose。
- SQLAlchemy ORM、Alembic migration、Workspace/User/API Key 隔离。
- Redis Queue、Scheduler、TaskExecutor、任务事件、任务日志、取消、重试、超时与观测 summary。
- LLM Client Layer，默认 `mock`，支持本地 Ollama `mistral`。
- Embedding Pipeline，默认 `mock`，支持本地 Ollama `bge-m3`。
- Knowledge Lifecycle：`documents`、`document_chunks`、`collections_metadata`。
- Agentic RAG、Hybrid Search、Reranker Layer、RAG Eval / Debug Trace。
- File Upload Pipeline：PDF、DOCX、TXT、MD、CSV。
- Tool Calling Foundation：`BaseTool`、`ToolRegistry`、builtin tools、`tool_call_logs`。
- Memory Foundation：`conversation_sessions`、`conversation_messages`、`agent_memories`、`memory_operation_logs`。
- Multi-Agent Foundation：`AgentRegistry`、`agent_runs`、`agent_messages`、`agent_handoffs`、固定 Agent Chain。
- Agent Planning Foundation：`plans`、`plan_steps`、`plan_reviews`、`SimplePlannerAgent`、Plan Execution Flow。
- ContentAgent 示例 Agent。
- 中英文 Docs System、`PROJECT_OVERVIEW.md`、`CURRENT_RUNTIME.md`、Docs Runtime Verification。
- Customer Machine Worker Bootstrap：`worker_client`、`worker_config.example.yaml`、本地 `worker_config.yaml`、本地 `worker_state.json`、registration flow、heartbeat flow、local worker runtime。

## 已完成 Phase

| Phase | 状态 | 说明 |
| --- | --- | --- |
| Phase 1 | 已完成 | Docker、PostgreSQL、Redis、Qdrant、FastAPI、health check。 |
| Phase 2 | 已完成 | ORM、Task System、Redis Queue、Scheduler、Task API。 |
| Phase 2.5 | 已完成 | LLM Client Layer、MockProvider、LocalProvider、ServerProvider、Prompt Manager。 |
| Phase 3 | 已完成 | Embedding Pipeline、Qdrant Collection Layer、RAG ingest/search。 |
| Phase 3.5 | 已完成 | embedding 归一化、score normalizer、collection health、RAG debug API。 |
| Phase 4 | 已完成 | 单一 Agentic RAG Orchestrator。 |
| Phase 4.5 | 已完成 | Agentic RAG Task Executor handler 与 task API。 |
| Phase 4.6 | 已完成 | Ollama Mistral local LLM 接口与 LLM health check。 |
| Phase 5 | 已完成 | BaseAgent、ContentAgent、content_generation task。 |
| Phase 6 | 已完成 | Knowledge Lifecycle、source versioning、delete/reingest、active-only retrieval。 |
| Phase 6.5 | 已完成 | users、workspaces、workspace_members、api_keys、workspace middleware。 |
| Phase 7 | 已完成 | Ollama bge-m3 local embedding，自动检测 embedding dimension。 |
| Phase 8 | 已完成 | `rag_eval_runs`、`rag_eval_items`、Agentic RAG trace。 |
| Phase 9 | 已完成 | Reranker Provider Layer，mock/local provider，rerank trace。 |
| Phase 10 | 已完成 | Dense + Keyword -> Merge -> Rerank -> LLM 的 Hybrid Search。 |
| Phase 10.5 | 已完成 | 中英文 Docs System、PROJECT_OVERVIEW、CURRENT_RUNTIME、Docs SSOT。 |
| Phase 11 | 已完成 | File Upload Pipeline 与 Docs Runtime Verification。 |
| Phase 12 | 已完成 | Task Reliability & Observability，`task_events`、`task_logs`、cancel/retry、timeout、duration_ms、summary API。 |
| Phase 13 | 已完成 | Tool Calling Foundation，`BaseTool`、`ToolRegistry`、builtin tools、`tool_call_logs`、Tool API、Agent 手动 tool call。 |
| Phase 14 | 已完成 | Memory Foundation，`conversation_sessions`、`conversation_messages`、`agent_memories`、`memory_operation_logs`、Memory API、Agentic RAG `memory_trace`。 |
| Phase 15 | 已完成 | Multi-Agent Foundation，`AgentRegistry`、`agent_runs`、`agent_messages`、`agent_handoffs`、固定 Agent Chain、ToolAgent、Memory 集成基础。 |
| Phase 16 | 已完成 | Agent Planning Foundation，`plans`、`plan_steps`、`plan_reviews`、`SimplePlannerAgent`、可观测 Plan Execution Flow、step duration/error、cancel、memory_trace。 |
| Phase 17 | 已完成 | Browser Automation Adapter Foundation，`browser_sessions`、`browser_actions`、`browser_action_logs`、`BrowserProvider`、`MockBrowserProvider`、`PlaywrightBrowserProvider` placeholder、`BrowserService`、`browser_tool`、Browser API。 |
| Phase 18 | 已完成 | Playwright Local Provider Integration，`PlaywrightLocalProvider`、`BROWSER_PROVIDER=playwright_local`、本地 headless Chromium、`browser_id`、`page_id`、`provider_session_metadata`、`selector`、`target_url`、`screenshot_path`、`page_title`、Screenshot System、`get_page_content`。 |
| Phase 19 | 已完成 | Remote Browser Worker Foundation，`RemoteBrowserProvider`、`BrowserWorkerClient`、`browser_workers`、`browser_worker_sessions`、`browser_worker_actions`、Worker Registration、Worker Heartbeat、Worker Runtime Mock、`BROWSER_PROVIDER=remote`。 |
| Phase 20 | 已完成 | Real Browser Worker Service，独立 `browser-worker` Docker 服务、`worker/main.py`、`worker/browser_worker/playwright_runtime.py`、Playwright Chromium、`http://browser-worker:9100`、`worker/screenshots`。 |
| Phase 21 | 已完成 | Browser Worker Reliability，`BrowserWorkerHealthService`、`BrowserWorkerSelector`、`BrowserSessionCleanupService`、`ScreenshotCleanupService`、capacity、least loaded selection、action retry、screenshot cleanup。 |
| Phase 22 | 已完成 | Persistent Browser Profile Foundation，`browser_profiles`、`BrowserProfileService`、Profile Lock / Profile Release、`profile_id`、`profile_path`、`persistent_context_enabled`、`launch_persistent_context`、`worker/profiles`。 |
| Phase 23 | 已完成 | Browser Profile Health & Recovery，`BrowserProfileHealthService`、`BrowserProfileBackupService`、`BrowserProfileCleanupService`、`browser_profile_usage_logs`、`health_status`、`usage_count`、stale lock recovery、profile backup、profile cleanup。 |
| Phase 24 | 已完成 | Human-in-the-loop Browser Control，`BrowserHumanControlService`、`browser_human_control_sessions`、`browser_human_control_events`、session paused/resumed、`request_human_control`、`complete_human_control`。 |
| Phase 25 | 已完成 | Browser Worker UI Access Placeholder，`BrowserUIAccessService`、`browser_ui_access_sessions`、`access_token_hash`、placeholder URL、token validate/revoke/expire、`/ui-access/capabilities`、`create_ui_access`、`revoke_ui_access`。 |
| Phase 26 | 已完成 | Browser Worker Security & Access Control，`BrowserWorkerAuthService`、`worker_secret_hash`、signed worker request、UI Access Scope、`BrowserActionPolicyService`、`browser_security_audit_logs`。 |
| Phase 27 | 已完成 | Customer Machine Worker Bootstrap，`worker_client`、`worker_config.example.yaml`、本地 `worker_config.yaml`、本地 `worker_state.json`、`python -m worker_client.cli register`、`heartbeat`、`serve`、`start`、registration flow、heartbeat flow、local worker runtime。 |
| Phase 28 | 已完成 | OpenClaw Worker Adapter Foundation，`worker_client/openclaw`、`MockOpenClawProvider`、`OpenClawRuntime`、服务端 `OpenClawWorkerClient`、`openclaw_tool`、`openclaw_action_logs`、mock `/openclaw/*` runtime routes。 |

## Phase 15 完成内容

Multi-Agent Foundation：

- 新增 `app/multi_agent/`，包含 `services` 与 `repositories`。
- 新增 `AgentRegistry`，支持 `register_agent`、`get_agent`、`list_agents`、enable/disable 和 agent metadata。
- 新增数据库表：`agent_runs`、`agent_messages`、`agent_handoffs`。
- 新增 `MultiAgentService`，支持 `create_run`、`append_message`、`handoff`、`execute_single_agent`、`execute_agent_chain`、`get_run`、`list_runs`。
- 注册 Agent：`content_planner`、`rag_agent`、`content_agent`、`review_agent`、`runtime_agent`、`tool_agent`。
- 固定 Agent Chain：`content_planner -> rag_agent -> content_agent -> review_agent`。
- `ToolAgent` 可调用已有 `ToolRegistry` 内置工具：`rag_search_tool`、`file_search_tool`、`create_task_tool`、`get_task_status_tool`、`current_runtime_tool`。
- 新增 API：`GET /api/v1/agents/registry`、`POST /api/v1/multi-agent/runs`、`GET /api/v1/multi-agent/runs`、`GET /api/v1/multi-agent/runs/{run_id}`、`POST /api/v1/multi-agent/runs/{run_id}/execute-chain`、`GET /api/v1/multi-agent/runs/{run_id}/messages`、`GET /api/v1/multi-agent/runs/{run_id}/handoffs`。
- run output 包含 `agents_involved`、message history、handoff records 和 `handoff_trace`。
- 支持 `session_id`，并可复用 Phase 14 Memory Foundation 的 recent messages 与 memory context。

Phase 15 明确不包含：

- autonomous planner。
- ReAct。
- Browser Agent。
- Playwright、OpenClaw、Selenium。
- 外部平台 API 或真实自动化执行。

## Phase 16 完成内容

Agent Planning Foundation：

- 新增 `app/planning/`，包含 `services` 与 `repositories`。
- 新增数据库表：`plans`、`plan_steps`、`plan_reviews`。
- 新增 `SimplePlannerAgent`，当前为 rule-based planner，输出有限、确定性的结构化 plan。
- 新增 `PlanningService`，支持 `create_plan`、`create_steps`、`execute_step`、`execute_plan`、`review_plan`、`cancel_plan`、`get_plan`、`list_plans`。
- 新增 API：`POST /api/v1/plans`、`GET /api/v1/plans`、`GET /api/v1/plans/{plan_id}`、`POST /api/v1/plans/{plan_id}/execute`、`POST /api/v1/plans/{plan_id}/cancel`、`GET /api/v1/plans/{plan_id}/steps`、`GET /api/v1/plans/{plan_id}/reviews`。
- Plan Execution Flow：plan -> steps -> AgentRegistry 或 ToolRegistry -> step output / duration / error -> review -> final result。
- step 支持 `pending`、`running`、`completed`、`failed`、`skipped`，并在 service 层支持 retry / skip。
- Planning 支持 `session_id` 与 `memory_trace`，但不做高级长期记忆规划。

Phase 16 明确不包含：

- autonomous AGI planner。
- tree-of-thought。
- recursive planning。
- 无限 Agent loop。
- ReAct。
- Browser Agent / Playwright / OpenClaw / Selenium。

## Phase 17 完成内容

Browser Automation Adapter Foundation：

- 新增 `app/browser/`，包含 providers、repositories、services。
- 新增数据库表：`browser_sessions`、`browser_actions`、`browser_action_logs`。
- 新增 `BrowserProvider` 接口：`create_session`、`close_session`、`navigate`、`click`、`type_text`、`scroll`、`screenshot`、`get_page_content`。
- 新增 `MockBrowserProvider`，当前默认使用，不启动真实浏览器。
- 新增 `PlaywrightBrowserProvider` placeholder，只返回清晰的未执行响应。
- 新增 `BrowserService`，支持 workspace 隔离的 session 创建、action 执行、session/action 查询、log 查询、`duration_ms` 和错误记录。
- 新增 API：`POST /api/v1/browser/sessions`、`GET /api/v1/browser/sessions`、`POST /api/v1/browser/actions`、`GET /api/v1/browser/actions/{session_id}`、`GET /api/v1/browser/logs/{session_id}`。
- 新增内置工具 `browser_tool`，支持 `navigate`、`click`、`type_text`、`screenshot`，全部走 `MockBrowserProvider`。
- Planning step 支持 `tool_name=browser_tool`。

Phase 17 明确不包含：

- Browser Agent。
- autonomous browser planning。
- Playwright / Selenium / OpenClaw 真实执行。

## Phase 18 完成内容

Playwright Local Provider Integration：

- 新增 `app/browser/providers/playwright_provider.py`，实现 `PlaywrightLocalProvider`，provider name 为 `playwright_local`。
- 支持 `create_session`、`close_session`、`navigate`、`click`、`type_text`、`screenshot`、`get_page_content`。
- `BrowserSession` 新增 `browser_id`、`page_id`、`provider_session_metadata`。
- `BrowserAction` 新增 `selector`、`target_url`、`screenshot_path`、`page_title`。
- 新增 Screenshot System：`screenshots/{workspace_id}/{session_id}/{filename}.png`。
- 新增 API：`GET /api/v1/browser/screenshot/{session_id}/{filename}`。
- `browser_tool` 扩展支持 `get_page_content`，并继续记录 `tool_call_logs`。
- Docker 镜像安装 Playwright Python 与 Chromium，仅安装 Chromium。

Phase 18 安全边界：

- 默认仍为 `BROWSER_PROVIDER=mock`。
- 使用 `BROWSER_PROVIDER=playwright_local` 时只允许 `example.com`、本地测试页面、静态 `file://` 页面。
- 不做 TikTok / YouTube / X 自动化。
- 不做自动登录、Cookie 注入、指纹绕过、代理池、验证码自动化。
- 不做 OCR、视觉 AI、autonomous browser planning、Browser Worker 或真实平台自动化。

## Phase 19 完成内容

Remote Browser Worker Foundation：

- 新增 `app/browser/remote/`，包含 `client`、`schemas`、`services`。
- 新增 `BrowserWorkerClient`，支持 `create_session`、`close_session`、`execute_action`、`health_check`。
- 新增 `RemoteBrowserProvider`，provider name 为 `remote`，通过注册 worker 的 `base_url` 分发 browser action。
- 新增数据库表：`browser_workers`、`browser_worker_sessions`、`browser_worker_actions`。
- 新增 API：`POST /api/v1/browser-workers/register`、`POST /api/v1/browser-workers/{worker_id}/heartbeat`、`GET /api/v1/browser-workers`。
- 新增 mock worker runtime：`GET /api/v1/browser-worker-runtime/health`、`POST /api/v1/browser-worker-runtime/sessions`、`POST /api/v1/browser-worker-runtime/actions`、`POST /api/v1/browser-worker-runtime/sessions/{session_id}/close`。
- `BrowserService` 支持 `BROWSER_PROVIDER=remote`。
- `browser_tool` 继续通过 `BrowserService` 执行，因此 remote provider 模式下仍保留 `tool_call_logs` 与 `browser_action_logs`。

Phase 19 明确不包含：

- 真实外部 Worker 部署。
- TikTok / YouTube / X 自动化。
- 账号登录、自动发布、Cookie 注入、指纹绕过、代理池、验证码。
- autonomous browser agent。
- TikTok / YouTube / X 平台自动化。
- OCR、视觉 AI、真实登录流程。

## 当前运行默认值

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
BROWSER_PROVIDER=mock
```

本地模型接口已支持：

- `LOCAL_LLM_MODEL=mistral`
- `LOCAL_EMBEDDING_MODEL=bge-m3`

当前 Multi-Agent 不新增环境变量。完整运行态见 `docs/CURRENT_RUNTIME.md`。

## 当前限制

- Multi-Agent 当前是固定链路基础层，不做动态规划、自动路由或 ReAct。
- local reranker 仍是 placeholder。
- Keyword retrieval 仍是 PostgreSQL `ILIKE` 和简单关键词评分。
- Memory 仍是 PostgreSQL 文本检索基础层，不包含 vector memory、graph memory 或 autonomous memory planning。
- 不包含 Browser Agent、Playwright、OpenClaw、Selenium。
- 不包含 Elasticsearch、OpenSearch、真实 BM25。
- 不包含完整 RBAC、JWT、OAuth。
- 不包含前端 Dashboard、Prometheus、Grafana。

## 固定验证流程

每个 Phase 完成后必须执行：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

只有 docs verifier 输出 `SUMMARY: PASS` 后，docs 才视为与当前 runtime 同步。

## Phase 29 Worker Client Packaging & Worker Console Foundation

已完成：

- 新增 `Worker Runtime Manager`：`worker_client/runtime_manager.py`，支持 `start_runtime`、`stop_runtime`、`restart_runtime`、`runtime_health`、`start_heartbeat`、`stop_heartbeat`、`runtime_state`。
- 新增本地状态层：`worker_client/status.py`，运行时写入 `worker_client/runtime_state/status.json`，记录 `worker_id`、`worker_name`、`workspace_id`、`server_url`、`runtime_running`、`heartbeat_running`、`registered`、`last_heartbeat_at`、`last_error`、`current_status`、`openclaw_enabled`、`browser_enabled`。
- 新增本地日志层：`worker_client/logging.py`，写入 `worker_client/logs/worker.log`，支持简单轮转和 secret 脱敏。
- 扩展 `worker_client/runtime.py` 本地管理 API：`GET /local/status`、`GET /local/health`、`POST /local/runtime/start`、`POST /local/runtime/stop`、`POST /local/runtime/restart`、`POST /local/heartbeat/start`、`POST /local/heartbeat/stop`、`GET /local/logs`。
- 新增 `worker_client/local_api_client.py`，作为未来 Worker Console Foundation / GUI 的 Python client。
- 新增 Packaging Scripts：`packaging/windows_start_worker.ps1`、`packaging/mac_start_worker.sh` 等 Windows/Mac 基础脚本。
- 新增 `Desktop Runtime Placeholder`：`worker_client/desktop/README.md` 与 `placeholder.py`。

明确不包含：GUI、系统托盘、Electron、Tauri、PySide、exe/dmg 打包、真实浏览器远程画面、真实平台自动化、TikTok / YouTube / X 自动化、登录自动化、Cookie 注入、指纹绕过、代理池或验证码自动化。

## Phase 30 Worker Console GUI Foundation

已完成：

- 新增 `worker_console` 独立前端项目，技术栈为 Vite、React、TypeScript、Tailwind。
- 默认本地 API：`VITE_LOCAL_WORKER_API=http://127.0.0.1:9100`。
- 新增 Dashboard、Runtime Control、Logs、Connection Info 页面区域。
- 新增 `worker_console/src/api/localWorkerClient.ts`，支持 `getStatus`、`getHealth`、`getLogs`、`startRuntime`、`stopRuntime`、`restartRuntime`、`startHeartbeat`、`stopHeartbeat`。
- 本地 API 不可用时显示 `Worker API unreachable`、`请确认 worker_client 是否启动`、`请确认端口是否为 9100`。

明确不包含：system tray、auto update、Electron、Tauri、PySide、no exe / dmg、TikTok / YouTube / X 自动化、登录自动化、Cookie 注入、代理池、指纹绕过、验证码自动化或真实平台自动化。
## Phase 31：Worker Console Desktop App Foundation

状态：已完成。

本阶段新增 `worker_console_desktop`，使用 Tauri + React + Vite + TypeScript + Tailwind 建立本地 Worker Console 桌面壳基础。桌面端默认通过 `VITE_LOCAL_WORKER_API=http://127.0.0.1:9100` 调用 Phase 29 的 Local API，并显示 Worker status、runtime state、heartbeat state、connection info 和 logs。

关键文件：

- `worker_console_desktop/package.json`
- `worker_console_desktop/src/api/localWorkerClient.ts`
- `worker_console_desktop/src/main.tsx`
- `worker_console_desktop/src-tauri/tauri.conf.json`
- `worker_console_desktop/src-tauri/src/main.rs`

开发命令：

```powershell
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

边界：当前没有正式安装包、no exe / dmg、no system tray、no auto update、无开机自启、无真实平台自动化。
