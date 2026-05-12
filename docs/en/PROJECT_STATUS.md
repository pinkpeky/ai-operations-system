# Project Status

Last updated: 2026-05-12

This document summarizes the current engineering status of `E:\ai-operations-system`.

## Overall Status

Phase 1 through Phase 11 are complete.

The system currently includes:

- FastAPI.
- PostgreSQL, Redis, Qdrant, and Docker Compose.
- SQLAlchemy ORM and Alembic migrations.
- Redis Queue, Scheduler, TaskExecutor, and task handlers.
- LLM Client Layer.
- Ollama Mistral local LLM integration.
- Embedding Pipeline.
- Ollama bge-m3 local embedding integration.
- Knowledge Lifecycle Management.
- Workspace, user, and API key isolation foundation.
- Agentic RAG Orchestrator.
- ContentAgent.
- RAG Eval and Debug Trace.
- Reranker Provider Layer.
- Hybrid Search.
- File Upload Pipeline.
- Docs Runtime Verification.

## Completed Phases

| Phase | Status | Summary |
| --- | --- | --- |
| Phase 1 | Complete | Docker, PostgreSQL, Redis, Qdrant, FastAPI, health check. |
| Phase 2 | Complete | ORM, task system, Redis queue, Scheduler, Task API. |
| Phase 2.5 | Complete | LLM client, mock/local/server providers, prompt manager. |
| Phase 3 | Complete | Embedding pipeline and Qdrant collection layer. |
| Phase 3.5 | Complete | RAG quality improvements, score normalization, collection health, debug API. |
| Phase 4 | Complete | Single Agentic RAG orchestrator. |
| Phase 4.5 | Complete | Agentic RAG task execution handler. |
| Phase 4.6 | Complete | Ollama Mistral local LLM integration. |
| Phase 5 | Complete | BaseAgent and ContentAgent. |
| Phase 6 | Complete | Knowledge lifecycle with document versioning and active-only retrieval. |
| Phase 6.5 | Complete | Workspace/user/API key isolation foundation. |
| Phase 7 | Complete | Ollama bge-m3 real embedding support. |
| Phase 8 | Complete | RAG eval runs/items and trace persistence. |
| Phase 9 | Complete | Reranker provider layer. |
| Phase 10 | Complete | Hybrid Search: Dense + Keyword -> Merge -> Rerank -> LLM. |
| Phase 10.5 | Complete | Bilingual docs system and docs SSOT. |
| Phase 11 | Complete | File Upload Pipeline and Docs Runtime Verification. |

## Phase 11 Summary

File Upload:

- Adds `app/file_pipeline/`.
- Supports PDF, DOCX, TXT, MD, and CSV.
- Adds `POST /api/v1/files/upload`.
- Uses multipart/form-data.
- Saves a temp file, computes `file_hash`, parses text, cleans text, and calls DocumentLifecycle ingest.
- Writes `documents`, `document_chunks`, and Qdrant points.
- Stores file metadata: `filename`, `file_type`, `file_size`, `file_hash`, `ingest_status`, `ingest_error`, and `chunk_count`.
- Supports duplicate detection by `file_hash + workspace_id`.
- Supports `duplicate_strategy=skip` and `duplicate_strategy=force_reingest`.

Docs Runtime Verification:

- Adds `scripts/verify_docs_runtime.py`.
- Adds `docs/zh/DOCS_RUNTIME_VERIFICATION.md`.
- Adds `docs/en/DOCS_RUNTIME_VERIFICATION.md`.
- Checks config, docker-compose, OpenAPI routes, runtime docs, overview docs, API reference, and phase status.
- Outputs `PASS`, `WARNING`, and `ERROR`.

## Current Defaults

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
```

Supported local models:

- `LOCAL_LLM_MODEL=mistral`
- `LOCAL_EMBEDDING_MODEL=bge-m3`

Upload defaults:

```text
MAX_UPLOAD_FILE_SIZE_MB=20
UPLOAD_TEMP_DIR=/tmp/aiops_uploads
ALLOWED_FILE_TYPES=pdf,docx,txt,md,csv
```

## Production Foundation

- Health checks.
- Task creation, querying, queueing, execution, and retry.
- Text RAG ingest/search.
- File upload ingest.
- Knowledge lifecycle: active, outdated, deleted.
- Workspace-level data isolation.
- API key hash storage with one-time plaintext return.
- Dense, keyword, and hybrid search.
- Mock reranker.
- Agentic RAG debug trace.
- RAG eval run/item storage.
- ContentAgent.

## Experimental

- Local Ollama LLM and embedding providers.
- Local reranker provider placeholder.
- RAG eval trace and manual scoring without automatic metrics.

## Planned

- Real reranker integration.
- Real BM25 or external search engine.
- Memory.
- Tool Calling.
- Multi-Agent orchestration.
- Browser Agent / OpenClaw / Playwright.
- Grafana / Prometheus.
- Full RBAC / JWT / OAuth.

## Current Limitations

- PDF parsing only extracts embedded text. No OCR.
- PPTX, XLSX, and image parsing are not supported.
- Keyword retrieval uses PostgreSQL `ILIKE` and simple scoring.
- Local reranker is still a placeholder.
- No Elasticsearch, OpenSearch, or real BM25.
- No full authentication system.
- No frontend dashboard.

## Required Verification

Every phase must finish with:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Docs are considered synchronized only when the docs verifier returns `SUMMARY: PASS`.
