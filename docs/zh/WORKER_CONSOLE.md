# Worker Console GUI Foundation

状态：已完成，Phase 30。

`worker_console` 是客户机 Worker 的本地 Web GUI Foundation。它是独立 Vite + React + TypeScript + Tailwind 前端项目，默认连接本地 Worker API：

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

## 当前页面

Dashboard：

- `worker_name`
- `worker_id`
- `workspace_id`
- `server_url`
- `registered`
- `runtime_running`
- `heartbeat_running`
- `current_status`
- `last_heartbeat_at`
- `last_error`

Runtime Control：

- Start Runtime
- Stop Runtime
- Restart Runtime
- Start Heartbeat
- Stop Heartbeat

Logs：

- 调用 `GET /local/logs`
- 支持 refresh
- 高亮 error / failed / exception / traceback 行

Connection Info：

- `server_url`
- `worker_base_url`
- `runtime_port`
- `openclaw_enabled`
- `browser_enabled`

## Local API Client

前端 client 文件：

```text
worker_console/src/api/localWorkerClient.ts
```

支持：

- `getStatus`
- `getHealth`
- `getLogs`
- `startRuntime`
- `stopRuntime`
- `restartRuntime`
- `startHeartbeat`
- `stopHeartbeat`

## 启动方式

```powershell
python -m worker_client.cli start
cd worker_console
npm install
npm run dev
```

打开：

```text
http://localhost:5173
```

如果本地 Worker API 不可用，页面显示：

- `Worker API unreachable`
- `请确认 worker_client 是否启动`
- `请确认端口是否为 9100`

## 当前边界

当前只是本地 Web GUI Foundation，不是桌面应用。当前没有 system tray，没有自动更新，没有 Electron，没有 Tauri，没有 PySide，没有 no exe / dmg 打包。未来可接 Tauri / Electron / PySide / system tray / auto start / exe / dmg。

不包含 TikTok / YouTube / X 自动化、账号登录、Cookie 注入、代理池、指纹绕过、验证码自动化或真实平台自动化。

Boundary marker: no system tray, no auto update, no Electron, no Tauri, no PySide, no exe / dmg.

## Phase 31：Worker Console Desktop App Foundation

状态：已完成，Phase 31。

`worker_console_desktop` 是当前 Worker Console 的 Tauri 桌面壳基础。它复用 Phase 30 的本地 Worker API 契约，默认连接：

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

### 桌面壳能力

- 打开 Tauri 窗口。
- 显示 Worker status、Runtime status、Heartbeat status、Connection Info 和 Logs。
- 调用 `GET /local/status`、`GET /local/health`、`GET /local/logs`。
- 调用 `POST /local/runtime/start`、`POST /local/runtime/stop`、`POST /local/runtime/restart`。
- 调用 `POST /local/heartbeat/start`、`POST /local/heartbeat/stop`。
- 本地 Worker API 不可达时显示：`Worker API unreachable`、`Worker Runtime 未启动`、`请先启动 worker_client`、`packaging 脚本启动`。

### 开发启动

```powershell
python -m worker_client.cli start
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

### 当前边界

当前只是 Worker Console Desktop App Foundation。没有正式安装包，没有 no exe / dmg，没有系统托盘，没有 no system tray，没有开机自启，没有自动更新，没有 no auto update。未来可在此基础上继续增加 tray / autostart / installer。

本阶段仍不包含 TikTok / YouTube / X 自动化、账号登录、Cookie 注入、代理池、指纹绕过、验证码自动化或真实平台自动化。

## Phase 32：Worker Console System Tray & Desktop Runtime Foundation

状态：已完成，Phase 32。

`worker_console_desktop` 现在从桌面壳基础升级为桌面 Runtime 基础，新增 Tauri System Tray、Minimize To Tray、Tray Runtime Control 和 Desktop Status Sync。

### System Tray

托盘菜单包含：

- Show Console
- Hide Window
- Start Runtime
- Stop Runtime
- Restart Runtime
- Start Heartbeat
- Stop Heartbeat
- Refresh Status
- Quit

Show Console 会显示窗口，Hide Window 会隐藏窗口，Quit 才真正退出程序。

### Minimize To Tray

默认配置：

```json
{
  "minimize_to_tray": true
}
```

配置文件：`worker_console_desktop/src-tauri/desktop-runtime.json`。点击窗口关闭按钮时默认隐藏到托盘，不退出进程。

### Tray Runtime Control

托盘菜单不会执行 shell 命令，也不会执行远程命令。托盘动作会发送给前端，由前端调用本地 Worker API：

- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`

### Desktop Status Sync

桌面端定时调用：

- `GET /local/status`
- `GET /local/health`

托盘 tooltip 显示 `worker_name`、`current_status`、`runtime_running`、`heartbeat_running`。UI 显示 connected、reconnecting、disconnected、online、offline、error，以及 last successful sync 和 last error。

### AutoStart Placeholder

新增占位目录：`worker_console_desktop/autostart/`。当前只是 AutoStart Placeholder，说明未来可支持 Windows registry startup、macOS LaunchAgent 和 start on login。本阶段没有真正开机自启。

### 当前边界

当前没有正式 installer，没有正式安装包，没有 exe / dmg，没有真正开机自启，没有 auto-update / 自动更新，没有远程 shell，没有任意命令执行。仍不包含 TikTok / YouTube / X 自动化、账号登录、Cookie 注入、代理池、指纹绕过、验证码自动化或真实平台自动化。

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

## Phase 34 Browser Sessions Panel

Worker Console Web and Worker Console Desktop now include a Browser Sessions Panel for Remote Browser Runtime Foundation.

The panel shows:

- active sessions
- worker id
- browser
- status
- created_at
- current_url

Supported actions:

- refresh active sessions
- close a runtime session through `POST /api/v1/browser-runtime/sessions/{session_id}/close`

Client files:

- `worker_console/src/api/browserRuntimeClient.ts`
- `worker_console_desktop/src/api/browserRuntimeClient.ts`

This is not live streaming, not VNC, not noVNC, not DevTools remote UI, and not a browser-control visual stream.

## Phase 35B Worker Console Validation Checklist

Web Console:

```powershell
cd worker_console
npm.cmd run dev
```

Open `http://localhost:5173` and check:

- `registered=true`
- `runtime_running=true`
- `heartbeat_running=true`
- `current_status=online`
- logs include heartbeat success
- Browser Sessions Panel can refresh sessions

Desktop Console:

```powershell
cd worker_console_desktop
npm.cmd run tauri dev
```

If Rust/MSVC is not ready, mark `desktop native validation pending` and do not report native desktop validation as passed.

## Phase 35A Browser Runtime Timeline / Snapshots / Replay

Worker Console Web 和 Worker Console Desktop 的 Browser Sessions Panel 已增强：

- Timeline：调用 `GET /api/v1/browser-runtime/sessions/{session_id}/events`
- Screenshot history：从 `browser_runtime_snapshots` 读取 `snapshot_type=screenshot`
- Page snapshots：从 `browser_runtime_snapshots` 读取 `snapshot_type=page`
- Replay metadata：调用 `POST /api/v1/browser-runtime/sessions/{session_id}/replay`
- Replay export：调用 `GET /api/v1/browser-runtime/replays/{replay_id}/export`
- Refresh events / Refresh snapshots：polling 查询，不是 live stream

当前 Replay 是 metadata-only replay，不重新执行浏览器动作。当前没有 VNC、noVNC、DevTools remote control、live browser stream，也不做 TikTok / YouTube / X、登录、Cookie 注入、代理池、指纹绕过、验证码或真实平台自动化。

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
## Phase 38：Worker Console Chat Panel Bridge

Worker Console 和 Worker Console Desktop 的 Chat Panel 已展示 `route_name`、`selected_tool`、run status、result summary、`result_metadata` 和 event payload。Browser Bridge、OpenClaw mock bridge、RAG bridge、Content bridge、Planning bridge 均通过 Conversation Runtime polling 事件展示。当前不是 WebSocket，不是 SSE，不做真实平台自动化。

## Phase 39：Conversation Approval Panel

Worker Console Web 和 Worker Console Desktop 的 Chat Panel 已新增 pending approvals panel。面板展示 proposed action preview、proposed payload JSON、risk badge、approval_status，以及 approve / reject / cancel / execute approved action 控制。

Chat Panel 默认使用 `review_first` 运行用户消息，让 Browser / OpenClaw 类动作先进入审批队列再执行。前端调用 `GET /api/v1/conversations/{thread_id}/approvals` 以及 `/api/v1/conversation-approvals/{approval_id}` 的 approve / reject / cancel / execute API。

当前边界：不是完整权限系统，not a full permission system；不是 WebSocket/SSE；不做真实平台发布、真实 OpenClaw、登录、验证码、代理或指纹绕过。
## Phase 40：Worker Console Playbook Entry

Worker Console Web 和 Desktop Chat Panel 增加 Playbook selector、Run playbook、Playbook runs 和 Step timeline 展示。

该入口主要用于客户机侧快速触发标准化 Conversation Playbook，但仍然：

- 使用 polling，不是 WebSocket/SSE。
- 保留 pending approvals panel。
- medium/high risk step 必须审批后执行。
- 不实现完整 workflow builder。
- 不做真实平台发布、登录、验证码、代理、指纹或真实 OpenClaw。

## Phase 41：Worker Console Output Library

Worker Console Web 和 Desktop Chat Panel 增加 Output Library 基础展示：

- generated artifacts list
- assistant message 的 Save as Artifact
- artifact type / source type badge
- related `playbook_run_id`
- Export markdown

该能力用于查看 Playbook / Conversation 生成的 `content_draft`、`report`、`rag_answer`、`screenshot`、`html_snapshot`、`plan`、`json` 等产物。当前只是 Output Library Foundation，不是完整 DAM，不接 S3 / MinIO，也不做真实平台发布资产管理。
## Phase 42?Task Orchestration & Background Execution

????? Task Orchestration foundation?`task_runs`?`task_run_events`?`TaskOrchestratorService`?`BackgroundTaskExecutor`?`TaskRetryPolicy`?Conversation / Playbook ??? `execution_mode=background` ??????? `/api/v1/task-runs` ?? queued?running?waiting_approval?retrying?completed?failed?cancelled?expired ??? timeline?`scheduled_at` ?? scheduled run?retry ?? exponential backoff?approval resume ???? Phase 39 Approval Gate?Output Library artifacts ?? `task_run_id` ?? artifact linkage?

???????? in-process queue??? Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue???????????? OpenClaw?ComfyUI?????????????
## Phase 43?Task Scheduler Persistence & Worker Recovery?????

????Task Scheduler Persistence?`task_scheduler_state`?`task_runs` ? Task Lease ???`TaskRecoveryService`?Scheduler Health API?manual recovery API?Failed Diagnostics????? scheduler health ???

Task Lease?running task run ??? `lease_owner`?`lease_token`?`lease_expires_at`?`heartbeat_at`?expired lease ? stale heartbeat ??? scan ? manual recover ???

Recovery rules?running + expired lease ? stale heartbeat -> retrying????? retry budget ? failed?pending scheduled due -> queued?retrying delay elapsed -> queued?waiting_approval ??????completed/cancelled/expired ????

Admin Dashboard ?? Scheduler Health?lease status?recoverable badge?diagnostics panel?scheduled due indicator?manual recover?Worker Console ? Worker Console Desktop ???? Task recovery ???

??????? in-process scheduler foundation??? Celery??? Kubernetes???? production HA distributed queue?
## Phase 43??? Task Recovery ??

Worker Console Web ? Worker Console Desktop ???? scheduler ? task recovery ???scheduler health?recovered count?lease expiry?recoverable state?suggested action?manual recover?????????? shell ????????? scheduler console?
