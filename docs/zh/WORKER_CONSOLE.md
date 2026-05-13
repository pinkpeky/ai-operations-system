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
