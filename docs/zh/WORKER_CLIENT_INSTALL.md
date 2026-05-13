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
