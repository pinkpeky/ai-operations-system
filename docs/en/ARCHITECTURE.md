# Architecture

Last updated: 2026-05-12

This document describes the architecture that exists in the current codebase.

## Overview

```text
Client / Swagger / API caller
 -> FastAPI
 -> WorkspaceContextMiddleware
 -> Routes
 -> Services
 -> Repositories / Providers
 -> PostgreSQL / Redis / Qdrant / Ollama
```

Key boundaries:

- Scheduler scans tasks, transitions status, and enqueues work.
- TaskExecutor consumes queued tasks and dispatches handlers.
- RAG, LLM, Reranker, and File Upload logic live outside Scheduler core logic.
- Workspace isolation is enforced by middleware and workspace-aware queries.
- Docs are treated as Single Source of Truth and verified by runtime checks.

## Project Structure

```text
app/api/            FastAPI routes and endpoint modules.
app/agents/         LLM client, BaseAgent, and ContentAgent.
app/core/           Settings, errors, logging, workspace context.
app/db/             PostgreSQL, Redis, and Qdrant helpers.
app/file_pipeline/  File upload parsers, text cleaner, upload ingestion service.
app/middleware/     Workspace context middleware.
app/rag/            Embedding, chunking, vector store, retrieval, hybrid search, Agentic RAG.
app/reranker/       Reranker abstraction and mock/local providers.
app/repositories/   Database access layer.
app/schemas/        Pydantic models.
app/services/       Prompt manager, queue, lifecycle, eval, scheduler.
app/workers/        TaskExecutor and handlers.
scripts/            Runtime verification scripts.
docs/               Documentation SSOT.
```

## Data Stores

PostgreSQL tables:

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

Qdrant stores chunk embeddings. Payloads include `document_id`, `source_id`, `version`, `workspace_id`, `user_id`, and `status`.

Redis stores task queue data.

Ollama is used by local providers for Mistral and bge-m3 when explicitly enabled.

## Workspace Isolation

Workspace-scoped requests require:

```http
X-Workspace-Id: <workspace id>
X-User-Id: <optional user id>
```

Rules:

- Document queries are workspace-filtered.
- Task queries are workspace-filtered.
- Collection queries are workspace-filtered.
- Dense retrieval filters Qdrant payload by workspace/status/source.
- Keyword retrieval filters PostgreSQL rows by workspace/status/source.
- Protected endpoints never default to global reads.

## Knowledge Lifecycle

```text
ingest text/file
 -> create document
 -> chunk text
 -> create document_chunks
 -> embed chunks
 -> upsert Qdrant points
 -> update lifecycle metadata
```

Statuses:

- `active`
- `outdated`
- `deleted`

Re-ingesting the same `source_id` marks the previous active document as `outdated` and creates a new version.

## File Upload Pipeline

```text
POST /api/v1/files/upload
 -> validate workspace
 -> validate file type and size
 -> save temp file
 -> compute SHA-256 file_hash
 -> duplicate check by file_hash + workspace_id + collection_name
 -> parse file text
 -> clean extracted text
 -> DocumentLifecycleService.ingest_text
 -> update file metadata
 -> cleanup temp file
```

Supported parsers:

- PDF via `pypdf`
- DOCX via `python-docx`
- CSV via `pandas`
- TXT and MD via UTF-8 text parser

Unsupported:

- PPTX
- XLSX
- OCR
- Images

Duplicate strategies:

- `skip`: return the existing active document.
- `force_reingest`: reuse the source and let lifecycle versioning create a new version.

## RAG Query Architecture

```text
query
 -> dense retrieval
 -> keyword retrieval
 -> merge by chunk id
 -> dense_score / keyword_score / hybrid_score
 -> reranker
 -> top_n context
 -> prompt assembly
 -> LLM
 -> answer + trace
```

Modes:

- `dense`
- `keyword`
- `hybrid`

Defaults:

```text
DEFAULT_SEARCH_MODE=hybrid
DENSE_TOP_K=20
KEYWORD_TOP_K=20
FINAL_TOP_K=5
```

## Reranker

Providers:

- `MockRerankerProvider`
- `LocalRerankerProvider`

Default:

```text
RERANKER_PROVIDER=mock
```

The mock reranker uses deterministic query-token overlap. The local reranker provider is a placeholder interface.

## Agentic RAG Trace

When `debug=true`, `POST /api/v1/agentic-rag/query` returns:

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

## Docs Runtime Verification

```text
python scripts/verify_docs_runtime.py
 -> Settings defaults
 -> docker-compose environment
 -> FastAPI OpenAPI schema
 -> CURRENT_RUNTIME
 -> PROJECT_OVERVIEW
 -> zh/en API_REFERENCE
 -> PASS / WARNING / ERROR
```

The verifier prevents documentation drift after runtime or API changes.

## Boundaries

- No real reranker model is wired.
- No Elasticsearch or OpenSearch.
- No OCR.
- No PPTX, XLSX, or image parsing.
- No full RBAC, JWT, or OAuth.
- No frontend dashboard.
- No Browser Agent, OpenClaw, or Playwright.
