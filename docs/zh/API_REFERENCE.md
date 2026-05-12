# API 参考

更新时间：2026-05-12

所有 API 挂载在 `/api/v1` 下。本文只记录当前真实代码中存在的 API。

## 通用 Header

Workspace-scoped API 必须携带：

```http
X-Workspace-Id: <workspace id>
X-User-Id: <optional user id>
```

规则：

- 需要 workspace 的接口未提供 `X-Workspace-Id` 时必须返回错误。
- 不允许默认查全库。
- `X-User-Id` 当前用于审计和预留，不是完整认证。

## 状态标记

- 生产基础：后端基础能力已实现，可作为系统基础使用。
- 实验性：接口或存储已实现，但模型、指标或外部依赖尚未最终化。
- 规划中：不列为当前可用 API。

## Health

### GET `/api/v1/health`

状态：生产基础

Required headers：无

Workspace：不需要

Response：

```json
{
  "status": "ok",
  "components": [
    {
      "name": "postgres",
      "status": "ok",
      "detail": "ready"
    }
  ]
}
```

## LLM

### GET `/api/v1/llm/health`

状态：生产基础。local provider 依赖 Ollama，但失败时必须返回清晰错误。

Required headers：无

Workspace：不需要

Response：

```json
{
  "provider": "mock",
  "model": "mock-llm",
  "reachable": true,
  "error": null
}
```

### POST `/api/v1/llm/test`

状态：生产基础测试接口

Required headers：无

Workspace：不需要

Request：

```json
{
  "system_prompt": "You are a helpful assistant.",
  "user_prompt": "Say hello.",
  "template": null,
  "variables": {},
  "temperature": null,
  "max_tokens": null
}
```

Response：

```json
{
  "provider": "mock",
  "model": "mock-llm",
  "content": "MockProvider response",
  "usage": {},
  "metadata": {}
}
```

## Embedding

### GET `/api/v1/rag/embedding/health`

状态：生产基础。local provider 依赖 Ollama `bge-m3`。

Required headers：无

Workspace：不需要

Response：

```json
{
  "provider": "mock",
  "model": "mock-embedding-model",
  "reachable": true,
  "dimension": 384,
  "error": null
}
```

## File Upload

### POST `/api/v1/files/upload`

状态：生产基础

Content-Type：`multipart/form-data`

Required headers：

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Workspace：必须

Form fields：

| Field | Required | Description |
| --- | --- | --- |
| `file` | yes | 上传文件，支持 PDF、DOCX、TXT、MD、CSV。 |
| `collection_name` | no | 目标 collection，默认使用配置中的 Qdrant collection。 |
| `duplicate_strategy` | no | `skip` 或 `force_reingest`，默认 `skip`。 |
| `chunk_size` | no | 默认 `500`。 |
| `chunk_overlap` | no | 默认 `50`，必须小于 `chunk_size`。 |

成功 Response：

```json
{
  "filename": "knowledge.md",
  "file_type": "md",
  "file_size": 1024,
  "file_hash": "sha256",
  "collection_name": "uploaded_knowledge",
  "source_id": "file-sha256",
  "document_id": "uuid",
  "version": 1,
  "chunk_count": 3,
  "chunk_ids": ["point-id-1", "point-id-2"],
  "ingest_status": "completed",
  "ingest_error": null,
  "skipped_duplicate": false,
  "metadata": {
    "filename": "knowledge.md",
    "file_type": "md",
    "file_size": 1024,
    "file_hash": "sha256",
    "ingest_status": "completed",
    "ingest_error": null,
    "chunk_count": 3
  }
}
```

重复文件 Response 示例：

```json
{
  "filename": "knowledge.md",
  "file_type": "md",
  "file_size": 1024,
  "file_hash": "sha256",
  "collection_name": "uploaded_knowledge",
  "source_id": "existing-source",
  "document_id": "existing-document-id",
  "version": 1,
  "chunk_count": 3,
  "chunk_ids": [],
  "ingest_status": "skipped_duplicate",
  "ingest_error": null,
  "skipped_duplicate": true,
  "metadata": {}
}
```

限制：

- 不支持 PPTX、XLSX、OCR、图片。
- PDF 只抽取可复制文本。

## RAG Ingest

### POST `/api/v1/rag/ingest`

状态：生产基础

Required headers：

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Workspace：必须

Request：

```json
{
  "text": "AI 自动化运营系统支持任务调度、RAG 检索、内容生成、Agent 执行、Hybrid Search 和 Reranker Trace。",
  "metadata": {
    "source": "docs"
  },
  "source_id": "docs-demo-001",
  "source_name": "Docs Demo",
  "source_type": "text",
  "chunk_size": 120,
  "chunk_overlap": 20,
  "collection_name": "docs_demo_collection"
}
```

Response：

```json
{
  "collection_name": "docs_demo_collection",
  "source_id": "docs-demo-001",
  "document_id": "uuid",
  "version": 1,
  "chunk_count": 2,
  "chunk_ids": ["point-id-1", "point-id-2"]
}
```

## RAG Search

### POST `/api/v1/rag/search`

状态：生产基础

Required headers：

```http
X-Workspace-Id: demo-workspace
```

Workspace：必须

Request：

```json
{
  "query": "自动化内容生成和智能调度",
  "search_mode": "hybrid",
  "dense_top_k": 20,
  "keyword_top_k": 20,
  "final_top_k": 5,
  "collection_name": "docs_demo_collection",
  "source_id": "docs-demo-001"
}
```

兼容字段：

```json
{
  "query": "自动化内容生成",
  "top_k": 5,
  "collection_name": "docs_demo_collection"
}
```

`search_mode` 支持：

- `dense`
- `keyword`
- `hybrid`

Response：

```json
{
  "collection_name": "docs_demo_collection",
  "query": "自动化内容生成和智能调度",
  "search_mode": "hybrid",
  "items": [
    {
      "id": "point-id",
      "text": "chunk text",
      "similarity_score": 0.74,
      "raw_score": 0.74,
      "rerank_score": 0.51,
      "original_similarity_score": 0.74,
      "dense_score": 0.58,
      "keyword_score": 0.87,
      "hybrid_score": 0.75,
      "metadata": {
        "workspace_id": "demo-workspace",
        "source_id": "docs-demo-001",
        "status": "active"
      },
      "chunk_index": 0
    }
  ]
}
```

隔离规则：

- dense search 通过 Qdrant payload 过滤 workspace/status/source。
- keyword search 通过 PostgreSQL 过滤 workspace/status/source。
- 默认只返回 active chunks。

## RAG Debug

### POST `/api/v1/rag/debug`

状态：生产基础调试接口

Required headers：`X-Workspace-Id`

Workspace：必须

说明：该接口调试 dense retrieval。完整 hybrid/rerank trace 请使用 `/api/v1/agentic-rag/query` 并设置 `debug=true`。

## Collections

### GET `/api/v1/rag/collections`

状态：生产基础

Required headers：`X-Workspace-Id`

Workspace：必须

### GET `/api/v1/rag/collections/{collection_name}`

状态：生产基础

Required headers：`X-Workspace-Id`

Workspace：必须

## Reranker

### GET `/api/v1/reranker/health`

状态：生产基础。local reranker 属于实验性接口预留。

Required headers：无

Workspace：不需要

Response：

```json
{
  "provider": "mock",
  "model": "mock-reranker",
  "reachable": true,
  "enabled": true,
  "error": null
}
```

## Agentic RAG

### POST `/api/v1/agentic-rag/query`

状态：生产基础

Required headers：

```http
X-Workspace-Id: demo-workspace
```

Workspace：必须

Request：

```json
{
  "query": "Phase 11 增加了什么文件导入能力？",
  "collection_name": "docs_demo_collection",
  "top_k": 3,
  "debug": true
}
```

Response：

```json
{
  "answer": "MockProvider response",
  "used_retrieval": true,
  "retrieved_chunks": [],
  "provider": "mock",
  "model": "mock-llm",
  "debug": {
    "query": "Phase 11 增加了什么文件导入能力？",
    "workspace_id": "demo-workspace",
    "collection_name": "docs_demo_collection",
    "search_mode": "hybrid",
    "dense_results_count": 3,
    "keyword_results_count": 3,
    "merged_results_count": 3,
    "final_results_count": 3,
    "dense_scores": [0.58],
    "keyword_scores": [0.87],
    "hybrid_scores": [0.75],
    "retrieval_before_rerank": [],
    "retrieval_after_rerank": [],
    "reranked_chunks": [],
    "rerank_scores": [0.51],
    "reranker_provider": "mock",
    "reranker_model": "mock-reranker",
    "final_prompt": "...",
    "final_answer": "...",
    "llm_provider": "mock",
    "llm_model": "mock-llm",
    "embedding_provider": "mock",
    "embedding_model_name": "mock-embedding-model",
    "latency_ms": 10
  }
}
```

核心 debug fields：

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

## Agents

### POST `/api/v1/agents/content/generate`

状态：生产基础示例 Agent

Required headers：无

Workspace：当前不强制

Request：

```json
{
  "topic": "AI 自动化运营",
  "platform": "tiktok",
  "style": "专业简洁"
}
```

## Tasks

### POST `/api/v1/tasks`

状态：生产基础

Required headers：`X-Workspace-Id`

Workspace：必须

### POST `/api/v1/tasks/agentic-rag`

状态：生产基础

Required headers：`X-Workspace-Id`

Workspace：必须

### POST `/api/v1/tasks/content-generation`

状态：生产基础

Required headers：`X-Workspace-Id`

Workspace：必须

### GET `/api/v1/tasks?status=pending`

状态：生产基础

Required headers：`X-Workspace-Id`

Workspace：必须

## Documents

### GET `/api/v1/documents`

状态：生产基础

Required headers：`X-Workspace-Id`

Workspace：必须

### GET `/api/v1/documents/{document_id}`

状态：生产基础

Required headers：`X-Workspace-Id`

Workspace：必须

### DELETE `/api/v1/documents/by-source/{source_id}`

状态：生产基础

Required headers：`X-Workspace-Id`

Workspace：必须

### POST `/api/v1/documents/reingest`

状态：生产基础

Required headers：`X-Workspace-Id`

Workspace：必须

## Workspaces / Users / API Keys

### POST `/api/v1/workspaces`

状态：生产基础

### GET `/api/v1/workspaces`

状态：生产基础

### POST `/api/v1/users`

状态：生产基础

### GET `/api/v1/users`

状态：生产基础

### POST `/api/v1/api-keys`

状态：生产基础，不是完整 auth。

说明：明文 key 只返回一次，数据库只保存 hash。

## RAG Eval

状态：实验性基础能力

### POST `/api/v1/rag/eval/runs`

Required headers：`X-Workspace-Id`

### GET `/api/v1/rag/eval/runs`

Required headers：`X-Workspace-Id`

### POST `/api/v1/rag/eval/runs/{run_id}/items`

Required headers：`X-Workspace-Id`

### GET `/api/v1/rag/eval/runs/{run_id}/items`

Required headers：`X-Workspace-Id`

### PATCH `/api/v1/rag/eval/items/{item_id}/score`

Required headers：`X-Workspace-Id`
