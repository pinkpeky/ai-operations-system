# 部署与运行

更新时间：2026-05-12

本文记录当前真实代码的本地运行、Docker 验证、Ollama 验证、文件上传验证和 docs runtime 验证流程。

## 本地前置条件

需要：

- Python 3.11+
- Docker Desktop
- Docker Compose
- 可选：Ollama
- 可选本地模型：`mistral`、`bge-m3`

默认 Docker smoke test 使用 mock provider，不强制依赖 Ollama 在线。

## 安装依赖

```powershell
python -m pip install -r requirements.txt
```

Phase 11 新增依赖：

- `python-multipart`
- `pypdf`
- `python-docx`
- `pandas`

用途：

- multipart upload
- PDF 文本抽取
- DOCX 文本抽取
- CSV 文本抽取

## 单元测试

```powershell
python -m pytest
```

每次改代码后必须先跑 pytest。

## Docker 启动

```powershell
docker compose up --build -d
```

Swagger：

```text
http://localhost:8000/docs
```

Docker Compose 当前服务：

- api
- postgres
- redis
- qdrant
- scheduler

## 配置文件

当前默认配置见：

- `app/core/config.py`
- `.env.example`
- `docker-compose.yml`
- `docs/CURRENT_RUNTIME.md`

默认 provider：

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
```

上传默认配置：

```text
MAX_UPLOAD_FILE_SIZE_MB=20
UPLOAD_TEMP_DIR=/tmp/aiops_uploads
ALLOWED_FILE_TYPES=pdf,docx,txt,md,csv
```

## Ollama 启动方式

如果要使用真实本地 LLM / embedding：

```powershell
ollama serve
ollama list
```

需要看到：

```text
mistral
bge-m3
```

`.env` 示例：

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

重启：

```powershell
docker compose up --build -d
```

## Swagger Smoke Test

健康检查：

```http
GET /api/v1/health
GET /api/v1/llm/health
GET /api/v1/rag/embedding/health
GET /api/v1/reranker/health
```

文件上传：

```http
POST /api/v1/files/upload
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
Content-Type: multipart/form-data
```

Form：

```text
file=@knowledge.md
collection_name=phase11_file_upload_demo
duplicate_strategy=force_reingest
chunk_size=800
chunk_overlap=80
```

RAG search：

```http
POST /api/v1/rag/search
X-Workspace-Id: demo-workspace
```

```json
{
  "query": "File Upload Pipeline Docs Runtime Verification",
  "search_mode": "hybrid",
  "dense_top_k": 20,
  "keyword_top_k": 20,
  "final_top_k": 5,
  "collection_name": "phase11_file_upload_demo"
}
```

Agentic RAG：

```http
POST /api/v1/agentic-rag/query
X-Workspace-Id: demo-workspace
```

```json
{
  "query": "Phase 11 增加了什么？",
  "collection_name": "phase11_file_upload_demo",
  "top_k": 3,
  "debug": true
}
```

## Docs Runtime Verification

```powershell
python scripts/verify_docs_runtime.py
```

通过标准：

```text
SUMMARY: PASS
```

如果出现 `ERROR`，必须修正文档或代码后重跑。

如果出现 `WARNING`，需要判断是否为可接受提醒；正式交付建议保持无 warning。

## 常见错误

### 缺少 X-Workspace-Id

现象：

```json
{
  "detail": "缺少工作区上下文"
}
```

解决：

```http
X-Workspace-Id: demo-workspace
```

### collection dimension mismatch

原因：

- 同一 collection 曾使用 mock embedding `384` 维。
- 后续切换到 local `bge-m3`，实际维度不同。

处理：

- 使用新的 collection name。
- 或在测试环境删除旧 collection 和 metadata。
- 不要在同一 collection 混写不同 embedding dimension。

### Ollama 不可达

现象：

- `/api/v1/llm/health` 或 `/api/v1/rag/embedding/health` 返回 `reachable=false`。

解决：

```powershell
ollama serve
ollama pull mistral
ollama pull bge-m3
```

或者切回：

```env
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
```

### 文件上传 parser 错误

可能原因：

- 文件类型不在 `ALLOWED_FILE_TYPES`。
- PDF 是扫描件，没有可提取文本。
- 文件超过 `MAX_UPLOAD_FILE_SIZE_MB`。
- TXT/MD 不是 UTF-8。

## 正式服务器迁移说明

正式部署前需要补齐：

- `.env` 中的生产数据库、Redis、Qdrant 地址。
- 持久化卷和备份策略。
- 正式鉴权系统。
- API key 权限边界。
- HTTPS / 反向代理。
- 日志采集。
- Prometheus / Grafana。
- 真实 reranker 和 eval 指标。
- 文件上传病毒扫描、对象存储、异步 ingest。

当前 Phase 11 仍是后端基础能力，不是完整生产安全网关。
