# 生产服务器正式配置基线

本文档记录真实服务器运行时必须满足的正式配置要求。它不是演示环境说明，也不是 production-like 彩排说明。

## 配置原则

- `APP_ENV=production` 才能视为真实服务器运行。
- 真实服务器不允许使用 `mock` provider 承担生产职责。
- ComfyUI 必须走 guarded runtime，明确 host/path allowlist，并开启 prompt submission。
- Browser Worker 必须开启严格鉴权；社媒自动发布必须使用真实 worker/runtime，不使用 mock browser。
- secrets 只允许放在服务器私有 `.env`、密钥管理系统或客户机本地状态文件中，不允许写入 docs、模板或 Git。
- 所有生产配置变更后必须运行 `scripts/check_production_config.py`。

## 已落地的校验入口

```powershell
.\.venv\Scripts\python.exe scripts\check_production_config.py
```

只审计、不让命令失败：

```powershell
.\.venv\Scripts\python.exe scripts\check_production_config.py --report-only
```

JSON 输出：

```powershell
.\.venv\Scripts\python.exe scripts\check_production_config.py --json --report-only
```

当 `.env` 中设置 `PRODUCTION_CONFIG_STRICT=true` 时，API 进程启动会执行同一套 blocking 校验。当前服务器还有 blocking findings 时，不要开启 strict，否则服务会按预期拒绝启动。

## 正式配置基线

| 配置项 | 正式值/要求 |
|---|---|
| `APP_ENV` | `production` |
| `PRODUCTION_CONFIG_STRICT` | blocking findings 清零后设为 `true` |
| `POSTGRES_PASSWORD` / `REDIS_PASSWORD` / `QDRANT_API_KEY` | 非空、非 placeholder、只在服务器私有配置中保存 |
| `LLM_PROVIDER` | `local` 或 `server`，不可为 `mock` |
| `EMBEDDING_PROVIDER` | `local`，不可为 `mock` |
| `RERANKER_PROVIDER` | `local`，并且本地服务必须提供真实 `/api/rerank` |
| `LOCAL_RERANKER_ALLOW_FALLBACK` | `false`，生产环境不允许静默回退 mock 分数 |
| `RERANKER_RUNTIME_ENGINE` | 当前正式基线为 `ollama_embedding` |
| `RERANKER_RUNTIME_EMBEDDING_MODEL` | 当前正式基线为 `bge-m3`，模型必须已下载并可被 Ollama 调用 |
| `BROWSER_PROVIDER` | `remote` 优先；单机受控场景可用 `playwright_local` |
| `BROWSER_ALLOWED_DOMAINS` | 真实业务域名 allowlist，不能保留 `example.com` |
| `BROWSER_WORKER_AUTH_ENABLED` | `true` |
| `BROWSER_WORKER_AUTH_STRICT` | `true` |
| `BROWSER_WORKER_SHARED_SECRET` | 非空、非 placeholder；API 与本机 Browser Worker 必须使用同一密钥 |
| `OPENCLAW_ENABLED` | 需要社媒自动发布时为 `true` |
| `OPENCLAW_PROVIDER` | 真实 worker/runtime 标签，例如 `worker_runtime`，不可为 `mock` |
| `COMFYUI_RUNTIME_PROVIDER` | `guarded` |
| `COMFYUI_RUNTIME_ENABLED` | `true` |
| `COMFYUI_RUNTIME_ALLOW_NETWORK` | `true` |
| `COMFYUI_RUNTIME_ALLOWED_HOSTS` | 只列 ComfyUI 实际 host |
| `COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED` | `true` |
| `COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS` | 至少包含 `/prompt,/history,/queue` |
| `DIGITAL_HUMAN_PROVIDER` | 真实本地 provider，例如 `local_musetalk_liveportrait` |
| `DIGITAL_HUMAN_ALLOW_EXTERNAL_API` | 默认 `false` |

## 当前服务器审计结论

审计日期：2026-05-28。

已满足：

- `APP_ENV=production`
- `LLM_PROVIDER=local`
- `EMBEDDING_PROVIDER=local`
- `RERANKER_PROVIDER=local`
- `LOCAL_RERANKER_ALLOW_FALLBACK=false`
- `COMFYUI_RUNTIME_PROVIDER=guarded`
- `COMFYUI_RUNTIME_ENABLED=true`
- `COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=true`
- `DIGITAL_HUMAN_PROVIDER=local_musetalk_liveportrait`
- `BROWSER_PROVIDER=remote`
- `BROWSER_WORKER_AUTH_ENABLED=true`
- `BROWSER_WORKER_AUTH_STRICT=true`
- `BROWSER_WORKER_SHARED_SECRET` 已设置在服务器私有 `.env`，文档不输出明文
- `BROWSER_ALLOWED_DOMAINS` 已替换为抖音相关域名与本机受控地址
- 数据库、Redis、Qdrant secrets 已设置且未在文档中输出明文

仍需修正的 blocking 项：

- `OPENCLAW_PROVIDER=mock`：OpenClaw 已启用，但 provider 仍是 mock 标签。

需要人工确认的 warning 项：

- `PRODUCTION_CONFIG_STRICT=false`：这是为了避免当前 blocking findings 直接导致真实服务启动失败。修完后应改为 `true`。
- `CORS_ALLOWED_ORIGINS` 仍包含 localhost / Tauri origin：如果客户机和管理端确实只在可信本机运行，可以保留；否则应替换为正式客户端域名。

## 下一步顺序

1. 补齐真实 OpenClaw runtime：`/openclaw/health`、`/openclaw/capabilities`、`/openclaw/actions` 必须由真实 worker 提供。
2. 把 `OPENCLAW_PROVIDER` 改成真实 worker/runtime 标签，并跑通 health、capabilities、action 三类接口。
3. 根据最终客户机形态确认 `CORS_ALLOWED_ORIGINS` 是否继续允许 localhost / Tauri origin。
4. 运行 `scripts/check_production_config.py`，确认 blocking findings 为 0。
5. 设置 `PRODUCTION_CONFIG_STRICT=true`，重启 API，进入正式配置保护状态。

## 本地 Browser Worker Runtime

当前服务器已经把 browser 执行链切到真实 remote worker：

```env
BROWSER_PROVIDER=remote
BROWSER_WORKER_AUTH_ENABLED=true
BROWSER_WORKER_AUTH_STRICT=true
BROWSER_WORKER_SHARED_SECRET=<server-private-secret>
BROWSER_ALLOWED_DOMAINS=douyin.com,v.douyin.com,open.douyin.com,iesdouyin.com,amemv.com,localhost,127.0.0.1
```

运行与验证脚本：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\start_browser_worker_aiops.ps1 -Force
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\verify_browser_worker_aiops.ps1
```

`verify_browser_worker_aiops.ps1` 会检查三件事：`/health` 可达、未签名请求在 strict 模式下被 401 拒绝、签名请求可以创建并关闭真实 Playwright browser session。Worker 的 session/action/browser-runtime/human-control 控制面都走同一套签名校验。

当前已注册开机任务：

- `AI Ops Browser Worker`

Phase 68W 后，API 已可在 Docker 中运行，宿主机 `worker.main:app` 作为正式客户机 worker 注册到 `production-workspace`。`worker_client/worker_config.yaml` 与 `worker_client/worker_state.json` 都是本机私有文件并被 Git 忽略；前者记录服务器 URL、worker 名称、workspace、base URL，后者保存 API 注册返回的一次性 `worker_secret`。由于 API 在 Docker 内，写入数据库的 worker base URL 应为 `http://host.docker.internal:9100`，本机直接验证才使用 `http://127.0.0.1:9100`。

如果 Docker 自动拉起了 `aiops-browser-worker`，应先停止该容器，避免它和宿主机 worker 争用 9100：

```powershell
docker stop aiops-browser-worker
```

注册和心跳命令：

```powershell
.\.venv\Scripts\python.exe -m worker_client.cli --config worker_client\worker_config.yaml register --force
.\.venv\Scripts\python.exe -m worker_client.cli --config worker_client\worker_config.yaml heartbeat --once
```

注册完成后，API 侧应能在以下接口看到 `aiops-production-browser-worker`：

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/browser-workers/health/summary" `
  -Headers @{ "X-Workspace-Id" = "production-workspace" }
```

登记脚本：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\register_browser_worker_with_api.ps1 -WorkspaceId "<workspace-id>"
```

当前生产 workspace 示例：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\register_browser_worker_with_api.ps1 -WorkspaceId "production-workspace" -WorkerName "aiops-production-browser-worker"
```

## 部署模板

正式单服务器模板在：

```text
deployment/profiles/production-server/env.template
```

模板中的 secret 和域名必须替换后才能用于真实 `.env`。

## 本地 Reranker Runtime

当前仓库已经包含独立 reranker runtime：

```powershell
.\.venv\Scripts\uvicorn.exe worker.reranker_worker.main:app --host 0.0.0.0 --port 8002
```

正式路径：

- `GET /health`：检查 Ollama embedding 后端是否可用。
- `POST /api/rerank`：输入 `query` 与 `documents`，返回与 documents 原始顺序一致的 `scores`。

当前 runtime 使用 `RERANKER_RUNTIME_ENGINE=ollama_embedding`。这不是 mock：它会调用本地 Ollama embedding 模型计算 query/document 语义分数。但它也不是 cross-encoder 精排模型；后续如果接入独立 cross-encoder 服务，需要保持同样的 `/health` 与 `/api/rerank` 契约。

详细运行说明见 `docs/LOCAL_RERANKER_RUNTIME.md`。

当前服务器已注册四个开机任务：

- `AI Ops ComfyUI CU130`
- `AI Ops Ollama D Drive`
- `AI Ops Reranker Worker`
- `AI Ops Browser Worker`
