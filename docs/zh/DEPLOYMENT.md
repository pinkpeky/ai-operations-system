# 部署与本地验证

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
