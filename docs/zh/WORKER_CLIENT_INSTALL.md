# Worker Client 安装与本地 Runtime 管理

状态：已完成，Phase 29。

本文说明客户机 Worker 的本地安装、注册、启动、状态、日志和 Worker Console Foundation。当前没有 GUI、系统托盘、Electron、Tauri、PySide、exe/dmg 打包或真实平台自动化。

## 当前能力

- `Worker Runtime Manager`：`worker_client/runtime_manager.py`
- 本地状态：`worker_client/status.py`
- 状态文件：`worker_client/runtime_state/status.json`
- 本地日志：`worker_client/logging.py`
- 日志文件：`worker_client/logs/worker.log`
- Local API client：`worker_client/local_api_client.py`
- Packaging Scripts：`packaging/windows_start_worker.ps1`、`packaging/mac_start_worker.sh`
- Desktop Runtime Placeholder：`worker_client/desktop/README.md`

## Windows

```powershell
copy worker_client\worker_config.example.yaml worker_client\worker_config.yaml
.\packaging\windows_install_requirements.ps1
.\packaging\windows_register_worker.ps1
.\packaging\windows_start_worker.ps1
```

停止：

```powershell
.\packaging\windows_stop_worker.ps1
```

## Mac

```bash
cp worker_client/worker_config.example.yaml worker_client/worker_config.yaml
bash packaging/mac_install_requirements.sh
bash packaging/mac_register_worker.sh
bash packaging/mac_start_worker.sh
```

停止：

```bash
bash packaging/mac_stop_worker.sh
```

## 本地管理 API

默认监听：

```text
http://127.0.0.1:9100
```

接口：

- `GET /local/status`
- `GET /local/health`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`
- `GET /local/logs`

## 安全说明

- `worker_client/worker_state.json` 保存明文 `worker_secret`，只存在客户机本地，已加入 `.gitignore`。
- `worker_client/runtime_state/status.json` 不包含 `worker_secret`。
- `worker_client/logs/worker.log` 会做基础 secret 脱敏。
- 不要把 `worker_config.yaml`、`worker_state.json`、runtime state 或 logs 提交到 Git。

## 当前边界

当前只是 Worker Console Foundation，不是 Worker Console GUI。未实现 GUI、系统托盘、Electron、Tauri、PySide、exe/dmg、TikTok / YouTube / X 自动化、自动登录、Cookie 注入、指纹绕过、代理池或验证码自动化。
## Phase 31：桌面控制台入口

Phase 31 新增 `worker_console_desktop`，作为 Tauri 桌面壳基础。安装并启动 `worker_client` 后，可以用桌面控制台连接本地 Local API：

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

当前仍没有正式安装包、no exe / dmg、no system tray、no auto update；这只是 Worker Console Desktop App Foundation。

## Phase 32：托盘运行说明

Phase 32 后，桌面端支持 System Tray 和 Minimize To Tray。启动方式不变：

```powershell
python -m worker_client.cli start
cd worker_console_desktop
npm run tauri dev
```

托盘菜单可以控制 Start Runtime、Stop Runtime、Restart Runtime、Start Heartbeat、Stop Heartbeat 和 Refresh Status。它只调用本地 Worker API，不执行 shell 命令。

当前仍没有正式 installer、没有 auto-update、没有真正开机自启。

## Phase 33 Chat Panel Foundation

Worker Console Web and Desktop now include a Chat Panel Foundation:

- input box
- Send button
- Message list
- Event Timeline
- Refresh events
- route display for planning / tool / worker status
- `conversationClient.ts` for AI Server conversation APIs

Configuration:

```text
VITE_AI_SERVER_API=http://localhost:8000/api/v1
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

The Event Timeline uses polling. It is not a ChatGPT-level UI, not WebSocket streaming, and not SSE streaming.

## Phase 34 Worker Browser Runtime Setup

Customer-machine workers can now host the Remote Browser Runtime. Install Playwright Chromium on the customer machine before using real browser runtime actions:

```powershell
python -m pip install playwright
playwright install chromium
```

Runtime endpoints exposed by `worker_client.runtime`:

- `POST /browser/session/create`
- `POST /browser/session/{session_id}/navigate`
- `POST /browser/session/{session_id}/screenshot`
- `GET /browser/session/{session_id}/page`
- `POST /browser/session/{session_id}/close`

The runtime implementation lives in `worker_client/browser_runtime`. It supports basic Chromium sessions, screenshots, and page content. It does not implement stealth, proxy, cookie injection, captcha bypass, platform automation, remote desktop streaming, or DevTools remote control.

## Phase 35B Real Client Worker E2E Checklist

After the customer machine is prepared:

```powershell
python -m worker_client.cli register --config worker_client\worker_config.yaml
python -m worker_client.cli start --config worker_client\worker_config.yaml
```

Then validate from AI Server:

```powershell
python scripts\validate_real_client_worker_e2e.py `
  --server-url http://localhost:8000 `
  --workspace-id demo-workspace `
  --user-id demo-user `
  --expected-worker-name customer-machine-worker-1
```

If the worker is not online, the script returns `SKIPPED` and `real client worker not online`. This is the correct result when the real customer machine is unavailable.

Do not expose port 9100 to the public internet; use Tailscale, VPN, or LAN.

## Phase 35A 说明：Runtime 可观测性

客户机 Worker 不需要新增真实平台能力。AI Server 会在 Browser Runtime 动作后记录 Timeline、Snapshots 和 Replay metadata。

客户机仍需满足 Phase 34 要求：

```powershell
playwright install chromium
```

Phase 35A 不会要求客户机提供 live stream、VNC/noVNC、DevTools remote control，也不会重新执行 replay。不要把 9100 端口暴露到公网；推荐 Tailscale、VPN 或可信局域网。

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
## Phase 38 对 worker_client 的影响

Phase 38 不改变 worker_client 安装流程。Conversation Runtime 通过 Browser Bridge 调用 `browser_tool` 时，仍依赖已注册且在线的 Browser Worker / worker_client runtime。若 worker 不在线，Conversation run 会通过 `tool_execution_failed` / `bridge_fallback` 返回清晰错误，不会伪造执行成功。

## Phase 41 对 worker_client 的影响

Phase 41 不改变 worker_client 安装流程。Output Library 在 AI Server 侧保存 artifacts；worker_client 仍只负责 Browser Runtime / Playwright 执行和结果回传。截图文件仍由既有 screenshot storage 管理，Output Library 只保存引用路径。
## Phase 42?Task Orchestration & Background Execution

????? Task Orchestration foundation?`task_runs`?`task_run_events`?`TaskOrchestratorService`?`BackgroundTaskExecutor`?`TaskRetryPolicy`?Conversation / Playbook ??? `execution_mode=background` ??????? `/api/v1/task-runs` ?? queued?running?waiting_approval?retrying?completed?failed?cancelled?expired ??? timeline?`scheduled_at` ?? scheduled run?retry ?? exponential backoff?approval resume ???? Phase 39 Approval Gate?Output Library artifacts ?? `task_run_id` ?? artifact linkage?

???????? in-process queue??? Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue???????????? OpenClaw?ComfyUI?????????????
## Phase 43?Task Scheduler Persistence & Worker Recovery?????

????Task Scheduler Persistence?`task_scheduler_state`?`task_runs` ? Task Lease ???`TaskRecoveryService`?Scheduler Health API?manual recovery API?Failed Diagnostics????? scheduler health ???

Task Lease?running task run ??? `lease_owner`?`lease_token`?`lease_expires_at`?`heartbeat_at`?expired lease ? stale heartbeat ??? scan ? manual recover ???

Recovery rules?running + expired lease ? stale heartbeat -> retrying????? retry budget ? failed?pending scheduled due -> queued?retrying delay elapsed -> queued?waiting_approval ??????completed/cancelled/expired ????

Admin Dashboard ?? Scheduler Health?lease status?recoverable badge?diagnostics panel?scheduled due indicator?manual recover?Worker Console ? Worker Console Desktop ???? Task recovery ???

??????? in-process scheduler foundation??? Celery??? Kubernetes???? production HA distributed queue?
