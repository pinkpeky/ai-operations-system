# 部署与本地验证

## Phase 28 OpenClaw Adapter Smoke Test

?? OpenClaw runtime ??? mock?

```env
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=true
OPENCLAW_ACTION_TIMEOUT_SECONDS=60
```

Docker / ?? smoke flow?

1. ?? `docker compose up --build -d`?
2. ????? capabilities ?? `"openclaw": true` ? worker?
3. ? `X-Workspace-Id` ?? `GET /api/v1/openclaw/health`?
4. ?? `GET /api/v1/openclaw/capabilities`?
5. ?? `POST /api/v1/openclaw/actions`??? `mock_inspect`?
6. ?? `openclaw_action_logs`????? `openclaw_tool` ??????? `tool_call_logs` ? `browser_security_audit_logs`?

?????????? OpenClaw???? TikTok / YouTube / X????Cookie?????????????????????????

## Phase 20 browser-worker 启动与验证

Docker Compose 现在包含独立服务：

```text
browser-worker
  command: uvicorn worker.main:app --host 0.0.0.0 --port 9100
  port: 9100
  runtime: worker/browser_worker/playwright_runtime.py
  screenshots: worker/screenshots
```

启动：

```powershell
docker compose up --build -d
```

Worker health：

```powershell
Invoke-RestMethod http://localhost:9100/health
```

API Server 对接 worker：

1. 设置或确认 `BROWSER_PROVIDER=remote`。
2. 注册 worker，`base_url` 必须使用 Docker 网络地址 `http://browser-worker:9100`。
3. 创建 browser session。
4. 执行 `navigate` 到 `https://example.com`。
5. 执行 `screenshot` 与 `get_page_content`。

注意：Phase 20 仍不支持社媒自动化、登录、Cookie、代理、指纹、验证码、OCR、视觉 AI 或 OpenClaw。

更新日期：2026-05-12

本文记录当前真实部署和 smoke test 流程。当前状态：Phase 1 到 Phase 15 已完成。

## 本地启动

```powershell
docker compose up --build -d
```

Swagger：

```text
http://localhost:8000/docs
```

基础检查：

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
```

## Ollama

本机可选本地模型：

```powershell
ollama serve
ollama pull mistral
ollama pull bge-m3
ollama list
```

默认仍是 mock：

```env
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
```

切换本地 Ollama：

```env
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://host.docker.internal:11434
LOCAL_LLM_MODEL=mistral

EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_BASE_URL=http://host.docker.internal:11434
LOCAL_EMBEDDING_MODEL=bge-m3

RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
```

## Swagger Smoke Test

通用 headers：

```powershell
$headers = @{ "X-Workspace-Id" = "demo-workspace"; "X-User-Id" = "demo-user" }
```

建议顺序：

- `GET /api/v1/health`
- `GET /api/v1/llm/health`
- `GET /api/v1/rag/embedding/health`
- `GET /api/v1/reranker/health`
- `POST /api/v1/rag/ingest`
- `POST /api/v1/rag/search`
- `POST /api/v1/agentic-rag/query`
- `GET /api/v1/tools`
- `POST /api/v1/memory/sessions`
- `GET /api/v1/agents/registry`
- `POST /api/v1/multi-agent/runs`

## File Upload Smoke Test

`POST /api/v1/files/upload` 使用 `multipart/form-data`。

支持：PDF、DOCX、TXT、MD、CSV。

不支持：PPTX、XLSX、OCR、图片解析。

重复检测基于 `file_hash + workspace_id`，支持 `duplicate_strategy=skip` 和 `duplicate_strategy=force_reingest`。

## Task Observability Smoke Test

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri http://localhost:8000/api/v1/observability/summary `
  -Headers $headers
```

任务事件和日志：

- `GET /api/v1/tasks/{task_id}/events`
- `GET /api/v1/tasks/{task_id}/logs`

## Tool Calling Smoke Test

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri http://localhost:8000/api/v1/tools `
  -Headers $headers

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/tools/current_runtime_tool/execute `
  -Headers $headers `
  -ContentType application/json `
  -Body '{ "input": { "include_document": false } }'
```

## Memory Smoke Test

```powershell
$session = Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/memory/sessions `
  -Headers $headers `
  -ContentType application/json `
  -Body '{ "title": "Phase 15 memory smoke", "metadata": { "phase": "15" } }'

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/memory/messages `
  -Headers $headers `
  -ContentType application/json `
  -Body (@{
    session_id = $session.id
    role = "user"
    content = "请记住我关注 Multi-Agent handoff_trace。"
    metadata = @{ turn = 1 }
  } | ConvertTo-Json)
```

## Phase 15 Multi-Agent Smoke Test

```powershell
$headers = @{ "X-Workspace-Id" = "demo-workspace"; "X-User-Id" = "demo-user" }

Invoke-RestMethod `
  -Method Get `
  -Uri http://localhost:8000/api/v1/agents/registry `
  -Headers $headers

$run = Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/multi-agent/runs `
  -Headers $headers `
  -ContentType application/json `
  -Body '{
    "root_agent": "content_planner",
    "input": {
      "topic": "AI 自动化运营",
      "platform": "tiktok",
      "style": "专业简洁",
      "query": "ping",
      "collection_name": "phase15_multi_agent_demo"
    }
  }'

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/v1/multi-agent/runs/$($run.id)/execute-chain" `
  -Headers $headers `
  -ContentType application/json `
  -Body '{ "chain_name": "content_planning" }'

Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/v1/multi-agent/runs/$($run.id)/messages" `
  -Headers $headers

Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/v1/multi-agent/runs/$($run.id)/handoffs" `
  -Headers $headers
```

预期输出包含：

- `agents_involved`
- `agent_messages`
- `agent_handoffs`
- `handoff_trace`

## Phase 16 Planning Smoke Test

```powershell
$headers = @{ "X-Workspace-Id" = "demo-workspace"; "X-User-Id" = "demo-user" }

$plan = Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/plans `
  -Headers $headers `
  -ContentType application/json `
  -Body '{
    "root_goal": "生成 AI 自动化运营 TikTok 内容",
    "planner_agent": "simple_planner",
    "metadata": {
      "query": "ping",
      "platform": "tiktok",
      "style": "专业简洁"
    }
  }'

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/v1/plans/$($plan.id)/execute" `
  -Headers $headers `
  -ContentType application/json `
  -Body '{ "input": { "query": "ping" } }'

Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/v1/plans/$($plan.id)/steps" `
  -Headers $headers

Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/v1/plans/$($plan.id)/reviews" `
  -Headers $headers
```

预期输出包含：

- `plans`
- `plan_steps`
- `plan_reviews`
- `PlanStep.duration_ms`
- planning `memory_trace`

## Docs Runtime Verification

```powershell
python scripts/verify_docs_runtime.py
```

预期最终输出：

```text
SUMMARY: PASS
```

## 常见问题

### 缺少 Workspace Header

带 workspace 隔离的接口必须携带：

```http
X-Workspace-Id: demo-workspace
```

### Collection Dimension Mismatch

原因通常是同一 collection 混用了 mock embedding dimension `384` 和本地 `bge-m3` 实际维度。

处理方式：

- 使用新的 collection name。
- 或在测试环境中删除对应 Qdrant collection 和 `collections_metadata`。
- 不允许混写不同维度向量。

### Ollama Unreachable

检查：

```powershell
ollama serve
ollama list
```

也可以切回 mock provider。

## Browser Adapter Smoke Test

Phase 17 默认 `BROWSER_PROVIDER=mock`，不会启动真实浏览器。

创建 session：

```http
POST /api/v1/browser/sessions
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

```json
{
  "metadata": {
    "purpose": "deployment-smoke"
  }
}
```

执行 action：

```http
POST /api/v1/browser/actions
X-Workspace-Id: demo-workspace
```

```json
{
  "session_id": "uuid-from-create-session",
  "action_type": "navigate",
  "target": "https://example.com",
  "input_payload": {
    "wait": "none"
  }
}
```

验证：

```http
GET /api/v1/browser/actions/{session_id}
GET /api/v1/browser/logs/{session_id}
POST /api/v1/tools/browser_tool/execute
```

限制：

- 仅 `MockBrowserProvider` 真正可用。
- `PlaywrightBrowserProvider` 只是 placeholder。
- 不安装 Playwright / Selenium。

## Playwright Local Provider Smoke Test

Phase 18 支持 `PlaywrightLocalProvider`。Docker 镜像会安装 Playwright Python 与 Chromium：

```text
python -m playwright install --with-deps chromium
```

启用方式：

```powershell
$env:BROWSER_PROVIDER="playwright_local"
docker compose up --build -d
```

建议 smoke test：

```http
POST /api/v1/browser/sessions
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

```json
{
  "metadata": {
    "test": "phase18"
  }
}
```

```http
POST /api/v1/browser/actions
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

```json
{
  "session_id": "SESSION_ID",
  "action_type": "navigate",
  "target": "https://example.com"
}
```

截图：

```json
{
  "session_id": "SESSION_ID",
  "action_type": "screenshot",
  "screenshot_name": "example-home"
}
```

读取截图：

```http
GET /api/v1/browser/screenshot/{session_id}/example-home.png
X-Workspace-Id: demo-workspace
```

安全边界：

- 仅测试 `example.com`、本地页面、静态 `file://` 页面。
- 不做 TikTok / YouTube / X、登录、Cookie 注入、指纹绕过、代理池、验证码自动化、OCR、视觉 AI 或 Browser Worker。

## Remote Browser Worker Smoke Test

Phase 19 默认不启用 remote provider。要验证 Remote Browser Worker Foundation：

```powershell
$env:BROWSER_PROVIDER="remote"
docker compose up --build -d
```

注册同项目 mock worker runtime：

```http
POST /api/v1/browser-workers/register
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

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

Heartbeat：

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

Remote action：

```json
{
  "session_id": "SESSION_ID",
  "action_type": "navigate",
  "target": "https://example.com"
}
```

Mock runtime health：

```http
GET /api/v1/browser-worker-runtime/health
```

注意：这只是同项目 mock runtime，不是真实外部 Browser Worker 部署，不启动真实浏览器，不做平台自动化。
- 不做平台自动化、OCR、视觉 AI、真实登录流程。

## 正式服务器迁移说明

上线前仍需：

- 配置生产 PostgreSQL、Redis、Qdrant。
- 配置持久化 volume 和备份策略。
- 增加完整 RBAC、JWT、OAuth 或企业身份系统。
- 增加 HTTPS、反向代理、日志采集。
- 增加 Prometheus / Grafana。
- 增加真实 reranker 与 RAG 自动评估指标。
- 增加文件上传安全扫描、对象存储和异步 ingest。
## Phase 21 Worker Reliability 部署说明

新增环境变量：

```env
BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS=60
BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS=30
BROWSER_SESSION_TIMEOUT_SECONDS=1800
BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS=300
BROWSER_ACTION_TIMEOUT_SECONDS=60
BROWSER_ACTION_RETRY_COUNT=2
BROWSER_ACTION_RETRY_BACKOFF_SECONDS=2
SCREENSHOT_RETENTION_DAYS=7
```

Docker Compose 中 API 容器会挂载：

```text
./screenshots:/app/screenshots
./worker/screenshots:/app/worker/screenshots
```

用于让 `ScreenshotCleanupService` 同时覆盖 API 截图和独立 `browser-worker` 截图。

部署 smoke test：

```powershell
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Swagger 验证：

- `GET /api/v1/browser-workers/health/summary`
- `GET /api/v1/browser-workers/available`
- `POST /api/v1/browser-workers/{worker_id}/mark-offline`
- `POST /api/v1/browser-workers/cleanup-sessions`
- `POST /api/v1/browser/screenshots/cleanup`

注意：当前只验证 worker reliability，不启用 TikTok / YouTube / X 自动化、登录、代理、指纹绕过、验证码或真实平台自动化。

## Phase 22 Persistent Browser Profile 部署说明

Phase 22 为 browser session 增加 profile 持久化。API 在 PostgreSQL 中保存 profile 元数据，并把 profile 信息传递给当前 browser provider。独立 `browser-worker` 会把持久化 context 文件保存到 `worker/profiles/{workspace_id}/{profile_id}`。

## Phase 23 Browser Profile Health & Recovery 部署说明

Phase 23 需要随 API 服务启用以下运行配置：

```env
BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS=1800
BROWSER_PROFILE_BACKUP_ENABLED=true
BROWSER_PROFILE_MAX_BACKUPS=3
BROWSER_PROFILE_UNUSED_DAYS=30
BROWSER_PROFILE_BACKUP_ROOT=worker/profile_backups
```

Docker Compose 中 API 服务挂载 `./worker/profile_backups:/app/worker/profile_backups`，profile backup 会按 `workspace_id/profile_id` 分类保存为 zip。`browser_profiles.profile_path` 仍必须位于 `BROWSER_PROFILE_ROOT` 下，health check 会拒绝并标记损坏的越界或缺失路径。

部署后 smoke test：

```powershell
docker compose up --build -d
python -m pytest tests/test_profile_health.py tests/test_profile_recovery.py tests/test_profile_backup.py tests/test_profile_cleanup.py tests/test_profile_usage_logs.py
python scripts/verify_docs_runtime.py
```

Swagger 验证：

- `GET /api/v1/browser/profiles/health/summary`
- `POST /api/v1/browser/profiles/{profile_id}/health-check`
- `POST /api/v1/browser/profiles/recover-stale-locks`
- `POST /api/v1/browser/profiles/{profile_id}/backup`
- `GET /api/v1/browser/profiles/{profile_id}/backups`
- `POST /api/v1/browser/profiles/{profile_id}/restore`
- `POST /api/v1/browser/profiles/cleanup`
- `GET /api/v1/browser/profiles/{profile_id}/usage-logs`

生产迁移注意：

- 备份目录应使用持久卷，并纳入服务器备份策略。
- `dry_run=true` 是 profile cleanup 的默认值；正式删除前先审查响应中的 `matched_profiles` 和 `bytes_freed`。
- 如果 worker offline 或 session stale，先运行 `recover-stale-locks`，再创建新的 profile-backed session。
- 本阶段不增加社媒自动化、登录、Cookie 注入、代理池、指纹绕过或验证码能力。

新增环境变量：

```env
BROWSER_PROFILE_ROOT=worker/profiles
WORKER_PROFILE_DIR=worker/profiles
```

Docker Compose 需要挂载 profile 目录：

```text
./worker/profiles:/app/worker/profiles
```

部署 smoke test：

```powershell
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Swagger 验证：

- `POST /api/v1/browser/profiles`
- `GET /api/v1/browser/profiles`
- `POST /api/v1/browser/sessions`，请求体包含 `profile_id` 和 `use_persistent_profile=true`
- `POST /api/v1/browser/actions`，`navigate` 到 `https://example.com`
- `POST /api/v1/browser/actions`，执行 `screenshot`
- `POST /api/v1/browser/sessions/{session_id}/close`

预期结果：

- session 活跃期间 profile 状态为 `locked`。
- worker 对该 session 使用 `launch_persistent_context`。
- 关闭 session 后 profile 自动 release，并更新 `last_used_at`。
- 同一个 profile release 后可以再次创建 session 使用。

边界：本部署不启用 TikTok / YouTube / X 自动化、登录、Cookie 注入、代理池、指纹绕过、验证码或真实平台自动化。
## Phase 24 Human-in-the-loop Browser Control 部署说明

Phase 24 主要运行在 API Server：新增 human-control 数据表、Browser Session pause/resume 字段，以及 browser-worker 的 metadata-level 接管接口。当前不需要 VNC、noVNC、Chrome DevTools 远程 UI 或真实人工桌面。

新增运行配置：

```env
BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS=900
```

Docker Compose 会把该配置注入 API 服务。独立 `browser-worker` 暴露 metadata-level 接口：

```text
POST /human-control/start
POST /human-control/complete
GET /human-control/status/{session_id}
```

部署 smoke test：

```powershell
docker compose up --build -d
python -m pytest tests/test_browser_human_control.py tests/test_human_control_state_flow.py tests/test_human_control_api.py tests/test_browser_session_pause_resume.py tests/test_browser_tool_human_control.py
python scripts/verify_docs_runtime.py
```

Swagger 验证：

- `POST /api/v1/browser/human-control/request`
- `POST /api/v1/browser/human-control/{control_session_id}/approve`
- `POST /api/v1/browser/human-control/{control_session_id}/start`
- `POST /api/v1/browser/human-control/{control_session_id}/complete`
- `GET /api/v1/browser/human-control/{control_session_id}/events`
- `POST /api/v1/tools/browser_tool/execute`，`action_type=request_human_control`
- `POST /api/v1/tools/browser_tool/execute`，`action_type=complete_human_control`

预期结果：

- request 后 browser session 变为 `paused`。
- paused 期间普通 browser action 会被拒绝。
- complete 后 browser session 恢复为 `active`。
- human-control 窗口期间 profile lock 和 worker session 保持不释放。

边界：Phase 24 不实现 VNC、noVNC、DevTools 真实远程 UI、平台登录、验证码处理、Cookie 注入、代理池、指纹绕过或真实社媒平台自动化。
## Phase 25 Browser Worker UI Access Placeholder 部署说明

Phase 25 是后端 placeholder 层。它新增 `browser_ui_access_sessions`、token hash 校验、placeholder URL 和 worker capabilities，不启动 VNC/noVNC/DevTools 服务。

新增运行配置：

```env
BROWSER_UI_ACCESS_TIMEOUT_SECONDS=900
```

Worker 能力接口：

```text
GET http://localhost:9100/ui-access/capabilities
```

预期响应：

```json
{
  "vnc": false,
  "novnc": false,
  "devtools": false,
  "placeholder": true
}
```

部署 smoke test：

```powershell
docker compose up --build -d
python -m pytest tests/test_browser_ui_access.py tests/test_ui_access_token.py tests/test_ui_access_api.py tests/test_human_control_ui_access.py tests/test_browser_tool_ui_access.py
python scripts/verify_docs_runtime.py
```

Swagger 验证：

- `POST /api/v1/browser/ui-access`
- `GET /api/v1/browser/ui-access/{access_session_id}`
- `GET /api/v1/browser/ui-access/{access_session_id}/validate?token=TOKEN`
- `POST /api/v1/browser/ui-access/{access_session_id}/revoke`
- `POST /api/v1/browser/ui-access/expire`
- `GET /api/v1/browser-worker-runtime/ui-access/capabilities`
- `POST /api/v1/tools/browser_tool/execute`，`action_type=create_ui_access`
- `POST /api/v1/tools/browser_tool/execute`，`action_type=revoke_ui_access`

预期结果：

- create API 只返回一次明文 token。
- 后续读取 API 返回 `access_token=null`。
- revoke/expire 前 token validate 成功，撤销或过期后失败。
- `remote_control_url` 和 `live_view_url` 只是 placeholder URL。

边界：Phase 25 不启用真实 VNC、noVNC、DevTools UI、浏览器实时画面、平台登录、验证码处理、Cookie 注入、代理池、指纹绕过、TikTok / YouTube / X 或真实平台自动化。

## Phase 26 Browser Worker Security & Access Control 部署说明

Phase 26 不需要额外外部服务。它依赖 API Server、数据库 migration、现有 `browser-worker` 服务和以下运行配置：

```env
BROWSER_WORKER_AUTH_ENABLED=true
BROWSER_WORKER_AUTH_STRICT=false
BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1
BROWSER_BLOCKED_DOMAINS=
BROWSER_ALLOW_EXTERNAL_DOMAINS=false
```

本地 Docker 默认 `BROWSER_WORKER_AUTH_STRICT=false`，因此当 worker runtime 未配置共享 secret 时不会阻断 smoke test。API Server 注册 worker 后会保存 `worker_secret_hash`，明文 `worker_secret` 只在注册/rotate 响应中返回一次；同一进程内的 `BrowserWorkerClient` 会尽力签名请求。生产化时应把 worker secret 分发到 Worker 服务并开启 strict 模式。

部署验证：

```powershell
python -m pytest tests/test_browser_worker_auth.py tests/test_worker_signed_requests.py tests/test_ui_access_scopes.py tests/test_browser_action_policy.py tests/test_browser_security_audit_logs.py
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Swagger smoke：

- `POST /api/v1/browser-workers/register`，确认响应含一次性 `worker_secret`。
- `POST /api/v1/browser-workers/{worker_id}/heartbeat`，可携带 `X-Worker-Secret`。
- `POST /api/v1/browser-workers/{worker_id}/rotate-secret`。
- `POST /api/v1/browser/security/policy/check`，`https://example.com` 应允许，`https://not-allowed.example.org` 应被拦截。
- `POST /api/v1/browser/ui-access`，传入 `scopes` 和 `one_time`。
- `GET /api/v1/browser/ui-access/{id}/validate?token=TOKEN&scope=view`。
- `GET /api/v1/browser/security/audit-logs`。

边界：Phase 26 不实现真实平台账号安全、TikTok / YouTube / X 自动化、自动登录、Cookie 注入、代理池、指纹绕过、验证码处理或完整 RBAC/JWT/OAuth。

## Phase 27 Customer Machine Worker Bootstrap 部署说明

Phase 27 新增本地 `worker_client` 包，用于客户机 / Windows / Mac 机器接入 AI Server。它不需要新增 API Server 容器；Docker `browser-worker` 服务仍然可用，客户机 Worker 复用同一套注册、心跳和 Worker Runtime 协议。

客户机手动启动流程：

```powershell
Copy-Item worker_client\worker_config.example.yaml worker_client\worker_config.yaml
# 修改 server_url、workspace_id、worker_name、worker_base_url、runtime_port。
python -m worker_client.cli register
python -m worker_client.cli serve
python -m worker_client.cli heartbeat
```

一键启动流程：

```powershell
python -m worker_client.cli start
python -m worker_client.cli start --force-register
```

如果使用非默认配置文件，`--config` 是全局参数，必须放在子命令前：

```powershell
python -m worker_client.cli --config C:\path\worker_config.yaml register
python -m worker_client.cli --config C:\path\worker_config.yaml heartbeat --once
python -m worker_client.cli --config C:\path\worker_config.yaml serve --host 0.0.0.0 --port 9100
python -m worker_client.cli --config C:\path\worker_config.yaml start
```

部署验证：

```powershell
python -m pytest tests/test_worker_client_config.py tests/test_worker_client_registration.py tests/test_worker_client_heartbeat.py tests/test_worker_client_cli.py tests/test_worker_client_runtime_compatibility.py
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

安全说明：

- `worker_client/worker_config.yaml` 与 `worker_client/worker_state.json` 只保存在客户机本地，并已加入 `.gitignore`。
- `worker_state.json` 保存一次性明文 `worker_secret`，不能提交、打印或写入 docs。
- `heartbeat flow` 会发送 `X-Worker-Secret` 与 Phase 26 签名请求头。

边界：Phase 27 只是 Customer Machine Worker Bootstrap，不接 OpenClaw，不做 TikTok / YouTube / X 自动化、自动登录、Cookie 注入、代理池、指纹绕过、验证码处理或真实平台自动化。

## Phase 29 Worker Client Packaging

Windows:

```powershell
copy worker_client\worker_config.example.yaml worker_client\worker_config.yaml
.\packaging\windows_install_requirements.ps1
.\packaging\windows_register_worker.ps1
.\packaging\windows_start_worker.ps1
```

Mac:

```bash
cp worker_client/worker_config.example.yaml worker_client/worker_config.yaml
bash packaging/mac_install_requirements.sh
bash packaging/mac_register_worker.sh
bash packaging/mac_start_worker.sh
```

Local verification:

```text
GET http://127.0.0.1:9100/local/status
GET http://127.0.0.1:9100/local/health
GET http://127.0.0.1:9100/local/logs
```

Scripts include `packaging/windows_start_worker.ps1` and `packaging/mac_start_worker.sh`. Runtime writes `worker_client/runtime_state/status.json` and `worker_client/logs/worker.log`; both are ignored by Git. This is Worker Console Foundation only: no GUI, no exe/dmg packaging.

## Phase 30 Worker Console Deployment

Local development:

```powershell
python -m worker_client.cli start
cd worker_console
npm install
npm run dev
```

Open `http://localhost:5173`. The console uses `VITE_LOCAL_WORKER_API=http://127.0.0.1:9100`. Build with `npm run build`.

This is Web GUI Foundation only: no system tray, no auto update, no Electron, no Tauri, no PySide, no exe / dmg packaging.
## Phase 31：Worker Console Desktop 本地运行

桌面端仍依赖客户机本地 Worker API。先启动 `worker_client`：

```powershell
python -m worker_client.cli start
```

再启动 Tauri 桌面壳：

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

如果当前机器缺少 Rust 或 Tauri 系统依赖，可以先以 `npm run build` 作为前端构建验证，并检查 `worker_console_desktop/src-tauri/tauri.conf.json`。当前没有正式 exe / dmg，没有系统托盘，没有自动更新。

## Phase 32：System Tray 桌面运行

启动方式仍是开发模式：

```powershell
python -m worker_client.cli start
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

本阶段已有 System Tray 和 Minimize To Tray，但仍没有正式 installer，没有 exe / dmg，没有真正开机自启，没有 auto-update。

配置文件：

- `worker_console_desktop/settings.example.json`
- `worker_console_desktop/src-tauri/desktop-runtime.json`
- `worker_console_desktop/autostart/README.md`

安全说明：托盘菜单只触发本地 Worker API，不执行 shell，不执行远程命令。

## Phase 33 Runtime Notes

Conversation Runtime adds no new environment variable. It depends on the existing workspace headers and existing provider defaults.

Current defaults remain:

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
BROWSER_PROVIDER=mock
OPENCLAW_PROVIDER=mock
```

Conversation APIs require:

```text
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Worker Console chat clients use:

```text
VITE_AI_SERVER_API=http://localhost:8000/api/v1
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

Event feed mode: polling only through `GET /api/v1/conversations/{thread_id}/events`. WebSocket and SSE are placeholders only.

## Phase 34 Remote Browser Runtime Deployment

Deployment requirements:

- API Server must expose `BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots`.
- `docker-compose.yml` mounts `./storage:/app/storage` so runtime screenshots survive container restarts.
- Remote customer-machine workers must run the Worker Runtime API from `worker_client/runtime.py`.
- Customer machines that execute the real browser runtime must run `playwright install chromium`.
- Registered workers should include capabilities such as `{"browser_runtime": true, "browser": "chromium"}`.

Smoke test sequence:

1. Register or heartbeat an online worker.
2. `POST /api/v1/browser-runtime/sessions`
3. `POST /api/v1/browser-runtime/sessions/{session_id}/navigate`
4. `POST /api/v1/browser-runtime/sessions/{session_id}/screenshot`
5. `GET /api/v1/browser-runtime/sessions/{session_id}/page`
6. `POST /api/v1/browser-runtime/sessions/{session_id}/close`

Current deployment boundary: no stealth browser, no proxy, no login persistence, no cookie injection, no captcha bypass, no remote desktop stream, and no real platform automation.

## Phase 35B Real Client Worker E2E Deployment Check

Run after AI Server is online:

```powershell
python scripts\validate_real_client_worker_e2e.py `
  --server-url http://localhost:8000 `
  --workspace-id demo-workspace `
  --user-id demo-user `
  --expected-worker-name customer-machine-worker-1
```

Expected result before a real customer machine is connected: `SKIPPED` with reason `real client worker not online`.

Expected result when the customer machine worker is online: `PASS`, with screenshot metadata under `storage/browser_screenshots`.

Do not expose customer-machine port 9100 to the public internet. Use Tailscale, VPN, or LAN routing.

## Phase 35A Browser Runtime Observability Smoke Test

Docker 验证流程：

```powershell
docker compose up --build -d
```

Swagger / API 验证：

1. `GET /api/v1/health`
2. `POST /api/v1/browser-runtime/sessions`
3. `POST /api/v1/browser-runtime/sessions/{session_id}/navigate`
4. `POST /api/v1/browser-runtime/sessions/{session_id}/screenshot`
5. `GET /api/v1/browser-runtime/sessions/{session_id}/page`
6. `GET /api/v1/browser-runtime/sessions/{session_id}/events`
7. `GET /api/v1/browser-runtime/sessions/{session_id}/snapshots`
8. `POST /api/v1/browser-runtime/sessions/{session_id}/replay`
9. `GET /api/v1/browser-runtime/replays/{replay_id}/export`
10. `POST /api/v1/browser-runtime/sessions/{session_id}/close`

运行时目录：

```text
BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
```

Replay 当前只是 metadata-only replay，不重新执行浏览器动作；当前也不是 live stream、VNC/noVNC 或 DevTools remote control。

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
## Phase 38 部署与验证补充

Conversation Tool Execution Bridge 不新增独立服务。部署后使用已有 AI Server API 验证：创建 conversation，调用 `POST /api/v1/conversations/{thread_id}/run`，检查响应中的 `route_name`、`selected_tool`、`events_created`、`success`、`summary`、`result_metadata`，并通过 `GET /api/v1/conversations/{thread_id}/events` 查看 `route_selected`、`tool_execution_started`、`tool_execution_completed`、`agent_execution_started`、`planning_execution_started` 等事件。

边界：not autonomous agent，not WebSocket，not SSE，不做真实平台发布，不做真实 OpenClaw，不做 ComfyUI。

## Phase 39 部署验证

部署后需要验证 Approval Flow：

1. `POST /api/v1/conversations` 创建 thread。
2. `POST /api/v1/conversations/{thread_id}/run`，使用 `mode=review_first`。
3. `GET /api/v1/conversations/{thread_id}/approvals` 确认 `approval_status=pending`。
4. `POST /api/v1/conversation-approvals/{approval_id}/approve`。
5. `POST /api/v1/conversation-approvals/{approval_id}/execute`。
6. 再次 execute 应返回错误，避免重复执行。

当前不需要额外环境变量；审批流依赖数据库 migration `conversation_approvals`。生产迁移前必须先运行 Alembic，再更新 Admin Dashboard / Worker Console 静态包。当前不是完整权限系统，不做真实平台发布。
## Phase 40 部署验证：Conversation Playbooks

部署后建议 smoke test：

1. `GET /api/v1/conversation-playbooks`
2. `POST /api/v1/conversation-playbooks/{playbook_id}/run`，优先测试 `content_generation`
3. `POST /api/v1/conversations/{thread_id}/run`，传入 `playbook_name=browser_screenshot_report` 与 `mode=review_first`
4. 审批生成的 approval
5. `POST /api/v1/conversation-approvals/{approval_id}/execute`
6. `GET /api/v1/conversation-playbook-runs`

如果 browser 类 Playbook 卡在 `waiting_approval`，这是预期行为；不得在未批准时执行 medium/high risk step。

## Phase 41 部署补充

Output Library 需要 API 容器可写 `OUTPUT_ARTIFACT_DIR=storage/output_artifacts`。本阶段导出 markdown/json/txt 到本地磁盘；截图和 HTML snapshot 只引用既有路径。当前不接 S3 / MinIO，不是完整 DAM，也不做真实平台发布资产管理。
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
## Phase 46 Deployment Notes

Phase 46 adds workflow graph database tables and API routes only. Deploy migrations for `workflow_graphs`, `workflow_graph_nodes`, `workflow_graph_edges`, `workflow_replays`, and nullable graph lineage fields before enabling the updated Admin Dashboard and Worker Console builds. Runtime remains in-process and is not a distributed orchestration engine, not Kubernetes/Celery scheduling, and not ComfyUI.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47：部署说明

Phase 47 不新增外部基础设施依赖。部署后执行数据库 migration 即可启用 `workflow_templates`、`workflow_template_versions`、`workflow_template_runs`。前端 Admin Dashboard / Worker Console / Worker Console Desktop 通过 AI Server API 使用 Template Library、Validation result、Compatibility result、Import / Export JSON 和 Template runs。

边界：不需要 ComfyUI、DAG 可视化编辑器、WebSocket/SSE 或生产级分布式编排器。
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
