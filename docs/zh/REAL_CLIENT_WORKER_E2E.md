# Real Client Worker E2E Validation

Status: completed validation plan and script. Real customer-machine E2E success must be executed later when the customer machine is online. Do not fabricate or backfill a passing real-client result.

## Goal

Validate the final Phase 34 chain:

```text
AI Server
-> RemoteBrowserProvider
-> BrowserWorkerSelector
-> real customer-machine worker_client
-> local browser_runtime
-> local Playwright Chromium
-> screenshot / page content / status returned to AI Server
```

## Customer Machine Preparation

Required:

- Python 3.11+
- project source or packaged `worker_client`
- Playwright
- Chromium browser runtime

Install:

```powershell
python -m pip install -r requirements.txt
python -m pip install playwright
playwright install chromium
```

Optional for Worker Console Desktop native validation:

- Node.js
- Rust
- MSVC Build Tools on Windows

If Rust/MSVC is not ready, mark desktop native validation pending. Do not pretend `npm run tauri dev` passed.

## worker_config.yaml Example

```yaml
server_url: http://AI_SERVER_HOST:8000
worker_name: customer-machine-worker-1
worker_type: playwright
workspace_id: demo-workspace
worker_secret: null
heartbeat_interval_seconds: 30
runtime_host: 127.0.0.1
runtime_port: 9100
capabilities:
  browser: chromium
  browser_runtime: true
  screenshot: true
  page_content: true
  persistent_profile: false
```

Security note: do not expose port 9100 to the public internet. Prefer Tailscale, VPN, or a trusted LAN. The worker runtime should listen on localhost unless there is an explicit private-network deployment reason.

## Worker Registration And Startup

```powershell
copy worker_client\worker_config.example.yaml worker_client\worker_config.yaml
python -m worker_client.cli register --config worker_client\worker_config.yaml
python -m worker_client.cli start --config worker_client\worker_config.yaml
```

The registration step stores `worker_state.json` locally. Do not commit it. Do not paste the worker secret into docs, issues, screenshots, or logs.

## Worker Console Checklist

Web Console:

```powershell
cd worker_console
npm.cmd run dev
```

Open:

```text
http://localhost:5173
```

Check:

- `registered=true`
- `runtime_running=true`
- `heartbeat_running=true`
- `current_status=online`
- logs show heartbeat success
- Browser Sessions Panel can refresh active sessions

Desktop Console:

```powershell
cd worker_console_desktop
npm.cmd run tauri dev
```

If Rust/MSVC is not installed or still being validated, record: `desktop native validation pending`.

## Swagger Validation Flow

Headers:

```text
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Steps:

1. `GET /api/v1/health`
2. `GET /api/v1/browser-workers/health/summary`
3. `GET /api/v1/browser-workers/available`
4. `POST /api/v1/browser-runtime/sessions`
5. `POST /api/v1/browser-runtime/sessions/{session_id}/navigate`
6. `POST /api/v1/browser-runtime/sessions/{session_id}/screenshot`
7. `GET /api/v1/browser-runtime/sessions/{session_id}/page`
8. `POST /api/v1/browser-runtime/sessions/{session_id}/close`

Create session:

```json
{
  "browser": "chromium",
  "metadata": {
    "phase": "35B",
    "source": "swagger"
  }
}
```

Navigate:

```json
{
  "url": "https://example.com"
}
```

Screenshot:

```json
{
  "full_page": true,
  "screenshot_name": "real-client-worker-e2e-example"
}
```

## E2E Script Validation

Run:

```powershell
python scripts\validate_real_client_worker_e2e.py `
  --server-url http://localhost:8000 `
  --workspace-id demo-workspace `
  --user-id demo-user `
  --expected-worker-name customer-machine-worker-1
```

Exit codes:

- `0`: PASS
- `1`: FAIL
- `2`: SKIPPED / client unavailable

If `expected_worker_name` is not online, the script returns `SKIPPED` with reason `real client worker not online` and does not execute browser actions.

## Server Configuration Checks

The script inspects:

- `BROWSER_PROVIDER`
- `BROWSER_WORKER_AUTH_ENABLED`
- `BROWSER_ALLOWED_DOMAINS` includes `example.com`
- browser runtime OpenAPI routes exist
- `storage/browser_screenshots` / `BROWSER_RUNTIME_SCREENSHOT_DIR`

If `BROWSER_PROVIDER` is not `remote`, the script emits a WARNING rather than failing. The Phase 34 browser runtime API can still be validated directly, but old browser action API paths may continue using the mock provider.

## Common Troubleshooting

- Worker not listed: verify `worker_config.yaml`, registration, workspace id, and heartbeat loop.
- Worker listed but not available: check `max_sessions`, `active_sessions`, `status`, and `capabilities.browser_runtime`.
- Browser action fails: run `playwright install chromium` on the customer machine.
- Screenshot missing: check `storage/browser_screenshots` on AI Server and local worker logs.
- Connection refused: do not open port 9100 publicly; use Tailscale, VPN, or LAN routing.

## Boundaries

Current Phase 35B is only a validation plan and script. It does not implement TikTok / YouTube / X automation, login automation, cookie injection, proxy pools, fingerprint bypass, captcha automation, real platform automation, OpenClaw real device, or ComfyUI.
## Phase 35A 调试扩展

完成真实客户机 E2E 后，可以继续调用 Browser Runtime Observability API 排查执行过程：

1. `GET /api/v1/browser-runtime/sessions/{session_id}/events`
2. `GET /api/v1/browser-runtime/sessions/{session_id}/snapshots`
3. `POST /api/v1/browser-runtime/sessions/{session_id}/replay`
4. `GET /api/v1/browser-runtime/replays/{replay_id}/export`

这些接口只生成 Timeline、Snapshot Storage 和 metadata-only replay；不会重新执行浏览器动作，也不是 live stream / VNC / noVNC / DevTools remote control。

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
## Phase 38 验证补充

真实客户机 Worker E2E 验证可增加 Conversation run 场景：创建 conversation 后发送“请打开 https://example.com 并截图”，检查 `route_name=browser`、`selected_tool=browser_tool`、`events_created`、`result_metadata`，以及事件 `route_selected`、`tool_execution_started`、`tool_execution_completed`。若客户机不在线，必须标记为 SKIPPED 或清晰失败，不允许伪造成功。

## Phase 41 验证补充

真实客户机完成 Playbook 或 Conversation 后，可验证 Output Library：`GET /api/v1/output-artifacts`、`POST /api/v1/output-artifacts/from-playbook-run/{run_id}`、`POST /api/v1/output-artifacts/from-message/{message_id}`、`GET /api/v1/output-artifacts/{artifact_id}/export?format=markdown`。截图 artifact 只引用路径，不复制大截图文件；当前不接 S3 / MinIO，也不是完整 DAM。
## Phase 42?Task Orchestration & Background Execution

????? Task Orchestration foundation?`task_runs`?`task_run_events`?`TaskOrchestratorService`?`BackgroundTaskExecutor`?`TaskRetryPolicy`?Conversation / Playbook ??? `execution_mode=background` ??????? `/api/v1/task-runs` ?? queued?running?waiting_approval?retrying?completed?failed?cancelled?expired ??? timeline?`scheduled_at` ?? scheduled run?retry ?? exponential backoff?approval resume ???? Phase 39 Approval Gate?Output Library artifacts ?? `task_run_id` ?? artifact linkage?

???????? in-process queue??? Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue???????????? OpenClaw?ComfyUI?????????????
## Phase 43?Task Scheduler Persistence & Worker Recovery?????

????Task Scheduler Persistence?`task_scheduler_state`?`task_runs` ? Task Lease ???`TaskRecoveryService`?Scheduler Health API?manual recovery API?Failed Diagnostics????? scheduler health ???

Task Lease?running task run ??? `lease_owner`?`lease_token`?`lease_expires_at`?`heartbeat_at`?expired lease ? stale heartbeat ??? scan ? manual recover ???

Recovery rules?running + expired lease ? stale heartbeat -> retrying????? retry budget ? failed?pending scheduled due -> queued?retrying delay elapsed -> queued?waiting_approval ??????completed/cancelled/expired ????

Admin Dashboard ?? Scheduler Health?lease status?recoverable badge?diagnostics panel?scheduled due indicator?manual recover?Worker Console ? Worker Console Desktop ???? Task recovery ???

??????? in-process scheduler foundation??? Celery??? Kubernetes???? production HA distributed queue?
