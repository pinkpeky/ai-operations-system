# Current Runtime

Last updated: 2026-05-12

This document records the current real runtime defaults for `E:\ai-operations-system`. Values are based on `app/core/config.py`, `.env.example`, and `docker-compose.yml`.

The repository currently has no committed `.env` file. Without local overrides, the application uses the defaults below.

## Provider Defaults

| Key | Current default | Meaning |
| --- | --- | --- |
| `LLM_PROVIDER` | `mock` | Default LLM provider. Does not call a real model. |
| `LOCAL_LLM_BASE_URL` | `http://host.docker.internal:11434` | Ollama base URL for local LLM mode. |
| `LOCAL_LLM_MODEL` | `mistral` | Ollama local LLM model. |
| `EMBEDDING_PROVIDER` | `mock` | Default embedding provider. Does not call a real embedding model. |
| `EMBEDDING_DIMENSION` | `384` | Mock embedding dimension. |
| `LOCAL_EMBEDDING_BASE_URL` | `http://host.docker.internal:11434` | Ollama base URL for local embedding mode. |
| `LOCAL_EMBEDDING_MODEL` | `bge-m3` | Ollama local embedding model. |
| `RERANKER_PROVIDER` | `mock` | Default reranker provider. |
| `LOCAL_RERANKER_BASE_URL` | `http://host.docker.internal:8003` | Placeholder local reranker endpoint. |
| `LOCAL_RERANKER_MODEL` | `local-reranker-model` | Placeholder local reranker model name. |

## Search Defaults

| Key | Current default | Meaning |
| --- | --- | --- |
| `DEFAULT_SEARCH_MODE` | `hybrid` | Default search mode. |
| `DENSE_TOP_K` | `20` | Dense candidate count. |
| `KEYWORD_TOP_K` | `20` | Keyword candidate count. |
| `FINAL_TOP_K` | `5` | Final search response count. |
| `RERANK_TOP_N` | `5` | Agentic RAG context count after reranking. |

Current retrieval chain:

```text
Dense Vector Search
+ Keyword Search
-> Hybrid Merge
-> Reranker
-> LLM
```

## File Upload Defaults

| Key | Current default | Meaning |
| --- | --- | --- |
| `MAX_UPLOAD_FILE_SIZE_MB` | `20` | Maximum uploaded file size. |
| `UPLOAD_TEMP_DIR` | `/tmp/aiops_uploads` | Temporary upload directory inside the API container. |
| `ALLOWED_FILE_TYPES` | `pdf,docx,txt,md,csv` | Supported upload extensions. |

Supported in Phase 11:

- PDF
- DOCX
- TXT
- MD
- CSV

Not implemented:

- PPTX
- XLSX
- OCR
- Image parsing

## Mock vs Local

Current default mock components:

- `LLM_PROVIDER=mock`
- `EMBEDDING_PROVIDER=mock`
- `RERANKER_PROVIDER=mock`

Supported local components:

- Ollama LLM: `LOCAL_LLM_MODEL=mistral`
- Ollama embedding: `LOCAL_EMBEDDING_MODEL=bge-m3`

The local reranker provider is only an interface placeholder. A real local reranker model is not currently wired.

## Embedding Dimension

In mock mode:

```text
EMBEDDING_DIMENSION=384
```

In local `bge-m3` mode, the embedding dimension is detected from the first health or embedding call and stored in `collections_metadata.embedding_dimension`. If an existing collection has a different dimension, the system rejects the write to avoid mixed vectors.

## Docker Runtime

Start services:

```powershell
docker compose up --build -d
```

Swagger:

```text
http://localhost:8000/docs
```

Core health checks:

```http
GET /api/v1/health
GET /api/v1/llm/health
GET /api/v1/rag/embedding/health
GET /api/v1/reranker/health
```

## Switching to Local Ollama

Create a local `.env` file or set environment variables:

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

## Switching Back to Mock

```env
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
```

Restart:

```powershell
docker compose up --build -d
```

## Docs Runtime Verification

Run:

```powershell
python scripts/verify_docs_runtime.py
```

Expected final line:

```text
SUMMARY: PASS
```
