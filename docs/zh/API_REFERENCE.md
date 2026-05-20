# API 参考

更新日期：2026-05-12

本文记录当前真实可用 API。除 workspace/user 创建类接口外，业务接口默认要求：

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

## Phase 28 OpenClaw Worker Adapter Foundation

状态：生产基础 / mock placeholder。Phase 28 在客户机 Browser Worker 协议上新增 OpenClaw Adapter Foundation。当前只实现 `MockOpenClawProvider`、`OpenClawRuntime`、服务端 `OpenClawWorkerClient`、`openclaw_tool`、`openclaw_action_logs` 和 mock runtime routes，不调用真实 OpenClaw，不做 TikTok / YouTube / X 自动化、自动登录、Cookie 注入、代理池、指纹绕过或验证码自动化。

核心配置：`OPENCLAW_PROVIDER=mock`、`OPENCLAW_ENABLED=true`、`OPENCLAW_ACTION_TIMEOUT_SECONDS=60`。

数据表：`openclaw_action_logs`；安全审计继续写入 `browser_security_audit_logs`。

Worker Client 文件：`worker_client/openclaw/provider.py`、`worker_client/openclaw/mock_provider.py`、`worker_client/openclaw/schemas.py`、`worker_client/openclaw/runtime.py`。

### GET `/api/v1/openclaw/health`

Required headers：`X-Workspace-Id`，可选 `X-User-Id`。

Response JSON：

```json
{
  "success": true,
  "provider": "mock",
  "enabled": true,
  "reachable": true,
  "worker_id": "WORKER_ID",
  "worker_name": "local-windows-worker-1",
  "mock": true,
  "version": "mock-openclaw-0.1",
  "error": null,
  "raw": {
    "real_openclaw_called": false
  }
}
```

### GET `/api/v1/openclaw/capabilities`

Required headers：`X-Workspace-Id`，可选 `X-User-Id`。

Response JSON：

```json
{
  "success": true,
  "provider": "mock",
  "enabled": true,
  "worker_id": "WORKER_ID",
  "worker_name": "local-windows-worker-1",
  "mock": true,
  "capabilities": {
    "openclaw": true,
    "real_openclaw": false,
    "platform_automation": false
  },
  "actions": ["health_check", "list_capabilities", "execute_action"],
  "error": null,
  "raw": {}
}
```

### POST `/api/v1/openclaw/actions`

Required headers：`X-Workspace-Id`，可选 `X-User-Id`。

Request JSON：

```json
{
  "action_type": "mock_inspect",
  "target": "https://example.com",
  "input_payload": {
    "note": "phase28 smoke"
  },
  "profile_id": null,
  "browser_session_id": null,
  "metadata": {
    "phase": "28"
  }
}
```

Response JSON：

```json
{
  "success": true,
  "action_type": "mock_inspect",
  "output_payload": {
    "message": "mock openclaw action success",
    "real_openclaw_called": false
  },
  "error": null,
  "duration_ms": 0,
  "provider": "mock",
  "mock": true,
  "worker_id": "WORKER_ID",
  "log_id": "OPENCLAW_ACTION_LOG_ID"
}
```

### Worker Runtime OpenClaw Mock Routes

Worker Runtime 协议端点：

- `GET /api/v1/browser-worker-runtime/openclaw/health`
- `GET /api/v1/browser-worker-runtime/openclaw/capabilities`
- `POST /api/v1/browser-worker-runtime/openclaw/actions`
- `GET /openclaw/health`（worker_client runtime）
- `GET /openclaw/capabilities`（worker_client runtime）
- `POST /openclaw/actions`（worker_client runtime）

### `openclaw_tool`

Tool Registry 已注册 `openclaw_tool`，支持 `health_check`、`list_capabilities`、`execute_action`。

Tool input：

```json
{
  "action_type": "execute_action",
  "openclaw_action_type": "mock_inspect",
  "target": "https://example.com",
  "input_payload": {},
  "metadata": {
    "phase": "28"
  }
}
```

边界：`openclaw_tool` 只调用 mock worker adapter，会写 `tool_call_logs`、`openclaw_action_logs` 和 `browser_security_audit_logs`。它不是 Browser Agent，不做 autonomous planning，不调用真实 OpenClaw，不执行真实平台动作。

## Phase 27 Customer Machine Worker Bootstrap

状态：生产基础 / 客户机 Worker Bootstrap。Phase 27 新增本地 `worker_client` 包，让 Windows、Mac 或真实客户机可以注册为 Browser Worker，并暴露与 Docker `browser-worker` 服务兼容的 Worker Runtime 协议。本阶段不实现 OpenClaw、真实社媒平台自动化、自动登录、Cookie 注入、代理池、指纹绕过、验证码处理或 TikTok / YouTube / X 自动化。

本地文件与命令：

- `worker_client`
- `worker_client/worker_config.example.yaml`
- `worker_client/worker_config.yaml`
- `worker_client/worker_state.json`
- `python -m worker_client.cli register`
- `python -m worker_client.cli heartbeat`
- `python -m worker_client.cli serve`
- `python -m worker_client.cli start`

`registration flow` 会读取 `worker_config.yaml`，调用 `POST /api/v1/browser-workers/register`，一次性接收明文 `worker_secret`，并把 `worker_id` 与 `worker_secret` 保存到客户机本地 `worker_state.json`。`heartbeat flow` 会读取 `worker_state.json`，调用 `POST /api/v1/browser-workers/{worker_id}/heartbeat`，并发送 `X-Worker-Secret` 与 Phase 26 签名请求头。`local worker runtime` 由 `serve` 启动，兼容以下 Worker API：

- `GET /health`
- `POST /sessions`
- `POST /actions`
- `POST /sessions/{session_id}/close`
- `GET /ui-access/capabilities`

### `worker_config.yaml` 示例

```yaml
server_url: http://localhost:8000
worker_name: local-windows-worker-1
worker_type: playwright
workspace_id: demo-workspace
worker_secret: null
worker_base_url: http://localhost:9100
runtime_host: 0.0.0.0
runtime_port: 9100
state_path: worker_client/worker_state.json
heartbeat_interval_seconds: 30
capabilities:
  browser: chromium
  screenshot: true
  page_content: true
  persistent_profile: true
allowed_domains:
  - example.com
  - localhost
  - 127.0.0.1
```

安全说明：

- `worker_state.json` 已加入 `.gitignore`，只能保存在客户机本地。
- `worker_secret` 不允许写入日志或文档。
- AI Server 现有 Worker 注册、心跳、Policy 与 Audit API 仍是协议真实入口。

## Phase 26 Browser Worker Security & Access Control API

状态：生产基础 / security foundation。Phase 26 为 Browser Worker、UI Access、Browser Profile 和 Browser Action 增加基础安全控制层，但不实现真实平台账号安全、自动登录、Cookie 注入、代理池、指纹绕过、验证码处理或 TikTok / YouTube / X 自动化。

必需 Headers：业务 API 需要 `X-Workspace-Id`，建议传 `X-User-Id`。Worker runtime 签名请求使用 `X-Worker-Signature`、`X-Worker-Timestamp`、`X-Worker-Nonce` 和 body hash。`BROWSER_WORKER_AUTH_ENABLED=True`，`BROWSER_WORKER_AUTH_STRICT=False` 为当前默认值。

核心配置：

- `BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1`
- `BROWSER_BLOCKED_DOMAINS=`
- `BROWSER_ALLOW_EXTERNAL_DOMAINS=False`
- `BROWSER_WORKER_AUTH_ENABLED=True`
- `BROWSER_WORKER_AUTH_STRICT=False`

核心表、字段与服务：

- `browser_workers.worker_secret_hash`
- `browser_workers.api_key_hash`
- `browser_workers.last_auth_at`
- `browser_workers.auth_status`
- `browser_workers.allowed_actions`
- `browser_workers.allowed_domains`
- `worker_secret`
- `BrowserWorkerAuthService`
- `BrowserActionPolicyService`
- `BrowserSecurityAuditLog`
- `browser_security_audit_logs`
- `browser_ui_access_sessions.scopes`
- `browser_ui_access_sessions.one_time`
- `browser_ui_access_sessions.used_at`
- `browser_ui_access_sessions.revoked_reason`
- `browser_ui_access_sessions.client_ip`
- `browser_ui_access_sessions.user_agent`

### POST `/api/v1/browser-workers/{worker_id}/rotate-secret`

轮换 worker secret。明文 `worker_secret` 只在本次响应返回一次，数据库只保存 `worker_secret_hash`。

响应示例：

```json
{
  "id": "WORKER_ID",
  "auth_status": "unverified",
  "worker_secret": "PLAINTEXT_RETURNED_ONCE",
  "allowed_actions": ["navigate", "click", "type_text", "scroll", "screenshot", "get_page_content"],
  "allowed_domains": ["example.com", "localhost", "127.0.0.1"]
}
```

### POST `/api/v1/browser-workers/{worker_id}/revoke`

撤销 worker auth，状态变为 `revoked`，worker 也会标记为 `offline`。

请求示例：

```json
{
  "reason": "manual revoke"
}
```

### GET `/api/v1/browser/security/audit-logs`

读取当前 workspace 的安全审计日志。可用 `event_type` 和 `limit` 查询。审计事件包括 worker registered、worker auth success / failed、UI token created / validated / revoked / expired、action blocked by policy、profile access denied。

响应示例：

```json
{
  "items": [
    {
      "event_type": "action_blocked_by_policy",
      "target_type": "browser_action",
      "success": false,
      "error": "domain_not_allowed:not-allowed.example.org",
      "metadata": {
        "action_type": "navigate"
      }
    }
  ]
}
```

### POST `/api/v1/browser/security/policy/check`

调用 `BrowserActionPolicyService`，校验 action type、target domain、profile access、worker capability 和 UI access scope。

允许示例：

```json
{
  "action_type": "navigate",
  "target": "https://example.com"
}
```

拦截示例：

```json
{
  "action_type": "navigate",
  "target": "https://not-allowed.example.org"
}
```

拦截响应示例：

```json
{
  "allowed": false,
  "reason": "domain_not_allowed:not-allowed.example.org",
  "metadata": {
    "hostname": "not-allowed.example.org"
  }
}
```

### UI Access Scope 扩展

`POST /api/v1/browser/ui-access` 支持：

```json
{
  "browser_session_id": "SESSION_ID",
  "human_control_session_id": "CONTROL_SESSION_ID",
  "scopes": ["view", "control"],
  "one_time": false,
  "metadata": {
    "phase": "26"
  }
}
```

`GET /api/v1/browser/ui-access/{access_session_id}/validate?token=TOKEN&scope=view` 会校验 token、scope、过期时间、one-time 使用状态、`used_at`、`revoked_reason`、`client_ip` 和 `user_agent` 记录。

## Phase 25 Browser Worker UI Access Placeholder API

状态：生产基础 / placeholder。Phase 25 为未来人工远程接管浏览器 UI 建立 token 化占位访问层。当前不实现真实 VNC、noVNC、Chrome DevTools 远程 UI、浏览器实时画面、平台登录、验证码或平台自动化。

必需 Headers：`X-Workspace-Id`；建议提供 `X-User-Id`。所有 UI access API 都按 workspace 隔离。

核心数据与服务：

- `browser_ui_access_sessions`
- `BrowserUIAccessService`
- `access_token_hash`
- `remote_control_url`
- `live_view_url`
- `devtools_url`
- `BROWSER_UI_ACCESS_TIMEOUT_SECONDS=900`
- `browser_tool` action：`create_ui_access`、`revoke_ui_access`

### POST `/api/v1/browser/ui-access`

创建 UI Access Placeholder session。明文 `access_token` 只在本次响应返回一次，数据库只保存 `access_token_hash`。

请求：

```json
{
  "browser_session_id": "SESSION_ID",
  "human_control_session_id": "CONTROL_SESSION_ID",
  "metadata": {
    "phase": "25"
  }
}
```

响应：

```json
{
  "id": "ACCESS_SESSION_ID",
  "browser_session_id": "SESSION_ID",
  "human_control_session_id": "CONTROL_SESSION_ID",
  "remote_control_url": "http://localhost:8000/ui/browser-control/ACCESS_SESSION_ID",
  "live_view_url": "http://localhost:8000/ui/browser-live/ACCESS_SESSION_ID",
  "devtools_url": null,
  "status": "active",
  "access_token": "PLAINTEXT_RETURNED_ONCE",
  "metadata": {
    "placeholder": true,
    "vnc": false,
    "novnc": false,
    "devtools": false
  }
}
```

### GET `/api/v1/browser/ui-access/{access_session_id}`

读取单个 UI Access Placeholder session。`access_token` 永远为 `null`。

### POST `/api/v1/browser/ui-access/{access_session_id}/revoke`

撤销 UI access session，状态变为 `revoked`。

### POST `/api/v1/browser/ui-access/expire`

过期当前 workspace 中已超时的 UI access sessions。

### GET `/api/v1/browser/ui-access/{access_session_id}/validate`

校验 token：

```text
/api/v1/browser/ui-access/ACCESS_SESSION_ID/validate?token=TOKEN
```

响应：

```json
{
  "access_session_id": "ACCESS_SESSION_ID",
  "valid": true,
  "status": "active",
  "reason": null,
  "placeholder": true
}
```

### Worker UI Access Capabilities

- `GET /api/v1/browser-worker-runtime/ui-access/capabilities`
- `GET http://localhost:9100/ui-access/capabilities`

响应：

```json
{
  "vnc": false,
  "novnc": false,
  "devtools": false,
  "placeholder": true
}
```

边界：Phase 25 只建立 placeholder URL 和 token plumbing，不实现 VNC、noVNC、DevTools UI、真实远程桌面、实时浏览器画面、平台登录、验证码处理、Cookie 注入、代理池、指纹绕过、TikTok / YouTube / X 或真实平台自动化。

## Phase 24 Human-in-the-loop Browser Control API

状态：生产基础。Phase 24 建立人工接管浏览器控制协议，让自动化可以暂停、等待人工处理、恢复执行。当前只做 metadata-level 接管，不实现 VNC、noVNC、DevTools 远程 UI、平台登录或验证码处理。

必需 Headers：`X-Workspace-Id`，建议同时传 `X-User-Id`。所有 human control API 都按 workspace 隔离。

核心表与字段：

- `browser_human_control_sessions`
- `browser_human_control_events`
- `browser_sessions.human_control_status`
- `browser_sessions.human_control_session_id`
- `browser_sessions.paused_at`
- `browser_sessions.resumed_at`

核心服务与配置：

- `BrowserHumanControlService`
- `BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS=900`
- `browser_tool` action：`request_human_control`、`complete_human_control`

### POST `/api/v1/browser/human-control/request`

请求人工接管，并把对应 `browser_sessions.status` 标记为 `paused`。

请求：

```json
{
  "browser_session_id": "SESSION_ID",
  "reason": "manual login required",
  "metadata": {
    "phase": "24"
  }
}
```

响应：

```json
{
  "id": "CONTROL_SESSION_ID",
  "browser_session_id": "SESSION_ID",
  "status": "requested",
  "reason": "manual login required",
  "requested_by": "demo-user",
  "expires_at": "2026-05-13T12:15:00Z"
}
```

### POST `/api/v1/browser/human-control/{control_session_id}/approve`

批准人工接管请求，写入 `approved` event。

### POST `/api/v1/browser/human-control/{control_session_id}/start`

启动人工接管窗口，状态变为 `active`，并通知 worker metadata-level `/human-control/start`。

### POST `/api/v1/browser/human-control/{control_session_id}/complete`

完成人工接管，恢复 session 为 `active` 并写入 `resumed_at`。

请求：

```json
{
  "note": "manual step completed",
  "metadata": {
    "operator": "human"
  }
}
```

### POST `/api/v1/browser/human-control/{control_session_id}/cancel`

取消人工接管，恢复 session 为 `active`。

### GET `/api/v1/browser/human-control`

列出当前 workspace 的 human control sessions，可用 `status` 过滤。

### GET `/api/v1/browser/human-control/{control_session_id}`

读取单个 human control session。

### GET `/api/v1/browser/human-control/{control_session_id}/events`

返回事件流。事件类型包括 `requested`、`approved`、`started`、`completed`、`cancelled`、`expired`、`timeout`、`note`。

### Worker Runtime Human Control

API 进程内 mock worker runtime 和独立 `browser-worker` 都暴露 metadata-level 接口：

- `POST /api/v1/browser-worker-runtime/human-control/start`
- `POST /api/v1/browser-worker-runtime/human-control/complete`
- `GET /api/v1/browser-worker-runtime/human-control/status/{session_id}`

独立 worker 对应路径：

- `POST /human-control/start`
- `POST /human-control/complete`
- `GET /human-control/status/{session_id}`

边界：Phase 24 不支持 VNC / noVNC / DevTools 真实远程 UI，不支持自动登录、Cookie 注入、代理池、指纹绕过、验证码自动化、TikTok / YouTube / X 或真实平台自动化。

所有文档、RAG、任务、工具、Memory、Multi-Agent 查询都必须按 `workspace_id` 隔离，不允许默认查全库。

## 状态说明

- 生产基础：当前后端基础能力，可用于开发与本地验证。
- 实验性：接口存在，但仍是评估、调试或预留性质。
- 规划中：不列为当前可用 API。

## Health / Runtime

### GET `/api/v1/health`

状态：生产基础。

### GET `/api/v1/llm/health`

状态：生产基础。返回当前 LLM provider、model、reachable、error。

### POST `/api/v1/llm/test`

状态：生产基础。默认 `LLM_PROVIDER=mock`。

### GET `/api/v1/rag/embedding/health`

状态：生产基础。返回当前 embedding provider、model、reachable、dimension、error。

### GET `/api/v1/reranker/health`

状态：生产基础。当前默认 `RERANKER_PROVIDER=mock`。

## RAG

### POST `/api/v1/rag/ingest`

状态：生产基础。

Request：

```json
{
  "text": "AI 自动化运营系统支持任务调度、RAG 检索、内容生成和 Agent 执行。",
  "metadata": {"source": "swagger"},
  "source_id": "phase15-doc-001",
  "source_name": "Phase 15 文档",
  "source_type": "text",
  "workspace_id": "demo-workspace",
  "user_id": "demo-user",
  "chunk_size": 300,
  "chunk_overlap": 50,
  "collection_name": "phase15_demo"
}
```

### POST `/api/v1/rag/search`

状态：生产基础。

支持 `search_mode`：

- `dense`
- `keyword`
- `hybrid`

Request：

```json
{
  "query": "Multi-Agent 如何执行固定链路？",
  "collection_name": "phase15_demo",
  "workspace_id": "demo-workspace",
  "source_id": "phase15-doc-001",
  "search_mode": "hybrid",
  "dense_top_k": 20,
  "keyword_top_k": 20,
  "final_top_k": 5
}
```

Response 字段包含：

- `similarity_score`
- `raw_score`
- `dense_score`
- `keyword_score`
- `hybrid_score`

### POST `/api/v1/rag/debug`

状态：生产基础。返回 query embedding 维度、collection_name、retrieved_chunks 与 scores。

### POST `/api/v1/agentic-rag/query`

状态：生产基础。

`debug=true` 时 trace 包含：

- `retrieval_before_rerank`
- `retrieval_after_rerank`
- `reranked_chunks`
- `rerank_scores`
- `search_mode`
- `dense_results_count`
- `keyword_results_count`
- `merged_results_count`
- `final_results_count`
- `dense_scores`
- `keyword_scores`
- `hybrid_scores`
- `session_id`
- `recent_messages_count`
- `retrieved_memories_count`
- `memory_trace`

## File Upload

### POST `/api/v1/files/upload`

状态：生产基础。

Content-Type：`multipart/form-data`

支持文件类型：PDF、DOCX、TXT、MD、CSV。当前不支持 PPTX、XLSX、OCR、图片解析。

Request form fields：

- `file`
- `collection_name`
- `source_name`
- `source_type`
- `metadata`
- `chunk_size`
- `chunk_overlap`
- `duplicate_strategy`: `skip` 或 `force_reingest`

文件 metadata 会记录 `filename`、`file_type`、`file_size`、`file_hash`、`ingest_status`、`ingest_error`、`chunk_count`。

## Tasks / Observability

### GET `/api/v1/tasks`

状态：生产基础。支持 `status` 过滤。

### POST `/api/v1/tasks`

状态：生产基础。

### POST `/api/v1/tasks/{task_id}/cancel`

状态：生产基础。将任务标记为 `cancelled`。

### POST `/api/v1/tasks/{task_id}/retry`

状态：生产基础。失败任务可重新进入 `retry` / `pending` 流程。

### GET `/api/v1/tasks/{task_id}/events`

状态：生产基础。读取 `task_events`。

### GET `/api/v1/tasks/{task_id}/logs`

状态：生产基础。读取 `task_logs`。

### GET `/api/v1/observability/summary`

状态：生产基础。

Response：

```json
{
  "pending_count": 1,
  "running_count": 0,
  "failed_count": 0,
  "completed_count": 3,
  "cancelled_count": 1,
  "timeout_count": 0,
  "avg_duration_ms": 128.5
}
```

任务状态支持：`pending`、`running`、`retry`、`failed`、`completed`、`cancelled`、`timeout`。任务执行记录 `duration_ms`。

## Documents

### GET `/api/v1/documents`

状态：生产基础。

### GET `/api/v1/documents/{document_id}`

状态：生产基础。

### DELETE `/api/v1/documents/by-source/{source_id}`

状态：生产基础。逻辑删除 document/chunk，并过滤 deleted/outdated 内容。

### POST `/api/v1/documents/reingest`

状态：生产基础。按 source_id 创建新 version，旧 document 标记为 outdated。

## Workspaces / Users / API Keys

### POST `/api/v1/workspaces`

状态：生产基础。

### GET `/api/v1/workspaces`

状态：生产基础。

### POST `/api/v1/users`

状态：生产基础。

### GET `/api/v1/users`

状态：生产基础。

### POST `/api/v1/api-keys`

状态：生产基础，不是完整 auth。明文 key 只返回一次，数据库只保存 hash。

## RAG Eval

状态：实验性基础。

### POST `/api/v1/rag/eval/runs`

### GET `/api/v1/rag/eval/runs`

### POST `/api/v1/rag/eval/runs/{run_id}/items`

### GET `/api/v1/rag/eval/runs/{run_id}/items`

### PATCH `/api/v1/rag/eval/items/{item_id}/score`

Eval 支持 `retrieval only` 与 `retrieval + rerank` 对比记录，但尚未实现自动指标计算。

## Tool Calling

状态：生产基础。当前仅实现内部 Tool Framework 和手动工具调用；`openclaw_tool` 是 Phase 28 mock/placeholder adapter，不包含 Browser Agent、真实 OpenClaw、Playwright、Selenium、autonomous planner 或 ReAct。

数据表：

- `tool_call_logs`

字段：

- `tool_name`
- `tool_input`
- `tool_output`
- `success`
- `latency_ms`

### GET `/api/v1/tools`

返回当前 `ToolRegistry` 中的 builtin tools。

### GET `/api/v1/tools/{tool_name}`

返回单个 tool 的描述、input_schema、output_schema、enabled 状态和 permission scopes。

### POST `/api/v1/tools/{tool_name}/execute`

Request：

```json
{
  "input": {
    "query": "AI 自动化运营",
    "collection_name": "phase15_demo",
    "search_mode": "hybrid",
    "final_top_k": 3
  }
}
```

Builtin tools：

- `rag_search_tool`
- `file_search_tool`
- `create_task_tool`
- `get_task_status_tool`
- `current_runtime_tool`

### GET `/api/v1/tool-calls`

支持按 `tool_name`、`agent_name`、`success`、`limit` 查询。

## Memory

状态：生产基础。当前是 Memory Foundation，不是 vector memory、graph memory 或 autonomous memory planning。

数据表：

- `conversation_sessions`
- `conversation_messages`
- `agent_memories`
- `memory_operation_logs`

### POST `/api/v1/memory/sessions`

Request：

```json
{
  "title": "Phase 15 session",
  "metadata": {"source": "swagger"}
}
```

### GET `/api/v1/memory/sessions`

### GET `/api/v1/memory/sessions/{session_id}`

### POST `/api/v1/memory/messages`

Request：

```json
{
  "session_id": "uuid",
  "role": "user",
  "content": "请记住我关注 Multi-Agent handoff_trace。",
  "metadata": {"turn": 1}
}
```

`role` 支持：`system`、`user`、`assistant`、`tool`。

### GET `/api/v1/memory/messages/{session_id}`

### POST `/api/v1/memory/memories`

Request：

```json
{
  "agent_name": "MultiAgentService",
  "memory_type": "long_term",
  "content": "用户关注 agent_handoffs 和 handoff_trace。",
  "metadata": {"phase": "15"},
  "importance_score": 0.8
}
```

`memory_type` 支持：`short_term`、`long_term`、`task_memory`、`retrieval_memory`。

### GET `/api/v1/memory/memories`

### DELETE `/api/v1/memory/memories/{memory_id}`

## Multi-Agent

状态：生产基础。Phase 15 当前只实现固定链路 Multi-Agent Foundation，不实现 autonomous planner、ReAct、Browser Agent、Playwright、OpenClaw、Selenium 或外部平台自动化。

数据表：

- `agent_runs`
- `agent_messages`
- `agent_handoffs`

AgentRegistry 当前注册：

- `content_planner`
- `rag_agent`
- `content_agent`
- `review_agent`
- `runtime_agent`
- `tool_agent`

### GET `/api/v1/agents/registry`

返回当前可用 Agent 列表。

### POST `/api/v1/multi-agent/runs`

Request：

```json
{
  "root_agent": "content_planner",
  "session_id": null,
  "input": {
    "topic": "AI 自动化运营",
    "platform": "tiktok",
    "style": "专业简洁",
    "query": "ping",
    "collection_name": "phase15_multi_agent_demo"
  }
}
```

### GET `/api/v1/multi-agent/runs`

Query 参数：`status`、`limit`。

### GET `/api/v1/multi-agent/runs/{run_id}`

返回当前 workspace 下的单个 `agent_runs` 记录。

### POST `/api/v1/multi-agent/runs/{run_id}/execute-chain`

固定 Agent Chain：

```text
content_planner -> rag_agent -> content_agent -> review_agent
```

Request：

```json
{
  "chain_name": "content_planning",
  "input": {
    "topic": "AI 自动化运营",
    "platform": "tiktok",
    "style": "专业简洁",
    "query": "ping"
  }
}
```

Response：

```json
{
  "run": {
    "id": "uuid",
    "status": "completed",
    "duration_ms": 120
  },
  "agents_involved": ["content_planner", "rag_agent", "content_agent", "review_agent"],
  "success": true,
  "error": null,
  "duration_ms": 120,
  "messages": [],
  "handoffs": []
}
```

Run output 会保存 `agents_involved`、`handoff_trace` 和各 Agent 的中间结果。

### GET `/api/v1/multi-agent/runs/{run_id}/messages`

返回该 run 的 `agent_messages`。

### GET `/api/v1/multi-agent/runs/{run_id}/handoffs`

返回该 run 的 `agent_handoffs`。

## Planning

状态：生产基础。Phase 16 当前只实现 rule-based Agent Planning Foundation，不实现 autonomous AGI planner、tree-of-thought、recursive planning、无限 Agent loop、ReAct、Browser Agent、Playwright、OpenClaw、Selenium 或外部平台自动化。

Required headers：`X-Workspace-Id`，可选 `X-User-Id`

Workspace：必须。

数据表：

- `plans`
- `plan_steps`
- `plan_reviews`

### POST `/api/v1/plans`

Request：

```json
{
  "root_goal": "生成 AI 自动化运营 TikTok 内容",
  "session_id": null,
  "planner_agent": "simple_planner",
  "metadata": {
    "query": "ping",
    "platform": "tiktok",
    "style": "专业简洁"
  },
  "auto_create_steps": true
}
```

Response 包含 `plans` 字段：`id`、`workspace_id`、`session_id`、`root_goal`、`planner_agent`、`status`、`metadata`、`created_at`、`updated_at`。

### GET `/api/v1/plans`

Query 参数：

- `status`
- `limit`

### GET `/api/v1/plans/{plan_id}`

返回当前 workspace 下的单个 plan。

### POST `/api/v1/plans/{plan_id}/execute`

Request：

```json
{
  "input": {
    "query": "ping"
  }
}
```

Response：

```json
{
  "plan": {
    "id": "uuid",
    "status": "completed"
  },
  "success": true,
  "status": "completed",
  "step_outputs": {},
  "review_result": "approved",
  "duration_ms": 120,
  "memory_trace": [],
  "steps": [],
  "reviews": []
}
```

Plan Execution Flow：`SimplePlannerAgent -> PlanStep -> AgentRegistry or ToolRegistry -> PlanReview`。

`PlanStep` 记录 `status`、`duration_ms`、`error`、`input_payload`、`output_payload`。

`PlanReview` 记录 `reviewer_agent`、`review_result`、`score`、`notes`。

### POST `/api/v1/plans/{plan_id}/cancel`

将 plan 标记为 `cancelled`，并跳过 pending steps。

### GET `/api/v1/plans/{plan_id}/steps`

返回该 plan 的 `plan_steps`。

### GET `/api/v1/plans/{plan_id}/reviews`

## Browser Adapter

状态：生产基础。Phase 17 只实现 Browser Automation Adapter Foundation，不启动真实浏览器，不接 Playwright / Selenium / OpenClaw，不接 TikTok / YouTube / X。

Required headers：`X-Workspace-Id`，可选 `X-User-Id`

Workspace：必须。所有 `browser_sessions`、`browser_actions`、`browser_action_logs` 查询都按 workspace 隔离。

当前 provider：

- `BROWSER_PROVIDER=mock`
- `BrowserProvider`
- `MockBrowserProvider`
- `PlaywrightBrowserProvider` placeholder only

数据表：

- `browser_sessions`
- `browser_actions`
- `browser_action_logs`

### POST `/api/v1/browser/sessions`

Request：

```json
{
  "metadata": {
    "purpose": "swagger"
  }
}
```

### GET `/api/v1/browser/sessions`

Query 参数：`status`、`limit`。

### POST `/api/v1/browser/actions`

Request：

```json
{
  "session_id": "uuid",
  "action_type": "navigate",
  "target": "https://example.com",
  "input_payload": {
    "wait": "none"
  }
}
```

`action_type` 支持：`navigate`、`click`、`type_text`、`scroll`、`screenshot`、`get_page_content`。

Response 包含 `duration_ms`、`status`、`error`、`output_payload`。

### GET `/api/v1/browser/actions/{session_id}`

返回当前 workspace 下指定 session 的 `browser_actions`。

### GET `/api/v1/browser/logs/{session_id}`

返回当前 workspace 下指定 session 的 `browser_action_logs`。

### `browser_tool`

`browser_tool` 通过 Tool API 调用：

```json
{
  "input": {
    "action_type": "navigate",
    "target": "https://example.com",
    "input_payload": {
      "wait": "none"
    }
  }
}
```

工具只支持 `navigate`、`click`、`type_text`、`screenshot`，全部走 `MockBrowserProvider`。

## Phase 18 Browser API Update

状态：生产基础。Phase 18 新增 `PlaywrightLocalProvider`，provider name 为 `playwright_local`，用于本地 headless Chromium 基础执行验证。默认仍是 `BROWSER_PROVIDER=mock`。

Workspace：必须。所有 session、action、screenshot、log 都按 `X-Workspace-Id` 隔离。

Runtime 配置：

- `BROWSER_PROVIDER=mock`
- `BROWSER_PROVIDER=playwright_local`
- `BROWSER_TIMEOUT_SECONDS=30.0`
- `BROWSER_HEADLESS=True`
- `BROWSER_TYPE=chromium`
- `BROWSER_VIEWPORT_WIDTH=1280`
- `BROWSER_VIEWPORT_HEIGHT=720`
- `BROWSER_SCREENSHOT_DIR=screenshots`

新增/扩展字段：

- `browser_id`
- `page_id`
- `provider_session_metadata`
- `selector`
- `target_url`
- `screenshot_path`
- `page_title`
- `get_page_content`

### POST `/api/v1/browser/actions`

请求 JSON：

```json
{
  "session_id": "uuid",
  "action_type": "navigate",
  "target": "https://example.com",
  "selector": null,
  "text": null,
  "screenshot_name": null,
  "input_payload": {}
}
```

支持 action_type：

- `navigate`
- `click`
- `type_text`
- `scroll`
- `screenshot`
- `get_page_content`

响应 JSON 核心字段：

```json
{
  "id": "uuid",
  "workspace_id": "demo-workspace",
  "session_id": "uuid",
  "action_type": "screenshot",
  "target": null,
  "selector": null,
  "target_url": "https://example.com",
  "screenshot_path": "screenshots/demo-workspace/session/example-home.png",
  "page_title": "Example Domain",
  "status": "completed",
  "error": null,
  "duration_ms": 120
}
```

### GET `/api/v1/browser/screenshot/{session_id}/{filename}`

返回当前 workspace/session 下的 PNG 截图文件。`filename` 必须是安全文件名并以 `.png` 结尾。

安全边界：

- 允许：`example.com`、本地测试页面、静态 `file://` 页面。
- 禁止：TikTok / YouTube / X、自动登录、Cookie 注入、指纹绕过、代理池、验证码自动化、OCR、视觉 AI、autonomous browser planning、Browser Worker、真实平台自动化。

## Phase 19 Remote Browser Worker API

状态：生产基础。Phase 19 只实现 Remote Browser Worker Foundation：`RemoteBrowserProvider`、`BrowserWorkerClient`、Worker Registration、Worker Heartbeat、Worker Runtime Mock。当前不部署真实外部 worker。

Workspace：`/api/v1/browser-workers/*` 必须带 `X-Workspace-Id`；mock runtime `/api/v1/browser-worker-runtime/*` 是 worker 协议端点，不要求 workspace header。

Runtime 配置：

- `BROWSER_PROVIDER=remote`
- `BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30.0`
- `BROWSER_WORKER_RETRY_COUNT=2`

数据库表：

- `browser_workers`
- `browser_worker_sessions`
- `browser_worker_actions`

核心字段：

- `remote_session_id`
- `remote_action_id`
- `worker_id`
- `worker_name`
- `base_url`
- `capabilities`

### POST `/api/v1/browser-workers/register`

请求：

```json
{
  "worker_name": "local-worker-1",
  "worker_type": "playwright",
  "base_url": "http://localhost:8000/api/v1/browser-worker-runtime",
  "capabilities": {
    "browser": "chromium",
    "screenshot": true,
    "page_content": true
  },
  "metadata": {}
}
```

响应包含 `id`、`workspace_id`、`worker_name`、`worker_type`、`base_url`、`status`、`capabilities`、`last_heartbeat_at`。

### POST `/api/v1/browser-workers/{worker_id}/heartbeat`

请求：

```json
{
  "status": "online",
  "capabilities": {
    "browser": "chromium",
    "screenshot": true
  },
  "metadata": {}
}
```

`status` 支持：`online`、`offline`、`busy`、`error`。

### GET `/api/v1/browser-workers`

支持 query：

- `status`
- `worker_type`
- `limit`

### Mock Worker Runtime

```http
GET /api/v1/browser-worker-runtime/health
POST /api/v1/browser-worker-runtime/sessions
POST /api/v1/browser-worker-runtime/actions
POST /api/v1/browser-worker-runtime/sessions/{session_id}/close
```

Mock action 响应示例：

```json
{
  "success": true,
  "remote_action_id": "mock-remote-action-id",
  "message": "mock remote browser action success",
  "data": {
    "remote_session_id": "mock-remote-session-id",
    "action_type": "navigate",
    "target_url": "https://example.com",
    "page_title": "Mock Remote Browser"
  },
  "error": null
}
```

边界：当前 Remote Worker 只是协议基础和同项目 mock runtime，不接 TikTok / YouTube / X，不做账号登录、自动发布、代理池、指纹绕过、验证码或 autonomous browser agent。

返回该 plan 的 `plan_reviews`。

## Phase 20 Real Browser Worker Service

状态：生产基础。Phase 20 把 Phase 19 的 mock worker runtime 升级为独立 `browser-worker` 服务，但仍只允许安全测试页面，不做真实平台自动化。

API Server 调用链路：

```text
API Server
-> RemoteBrowserProvider
-> BrowserWorkerClient
-> http://browser-worker:9100
-> worker/main.py
-> worker/browser_worker/playwright_runtime.py
-> Playwright Chromium
```

运行配置：

- `BROWSER_PROVIDER=remote`
- `BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100`
- `BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30.0`
- `BROWSER_WORKER_RETRY_COUNT=2`
- `WORKER_TIMEOUT_SECONDS=30`
- `WORKER_SCREENSHOT_DIR=worker/screenshots`

Docker 服务：

- `browser-worker`
- 端口：`9100`
- 截图目录：`worker/screenshots/{workspace_id}/{remote_session_id}/{filename}.png`

Standalone worker endpoints：

```http
GET http://localhost:9100/health
POST http://localhost:9100/sessions
POST http://localhost:9100/actions
POST http://localhost:9100/sessions/{session_id}/close
```

Worker health response 示例：

```json
{
  "success": true,
  "worker_type": "playwright",
  "reachable": true,
  "capabilities": {
    "browser": "chromium",
    "headless": true,
    "screenshot": true,
    "page_content": true
  },
  "message": "browser worker reachable",
  "error": null
}
```

## Phase 21 Browser Worker Reliability API

状态：生产基础。Phase 21 在 Remote Browser Worker 和独立 `browser-worker` 服务上增加可靠性、容量、恢复和清理能力。所有 `/api/v1/browser-workers/*` 与 `/api/v1/browser/screenshots/cleanup` 都要求 `X-Workspace-Id`，`X-User-Id` 可选。

关键服务与字段：

- `BrowserWorkerHealthService`
- `BrowserWorkerSelector`
- `BrowserSessionCleanupService`
- `ScreenshotCleanupService`
- `max_sessions`
- `active_sessions`
- `max_actions_per_minute`
- `current_load`
- `priority`
- `error_message`
- `last_seen`
- `retry_count`
- `max_retries`
- `BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS`
- `BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS`
- `BROWSER_SESSION_TIMEOUT_SECONDS`
- `BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS`
- `BROWSER_ACTION_TIMEOUT_SECONDS`
- `BROWSER_ACTION_RETRY_COUNT`
- `BROWSER_ACTION_RETRY_BACKOFF_SECONDS`
- `SCREENSHOT_RETENTION_DAYS`

### POST `/api/v1/browser-workers/register`

Phase 21 扩展请求：

```json
{
  "worker_name": "local-worker-1",
  "worker_type": "playwright",
  "base_url": "http://browser-worker:9100",
  "capabilities": {
    "browser": "chromium",
    "screenshot": true,
    "page_content": true
  },
  "metadata": {},
  "max_sessions": 2,
  "max_actions_per_minute": 60,
  "priority": 100
}
```

响应包含：

```json
{
  "id": "worker-id",
  "workspace_id": "demo-workspace",
  "worker_name": "local-worker-1",
  "worker_type": "playwright",
  "base_url": "http://browser-worker:9100",
  "status": "online",
  "capabilities": {
    "browser": "chromium"
  },
  "last_seen": "2026-05-13T10:00:00",
  "max_sessions": 2,
  "active_sessions": 0,
  "max_actions_per_minute": 60,
  "current_load": 0,
  "priority": 100,
  "error_message": null,
  "metadata": {}
}
```

### GET `/api/v1/browser-workers/health/summary`

返回 worker 健康摘要，并触发 stale worker 检测：

```json
{
  "workspace_id": "demo-workspace",
  "total_workers": 2,
  "online_workers": 1,
  "offline_workers": 1,
  "busy_workers": 0,
  "error_workers": 0,
  "stale_workers": 1,
  "available_workers": 1
}
```

### GET `/api/v1/browser-workers/available`

返回 `BrowserWorkerSelector` 可分配 worker，默认按 `current_load`、`active_sessions`、`priority` 排序：

```json
{
  "items": [
    {
      "id": "worker-id",
      "worker_name": "local-worker-1",
      "status": "online",
      "active_sessions": 0,
      "max_sessions": 2,
      "current_load": 0,
      "priority": 100
    }
  ]
}
```

### POST `/api/v1/browser-workers/{worker_id}/mark-offline`

手动将 worker 标记为 offline：

```json
{
  "error_message": "manual maintenance"
}
```

### POST `/api/v1/browser-workers/cleanup-sessions`

手动执行 session cleanup：

```json
{
  "session_timeout_seconds": 1800,
  "close_remote": false
}
```

响应：

```json
{
  "workspace_id": "demo-workspace",
  "stale_sessions": 1,
  "offline_worker_sessions": 0,
  "closed_sessions": 1,
  "failed_sessions": 0,
  "log_count": 1
}
```

### GET `/api/v1/browser-workers/{worker_id}/sessions`

返回某个 worker 关联的 sessions：

```json
{
  "items": [
    {
      "id": "worker-session-id",
      "workspace_id": "demo-workspace",
      "worker_id": "worker-id",
      "remote_session_id": "remote-session-id",
      "local_browser_session_id": "browser-session-id",
      "status": "active",
      "metadata": {}
    }
  ]
}
```

### POST `/api/v1/browser/screenshots/cleanup`

按 workspace 清理截图。默认 dry-run，不会实际删除：

```json
{
  "older_than_days": 7,
  "dry_run": true
}
```

响应：

```json
{
  "workspace_id": "demo-workspace",
  "root_dir": "screenshots;worker/screenshots",
  "older_than_days": 7,
  "dry_run": true,
  "matched_files": 2,
  "deleted_files": 0,
  "bytes_freed": 0
}
```

边界：Phase 21 不提供 TikTok / YouTube / X 自动化、登录、Cookie 注入、代理池、指纹绕过、验证码、OCR、视觉 AI、OpenClaw、真实平台自动化或 autonomous browser planning。

## Phase 22 Persistent Browser Profile API

状态：生产基础。Phase 22 建立持久化 Browser Profile Foundation，用于保存浏览器状态并支持长期 session / 人工接管 / 后续账号环境隔离。当前不做登录、Cookie 注入、指纹配置或真实平台自动化。

核心对象与字段：

- `browser_profiles`
- `BrowserProfileService`
- `profile_id`
- `profile_path`
- `persistent_context_enabled`
- `locked_by_session_id`
- `locked_at`
- `last_used_at`
- `launch_persistent_context`
- `BROWSER_PROFILE_ROOT`
- `WORKER_PROFILE_DIR`

### POST `/api/v1/browser/profiles`

请求：

```json
{
  "profile_name": "demo-profile",
  "profile_type": "persistent",
  "provider": "remote",
  "metadata": {
    "purpose": "manual takeover preparation"
  }
}
```

响应：

```json
{
  "id": "profile-id",
  "workspace_id": "demo-workspace",
  "user_id": "demo-user",
  "profile_name": "demo-profile",
  "profile_type": "persistent",
  "provider": "remote",
  "profile_path": "worker/profiles/demo-workspace/profile-id",
  "status": "available",
  "locked_by_session_id": null,
  "locked_at": null,
  "last_used_at": null,
  "metadata": {},
  "created_at": "2026-05-13T10:00:00Z",
  "updated_at": "2026-05-13T10:00:00Z"
}
```

### GET `/api/v1/browser/profiles`

支持 query：`status`、`limit`。

### GET `/api/v1/browser/profiles/{profile_id}`

返回单个 profile，自动按 `X-Workspace-Id` 隔离。

### POST `/api/v1/browser/profiles/{profile_id}/lock`

手动锁定 profile。通常由 session 创建流程自动执行。

```json
{
  "session_id": "browser-session-id"
}
```

### POST `/api/v1/browser/profiles/{profile_id}/release`

手动释放 profile。通常由 session close 流程自动执行。

```json
{
  "session_id": "browser-session-id"
}
```

### DELETE `/api/v1/browser/profiles/{profile_id}`

逻辑删除 profile。已 locked 的 profile 不允许删除。

### POST `/api/v1/browser/sessions`

Phase 22 扩展请求：

```json
{
  "profile_id": "profile-id",
  "use_persistent_profile": true,
  "metadata": {
    "scenario": "persistent-context-smoke"
  }
}
```

响应新增字段：

```json
{
  "id": "browser-session-id",
  "profile_id": "profile-id",
  "profile_path": "worker/profiles/demo-workspace/profile-id",
  "persistent_context_enabled": true,
  "status": "active"
}
```

### POST `/api/v1/browser/sessions/{session_id}/close`

关闭 browser session，并释放 profile lock：

```json
{
  "id": "browser-session-id",
  "status": "closed",
  "profile_id": "profile-id",
  "persistent_context_enabled": true
}
```

Persistent Context Flow：

```text
POST /api/v1/browser/profiles
-> POST /api/v1/browser/sessions with profile_id
-> BrowserProfileService.lock_profile
-> RemoteBrowserProvider
-> browser-worker launch_persistent_context
-> worker/profiles/{workspace_id}/{profile_id}
-> POST /api/v1/browser/sessions/{session_id}/close
-> BrowserProfileService.release_profile
```

边界：Phase 22 不支持 TikTok / YouTube / X、登录、Cookie 注入、代理池、指纹绕过、验证码或真实平台自动化。

注册 worker 请求：

```json
{
  "worker_name": "browser-worker",
  "worker_type": "playwright",
  "base_url": "http://browser-worker:9100",
  "capabilities": {
    "browser": "chromium",
    "screenshot": true,
    "page_content": true
  },
  "metadata": {
    "phase": "20"
  }
}
```

Worker action 请求：

```json
{
  "remote_session_id": "worker-session-id",
  "action_type": "screenshot",
  "target": null,
  "input_payload": {
    "screenshot_name": "example-home"
  }
}
```

边界：Phase 20 不支持 TikTok / YouTube / X、自动登录、Cookie 注入、代理池、指纹绕过、验证码、OCR、视觉 AI、OpenClaw、autonomous browser agent 或生产级外部 Worker 集群。

## Phase 23 Browser Profile Health & Recovery API

状态：生产基础。Phase 23 增强 Persistent Browser Profile 的稳定性、恢复能力和生命周期管理。当前仍不做 TikTok / YouTube / X 自动化、账号登录、Cookie 注入、代理池、指纹绕过、验证码或真实平台自动化。

必需 Headers：`X-Workspace-Id`，建议同时传 `X-User-Id`。所有 profile API 都受 Workspace Isolation 约束，不允许跨 workspace 读取、恢复、备份或清理 profile。

核心表与字段：

- `browser_profiles` 新增 `health_status`、`last_health_check_at`、`last_error`、`usage_count`、`corrupted_at`、`backup_path`、`last_backup_at`。
- `browser_profile_usage_logs` 记录 `lock`、`release`、`session_start`、`session_close`、`backup`、`restore`、`recovery`、`cleanup`、`health_check` 等 profile 生命周期事件。
- `health_status` 支持 `healthy`、`warning`、`corrupted`、`stale`、`deleted`。

核心服务：

- `BrowserProfileHealthService`：profile health check、warning/corrupted 标记、stale lock recovery、profile path/runtime 校验、usage count、usage logs、health/summary。
- `BrowserProfileBackupService`：profile backup、list backups、restore backup、backup retention。
- `BrowserProfileCleanupService`：deleted/corrupted/unused profile 目录清理，默认 dry-run。

运行配置：

```text
BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS=1800
BROWSER_PROFILE_BACKUP_ENABLED=True
BROWSER_PROFILE_MAX_BACKUPS=3
BROWSER_PROFILE_UNUSED_DAYS=30
BROWSER_PROFILE_BACKUP_ROOT=worker/profile_backups
```

### GET `/api/v1/browser/profiles/health/summary`

返回当前 workspace 的 profile 健康汇总。

响应示例：

```json
{
  "workspace_id": "demo-workspace",
  "total_profiles": 3,
  "healthy_count": 1,
  "warning_count": 0,
  "corrupted_count": 1,
  "stale_count": 1,
  "deleted_count": 0
}
```

### POST `/api/v1/browser/profiles/{profile_id}/health-check`

检查单个 profile path、lock 状态和生命周期状态。

响应示例：

```json
{
  "healthy": true,
  "health_status": "healthy",
  "error": null,
  "profile": {
    "id": "profile-id",
    "health_status": "healthy",
    "usage_count": 1,
    "last_health_check_at": "2026-05-13T12:00:00Z",
    "last_error": null,
    "backup_path": null,
    "last_backup_at": null
  }
}
```

### POST `/api/v1/browser/profiles/recover-stale-locks`

恢复当前 workspace 中超时、closed/failed session 或 offline/error worker 持有的 stale profile lock。

响应示例：

```json
{
  "workspace_id": "demo-workspace",
  "recovered_count": 1,
  "checked_count": 2,
  "recovered_profile_ids": ["profile-id"]
}
```

### POST `/api/v1/browser/profiles/{profile_id}/backup`

创建 profile zip backup。备份路径：`worker/profile_backups/{workspace_id}/{profile_id}`。

响应示例：

```json
{
  "workspace_id": "demo-workspace",
  "profile_id": "profile-id",
  "backup_path": "worker/profile_backups/demo-workspace/profile-id/profile-20260513T120000Z.zip",
  "success": true,
  "error": null,
  "retained_backups": 1
}
```

### GET `/api/v1/browser/profiles/{profile_id}/backups`

列出 profile 当前保留的 zip backup。

### POST `/api/v1/browser/profiles/{profile_id}/restore`

从指定 backup zip 恢复 profile 文件。

请求示例：

```json
{
  "backup_path": "worker/profile_backups/demo-workspace/profile-id/profile-20260513T120000Z.zip"
}
```

### POST `/api/v1/browser/profiles/cleanup`

清理 deleted/corrupted/unused profile 目录。默认 `dry_run=true`，不会删除文件。

请求示例：

```json
{
  "include_deleted": true,
  "include_corrupted": true,
  "include_unused": true,
  "dry_run": true
}
```

响应示例：

```json
{
  "workspace_id": "demo-workspace",
  "dry_run": true,
  "deleted_profiles": 1,
  "corrupted_profiles": 1,
  "unused_profiles": 0,
  "matched_profiles": 2,
  "removed_paths": 0,
  "bytes_freed": 0
}
```

### GET `/api/v1/browser/profiles/{profile_id}/usage-logs`

返回 profile usage logs。

响应示例：

```json
{
  "items": [
    {
      "id": "usage-log-id",
      "workspace_id": "demo-workspace",
      "profile_id": "profile-id",
      "session_id": "browser-session-id",
      "action": "recovery",
      "success": true,
      "error": null,
      "metadata": {
        "reason": "profile lock exceeded 1800s"
      },
      "created_at": "2026-05-13T12:00:00Z"
    }
  ]
}
```

`BaseOpenClawProvider`

## Phase 29 Worker Client Local Management API

Status: completed runtime foundation. These endpoints are exposed by the customer-machine `worker_client.runtime` service, not by the central AI Server OpenAPI.

Required local host: default `runtime_host: 127.0.0.1`, `runtime_port: 9100`.

- `GET /local/status`
  - response: local runtime state from `worker_client/status.py`, backed by `worker_client/runtime_state/status.json`.
  - fields: `worker_id`, `worker_name`, `workspace_id`, `server_url`, `runtime_running`, `heartbeat_running`, `registered`, `last_heartbeat_at`, `last_error`, `current_status`, `openclaw_enabled`, `browser_enabled`.
- `GET /local/health`
  - response: `Worker Runtime Manager` health with `runtime_running`, `heartbeat_running`, `host`, `port`, and `localhost_only`.
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`
- `GET /local/logs`
  - response: recent lines from `worker_client/logs/worker.log`.

Implementation files:

- `worker_client/runtime_manager.py`
- `worker_client/status.py`
- `worker_client/logging.py`
- `worker_client/local_api_client.py`
- `worker_client/runtime_state/status.json`
- `worker_client/logs/worker.log`

Packaging Scripts:

- `packaging/windows_start_worker.ps1`
- `packaging/mac_start_worker.sh`

Worker Console Foundation:

- `Desktop Runtime Placeholder` exists under `worker_client/desktop/`.
- Current state is `no GUI`; no Electron, no Tauri, no PySide, no system tray, no exe/dmg packaging.

## Phase 30 Worker Console Local Web API Usage

Worker Console frontend calls the local worker client API through `worker_console/src/api/localWorkerClient.ts`.

Config:

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

Used local endpoints:

- `GET /local/status`
- `GET /local/health`
- `GET /local/logs`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`

UI unreachable state: `Worker API unreachable`, `请确认 worker_client 是否启动`, `请确认端口是否为 9100`.

Phase 30 API doc marker: Worker Console GUI Foundation uses Vite, React, TypeScript, and Tailwind. Runtime Control is local-only. Current boundary: no exe / dmg.
## Phase 31：Worker Console Desktop Local API

状态：已完成，本地桌面壳能力。范围名称：Worker Console Desktop App Foundation。

`worker_console_desktop` 不新增 AI Server API。它复用客户机本地 `worker_client` API：

- `GET /local/status`
- `GET /local/health`
- `GET /local/logs`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`

默认配置：

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
status_url=http://127.0.0.1:9100/local/status
tauri_config=worker_console_desktop/src-tauri/tauri.conf.json
src-tauri/tauri.conf.json
```

不可达提示：`Worker Runtime 未启动`。

开发命令：

```powershell
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

当前边界：no exe / dmg、no system tray、no auto update、无正式安装包。

## Phase 32：Worker Console Desktop Tray Runtime

状态：已完成，本地桌面 Runtime 能力。范围名称：Worker Console System Tray & Desktop Runtime Foundation。

能力关键词：System Tray、Minimize To Tray、Tray Runtime Control、Desktop Status Sync、AutoStart Placeholder。

本阶段不新增 AI Server API。桌面端继续调用本地 `worker_client` Local API：

- `GET /local/status`
- `GET /local/health`
- `GET /local/logs`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`

桌面端设置：

```json
{
  "localWorkerApi": "http://127.0.0.1:9100",
  "minimizeToTray": true,
  "refreshIntervalMs": 5000
}
```

设置示例文件：`worker_console_desktop/settings.example.json`。
Tauri runtime 配置：`worker_console_desktop/src-tauri/desktop-runtime.json`，包含 `minimize_to_tray=true`。

Tauri System Tray 菜单：Show Console、Hide Window、Start Runtime、Stop Runtime、Restart Runtime、Start Heartbeat、Stop Heartbeat、Refresh Status、Quit。

安全边界：不允许 arbitrary shell，不允许 remote shell，不允许远程命令执行，不允许文件系统全盘访问。当前没有 no formal installer、没有 no auto-update。

## Phase 33 Conversation Runtime APIs

Status: completed foundation.

Required headers for all endpoints:

```text
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

### POST /api/v1/conversations

Request:

```json
{
  "title": " ",
  "metadata": {"phase": "33"}
}
```

Response includes `id`, `workspace_id`, `user_id`, `title`, `status`, `metadata`, `created_at`, and `updated_at`.

### GET /api/v1/conversations

Lists `conversation_threads` filtered by current workspace.

### GET /api/v1/conversations/{thread_id}

Returns one workspace-scoped conversation thread.

### POST /api/v1/conversations/{thread_id}/messages

Request:

```json
{
  "role": "user",
  "content": " ",
  "metadata": {"source": "swagger"}
}
```

Writes to `conversation_messages` with `thread_id` and emits `message_received` for user messages.

### GET /api/v1/conversations/{thread_id}/messages

Returns the message list for the current workspace thread.

### GET /api/v1/conversations/{thread_id}/events

Polling event feed. Returns `conversation_events` such as `message_received`, `planning_started`, `plan_created`, `agent_started`, `tool_called`, `worker_action_started`, `worker_action_completed`, `assistant_response`, and `error`.

This is not WebSocket streaming and not SSE streaming. WebSocket and SSE are placeholders only.

### POST /api/v1/conversations/{thread_id}/run

Request:

```json
{
  "input": {
    "message": " "
  }
}
```

Response includes `assistant_message`, `route`, `events`, `output`, `websocket_placeholder=true`, and `sse_placeholder=true`.

Rule-based routing:

- search/browser/open-page keywords -> `browser_tool`
- content/copy/generate keywords -> `ContentAgent`
- `OpenClaw` keyword -> `openclaw_tool` mock

### Phase 33 API Reference Markers

Conversation Runtime Foundation implementation markers for docs verifier: `ConversationService`, `run_conversation_turn`, `Chat Panel Foundation`, `Event Timeline`, `polling`.

The polling event feed uses `GET /api/v1/conversations/{thread_id}/events`. WebSocket and SSE are placeholders only.

## Phase 34 Remote Browser Runtime API

Status: completed foundation. Workspace headers are required for all AI Server routes:

```text
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Implementation markers: `Remote Browser Runtime Foundation`, `browser_runtime_sessions`, `BrowserRuntimeSessionService`, `app/browser/providers/remote_provider.py`, `worker_client/browser_runtime`, `storage/browser_screenshots`, `BROWSER_RUNTIME_SCREENSHOT_DIR`, `Browser Sessions Panel`, `playwright install chromium`.

### POST /api/v1/browser-runtime/sessions

Create a remote browser runtime session.

Request:

```json
{
  "browser": "chromium",
  "metadata": {
    "phase": "34"
  }
}
```

Response:

```json
{
  "id": "RUNTIME_SESSION_ID",
  "workspace_id": "demo-workspace",
  "worker_id": "WORKER_ID",
  "provider": "remote",
  "browser": "chromium",
  "session_status": "active",
  "last_activity_at": "2026-05-14T00:00:00Z",
  "metadata": {
    "remote_session_id": "REMOTE_SESSION_ID"
  }
}
```

### GET /api/v1/browser-runtime/sessions

Lists browser runtime sessions for the current workspace. Supports status filtering, for example `?status=active`.

### GET /api/v1/browser-runtime/sessions/{session_id}

Returns one `browser_runtime_sessions` record scoped to the current workspace.

### POST /api/v1/browser-runtime/sessions/{session_id}/navigate

Request:

```json
{
  "url": "https://example.com"
}
```

Response includes `title`, `url`, `remote_action_id`, and structured remote worker data.

### POST /api/v1/browser-runtime/sessions/{session_id}/screenshot

Request:

```json
{
  "full_page": true,
  "screenshot_name": "example-home"
}
```

Response includes the saved screenshot path under `storage/browser_screenshots`.

### GET /api/v1/browser-runtime/sessions/{session_id}/page

Returns page title, current URL, and HTML/text content fetched from the remote worker page.

### POST /api/v1/browser-runtime/sessions/{session_id}/close

Closes the remote browser session and marks the local runtime session closed.

### Worker Runtime API

The registered worker exposes these compatible runtime endpoints:

- `POST /browser/session/create`
- `POST /browser/session/{session_id}/navigate`
- `POST /browser/session/{session_id}/screenshot`
- `GET /browser/session/{session_id}/page`
- `POST /browser/session/{session_id}/close`

The in-project mock worker runtime exposes equivalent test routes under `/api/v1/browser-worker-runtime/browser/session/create`, `/api/v1/browser-worker-runtime/browser/session/{session_id}/navigate`, `/api/v1/browser-worker-runtime/browser/session/{session_id}/screenshot`, `/api/v1/browser-worker-runtime/browser/session/{session_id}/page`, and `/api/v1/browser-worker-runtime/browser/session/{session_id}/close`.

Boundary: current runtime supports basic Chromium create / navigate / screenshot / page / close only. It does not implement stealth, proxy rotation, cookie injection, captcha bypass, platform automation, remote desktop streaming, or DevTools remote control.

## Phase 35B Real Client Worker E2E Validation Plan

Status: completed validation plan and script. This phase adds `validate_real_client_worker_e2e.py`; it does not claim that a real customer machine was online during implementation.

Script:

```powershell
python scripts\validate_real_client_worker_e2e.py `
  --server-url http://localhost:8000 `
  --workspace-id demo-workspace `
  --user-id demo-user `
  --expected-worker-name customer-machine-worker-1
```

Parameters:

- `server_url`
- `workspace_id`
- `user_id`
- `expected_worker_name`

Exit codes:

- `0`: PASS
- `1`: FAIL
- `2`: SKIPPED

If `expected_worker_name` is not online, the script returns `SKIPPED` with reason `real client worker not online` and does not execute browser actions.

Swagger validation flow:

1. `GET /api/v1/health`
2. `GET /api/v1/browser-workers/health/summary`
3. `GET /api/v1/browser-workers/available`
4. `POST /api/v1/browser-runtime/sessions`
5. `POST /api/v1/browser-runtime/sessions/{session_id}/navigate`
6. `POST /api/v1/browser-runtime/sessions/{session_id}/screenshot`
7. `GET /api/v1/browser-runtime/sessions/{session_id}/page`
8. `POST /api/v1/browser-runtime/sessions/{session_id}/close`

Security note: do not expose port 9100 to the public internet. Prefer Tailscale, VPN, or LAN.

## Phase 35A Browser Runtime Observability & Replay

Status: completed. Workspace headers are required for every route:

Service: `BrowserRuntimeObservabilityService`.

Concept map: Browser Runtime Timeline, Browser Runtime Snapshots, Browser Runtime Replay Metadata, Snapshot Storage, Timeline Event Flow, Failure Debug, metadata-only replay.

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

### GET /api/v1/browser-runtime/sessions/{session_id}/events

Lists `browser_runtime_events` for a runtime session. Events include `session_created`, `navigate_started`, `navigate_completed`, `screenshot_started`, `screenshot_completed`, `page_snapshot_captured`, `action_failed`, `session_closed`, and `replay_requested`.

Response:

```json
{
  "items": [
    {
      "event_type": "navigate_completed",
      "status": "completed",
      "message": "Browser runtime navigation completed",
      "payload": {
        "url": "https://example.com"
      },
      "duration_ms": 120,
      "error": null
    }
  ]
}
```

### GET /api/v1/browser-runtime/sessions/{session_id}/snapshots

Lists `browser_runtime_snapshots`. Optional query: `snapshot_type=page|screenshot|error|final`.

Response:

```json
{
  "items": [
    {
      "snapshot_type": "page",
      "url": "https://example.com",
      "page_title": "Example Domain",
      "html_path": "storage/browser_runtime_snapshots/demo-workspace/SESSION/page-SNAPSHOT.html",
      "text_path": "storage/browser_runtime_snapshots/demo-workspace/SESSION/page-SNAPSHOT.txt",
      "screenshot_path": null,
      "metadata": {
        "source": "get_page"
      }
    }
  ]
}
```

### POST /api/v1/browser-runtime/sessions/{session_id}/replay

Creates a `browser_runtime_replays` record. Replay is metadata-only and does not re-run browser actions.

Request:

```json
{
  "metadata": {
    "reason": "debug browser runtime session"
  }
}
```

### GET /api/v1/browser-runtime/replays/{replay_id}

Returns replay metadata, including `replay_steps`, `source_event_ids`, and `source_snapshot_ids`.

### GET /api/v1/browser-runtime/replays/{replay_id}/export

Writes and returns `replay-{replay_id}.json` under `BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots`.

Boundary: Browser Runtime Observability & Replay is not live stream, not VNC, not noVNC, not DevTools remote control, and not browser action re-execution.

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

Phase 37 UI error state exact marker: AI Server unreachable.
## Phase 38：Conversation Tool Execution Bridge API

Conversation Runtime Tool Execution Bridge：已完成 / foundation。

### POST `/api/v1/conversations/{thread_id}/run`

状态：已完成 / foundation。Required headers：`X-Workspace-Id`、`X-User-Id`。

请求：

```json
{
  "input": {
    "message": "请打开 https://example.com 并截图。"
  }
}
```

新增响应字段：

```json
{
  "thread_id": "uuid",
  "user_message_id": "uuid",
  "assistant_message_id": "uuid",
  "route": "browser",
  "route_name": "browser",
  "selected_tool": "browser_tool",
  "events_created": 8,
  "success": true,
  "summary": "Browser bridge opened https://example.com...",
  "result_metadata": {
    "runtime_session_id": "uuid",
    "target": "https://example.com"
  },
  "events": [],
  "output": {}
}
```

Route / Tool 字段：
- `ConversationToolRouter`
- `app/conversation/tool_router.py`
- `route_selected`
- `tool_execution_started`
- `tool_execution_completed`
- `tool_execution_failed`
- `agent_execution_started`
- `agent_execution_completed`
- `planning_execution_started`
- `planning_execution_completed`
- `bridge_fallback`
- `bridge_error`
- `route_name`
- `selected_tool`
- `events_created`
- `success`
- `summary`
- `result_metadata`

Routing Rules：
- Browser Bridge / Browser Bridge Flow：`browser_tool`，支持 create session -> navigate -> screenshot -> get page -> close session。
- OpenClaw mock bridge / OpenClaw Mock Bridge Flow：`openclaw_tool` mock，仅 `mock_inspect`。
- RAG bridge：`rag_search_tool`，需要 `collection_name`。
- Content bridge：`ContentAgent`。
- Planning bridge：`PlanningService`，返回 `plan_id` 和 steps。

边界：not autonomous agent，not WebSocket，not SSE，不做真实平台发布，不做真实 OpenClaw，不做 ComfyUI。

## Conversation Approval Flow API（Phase 39）

状态：已完成，Conversation Execution Review & Approval Flow / Approval Flow Foundation。服务层由 `ConversationApprovalService` 管理状态流转。`Tool Execution Gate` 负责阻止未审批的 medium/high risk 动作。当前不是完整权限系统，not a full permission system。

### `GET /api/v1/conversations/{thread_id}/approvals`

Required headers: `X-Workspace-Id`, `X-User-Id`。

Response:

```json
{
  "thread_id": "THREAD_ID",
  "items": [
    {
      "id": "APPROVAL_ID",
      "workspace_id": "demo-workspace",
      "thread_id": "THREAD_ID",
      "message_id": "MESSAGE_ID",
      "route_name": "browser",
      "selected_tool": "browser_tool",
      "risk_level": "medium",
      "approval_status": "pending",
      "proposed_action": "browser_tool:navigate_and_screenshot",
      "proposed_payload": {
        "decision": {},
        "tool_input": {},
        "source_message": "open https://example.com and screenshot"
      }
    }
  ]
}
```

### `GET /api/v1/conversation-approvals/{approval_id}`

返回单个 `conversation_approvals` 记录。字段包括 `risk_level`、`approval_status`、`proposed_action`、`proposed_payload`。

### `POST /api/v1/conversation-approvals/{approval_id}/approve`

```json
{
  "reviewer_notes": "Looks safe to execute."
}
```

状态流转：`pending -> approved`，写入 `approval_approved`。

### `POST /api/v1/conversation-approvals/{approval_id}/reject`

```json
{
  "reviewer_notes": "Need to rewrite before execution."
}
```

状态流转：`pending -> rejected`，写入 `approval_rejected`。Rejected approval 不得执行。

### `POST /api/v1/conversation-approvals/{approval_id}/cancel`

```json
{
  "reviewer_notes": "Cancelled before execution."
}
```

状态流转：`pending/approved -> cancelled`，写入 `approval_cancelled`。

### `POST /api/v1/conversation-approvals/{approval_id}/execute`

```json
{
  "input": {
    "approval_id": "APPROVAL_ID"
  }
}
```

要求：approval 必须是 `approved`。执行后写入 `approval_executed`、`execution_after_approval_started`、`execution_after_approval_completed` 或 `execution_after_approval_failed`。

### Conversation Run Mode

`POST /api/v1/conversations/{thread_id}/run` 新增 `mode`：

```json
{
  "input": {
    "message": "请打开 https://example.com 并截图。"
  },
  "mode": "review_first"
}
```

`mode` 支持：

- `auto_safe`：low risk 自动执行；medium/high 创建 approval，不执行。
- `review_first`：所有 route 都先创建 approval，不执行。
- `execute_after_approval`：需要 `input.approval_id`，且 approval 必须已 approved。

Response 新增：

```json
{
  "approval_required": true,
  "approval_id": "APPROVAL_ID",
  "approval_status": "pending",
  "risk_level": "medium",
  "proposed_action": "browser_tool:navigate_and_screenshot"
}
```

Risk Policy / `ConversationRiskPolicy`：

- `low`：content generation、RAG search、planning create-only。
- `medium`：browser navigate / screenshot / get page、OpenClaw mock inspect。
- `high`：browser click、form input、upload、publish、account/profile actions、real OpenClaw actions、future social platform actions。

Conversation events：`approval_required`、`approval_created`、`approval_approved`、`approval_rejected`、`approval_cancelled`、`approval_expired`、`approval_executed`、`execution_blocked_pending_approval`、`execution_after_approval_started`、`execution_after_approval_completed`、`execution_after_approval_failed`。

Frontend：Admin Dashboard、Worker Console、Worker Console Desktop 都有 pending approvals panel、proposed payload JSON、risk badge、approve / reject / cancel / execute approved action。当前仍不是 WebSocket/SSE，也不是完整权限系统。
## Phase 40 Conversation Playbooks API

Required headers: `X-Workspace-Id`, `X-User-Id`.

Database tables: `conversation_playbooks`, `conversation_playbook_runs`.

### `GET /api/v1/conversation-playbooks`

Lists active/disabled/archived playbooks in the current workspace. Built-in templates are seeded on demand.

Response includes `name`, `category`, `status`, `risk_level`, `steps`, `default_inputs`, and `metadata`.

### `GET /api/v1/conversation-playbooks/{playbook_id}`

Returns one Playbook definition.

### `POST /api/v1/conversation-playbooks`

Creates a custom Playbook. This is a foundation API, not a visual workflow builder.

### `PATCH /api/v1/conversation-playbooks/{playbook_id}`

Updates an existing Playbook definition or disables it by setting `status=disabled`.

### `POST /api/v1/conversation-playbooks/{playbook_id}/run`

Runs a Playbook directly.

```json
{
  "input": {
    "topic": "AI 自动化运营",
    "platform": "short_video",
    "style": "专业简洁"
  },
  "mode": "auto_safe"
}
```

Response stores run state in `conversation_playbook_runs` and includes `playbook_id`, `thread_id`, `status`, `input_payload`, `output_payload`, `current_step`, and `error`.

### `GET /api/v1/conversation-playbook-runs`

Lists Playbook Runs. Step Timeline is stored in `output_payload.steps`.

### `GET /api/v1/conversation-playbook-runs/{run_id}`

Returns one Playbook Run.

### `POST /api/v1/conversation-playbook-runs/{run_id}/cancel`

Cancels a pending/running/waiting Playbook Run.

### Conversation run with Playbook

`POST /api/v1/conversations/{thread_id}/run` now supports:

```json
{
  "input": {
    "message": "请打开 https://example.com 截图并生成报告。"
  },
  "playbook_name": "browser_screenshot_report",
  "mode": "review_first"
}
```

Additional response fields: `playbook_name`, `playbook_run_id`, `playbook_status`.

Events include `playbook_selected`, `playbook_run_started`, `playbook_step_started`, `playbook_step_completed`, `playbook_approval_required`, `playbook_waiting_approval`, `playbook_resumed_after_approval`, `playbook_completed`, `playbook_failed`, and `playbook_cancelled`.

Current limitation: this is not a full workflow builder and does not implement real social-platform publishing.

## Phase 41 Output Artifacts / Output Library API

Required headers: `X-Workspace-Id`, `X-User-Id`.

Database table: `output_artifacts`.

Service: `OutputArtifactService` handles workspace-scoped artifact creation, listing, soft delete, message/playbook conversion, and markdown/json/txt export.

Core fields: `source_type`, `artifact_type`, `title`, `summary`, `content`, `file_path`, `mime_type`, `metadata`, `thread_id`, `playbook_run_id`, `created_by`, `status`.

Source types: `conversation`, `playbook`, `tool`, `browser_runtime`, `rag`, `content_agent`, `planning`, `openclaw_mock`.

Artifact types: `text`, `markdown`, `json`, `screenshot`, `html_snapshot`, `report`, `plan`, `rag_answer`, `content_draft`.

Events: `artifact_created`, `artifact_exported`, `artifact_deleted`, `artifact_linked_to_playbook_run`.

### `GET /api/v1/output-artifacts`

Lists active artifacts in the current workspace. Supports filters: `artifact_type`, `source_type`, `thread_id`, `playbook_run_id`, created_at range (`created_from`, `created_to`), `include_deleted`, and `limit`.

### `GET /api/v1/output-artifacts/{artifact_id}`

Returns one artifact.

### `PATCH /api/v1/output-artifacts/{artifact_id}`

Updates editable fields such as `title`, `summary`, `content`, `file_path`, `mime_type`, and `metadata`.

### `DELETE /api/v1/output-artifacts/{artifact_id}`

Soft deletes the artifact by setting status to `deleted`; physical files are not removed.

### `POST /api/v1/output-artifacts/from-message/{message_id}`

Creates an artifact from a Conversation message. Assistant messages in the Conversation UI expose Save as Artifact.

### `POST /api/v1/output-artifacts/from-playbook-run/{run_id}`

Creates or returns generated artifacts for one Playbook Run. Completed Playbook Runs also create artifacts automatically.

### `GET /api/v1/output-artifacts/{artifact_id}/export`

Exports an artifact as markdown/json/txt.

```text
GET /api/v1/output-artifacts/{artifact_id}/export?format=markdown
GET /api/v1/output-artifacts/{artifact_id}/export?format=json
GET /api/v1/output-artifacts/{artifact_id}/export?format=txt
```

Export files are written under `storage/output_artifacts/{workspace_id}/{artifact_id}/`. Screenshot and `html_snapshot` artifacts return/retain file path metadata and do not copy large files.

Frontend: Admin Dashboard has an Output Library page with artifact list/detail, type badge, source type, related thread, related Playbook Run, preview content, Export markdown/json/txt, and filters. Conversation pages show generated artifacts and Save as Artifact.

Boundary: this is not a full DAM, not S3, not MinIO, and not production publishing asset management.
## Phase 42 API - Task Orchestration & Background Execution

### `GET /api/v1/task-runs`
Required headers: `X-Workspace-Id`, `X-User-Id`. Query filters: `status`, `task_type`, `source_type`, `created_from`, `created_to`, `limit`.

Response JSON:
```json
{
  "items": [
    {
      "id": "TASK_RUN_ID",
      "workspace_id": "demo-workspace",
      "task_type": "playbook",
      "source_type": "conversation",
      "source_id": "THREAD_ID",
      "status": "queued",
      "priority": "normal",
      "retry_count": 0,
      "max_retries": 3,
      "scheduled_at": null,
      "current_step": 0,
      "input_payload": {},
      "output_payload": {},
      "metadata": {},
      "created_by": "demo-user"
    }
  ]
}
```

### `GET /api/v1/task-runs/{task_run_id}`
  `task_runs`  `queued`, `running`, `waiting_approval`, `retrying`, `completed`, `failed`, `cancelled`, `expired`

### `GET /api/v1/task-runs/{task_run_id}/events`
  `task_run_events` timeline  `task_queued`, `task_started`, `task_step_started`, `task_step_completed`, `task_waiting_approval`, `task_retry_scheduled`, `task_completed`, `task_cancelled`, `artifact_created`.

### `POST /api/v1/task-runs/{task_run_id}/retry`
```json
{ "reason": "manual retry" }
```
,  failed / retryable task, retry, `TaskRetryPolicy`  exponential backoff, `approval rejected`, validation error, retry.

### `POST /api/v1/task-runs/{task_run_id}/cancel`
```json
{ "reason": "manual cancel" }
```
  task timeline?

### `POST /api/v1/task-runs/{task_run_id}/resume`
,  `waiting_approval`  approval, approved  queued  Phase 39 Approval Gate.

### Conversation Background Run
`POST /api/v1/conversations/{thread_id}/run`
```json
{
  "input": { "message": "  https://example.com  " },
  "playbook_name": "browser_screenshot_report",
  "mode": "review_first",
  "execution_mode": "background"
}
```
  `task_run_id`, `task_status`, `execution_mode`, `scheduled`  `scheduled_at`.

 Task Orchestration, Background Execution foundation  Celery / RabbitMQ / Kubernetes / production HA queue.

Phase 42 verifier markers: `TaskOrchestratorService`, `BackgroundTaskExecutor`, `TaskRetryPolicy`, artifact linkage, not Celery, not Kubernetes, not production HA.
## Phase 43: Task Scheduler Persistence & Worker Recovery

 Task Scheduler Persistence, `task_scheduler_state`, `task_runs`, Task Lease  `TaskRecoveryService`, Scheduler Health API, manual recovery API, Failed Diagnostics  scheduler health

Task Lease, running task run  `lease_owner`, `lease_token`, `lease_expires_at`, `heartbeat_at`, expired lease, stale heartbeat  scan, manual recover

Recovery rules, running + expired lease, stale heartbeat -> retrying  retry budget, failed, pending scheduled due -> queued, retrying delay elapsed -> queued, waiting_approval  completed/cancelled/expired

Admin Dashboard  Scheduler Health, lease status, recoverable badge, diagnostics panel, scheduled due indicator, manual recover, Worker Console, Worker Console Desktop  Task recovery

  in-process scheduler foundation  Celery  Kubernetes  production HA distributed queue?
## Phase 43 API - Task Scheduler Persistence & Worker Recovery

Required headers: `X-Workspace-Id`, `X-User-Id`.

 `task_scheduler_state`?

`task_runs`  Task Lease / Recovery / Failed Diagnostics  `lease_owner`, `lease_token`, `lease_expires_at`, `heartbeat_at`, `recovery_count`, `last_recovered_at`, `recovery_reason`, `failure_category`, `failure_reason`, `recoverable`, `suggested_action`, `last_event_summary`.

### `GET /api/v1/task-scheduler/health`

  workspace, Scheduler Health, scheduler status, heartbeat, last scan, active task count, recovered task count, metadata  in-process foundation  Celery  Kubernetes  production HA distributed queue.

### `POST /api/v1/task-scheduler/scan`

  recovery scan  scheduled due tasks, retrying due tasks, expired lease, stuck task recovery  recovered counts, scheduler health.

### `GET /api/v1/task-runs/{task_run_id}/diagnostics`

  Failed Diagnostics, `failure_category`, `failure_reason`, `recoverable`, `suggested_action`, `last_event_summary`, `lease_expired`, `scheduled_due`, `retry_count`, `max_retries`.

### `POST /api/v1/task-runs/{task_run_id}/recover`

  recoverable task, running + expired lease, retry policy, failed task  `TaskRetryPolicy`  retry, waiting_approval  approval resume.

###   `GET /api/v1/task-runs`

 `recoverable`, `lease_expired`, `scheduled_due`.

Recovery rules, running + expired lease, stale heartbeat -> retrying, failed, queued/pending  scheduled due -> queued, retrying delay elapsed -> queued, waiting_approval  completed/cancelled/expired  max retries -> failed.

Admin Dashboard  Scheduler Health, lease status, recoverable badge, diagnostics panel, manual recover button, Worker Console, Worker Console Desktop  Task recovery

Phase 43 verifier markers: `TaskRecoveryService`, `task_scheduler_state`, `Task Lease`, `Scheduler Health`, `Failed Diagnostics`, `lease_owner`, `lease_token`, `lease_expires_at`, `heartbeat_at`, `recovery_count`, `failure_category`, `recoverable`, stuck task recovery, expired lease, not Celery, not Kubernetes, not production HA.

Phase 43 runtime config markers: `TASK_SCHEDULER_NAME`, `TASK_LEASE_SECONDS`, `TASK_STUCK_TIMEOUT_SECONDS`, `TASK_SCHEDULER_RECOVERY_INTERVAL_SECONDS`.

<!-- PHASE44_API:START -->
## Phase 44 Output Artifact Pipeline APIs

### `GET /api/v1/output-artifacts/{artifact_id}/lineage`
  artifact, Artifact lineage  root artifact, ancestors, descendants, relationship graph

### `GET /api/v1/output-artifacts/{artifact_id}/relationships`
  artifact, `artifact_relationships`  `relationship_type`  `derived_from`, `packaged_into`, `summarized_from`, `exported_from`, `replay_of`.

### `POST /api/v1/output-artifacts/{artifact_id}/export`
  `ArtifactExportService`  artifact  markdown, html, json, txt, bundle_zip, report_package  exported child artifacts  runtime.

### `POST /api/v1/output-artifacts/{artifact_id}/package`
  `ArtifactPackagingService`  artifact  lineage  bundle artifact, `bundle.zip` package metadata.

### `POST /api/v1/output-artifacts/cleanup/preview`
  `ArtifactRetentionService`   cleanup preview  retention preview

Phase 44  `parent_artifact_id`, `root_artifact_id`, `source_task_run_id`, `source_playbook_run_id`, `source_conversation_id`, `source_runtime_session_id`, `artifact_role`, `artifact_stage`, `generated_by`, `exportable`, `retention_policy`, `expires_at`, `artifact_relationships`, `relationship_type`, `derived_from`, `packaged_into`, `exported_from`, `ArtifactExportService`, `ArtifactPackagingService`, `ArtifactRetentionService`, `Artifact Explorer`, `lineage graph`, `relationship graph`, `bundle.zip`, `storage/output_packages`, `storage/output_exports`, `retention preview`, `not a full DAM`, `S3`, `MinIO`  production object storage platform.
<!-- PHASE44_API:END -->

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

<!-- PHASE45_API:START -->
## Phase 45 API: Workflow State & Agent Memory Foundation

Workflow State API paths:

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

Data model/API field markers: `workflow_runs`, `workflow_steps`, `workflow_checkpoints`, `agent_memory_snapshots`, `WorkflowStateService`, `Workflow State`, `Workflow Steps`, `Checkpoints`, `Agent Memory Snapshots`, `workflow_run_id`, `workflow_step_id`, `checkpoint_id`, `memory_snapshot_id`, `workflow_run_created`, `workflow_step_started`, `workflow_step_completed`, `workflow_checkpoint_created`, `workflow_paused`, `workflow_resumed`, `memory_snapshot_created`, `Pause / Resume`, `Workflow lineage`, `not a full workflow builder`, `not ComfyUI`.
<!-- PHASE45_API:END -->

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
## Phase 46 API: Workflow Graph Runtime & Conditional Execution

New graph runtime routes:

- `GET /api/v1/workflow-graphs`
- `POST /api/v1/workflow-graphs`
- `GET /api/v1/workflow-graphs/{graph_id}`
- `POST /api/v1/workflow-graphs/{graph_id}/validate`
- `POST /api/v1/workflow-runs/{workflow_run_id}/replay`
- `GET /api/v1/workflow-runs/{workflow_run_id}/graph`
- `GET /api/v1/workflow-runs/{workflow_run_id}/planner`

New runtime tables and services:

- `workflow_graphs`
- `workflow_graph_nodes`
- `workflow_graph_edges`
- `workflow_replays`
- `WorkflowExecutionPlanner`
- `SafeConditionEvaluator`

Fields and events:

- `current_node_key`
- `planned_next_nodes`
- `skipped_nodes`
- `retry_state`
- `fallback_state`
- `node_key`
- `parent_node_key`
- `dependency_state`
- `producing_node_key`
- `replay_source`
- `graph_lineage`

Supported routing concepts: Workflow Graph Runtime, Conditional Execution, Retry/Fallback Path, Replay Foundation, conditional routing, dependency resolution, graph replay metadata, and safe evaluator conditions over `workflow.variables`, `workflow.status`, `step.output`, `artifact.metadata`, and `approval.status`.

Boundaries: not a visual DAG builder, not distributed orchestration engine, not ComfyUI, not WebSocket/SSE streaming, not real OpenClaw, and not real platform publishing.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47：Workflow Template Registry & Versioning API

Phase 47 新增 Workflow Template Registry & Versioning。核心表包括 `workflow_templates`、`workflow_template_versions`、`workflow_template_runs`。核心服务包括 `WorkflowTemplateRegistryService` 与 `WorkflowTemplateCompatibilityService`。

新增 API：

- `GET /api/v1/workflow-templates`
- `POST /api/v1/workflow-templates`
- `GET /api/v1/workflow-templates/{template_id}`
- `POST /api/v1/workflow-templates/{template_id}/versions`
- `GET /api/v1/workflow-templates/{template_id}/versions/{version_id}`
- `POST /api/v1/workflow-templates/{template_id}/activate-version/{version_id}`
- `POST /api/v1/workflow-templates/{template_id}/validate`
- `POST /api/v1/workflow-templates/{template_id}/run`
- `GET /api/v1/workflow-template-runs`
- `GET /api/v1/workflow-template-runs/{run_id}`
- `POST /api/v1/workflow-templates/import`
- `GET /api/v1/workflow-templates/{template_id}/export`

关键字段与概念：

- `template_key`
- `current_version`
- `latest_version`
- `validation_status`
- `compatibility`
- `workflow_template_id`
- `workflow_template_version_id`
- `workflow_template_run_id`
- `Template Library`
- `Import / Export`

内置模板：

- `browser_screenshot_report_graph`
- `content_generation_graph`
- `rag_answer_graph`
- `approval_then_browser_graph`
- `openclaw_mock_inspect_graph`
- `task_retry_demo_graph`

边界：当前不是可视化 DAG builder，不是 drag/drop workflow editor，不接 ComfyUI，不做真实平台自动化。
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

## Phase 61A: 商业运营基础

状态：已完成。

Phase 61A 增加 workspace 级商业运营项目中心。它提供 `commercial_operations`、`CommercialOperationService` 和 Admin Dashboard 商业运营页，用于把一个商业目标保存为可追踪记录，并生成可审阅的计划草案。

API：

- `GET /api/v1/commercial-operations`
- `POST /api/v1/commercial-operations`
- `GET /api/v1/commercial-operations/{operation_id}`
- `PATCH /api/v1/commercial-operations/{operation_id}`
- `POST /api/v1/commercial-operations/{operation_id}/plan-draft`

主要字段：`title`、`objective`、`target_audience`、`channels`、`status`、`priority`、`risk_level`、`budget_amount`、`budget_currency`、`start_at`、`end_at`、`knowledge_collection`、`success_metrics`、`constraints`、`plan_outline`、`metadata`。

边界：此阶段不会自动发布，不会执行 OpenClaw 动作，不会运行 ComfyUI 任务，不会控制真实账号，也不会绕过审批。

## Phase 61B: 商业运营证据与交接关联

状态：已完成。

Phase 61B 在每个商业运营项目下新增 `commercial_operation_links` 与 `CommercialOperationLink` 记录。操作人员可以先把沟通记录、内容产物、任务运行、工作流运行、RAG 文档、审批记录、知识来源或外部素材手动挂到项目上，供后续审批和执行阶段接手。

API：

- `GET /api/v1/commercial-operations/{operation_id}/links`
- `POST /api/v1/commercial-operations/{operation_id}/links`
- `DELETE /api/v1/commercial-operations/{operation_id}/links/{link_id}`

主要字段：`operation_id`、`link_type`、`target_type`、`target_id`、`title`、`summary`、`source_name`、`metadata`。

支持的 `link_type`：`conversation`、`artifact`、`task_run`、`workflow_run`、`rag_document`、`knowledge_source`、`approval`、`external`。

边界：这些关联只是可追踪引用，不会执行被关联任务，不会发布内容，不会运行 ComfyUI，不会运行 OpenClaw，也不会绕过审批。

## Phase 61C: 商业运营审批门禁

状态：已完成。

Phase 61C 在每个商业运营项目下新增 `commercial_operation_approvals` 与 `CommercialOperationApproval` 记录。操作人员可以针对某个 `plan_outline` 步骤发起审批，再批准、驳回或取消该门禁，供后续干运行或执行阶段接手。

API：

- `GET /api/v1/commercial-operations/{operation_id}/approvals`
- `POST /api/v1/commercial-operations/{operation_id}/approvals`
- `POST /api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/cancel`

主要字段：`operation_id`、`step_key`、`title`、`requested_action`、`approval_status`、`risk_level`、`requested_by`、`reviewer_user_id`、`reviewer_notes`、`approved_at`、`rejected_at`、`cancelled_at`、`metadata`。

支持的 `approval_status`：`pending`、`approved`、`rejected`、`cancelled`。

边界：审批只是人工审阅记录和计划步骤门禁，不会执行被关联任务，不会发布内容，不会运行 ComfyUI，不会运行 OpenClaw，不会控制真实账号，也不会绕过审批。

## Phase 61D: 商业运营安全干运行

状态：已通过 PR #44 合并到 `main`。

Phase 61D 在每个商业运营项目下新增 `commercial_operation_dry_runs` 与 `CommercialOperationDryRun` 记录。操作人员可以基于已批准的审批门禁创建 metadata-only 干运行，检查生成的 runbook、输入摘要、目标、预期输出和 readiness checks，再把干运行标记为完成、失败或取消，供后续交接。

API：

- `GET /api/v1/commercial-operations/{operation_id}/dry-runs`
- `POST /api/v1/commercial-operations/{operation_id}/dry-runs`
- `POST /api/v1/commercial-operations/{operation_id}/dry-runs/{dry_run_id}/complete`
- `POST /api/v1/commercial-operations/{operation_id}/dry-runs/{dry_run_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/dry-runs/{dry_run_id}/cancel`

主要字段：`operation_id`、`approval_id`、`step_key`、`title`、`dry_run_status`、`execution_mode`、`execution_target`、`input_summary`、`runbook`、`expected_outputs`、`readiness_checks`、`result_summary`、`failure_reason`、`requested_by`、`completed_by`、`metadata`。

支持的 `dry_run_status`：`created`、`completed`、`failed`、`cancelled`。

边界：干运行只是已审批后的 metadata-only 执行准备记录，不会发布内容，不会运行 ComfyUI，不会运行 OpenClaw，不会运行 Browser Worker 动作，不会控制真实账号，也不会绕过审批。

## Phase 61E: 商业运营内容草稿

状态：已通过 PR #45 合并到 `main`。

Phase 61E 在每个商业运营项目下新增 `commercial_operation_content_drafts` 与 `CommercialOperationContentDraft` 记录。操作人员可以针对计划步骤创建渠道内容草稿、编辑草稿、送审、批准、驳回或归档，供后续交接使用。

API：

- `GET /api/v1/commercial-operations/{operation_id}/content-drafts`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts`
- `PATCH /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/archive`

主要字段：`operation_id`、`step_key`、`channel`、`content_format`、`title`、`draft_status`、`audience_segment`、`content_body`、`summary`、`call_to_action`、`source_materials`、`asset_requests`、`reviewer_notes`、`created_by`、`updated_by`、`approved_by`、`metadata`。

支持的 `draft_status`：`draft`、`ready_for_review`、`approved`、`rejected`、`archived`。

边界：内容草稿只是审阅记录，不会发布内容，不会运行 ComfyUI，不会运行 OpenClaw，不会运行 Browser Worker 动作，不会控制真实账号，也不会绕过审批。

## Phase 61F: 商业运营素材请求

状态：已合并到 `main`。

Phase 61F 在每个商业运营项目下新增 `commercial_operation_asset_requests` 与 `CommercialOperationAssetRequest` 记录。操作人员可以针对计划步骤创建一等公民素材请求，也可以关联到内容草稿，再进行编辑、送审、批准、驳回、准备未来 ComfyUI 交接、记录准备失败或归档。

API：

- `GET /api/v1/commercial-operations/{operation_id}/asset-requests`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests`
- `PATCH /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/prepare`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/archive`

主要字段：`operation_id`、`content_draft_id`、`step_key`、`channel`、`asset_type`、`title`、`request_status`、`purpose`、`dimensions`、`style_constraints`、`generation_prompt`、`negative_prompt`、`source_materials`、`readiness_checks`、`handoff_payload`、`result_summary`、`failure_reason`、`reviewer_notes`、`requested_by`、`updated_by`、`approved_by`、`prepared_by`、`metadata`。

支持的 `request_status`：`draft`、`ready_for_review`、`approved`、`rejected`、`prepared`、`failed`、`archived`。

边界：素材请求和交接 payload 只是审阅记录，不会发布内容，不会运行 ComfyUI，不会运行 OpenClaw，不会运行 Browser Worker 动作，不会控制真实账号，也不会绕过审批。

## Phase 61G: 商业运营交付物

状态：已合并到 main。

Phase 61G 在每个商业运营项目下新增 `commercial_operation_deliverables` 与 `CommercialOperationDeliverable` 记录。操作人员可以把已批准的内容草稿与已批准或已准备的素材请求打包成商业交付物，再进行编辑、送审、批准、驳回、打包进 Output Library、记录打包失败或归档。

API：

- `GET /api/v1/commercial-operations/{operation_id}/deliverables`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables`
- `PATCH /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/package`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/archive`

主要字段：`operation_id`、`content_draft_id`、`output_artifact_id`、`asset_request_ids`、`step_key`、`channel`、`deliverable_type`、`title`、`deliverable_status`、`summary`、`delivery_notes`、`quality_checks`、`package_payload`、`result_summary`、`failure_reason`、`reviewer_notes`、`created_by`、`updated_by`、`approved_by`、`packaged_by`、`metadata`。

支持的 `deliverable_status`：`draft`、`ready_for_review`、`approved`、`rejected`、`packaged`、`failed`、`archived`。

边界：交付物和打包 payload 只是审阅与交接记录。它会创建 `source_type=commercial_operation` 的 Output Library 产物，但不会发布内容，不会运行 ComfyUI，不会运行 OpenClaw，不会运行 Browser Worker 动作，不会控制真实账号，也不会绕过审批。

## Phase 61H: 商业运营执行请求

状态：进行中。

Phase 61H 在每个商业运营项目下新增 `commercial_operation_execution_requests` 与 `CommercialOperationExecutionRequest` 记录。操作人员可以从已打包交付物创建 metadata-only 执行交接请求，再进行编辑、送审、批准、驳回、准备给未来受控运行适配器、记录交接前失败、准备前取消或归档。

API：

- `GET /api/v1/commercial-operations/{operation_id}/execution-requests`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests`
- `PATCH /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/prepare`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/cancel`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/archive`

主要字段：`operation_id`、`deliverable_id`、`output_artifact_id`、`step_key`、`channel`、`execution_type`、`execution_mode`、`title`、`request_status`、`execution_target`、`input_summary`、`runbook`、`readiness_checks`、`expected_outputs`、`handoff_payload`、`result_summary`、`failure_reason`、`reviewer_notes`、`requested_by`、`updated_by`、`approved_by`、`prepared_by`、`cancelled_by` 和 `metadata`。

支持的 `request_status`：`draft`、`ready_for_review`、`approved`、`rejected`、`prepared`、`failed`、`cancelled`、`archived`。

边界：执行请求和 handoff payload 只是审阅与未来运行交接记录。它不会发布内容，不会运行 ComfyUI，不会运行 OpenClaw，不会运行 Browser Worker 动作，不会控制真实账号，也不会绕过审批。
## Phase 61I: 商业运营执行运行记录

状态：进行中。

Phase 61I 在每个商业运营项目下新增 `commercial_operation_execution_runs` 与 `CommercialOperationExecutionRun` 记录。操作人员可以从 prepared 执行请求创建 metadata-only 执行运行记录，再进行编辑、启动、标记成功、标记失败、在重试次数内重试、取消或归档。

API：

- `GET /api/v1/commercial-operations/{operation_id}/execution-runs`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs`
- `PATCH /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/start`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/succeed`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/retry`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/cancel`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/archive`

主要字段：`operation_id`、`execution_request_id`、`deliverable_id`、`output_artifact_id`、`step_key`、`channel`、`execution_type`、`execution_mode`、`execution_target`、`title`、`run_status`、`input_payload`、`runbook_snapshot`、`readiness_checks`、`expected_outputs`、`runtime_payload`、`result_payload`、`recovery_plan`、`retry_count`、`max_retries`、`result_summary`、`failure_reason`、`operator_notes`、`queued_by`、`started_by`、`completed_by`、`cancelled_by` 和 `metadata`。

支持的 `run_status`：`queued`、`running`、`succeeded`、`failed`、`retrying`、`cancelled`、`archived`。

边界：执行运行记录和 runtime payload 只是审计与恢复记录。它不会发布内容，不会运行 ComfyUI/OpenClaw/Browser Worker，不会控制真实账号，也不会绕过审批。
## Phase 61J: 商业运营结果记录

状态：进行中。

Phase 61J 在每个商业运营项目下新增 `commercial_operation_results` 与 `CommercialOperationResult` 记录。操作人员可以从已成功、失败或取消的终态执行运行创建结果记录，再进行编辑、送审、批准、驳回或归档。

API：

- `GET /api/v1/commercial-operations/{operation_id}/results`
- `POST /api/v1/commercial-operations/{operation_id}/results`
- `PATCH /api/v1/commercial-operations/{operation_id}/results/{result_id}`
- `POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/archive`

主要字段：`operation_id`、`execution_run_id`、`execution_request_id`、`deliverable_id`、`output_artifact_id`、`step_key`、`channel`、`result_type`、`title`、`result_status`、`summary`、`outcome_summary`、`observed_metrics`、`commercial_signals`、`evidence_links`、`follow_up_actions`、`result_payload`、`recommendation_payload`、`reviewer_notes`、`created_by`、`updated_by`、`approved_by` 和 `metadata`。

支持的 `result_status`：`draft`、`ready_for_review`、`approved`、`rejected`、`archived`。

边界：结果记录只是人工观察和复盘记录；不会接入平台分析，不会宣称 ROI 归因，不会发布内容，不会运行 ComfyUI/OpenClaw/Browser Worker，不会控制真实账号，也不会绕过审批。
