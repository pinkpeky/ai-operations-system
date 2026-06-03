# 本地 Reranker Runtime

本文档记录本节新增的正式本地 reranker runtime。它用于替换生产配置中的 `RERANKER_PROVIDER=mock`，服务形态是一个独立 FastAPI worker。

## 目标

- 给主 API 提供稳定的 `GET /health` 和 `POST /api/rerank`。
- 使用本地模型服务计算 query/document 语义相关性，不使用 mock 分数。
- 生产环境设置 `LOCAL_RERANKER_ALLOW_FALLBACK=false`，reranker 不可用时 fail closed。

## 当前实现

代码入口：

- `worker/reranker_worker/main.py`
- `worker/reranker_worker/runtime.py`
- `worker/reranker_worker/config.py`
- `worker/reranker_worker/schemas.py`

当前 engine：

```text
RERANKER_RUNTIME_ENGINE=ollama_embedding
```

该 engine 会调用 Ollama：

```text
POST /api/embeddings
```

使用 `RERANKER_RUNTIME_EMBEDDING_MODEL` 生成 query 和 documents 向量，然后计算 cosine score。该实现是正式可运行的语义 reranker 基线，但不是 cross-encoder 精排。后续接入 cross-encoder 时必须保持同样的 worker API 契约。

## 启动

PowerShell：

```powershell
$env:RERANKER_RUNTIME_EMBEDDING_BASE_URL="http://127.0.0.1:11434"
$env:RERANKER_RUNTIME_EMBEDDING_MODEL="bge-m3"
.\.venv\Scripts\uvicorn.exe worker.reranker_worker.main:app --host 0.0.0.0 --port 8002
```

Docker Compose：

```powershell
docker compose up -d reranker-worker
```

## 主 API 配置

主 API 切换到正式 reranker 时使用：

```text
RERANKER_PROVIDER=local
LOCAL_RERANKER_BASE_URL=http://host.docker.internal:8002
LOCAL_RERANKER_MODEL=bge-m3-embedding-reranker
LOCAL_RERANKER_ALLOW_FALLBACK=false
```

如果 API 和 reranker worker 都在 Docker Compose 网络内运行，可使用：

```text
LOCAL_RERANKER_BASE_URL=http://reranker-worker:8002
```

## 接口

健康检查：

```http
GET /health
```

返回字段：

- `provider`
- `model`
- `engine`
- `embedding_model`
- `reachable`
- `enabled`
- `dimension`
- `error`

精排：

```http
POST /api/rerank
```

请求：

```json
{
  "model": "bge-m3-embedding-reranker",
  "query": "客户运营目标",
  "documents": ["候选文本 1", "候选文本 2"],
  "top_n": 1
}
```

响应：

```json
{
  "provider": "local",
  "model": "bge-m3-embedding-reranker",
  "engine": "ollama_embedding",
  "embedding_model": "bge-m3",
  "scores": [0.51, 0.94],
  "ranked_indices": [1],
  "top_n": 1
}
```

`scores` 的顺序必须和输入 `documents` 一致，主 API 会据此排序。

## 当前服务器状态

2026-05-28 已确认 `D:\ollama\models` 是当前 Ollama 模型目录，`bge-m3:latest`、`llama70b:latest` 和 `llama3.3:70b` 可见。当前服务器已启动：

- Ollama: `http://127.0.0.1:11434`
- Reranker worker: `http://127.0.0.1:8002`

并已注册开机任务：

- `AI Ops Ollama D Drive`
- `AI Ops Reranker Worker`

验证命令：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\verify_ollama_reranker_aiops.ps1
```

主 API `.env` 已切到：

```text
RERANKER_PROVIDER=local
LOCAL_RERANKER_BASE_URL=http://127.0.0.1:8002
LOCAL_RERANKER_ALLOW_FALLBACK=false
```

变更后运行：

```powershell
.\.venv\Scripts\python.exe scripts\check_production_config.py
```
