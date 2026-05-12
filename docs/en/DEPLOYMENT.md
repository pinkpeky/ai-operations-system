# Deployment

Last updated: 2026-05-12

This guide covers local setup, Docker validation, Ollama checks, file upload smoke tests, and docs runtime verification for the current codebase.

## Prerequisites

Required:

- Python 3.11+
- Docker Desktop
- Docker Compose

Optional:

- Ollama
- `mistral`
- `bge-m3`

Default Docker smoke tests use mock providers and do not require Ollama.

## Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

Phase 11 dependencies:

- `python-multipart`
- `pypdf`
- `python-docx`
- `pandas`

## Run Tests

```powershell
python -m pytest
```

Run tests after every code change.

## Start Docker

```powershell
docker compose up --build -d
```

Swagger:

```text
http://localhost:8000/docs
```

Current services:

- api
- postgres
- redis
- qdrant
- scheduler

## Configuration

Defaults are defined in:

- `app/core/config.py`
- `.env.example`
- `docker-compose.yml`
- `docs/CURRENT_RUNTIME.md`

Provider defaults:

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
```

Upload defaults:

```text
MAX_UPLOAD_FILE_SIZE_MB=20
UPLOAD_TEMP_DIR=/tmp/aiops_uploads
ALLOWED_FILE_TYPES=pdf,docx,txt,md,csv
```

## Ollama

For local LLM or embedding mode:

```powershell
ollama serve
ollama list
```

Expected models:

```text
mistral
bge-m3
```

`.env` example:

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

Restart:

```powershell
docker compose up --build -d
```

## Swagger Smoke Test

Health:

```http
GET /api/v1/health
GET /api/v1/llm/health
GET /api/v1/rag/embedding/health
GET /api/v1/reranker/health
```

File upload:

```http
POST /api/v1/files/upload
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
Content-Type: multipart/form-data
```

Form:

```text
file=@knowledge.md
collection_name=phase11_file_upload_demo
duplicate_strategy=force_reingest
chunk_size=800
chunk_overlap=80
```

RAG search:

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

Agentic RAG:

```http
POST /api/v1/agentic-rag/query
X-Workspace-Id: demo-workspace
```

```json
{
  "query": "What did Phase 11 add?",
  "collection_name": "phase11_file_upload_demo",
  "top_k": 3,
  "debug": true
}
```

## Docs Runtime Verification

```powershell
python scripts/verify_docs_runtime.py
```

Expected final line:

```text
SUMMARY: PASS
```

`ERROR` items must be fixed before delivery.

## Common Issues

### Missing Workspace Header

Workspace-scoped endpoints require:

```http
X-Workspace-Id: demo-workspace
```

### Collection Dimension Mismatch

Cause:

- The collection was created with mock embedding dimension `384`.
- Later, local `bge-m3` uses a different actual dimension.

Fix:

- Use a new collection name.
- Or delete the test collection and metadata in a controlled test environment.
- Do not mix embedding dimensions in one collection.

### Ollama Unreachable

Fix:

```powershell
ollama serve
ollama pull mistral
ollama pull bge-m3
```

Or switch back:

```env
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
```

### File Parser Error

Common causes:

- Extension not included in `ALLOWED_FILE_TYPES`.
- Scanned PDF without embedded text.
- File exceeds `MAX_UPLOAD_FILE_SIZE_MB`.
- TXT/MD is not UTF-8.

## Production Migration Notes

Before production migration:

- Configure production PostgreSQL, Redis, and Qdrant.
- Add persistent volumes and backup policy.
- Add real authentication and authorization.
- Harden API key permissions.
- Add HTTPS and reverse proxy.
- Add log collection.
- Add Prometheus and Grafana.
- Add real reranker and evaluation metrics.
- Add file upload malware scanning, object storage, and asynchronous ingest.

Phase 11 is a backend foundation, not a complete production security perimeter.
