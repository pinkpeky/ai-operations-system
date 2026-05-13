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
