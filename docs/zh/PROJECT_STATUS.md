# 项目状态

更新时间：2026-05-12

本文是中文主开发状态文档。当前项目路径为 `E:\ai-operations-system`。

## 总体状态

Phase 1 到 Phase 11 已完成。

当前系统已经具备后端 AI 自动化运营基础能力：

- FastAPI API 服务。
- PostgreSQL / Redis / Qdrant / Docker Compose。
- SQLAlchemy ORM 与 Alembic migration。
- Redis Queue、Scheduler、TaskExecutor。
- LLM Client Layer。
- Ollama Mistral 本地 LLM 接口。
- Embedding Pipeline。
- Ollama bge-m3 本地 embedding 接口。
- Knowledge Lifecycle。
- Workspace / User / API Key 隔离基础。
- Agentic RAG Orchestrator。
- ContentAgent 示例。
- RAG Eval / Debug Trace。
- Reranker Provider Layer。
- Hybrid Search。
- File Upload Pipeline。
- Docs Runtime Verification。

## 已完成 Phase

| Phase | 状态 | 说明 |
| --- | --- | --- |
| Phase 1 | 已完成 | Docker、PostgreSQL、Redis、Qdrant、FastAPI、health check。 |
| Phase 2 | 已完成 | ORM、tasks/accounts/publish_logs、Redis Queue、Scheduler、Task API。 |
| Phase 2.5 | 已完成 | LLM Client Layer、MockProvider、LocalProvider、ServerProvider、Prompt Manager。 |
| Phase 3 | 已完成 | Embedding Pipeline、Qdrant Collection Layer、RAG ingest/search 基础能力。 |
| Phase 3.5 | 已完成 | embedding 归一化、score normalizer、collection health、RAG debug API。 |
| Phase 4 | 已完成 | Agentic RAG 单一编排器。 |
| Phase 4.5 | 已完成 | Agentic RAG Task Executor handler 与 task API。 |
| Phase 4.6 | 已完成 | Ollama Mistral local LLM 接口与 LLM health check。 |
| Phase 5 | 已完成 | BaseAgent、ContentAgent、content_generation task。 |
| Phase 6 | 已完成 | documents、document_chunks、collections_metadata、source versioning、delete/reingest。 |
| Phase 6.5 | 已完成 | users、workspaces、workspace_members、api_keys、workspace middleware。 |
| Phase 7 | 已完成 | Ollama bge-m3 local embedding，自动检测 embedding dimension。 |
| Phase 8 | 已完成 | rag_eval_runs、rag_eval_items、Agentic RAG trace。 |
| Phase 9 | 已完成 | Reranker Provider Layer，mock/local provider，rerank trace。 |
| Phase 10 | 已完成 | Dense + Keyword -> Merge -> Rerank -> LLM 的 Hybrid Search。 |
| Phase 10.5 | 已完成 | 中英文 Docs System、PROJECT_OVERVIEW、CURRENT_RUNTIME、Docs SSOT。 |
| Phase 11 | 已完成 | File Upload Pipeline 与 Docs Runtime Verification。 |

## Phase 11 完成内容

File Upload Pipeline：

- 新增 `app/file_pipeline/`。
- 支持上传 PDF、DOCX、TXT、MD、CSV。
- 上传接口：`POST /api/v1/files/upload`。
- multipart/form-data。
- 自动保存临时文件、计算 `file_hash`、解析文本、清洗文本、调用 DocumentLifecycle ingest。
- 自动写入 `documents`、`document_chunks`、Qdrant。
- 自动记录文件 metadata：`filename`、`file_type`、`file_size`、`file_hash`、`ingest_status`、`ingest_error`、`chunk_count`。
- 支持基于 `file_hash + workspace_id` 的重复检测。
- 支持 `duplicate_strategy=skip` 和 `duplicate_strategy=force_reingest`。
- 临时文件在成功或失败后都会清理。

Docs Runtime Verification：

- 新增 `scripts/verify_docs_runtime.py`。
- 新增中文说明：`docs/zh/DOCS_RUNTIME_VERIFICATION.md`。
- 新增英文说明：`docs/en/DOCS_RUNTIME_VERIFICATION.md`。
- 自动检查 config、docker-compose、OpenAPI routes、CURRENT_RUNTIME、PROJECT_OVERVIEW、API_REFERENCE、Phase 状态。
- 输出 `PASS`、`WARNING`、`ERROR`。
- 文档同步通过标准：最终必须输出 `SUMMARY: PASS`。

## 当前运行态

默认 provider：

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
```

本地模型接口已支持：

- `LOCAL_LLM_MODEL=mistral`
- `LOCAL_EMBEDDING_MODEL=bge-m3`

默认上传配置：

```text
MAX_UPLOAD_FILE_SIZE_MB=20
UPLOAD_TEMP_DIR=/tmp/aiops_uploads
ALLOWED_FILE_TYPES=pdf,docx,txt,md,csv
```

完整运行态见 `docs/CURRENT_RUNTIME.md`。

## 已完成能力

生产基础能力：

- 健康检查。
- 任务创建、查询、入队、执行、失败重试。
- 文本 RAG ingest/search。
- 文件上传 ingest。
- Knowledge Lifecycle：active / outdated / deleted。
- Workspace 级数据隔离。
- API Key hash 存储，明文只返回一次。
- Dense / Keyword / Hybrid Search。
- Mock reranker 精排。
- Agentic RAG debug trace。
- RAG Eval run/item 存储。
- ContentAgent 示例。

实验性能力：

- local LLM 和 local embedding 可切换到 Ollama，但默认仍是 mock。
- local reranker provider 仍是接口预留。
- Eval 系统支持 trace 存储和人工评分，但未实现自动指标。

规划中能力：

- 真实 reranker。
- 真正 BM25 或外部搜索引擎。
- Memory。
- Tool Calling。
- Multi-Agent。
- Browser Agent / OpenClaw / Playwright。
- Grafana / Prometheus。
- 完整 RBAC / JWT / OAuth。

## 当前限制

- PDF 只抽取可复制文本，不做 OCR。
- 暂不支持 PPTX、XLSX、图片。
- Keyword retrieval 仍是 PostgreSQL `ILIKE` 加简单关键词评分。
- local reranker 仍是 placeholder。
- 没有 Elasticsearch、OpenSearch、真实 BM25。
- 没有完整权限系统。
- 没有前端 Dashboard。

## 固定验证流程

每个 Phase 完成后必须执行：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Docs 只有在 runtime verifier 输出 `SUMMARY: PASS` 后，才视为与当前代码同步。
