# API Reference

Last updated: 2026-05-12

All current APIs are mounted under `/api/v1`.

## Common Headers

Workspace-scoped APIs require:

```http
X-Workspace-Id: <workspace id>
X-User-Id: <optional user id>
```

Workspace-scoped endpoints do not fall back to global reads.

## Status Labels

- Production foundation: implemented and suitable as backend foundation.
- Experimental: implemented interface or storage, but model/metrics/external integration is not final.
- Planned: not listed as an available API.

## Health

### GET `/api/v1/health`

Status: Production foundation

Headers: none

Workspace: not required

Response:

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

Status: Production foundation

Headers: none

Workspace: not required

Response:

```json
{
  "provider": "mock",
  "model": "mock-llm",
  "reachable": true,
  "error": null
}
```

### POST `/api/v1/llm/test`

Status: Production foundation test endpoint

Headers: none

Workspace: not required

Request:

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

## Embedding

### GET `/api/v1/rag/embedding/health`

Status: Production foundation. Local mode depends on Ollama bge-m3.

Headers: none

Workspace: not required

Response:

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

Status: Production foundation

Content-Type: `multipart/form-data`

Required headers:

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Workspace: required

Form fields:

| Field | Required | Description |
| --- | --- | --- |
| `file` | yes | Uploaded file. Supports PDF, DOCX, TXT, MD, CSV. |
| `collection_name` | no | Target collection. Defaults to configured collection. |
| `duplicate_strategy` | no | `skip` or `force_reingest`. Default: `skip`. |
| `chunk_size` | no | Default: `500`. |
| `chunk_overlap` | no | Default: `50`; must be less than `chunk_size`. |

Response:

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

Unsupported: PPTX, XLSX, OCR, images.

## RAG Ingest

### POST `/api/v1/rag/ingest`

Status: Production foundation

Required headers:

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Workspace: required

Request:

```json
{
  "text": "AI operations supports task scheduling, RAG retrieval, content generation, agents, hybrid search, and reranker traces.",
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

## RAG Search

### POST `/api/v1/rag/search`

Status: Production foundation

Required headers:

```http
X-Workspace-Id: demo-workspace
```

Workspace: required

Request:

```json
{
  "query": "content generation and intelligent scheduling",
  "search_mode": "hybrid",
  "dense_top_k": 20,
  "keyword_top_k": 20,
  "final_top_k": 5,
  "collection_name": "docs_demo_collection",
  "source_id": "docs-demo-001"
}
```

Supported `search_mode` values:

- `dense`
- `keyword`
- `hybrid`

Response:

```json
{
  "collection_name": "docs_demo_collection",
  "query": "content generation and intelligent scheduling",
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

## RAG Debug

### POST `/api/v1/rag/debug`

Status: Production foundation debug endpoint

Headers: `X-Workspace-Id`

Workspace: required

This endpoint debugs dense retrieval only. Use Agentic RAG with `debug=true` for full hybrid/rerank trace.

## Collections

### GET `/api/v1/rag/collections`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

### GET `/api/v1/rag/collections/{collection_name}`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

## Reranker

### GET `/api/v1/reranker/health`

Status: Production foundation. Local reranker is experimental.

Headers: none

Workspace: not required

Response:

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

Status: Production foundation

Required headers:

```http
X-Workspace-Id: demo-workspace
```

Workspace: required

Request:

```json
{
  "query": "What did Phase 11 add?",
  "collection_name": "docs_demo_collection",
  "top_k": 3,
  "debug": true
}
```

Response:

```json
{
  "answer": "MockProvider response",
  "used_retrieval": true,
  "retrieved_chunks": [],
  "provider": "mock",
  "model": "mock-llm",
  "debug": {
    "query": "What did Phase 11 add?",
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

Debug fields include `search_mode`, `dense_results_count`, `keyword_results_count`, `merged_results_count`, `final_results_count`, `dense_scores`, `keyword_scores`, `hybrid_scores`, `retrieval_before_rerank`, `reranked_chunks`, `rerank_scores`, `retrieval_after_rerank`, `final_prompt`, and `final_answer`.

## Agents

### POST `/api/v1/agents/content/generate`

Status: Production foundation sample agent

Headers: none

Workspace: not currently required

Request:

```json
{
  "topic": "AI automation operations",
  "platform": "tiktok",
  "style": "professional and concise"
}
```

## Tasks

### POST `/api/v1/tasks`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

### POST `/api/v1/tasks/agentic-rag`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

### POST `/api/v1/tasks/content-generation`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

### GET `/api/v1/tasks?status=pending`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

## Documents

### GET `/api/v1/documents`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

### GET `/api/v1/documents/{document_id}`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

### DELETE `/api/v1/documents/by-source/{source_id}`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

### POST `/api/v1/documents/reingest`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

## Workspaces / Users / API Keys

### POST `/api/v1/workspaces`

Status: Production foundation

### GET `/api/v1/workspaces`

Status: Production foundation

### POST `/api/v1/users`

Status: Production foundation

### GET `/api/v1/users`

Status: Production foundation

### POST `/api/v1/api-keys`

Status: Production foundation, not full authentication. The plaintext key is returned only once.

## RAG Eval

Status: Experimental foundation

### POST `/api/v1/rag/eval/runs`

Headers: `X-Workspace-Id`

### GET `/api/v1/rag/eval/runs`

Headers: `X-Workspace-Id`

### POST `/api/v1/rag/eval/runs/{run_id}/items`

Headers: `X-Workspace-Id`

### GET `/api/v1/rag/eval/runs/{run_id}/items`

Headers: `X-Workspace-Id`

### PATCH `/api/v1/rag/eval/items/{item_id}/score`

Headers: `X-Workspace-Id`
