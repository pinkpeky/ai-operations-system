# 架构说明

更新时间：2026-05-12

本文描述当前真实代码中的架构，不记录尚未实现的能力。

## 总览

```text
Client / Swagger / API caller
 -> FastAPI
 -> WorkspaceContextMiddleware
 -> Routes
 -> Services
 -> Repositories / Providers
 -> PostgreSQL / Redis / Qdrant / Ollama
```

核心原则：

- Scheduler 只负责扫描任务、状态流转和入队。
- TaskExecutor 负责消费任务并分发 handler。
- RAG、LLM、Reranker、File Upload 都是独立服务层，不塞进 Scheduler 核心逻辑。
- Workspace 隔离由 middleware 和 service/repository 查询共同保证。
- docs 是 Single Source of Truth，并通过 runtime verifier 防漂移。

## 目录职责

```text
app/api/            FastAPI route 注册和 endpoint。
app/agents/         LLM client、BaseAgent、ContentAgent。
app/core/           配置、错误、日志、workspace context。
app/db/             PostgreSQL、Redis、Qdrant 连接。
app/file_pipeline/  文件上传、parser、清洗、ingest 服务。
app/middleware/     WorkspaceContextMiddleware。
app/rag/            embedding、chunk、vector store、retrieval、hybrid search、agentic orchestrator。
app/reranker/       reranker provider 抽象、mock/local 实现。
app/repositories/   数据库访问层。
app/schemas/        Pydantic schema。
app/services/       prompt、queue、document lifecycle、eval、scheduler。
app/workers/        TaskExecutor 和 task handlers。
scripts/            runtime/docs 验证脚本。
docs/               项目文档 SSOT。
```

## 数据层

PostgreSQL 当前核心表：

- `tasks`
- `accounts`
- `publish_logs`
- `documents`
- `document_chunks`
- `collections_metadata`
- `users`
- `workspaces`
- `workspace_members`
- `api_keys`
- `rag_eval_runs`
- `rag_eval_items`

Qdrant：

- 存储 chunk embedding。
- payload 包含 `document_id`、`source_id`、`version`、`workspace_id`、`user_id`、`status` 等过滤字段。

Redis：

- 任务队列。

Ollama：

- local LLM：`mistral`。
- local embedding：`bge-m3`。
- 默认 provider 仍是 mock，详见 `docs/CURRENT_RUNTIME.md`。

## Workspace 隔离

请求 header：

```http
X-Workspace-Id: <workspace id>
X-User-Id: <optional user id>
```

隔离规则：

- document query 必须按 workspace 过滤。
- task query 必须按 workspace 过滤。
- collection query 必须按 workspace 过滤。
- RAG dense search 使用 Qdrant payload 过滤 workspace/status/source。
- RAG keyword search 使用 PostgreSQL documents/document_chunks 过滤 workspace/status/source。
- 未提供 workspace 的受保护接口必须返回清晰错误，不允许查全库。

## Knowledge Lifecycle

```text
ingest text/file
 -> create documents row
 -> chunk text
 -> create document_chunks rows
 -> embed chunks
 -> upsert Qdrant points
 -> update chunk_count and ingest_status
```

生命周期状态：

- `active`
- `outdated`
- `deleted`

同一个 `source_id` 再次 ingest：

- 旧 document 标记为 `outdated`。
- 新 document 创建新 version。
- search 默认只返回 active chunk。

删除：

- 不物理删除数据库记录。
- documents 和 document_chunks 标记为 `deleted`。
- Qdrant point 可以删除，或至少通过 status 过滤不返回。

## File Upload Pipeline

```text
POST /api/v1/files/upload
 -> validate workspace
 -> validate extension and size
 -> save temp file
 -> calculate SHA-256 file_hash
 -> duplicate check by file_hash + workspace_id + collection_name
 -> parser registry selects parser
 -> clean extracted text
 -> DocumentLifecycleService.ingest_text
 -> update file metadata
 -> cleanup temp file
```

支持 parser：

- PDF：`pypdf`
- DOCX：`python-docx`
- CSV：`pandas`
- TXT / MD：UTF-8 text parser

不支持：

- PPTX
- XLSX
- OCR
- 图片

重复策略：

- `skip`：发现同 workspace 同 hash active document 时直接返回已有 document。
- `force_reingest`：复用 source_id，走 lifecycle versioning。

## RAG Query 架构

```text
query
 -> dense retrieval top_k
 -> keyword retrieval top_k
 -> merge by chunk id
 -> attach dense_score / keyword_score / hybrid_score
 -> reranker
 -> top_n context
 -> prompt assembly
 -> LLM
 -> answer + trace
```

Search mode：

- `dense`
- `keyword`
- `hybrid`

默认：

```text
DEFAULT_SEARCH_MODE=hybrid
DENSE_TOP_K=20
KEYWORD_TOP_K=20
FINAL_TOP_K=5
```

## Reranker 架构

Provider：

- `MockRerankerProvider`
- `LocalRerankerProvider`

当前默认：

```text
RERANKER_PROVIDER=mock
```

mock reranker 基于 query token overlap 做稳定排序，适合测试流程。local reranker 仍是预留接口。

## Agentic RAG Trace

`POST /api/v1/agentic-rag/query` 在 `debug=true` 时返回：

- `query`
- `workspace_id`
- `collection_name`
- `search_mode`
- `dense_results_count`
- `keyword_results_count`
- `merged_results_count`
- `final_results_count`
- `dense_scores`
- `keyword_scores`
- `hybrid_scores`
- `retrieval_before_rerank`
- `reranked_chunks`
- `rerank_scores`
- `retrieval_after_rerank`
- `final_prompt`
- `final_answer`
- `llm_provider`
- `llm_model`
- `embedding_provider`
- `embedding_model_name`
- `reranker_provider`
- `reranker_model`
- `latency_ms`

## Docs Runtime Verification 架构

```text
python scripts/verify_docs_runtime.py
 -> load Settings
 -> build FastAPI OpenAPI schema
 -> inspect docker-compose.yml
 -> inspect docs/CURRENT_RUNTIME.md
 -> inspect docs/PROJECT_OVERVIEW.md
 -> inspect zh/en API_REFERENCE
 -> report PASS / WARNING / ERROR
```

该脚本用于防止：

- config 改了但 docs 没改。
- API route 新增但 API_REFERENCE 没写。
- Phase 状态漂移。
- runtime provider 与 CURRENT_RUNTIME 不一致。
- 文件上传配置缺失。

## 当前边界

- 不接真实 reranker。
- 不接 Elasticsearch / OpenSearch。
- 不做 OCR。
- 不支持 PPTX / XLSX / 图片。
- 不做完整 RBAC / JWT / OAuth。
- 不做前端 Dashboard。
- 不接 Browser Agent、OpenClaw、Playwright。
