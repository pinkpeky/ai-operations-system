# Development Guide

Last updated: 2026-05-12

This guide is for future Codex sessions and developers extending the project.

## Principles

- Do not modify Scheduler core logic unless a phase explicitly requires it.
- Do not modify TaskExecutor core logic unless a phase explicitly requires it.
- Keep RAG, LLM, Reranker, and File Upload logic in separate service layers.
- Never bypass Workspace Isolation.
- Do not document features that do not exist in code.
- Update docs after every phase.

## Layering

API:

- `app/api/routes/`
- Parse requests, inject dependencies, convert errors.

Services:

- `app/services/` or domain-specific service folders.
- Own business workflows.

Repositories:

- `app/repositories/`
- Own database access.

Providers:

- LLM: `app/agents/providers/`
- Embedding: `app/rag/providers/`
- Reranker: `app/reranker/providers/`

Schemas:

- `app/schemas/`
- Pydantic request/response models.

Tests:

- `tests/`
- Unit tests should not require real Ollama.

## File Upload Development Rules

Relevant paths:

```text
app/file_pipeline/
  parsers/
  services/
app/api/routes/files.py
app/schemas/file.py
```

Rules:

- Parsers only extract text.
- Text cleaner only normalizes text.
- Upload service handles temp files, hash, duplicate detection, parser dispatch, and lifecycle ingestion.
- DocumentLifecycle remains the canonical path for document/chunk/Qdrant writes.
- New file types require parser tests.
- Do not document unsupported formats as supported.

## Docs-as-Code Rules

Docs are the project Single Source of Truth.

Every completed phase must update:

- `docs/PROJECT_OVERVIEW.md`
- `docs/CURRENT_RUNTIME.md`
- `docs/zh/*`
- `docs/en/*`
- `docs/Aiops Project Documentation Update Request For Codex.docx`

New APIs must update:

- Method.
- Path.
- Request JSON or form fields.
- Response JSON.
- Required headers.
- Workspace requirements.
- Debug fields.
- Production / experimental / planned status.

New config must update:

- `app/core/config.py`
- `.env.example`
- `docker-compose.yml`
- `docs/CURRENT_RUNTIME.md`
- zh/en deployment docs.

## Docs Runtime Verification

Run:

```powershell
python scripts/verify_docs_runtime.py
```

The verifier checks:

- Settings defaults.
- docker-compose environment.
- FastAPI OpenAPI routes.
- `CURRENT_RUNTIME.md`.
- `PROJECT_OVERVIEW.md`.
- zh/en API_REFERENCE.
- Phase status.
- File Upload Pipeline fields.

Passing condition:

```text
SUMMARY: PASS
```

If it fails:

1. Read the `ERROR`.
2. Decide whether code or docs are stale.
3. Fix the source.
4. Re-run the verifier.

## Delivery Checklist

Every phase must finish with:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Recommended smoke tests:

- `GET /api/v1/health`
- `POST /api/v1/files/upload`
- `POST /api/v1/rag/search`
- `POST /api/v1/agentic-rag/query`

## Testing Strategy

- Unit tests should not depend on real Ollama.
- Local providers should use mock HTTP clients in tests.
- File parser tests should use small fixtures or fake readers.
- Workspace isolation must be tested across workspaces.
- Docs verifier must be part of the test suite.

## Do Not Implement Yet

- Real reranker.
- Elasticsearch / OpenSearch.
- OCR.
- PPTX / XLSX / image parsing.
- Browser Agent / OpenClaw / Playwright.
- Full RBAC / JWT / OAuth.
- Scheduler core changes.
- TaskExecutor core changes.
