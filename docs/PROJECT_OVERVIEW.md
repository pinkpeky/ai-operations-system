# AI Operations System Project Overview

Last updated: 2026-05-12

This is the entry point for `E:\ai-operations-system`. After Phase 10.5, `docs/` is the project Single Source of Truth. After Phase 11, this source of truth is also verified by runtime checks through `scripts/verify_docs_runtime.py`.

## Project Summary

AI Operations System is a backend-first AI automation platform. It combines task orchestration, Agentic RAG, workspace isolation, knowledge lifecycle management, hybrid retrieval, reranking, evaluation trace storage, content generation, and file-based knowledge ingestion.

The project is not a frontend dashboard. It is a backend foundation for future content agents, support agents, data analysis agents, tool-calling agents, browser automation, monitoring, and multi-agent workflows.

## Current Status

Phase 1 through Phase 11 are completed.

Completed capabilities:

- FastAPI application and Swagger UI.
- PostgreSQL, Redis, Qdrant, and Docker Compose infrastructure.
- SQLAlchemy ORM and Alembic migrations.
- Redis queue, Scheduler, TaskExecutor, and task handlers.
- LLM Client Layer with mock provider and local Ollama Mistral support.
- Embedding Layer with mock provider and local Ollama bge-m3 support.
- Knowledge Lifecycle with `documents`, `document_chunks`, and `collections_metadata`.
- Workspace, user, and API key isolation foundation.
- Agentic RAG single orchestrator.
- ContentAgent as the first central agent example.
- RAG Eval and Debug Trace.
- Reranker Provider Layer.
- Hybrid Search: Dense + Keyword -> Merge -> Reranker -> LLM.
- File Upload Pipeline for PDF, DOCX, TXT, MD, and CSV.
- Docs Runtime Verification to detect drift between docs, config, routes, and OpenAPI.

Experimental capabilities:

- Local reranker provider is a placeholder interface. The active reranker is still mock.
- RAG Eval stores trace and manual score, but does not compute automatic metrics yet.
- Local Ollama providers are supported, but default Docker smoke tests use mock providers unless `.env` enables local providers.

Planned capabilities:

- Real reranker model integration.
- Real BM25 or external search engine.
- RAG metrics and batch evaluation.
- Memory.
- Tool Calling.
- Multi-Agent orchestration.
- Browser Agent, OpenClaw, and Playwright.
- Prometheus, Grafana, and production observability.
- Full RBAC, JWT, OAuth, and external identity providers.

## Current Architecture

```text
HTTP API
  -> FastAPI routes
  -> Workspace Context Middleware
  -> Service / Repository / Provider layers
  -> PostgreSQL / Redis / Qdrant / Ollama
```

Core RAG ingest flow:

```text
Text or uploaded file
 -> parse / clean
 -> chunk
 -> embedding
 -> Qdrant upsert
 -> documents / document_chunks / collections_metadata
```

Core RAG query flow:

```text
Query
 -> Dense Vector Search
 -> Keyword Search
 -> Hybrid Merge
 -> Reranker
 -> Prompt Assembly
 -> LLM
 -> Answer + Debug Trace
```

File Upload Pipeline:

```text
multipart upload
 -> save temp file
 -> compute file_hash
 -> duplicate check by file_hash + workspace_id
 -> parser layer
 -> text cleaner
 -> DocumentLifecycle ingest
 -> embedding + Qdrant + DB lifecycle records
 -> temp cleanup
```

Docs Runtime Verification Architecture:

```text
scripts/verify_docs_runtime.py
 -> app/core/config.py values
 -> docker-compose.yml environment
 -> FastAPI OpenAPI route list
 -> docs/CURRENT_RUNTIME.md
 -> docs/PROJECT_OVERVIEW.md
 -> docs/zh/API_REFERENCE.md
 -> docs/en/API_REFERENCE.md
 -> PASS / WARNING / ERROR
```

## Project Structure

```text
app/
  api/            FastAPI route registration and endpoint modules.
  agents/         LLM client, base agent, and ContentAgent.
  core/           Settings, logging, errors, and workspace context.
  db/             PostgreSQL, Redis, and Qdrant connection helpers.
  file_pipeline/  File upload parsers, text cleaning, and ingestion service.
  middleware/     Workspace context middleware.
  rag/            Embedding, chunking, vector store, retrieval, hybrid search, and Agentic RAG.
  reranker/       Reranker provider abstraction and mock/local providers.
  repositories/   Database access layer.
  schemas/        Pydantic request and response models.
  services/       Prompt manager, queues, document lifecycle, eval service, scheduler.
  workers/        TaskExecutor and task handlers.
tests/            Unit and integration-style tests.
scripts/          Runtime verification and maintenance scripts.
docs/             Single Source of Truth documentation.
```

## Docs Structure

```text
docs/
├── zh/
│   ├── PROJECT_STATUS.md
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT.md
│   ├── DEVELOPMENT_GUIDE.md
│   └── DOCS_RUNTIME_VERIFICATION.md
├── en/
│   ├── PROJECT_STATUS.md
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT.md
│   ├── DEVELOPMENT_GUIDE.md
│   └── DOCS_RUNTIME_VERIFICATION.md
├── PROJECT_OVERVIEW.md
├── CURRENT_RUNTIME.md
└── Aiops Project Documentation Update Request For Codex.docx
```

`docs/zh` is the primary development documentation. It is more detailed and implementation-oriented.

`docs/en` is the international and collaboration documentation. It is more standardized and easier to share with external teams.

## Recommended Reading Order

For Chinese development work:

1. `docs/PROJECT_OVERVIEW.md`
2. `docs/CURRENT_RUNTIME.md`
3. `docs/zh/PROJECT_STATUS.md`
4. `docs/zh/ARCHITECTURE.md`
5. `docs/zh/API_REFERENCE.md`
6. `docs/zh/DEPLOYMENT.md`
7. `docs/zh/DEVELOPMENT_GUIDE.md`
8. `docs/zh/DOCS_RUNTIME_VERIFICATION.md`

For English collaboration:

1. `docs/PROJECT_OVERVIEW.md`
2. `docs/CURRENT_RUNTIME.md`
3. `docs/en/PROJECT_STATUS.md`
4. `docs/en/ARCHITECTURE.md`
5. `docs/en/API_REFERENCE.md`
6. `docs/en/DEPLOYMENT.md`
7. `docs/en/DEVELOPMENT_GUIDE.md`
8. `docs/en/DOCS_RUNTIME_VERIFICATION.md`

## Current Runtime

Default runtime values are documented in `docs/CURRENT_RUNTIME.md`.

Default providers:

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
```

Supported local models:

- LLM: Ollama `mistral`
- Embedding: Ollama `bge-m3`
- Reranker: local provider interface only, no real local reranker model is wired yet.

Supported file upload types:

- PDF
- DOCX
- TXT
- MD
- CSV

Not supported in Phase 11:

- PPTX
- XLSX
- OCR
- Images

## Current Limitations

- Local reranker is still a placeholder interface.
- Keyword retrieval uses PostgreSQL `ILIKE` and simple keyword scoring.
- No Elasticsearch, OpenSearch, or real BM25 engine.
- No Memory layer.
- No Tool Calling.
- No Multi-Agent system.
- No Browser Agent.
- No OpenClaw or Playwright integration.
- No Grafana or Prometheus.
- No full RBAC, JWT, OAuth, or third-party login.
- File upload does not support PPTX, XLSX, OCR, or images.
- PDF parsing only extracts embedded text; scanned PDFs need future OCR.

## Verification Workflow

Every completed phase must run:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

The docs verifier must return `SUMMARY: PASS` before docs can be considered synchronized with runtime.

## Roadmap

Suggested next phases:

1. Real reranker model integration and reranker eval comparison.
2. RAG metrics and batch evaluation datasets.
3. Memory Layer.
4. Tool Calling Agent foundation.
5. Multi-Agent orchestration.
6. Browser Agent / OpenClaw / Playwright integration.
7. Production observability with Prometheus and Grafana.
8. Full authentication and authorization.
