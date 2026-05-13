# API Reference

Last updated: 2026-05-14

All current APIs are mounted under `/api/v1`.

## Common Headers

Workspace-scoped APIs require:

```http
X-Workspace-Id: <workspace id>
X-User-Id: <optional user id>
```

## Phase 28 OpenClaw Worker Adapter Foundation

Status: production foundation / mock placeholder. Phase 28 adds an OpenClaw Adapter Foundation on top of the customer-machine Browser Worker protocol. It implements `BaseOpenClawProvider`, `MockOpenClawProvider`, `OpenClawRuntime`, server-side `OpenClawWorkerClient`, `openclaw_tool`, `openclaw_action_logs`, and mock worker runtime routes. It does not call real OpenClaw, automate TikTok / YouTube / X, perform automatic login, inject cookies, use proxy pools, bypass fingerprints, or automate captchas.

Runtime config: `OPENCLAW_PROVIDER=mock`, `OPENCLAW_ENABLED=true`, `OPENCLAW_ACTION_TIMEOUT_SECONDS=60`.

Tables: `openclaw_action_logs`; security audit events continue to use `browser_security_audit_logs`.

Worker Client files: `worker_client/openclaw/provider.py`, `worker_client/openclaw/mock_provider.py`, `worker_client/openclaw/schemas.py`, and `worker_client/openclaw/runtime.py`.

### GET `/api/v1/openclaw/health`

Required headers: `X-Workspace-Id`, optional `X-User-Id`.

Response JSON:

```json
{
  "success": true,
  "provider": "mock",
  "enabled": true,
  "reachable": true,
  "worker_id": "WORKER_ID",
  "worker_name": "local-windows-worker-1",
  "mock": true,
  "version": "mock-openclaw-0.1",
  "error": null,
  "raw": {
    "real_openclaw_called": false
  }
}
```

### GET `/api/v1/openclaw/capabilities`

Required headers: `X-Workspace-Id`, optional `X-User-Id`.

Response JSON:

```json
{
  "success": true,
  "provider": "mock",
  "enabled": true,
  "worker_id": "WORKER_ID",
  "worker_name": "local-windows-worker-1",
  "mock": true,
  "capabilities": {
    "openclaw": true,
    "real_openclaw": false,
    "platform_automation": false
  },
  "actions": ["health_check", "list_capabilities", "execute_action"],
  "error": null,
  "raw": {}
}
```

### POST `/api/v1/openclaw/actions`

Required headers: `X-Workspace-Id`, optional `X-User-Id`.

Request JSON:

```json
{
  "action_type": "mock_inspect",
  "target": "https://example.com",
  "input_payload": {
    "note": "phase28 smoke"
  },
  "profile_id": null,
  "browser_session_id": null,
  "metadata": {
    "phase": "28"
  }
}
```

Response JSON:

```json
{
  "success": true,
  "action_type": "mock_inspect",
  "output_payload": {
    "message": "mock openclaw action success",
    "real_openclaw_called": false
  },
  "error": null,
  "duration_ms": 0,
  "provider": "mock",
  "mock": true,
  "worker_id": "WORKER_ID",
  "log_id": "OPENCLAW_ACTION_LOG_ID"
}
```

### Worker Runtime OpenClaw Mock Routes

Worker Runtime protocol endpoints:

- `GET /api/v1/browser-worker-runtime/openclaw/health`
- `GET /api/v1/browser-worker-runtime/openclaw/capabilities`
- `POST /api/v1/browser-worker-runtime/openclaw/actions`
- `GET /openclaw/health` on worker_client runtime
- `GET /openclaw/capabilities` on worker_client runtime
- `POST /openclaw/actions` on worker_client runtime

### `openclaw_tool`

The Tool Registry now includes `openclaw_tool`, supporting `health_check`, `list_capabilities`, and `execute_action`.

Tool input:

```json
{
  "action_type": "execute_action",
  "openclaw_action_type": "mock_inspect",
  "target": "https://example.com",
  "input_payload": {},
  "metadata": {
    "phase": "28"
  }
}
```

Boundary: `openclaw_tool` only calls the mock worker adapter and writes `tool_call_logs`, `openclaw_action_logs`, and `browser_security_audit_logs`. It is not a Browser Agent, does not do autonomous planning, does not call real OpenClaw, and does not execute real platform actions.

## Phase 27 Customer Machine Worker Bootstrap

Status: production foundation / customer machine bootstrap. Phase 27 adds the local `worker_client` package so a Windows, Mac, or customer-owned machine can register as a Browser Worker and expose the same Worker Runtime protocol as the Docker `browser-worker` service. It does not implement OpenClaw, platform automation, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha handling, or TikTok / YouTube / X automation.

Local files and commands:

- `worker_client`
- `worker_client/worker_config.example.yaml`
- `worker_client/worker_config.yaml`
- `worker_client/worker_state.json`
- `python -m worker_client.cli register`
- `python -m worker_client.cli heartbeat`
- `python -m worker_client.cli serve`
- `python -m worker_client.cli start`

The `registration flow` reads `worker_config.yaml`, calls `POST /api/v1/browser-workers/register`, receives a plaintext `worker_secret` once, and stores `worker_id` plus `worker_secret` in local-only `worker_state.json`. The `heartbeat flow` reads `worker_state.json`, calls `POST /api/v1/browser-workers/{worker_id}/heartbeat`, and sends `X-Worker-Secret` plus Phase 26 signed request headers. The `local worker runtime` started by `serve` is compatible with:

- `GET /health`
- `POST /sessions`
- `POST /actions`
- `POST /sessions/{session_id}/close`
- `GET /ui-access/capabilities`

### Example `worker_config.yaml`

```yaml
server_url: http://localhost:8000
worker_name: local-windows-worker-1
worker_type: playwright
workspace_id: demo-workspace
worker_secret: null
worker_base_url: http://localhost:9100
runtime_host: 0.0.0.0
runtime_port: 9100
state_path: worker_client/worker_state.json
heartbeat_interval_seconds: 30
capabilities:
  browser: chromium
  screenshot: true
  page_content: true
  persistent_profile: true
allowed_domains:
  - example.com
  - localhost
  - 127.0.0.1
```

Security notes:

- `worker_state.json` is ignored by Git and must stay on the customer machine.
- `worker_secret` must not be written to logs or docs.
- Existing AI Server APIs remain the source of truth for worker registration, heartbeat, policy, and audit.

## Phase 26 Browser Worker Security & Access Control API

Status: production foundation / security foundation. Phase 26 adds basic security controls for Browser Worker, UI Access, Browser Profile, and Browser Action. It does not implement real platform account security, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha handling, or TikTok / YouTube / X automation.

Required headers: business APIs require `X-Workspace-Id`; `X-User-Id` is recommended. Signed worker runtime calls use `X-Worker-Signature`, `X-Worker-Timestamp`, `X-Worker-Nonce`, and a request body hash. Current defaults are `BROWSER_WORKER_AUTH_ENABLED=True` and `BROWSER_WORKER_AUTH_STRICT=False`.

Core runtime config:

- `BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1`
- `BROWSER_BLOCKED_DOMAINS=`
- `BROWSER_ALLOW_EXTERNAL_DOMAINS=False`
- `BROWSER_WORKER_AUTH_ENABLED=True`
- `BROWSER_WORKER_AUTH_STRICT=False`

Core tables, fields, and services:

- `browser_workers.worker_secret_hash`
- `browser_workers.api_key_hash`
- `browser_workers.last_auth_at`
- `browser_workers.auth_status`
- `browser_workers.allowed_actions`
- `browser_workers.allowed_domains`
- `worker_secret`
- `BrowserWorkerAuthService`
- `BrowserActionPolicyService`
- `BrowserSecurityAuditLog`
- `browser_security_audit_logs`
- `browser_ui_access_sessions.scopes`
- `browser_ui_access_sessions.one_time`
- `browser_ui_access_sessions.used_at`
- `browser_ui_access_sessions.revoked_reason`
- `browser_ui_access_sessions.client_ip`
- `browser_ui_access_sessions.user_agent`

### POST `/api/v1/browser-workers/{worker_id}/rotate-secret`

Rotates a worker secret. The plaintext `worker_secret` is returned only once; only `worker_secret_hash` is stored.

Response example:

```json
{
  "id": "WORKER_ID",
  "auth_status": "unverified",
  "worker_secret": "PLAINTEXT_RETURNED_ONCE",
  "allowed_actions": ["navigate", "click", "type_text", "scroll", "screenshot", "get_page_content"],
  "allowed_domains": ["example.com", "localhost", "127.0.0.1"]
}
```

### POST `/api/v1/browser-workers/{worker_id}/revoke`

Revokes worker auth. `auth_status` becomes `revoked`, and the worker is marked `offline`.

Request example:

```json
{
  "reason": "manual revoke"
}
```

### GET `/api/v1/browser/security/audit-logs`

Lists workspace-scoped browser security audit records. Supports `event_type` and `limit`. Audit events include worker registered, worker auth success / failed, UI token created / validated / revoked / expired, action blocked by policy, and profile access denied.

Response example:

```json
{
  "items": [
    {
      "event_type": "action_blocked_by_policy",
      "target_type": "browser_action",
      "success": false,
      "error": "domain_not_allowed:not-allowed.example.org",
      "metadata": {
        "action_type": "navigate"
      }
    }
  ]
}
```

### POST `/api/v1/browser/security/policy/check`

Runs `BrowserActionPolicyService` to validate action type, target domain, profile access, worker capability, and UI access scope.

Allowed example:

```json
{
  "action_type": "navigate",
  "target": "https://example.com"
}
```

Blocked example:

```json
{
  "action_type": "navigate",
  "target": "https://not-allowed.example.org"
}
```

Blocked response example:

```json
{
  "allowed": false,
  "reason": "domain_not_allowed:not-allowed.example.org",
  "metadata": {
    "hostname": "not-allowed.example.org"
  }
}
```

### UI Access Scope Extension

`POST /api/v1/browser/ui-access` supports:

```json
{
  "browser_session_id": "SESSION_ID",
  "human_control_session_id": "CONTROL_SESSION_ID",
  "scopes": ["view", "control"],
  "one_time": false,
  "metadata": {
    "phase": "26"
  }
}
```

`GET /api/v1/browser/ui-access/{access_session_id}/validate?token=TOKEN&scope=view` validates token, scope, expiry, one-time usage state, `used_at`, `revoked_reason`, `client_ip`, and `user_agent` tracking.

## Phase 25 Browser Worker UI Access Placeholder API

Status: production foundation / placeholder. Phase 25 creates a tokenized UI access placeholder for future manual browser takeover surfaces. It does not implement real VNC, noVNC, Chrome DevTools remote UI, live browser video, login, captcha handling, or platform automation.

Required headers: `X-Workspace-Id`; `X-User-Id` is recommended. All UI access APIs are workspace-isolated.

Canonical data and service:

- `browser_ui_access_sessions`
- `BrowserUIAccessService`
- `access_token_hash`
- `remote_control_url`
- `live_view_url`
- `devtools_url`
- `BROWSER_UI_ACCESS_TIMEOUT_SECONDS=900`
- `browser_tool` actions: `create_ui_access`, `revoke_ui_access`

### POST `/api/v1/browser/ui-access`

Creates a UI Access Placeholder session. The plaintext `access_token` is returned only once in this response. The database stores only `access_token_hash`.

Request:

```json
{
  "browser_session_id": "SESSION_ID",
  "human_control_session_id": "CONTROL_SESSION_ID",
  "metadata": {
    "phase": "25"
  }
}
```

Response:

```json
{
  "id": "ACCESS_SESSION_ID",
  "browser_session_id": "SESSION_ID",
  "human_control_session_id": "CONTROL_SESSION_ID",
  "remote_control_url": "http://localhost:8000/ui/browser-control/ACCESS_SESSION_ID",
  "live_view_url": "http://localhost:8000/ui/browser-live/ACCESS_SESSION_ID",
  "devtools_url": null,
  "status": "active",
  "access_token": "PLAINTEXT_RETURNED_ONCE",
  "metadata": {
    "placeholder": true,
    "vnc": false,
    "novnc": false,
    "devtools": false
  }
}
```

### GET `/api/v1/browser/ui-access/{access_session_id}`

Returns one UI Access Placeholder session. `access_token` is always `null`.

### POST `/api/v1/browser/ui-access/{access_session_id}/revoke`

Revokes the UI access session and sets status to `revoked`.

### POST `/api/v1/browser/ui-access/expire`

Expires all timeout-reached UI access sessions in the current workspace.

### GET `/api/v1/browser/ui-access/{access_session_id}/validate`

Validates a token:

```text
/api/v1/browser/ui-access/ACCESS_SESSION_ID/validate?token=TOKEN
```

Response:

```json
{
  "access_session_id": "ACCESS_SESSION_ID",
  "valid": true,
  "status": "active",
  "reason": null,
  "placeholder": true
}
```

### Worker UI Access Capabilities

- `GET /api/v1/browser-worker-runtime/ui-access/capabilities`
- `GET http://localhost:9100/ui-access/capabilities`

Response:

```json
{
  "vnc": false,
  "novnc": false,
  "devtools": false,
  "placeholder": true
}
```

Boundary: Phase 25 only creates placeholder URL and token plumbing. It does not implement VNC, noVNC, DevTools UI, real remote desktop, live browser view, platform login, captcha handling, cookie injection, proxy pools, fingerprint bypass, TikTok / YouTube / X, or real platform automation.

## Phase 24 Human-in-the-loop Browser Control API

Status: production foundation. Phase 24 adds a human-control protocol so browser automation can pause, wait for manual handling, and resume. The current implementation is metadata-level only and does not implement VNC, noVNC, Chrome DevTools remote UI, platform login, or captcha handling.

Required headers: `X-Workspace-Id`; `X-User-Id` is recommended. All human-control APIs are workspace-isolated.

Core tables and fields:

- `browser_human_control_sessions`
- `browser_human_control_events`
- `browser_sessions.human_control_status`
- `browser_sessions.human_control_session_id`
- `browser_sessions.paused_at`
- `browser_sessions.resumed_at`

Core service and setting:

- `BrowserHumanControlService`
- `BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS=900`
- `browser_tool` actions: `request_human_control`, `complete_human_control`

### POST `/api/v1/browser/human-control/request`

Requests human control and marks the browser session as `paused`.

Request:

```json
{
  "browser_session_id": "SESSION_ID",
  "reason": "manual login required",
  "metadata": {
    "phase": "24"
  }
}
```

Response:

```json
{
  "id": "CONTROL_SESSION_ID",
  "browser_session_id": "SESSION_ID",
  "status": "requested",
  "reason": "manual login required",
  "requested_by": "demo-user",
  "expires_at": "2026-05-13T12:15:00Z"
}
```

### POST `/api/v1/browser/human-control/{control_session_id}/approve`

Approves the request and writes an `approved` event.

### POST `/api/v1/browser/human-control/{control_session_id}/start`

Starts the human-control window, sets status to `active`, and notifies the worker metadata-level `/human-control/start` route.

### POST `/api/v1/browser/human-control/{control_session_id}/complete`

Completes human control, resumes the browser session as `active`, and writes `resumed_at`.

Request:

```json
{
  "note": "manual step completed",
  "metadata": {
    "operator": "human"
  }
}
```

### POST `/api/v1/browser/human-control/{control_session_id}/cancel`

Cancels human control and resumes the browser session as `active`.

### GET `/api/v1/browser/human-control`

Lists human-control sessions for the current workspace. Supports `status` filtering.

### GET `/api/v1/browser/human-control/{control_session_id}`

Returns one human-control session.

### GET `/api/v1/browser/human-control/{control_session_id}/events`

Returns the event stream. Event types include `requested`, `approved`, `started`, `completed`, `cancelled`, `expired`, `timeout`, and `note`.

### Worker Runtime Human Control

The in-process mock worker runtime and the independent `browser-worker` both expose metadata-level routes:

- `POST /api/v1/browser-worker-runtime/human-control/start`
- `POST /api/v1/browser-worker-runtime/human-control/complete`
- `GET /api/v1/browser-worker-runtime/human-control/status/{session_id}`

Independent worker paths:

- `POST /human-control/start`
- `POST /human-control/complete`
- `GET /human-control/status/{session_id}`

Boundary: Phase 24 does not support VNC, noVNC, real DevTools remote UI, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha automation, TikTok / YouTube / X, or real platform automation.

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
  "debug": true,
  "session_id": "optional-conversation-session-uuid"
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
    "latency_ms": 10,
    "session_id": "optional-conversation-session-uuid",
    "recent_messages_count": 1,
    "retrieved_memories_count": 1,
    "recent_messages": [],
    "retrieved_memories": [],
    "memory_trace": [
      {
        "operation": "agentic_rag_memory_retrieval",
        "session_id": "optional-conversation-session-uuid",
        "recent_messages_count": 1,
        "retrieved_memories_count": 1,
        "latency_ms": 2,
        "success": true,
        "error": null
      }
    ]
  }
}
```

Debug fields include `search_mode`, `dense_results_count`, `keyword_results_count`, `merged_results_count`, `final_results_count`, `dense_scores`, `keyword_scores`, `hybrid_scores`, `retrieval_before_rerank`, `reranked_chunks`, `rerank_scores`, `retrieval_after_rerank`, `final_prompt`, `final_answer`, `session_id`, `recent_messages_count`, `retrieved_memories_count`, and `memory_trace`.

## Memory

Status: Production foundation. Current retrieval uses PostgreSQL text search, not vector memory or graph memory.

All Memory APIs require:

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Workspace: required

Tables:

- `conversation_sessions`
- `conversation_messages`
- `agent_memories`
- `memory_operation_logs`

### POST `/api/v1/memory/sessions`

Request:

```json
{
  "title": "Support Conversation",
  "metadata": {
    "source": "swagger"
  }
}
```

Response:

```json
{
  "id": "uuid",
  "workspace_id": "demo-workspace",
  "user_id": "demo-user",
  "title": "Support Conversation",
  "status": "active",
  "metadata": {
    "source": "swagger"
  },
  "created_at": "2026-05-12T00:00:00Z",
  "updated_at": "2026-05-12T00:00:00Z"
}
```

### GET `/api/v1/memory/sessions`

Query parameters:

- `status`
- `limit`

### GET `/api/v1/memory/sessions/{session_id}`

Returns one conversation session in the current workspace.

### POST `/api/v1/memory/messages`

Request:

```json
{
  "session_id": "uuid",
  "role": "user",
  "content": "Remember that I care about memory_trace.",
  "token_count": null,
  "metadata": {
    "turn": 1
  }
}
```

Supported roles: `system`, `user`, `assistant`, `tool`.

### GET `/api/v1/memory/messages/{session_id}`

Returns ordered conversation messages for the current workspace and session.

### POST `/api/v1/memory/memories`

Request:

```json
{
  "agent_name": "AgenticRAGOrchestrator",
  "memory_type": "long_term",
  "content": "User wants Agentic RAG debug to include memory_trace.",
  "metadata": {
    "phase": "14"
  },
  "importance_score": 0.8
}
```

Supported `memory_type` values: `short_term`, `long_term`, `task_memory`, `retrieval_memory`.

### GET `/api/v1/memory/memories`

Query parameters:

- `query`
- `agent_name`
- `memory_type`
- `limit`

### DELETE `/api/v1/memory/memories/{memory_id}`

Deletes one Agent Memory entry in the current workspace.

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

### POST `/api/v1/tasks/{task_id}/cancel`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

Marks a non-terminal task in the current workspace as `cancelled` and writes `task_events` and `task_logs`.

Response:

```json
{
  "message": "Task cancelled",
  "task": {
    "id": "uuid",
    "status": "cancelled",
    "duration_ms": null
  }
}
```

### POST `/api/v1/tasks/{task_id}/retry`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

Only `failed`, `cancelled`, and `timeout` tasks can be manually retried. The task is reset to `retry`.

### GET `/api/v1/tasks/{task_id}/events`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

Response:

```json
{
  "task_id": "uuid",
  "items": [
    {
      "id": "uuid",
      "task_id": "uuid",
      "workspace_id": "demo-workspace",
      "event_type": "completed",
      "message": "Task execution completed",
      "payload": {
        "duration_ms": 120
      },
      "created_at": "2026-05-12T00:00:00Z"
    }
  ]
}
```

### GET `/api/v1/tasks/{task_id}/logs`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

Response:

```json
{
  "task_id": "uuid",
  "items": [
    {
      "id": "uuid",
      "task_id": "uuid",
      "workspace_id": "demo-workspace",
      "level": "info",
      "message": "Task execution completed",
      "metadata": {
        "provider": "mock",
        "model": "mock-llm",
        "latency_ms": 10,
        "duration_ms": 120,
        "error": null
      },
      "created_at": "2026-05-12T00:00:00Z"
    }
  ]
}
```

Task statuses:

- `pending`
- `running`
- `retry`
- `failed`
- `completed`
- `cancelled`
- `timeout`

Task observability tables:

- `task_events`
- `task_logs`
- `tasks.duration_ms`

## Observability

## Tool Calling

Status: production foundation. The current implementation is an internal Tool Framework with manual tool calls only. `openclaw_tool` is a Phase 28 mock/placeholder adapter; this layer does not include Browser Agent, real OpenClaw, Playwright, Selenium, autonomous planner, or ReAct.

### GET `/api/v1/tools`

Status: production foundation

Required headers: `X-Workspace-Id`

Workspace: required

Response:
```json
{
  "items": [
    {
      "name": "rag_search_tool",
      "description": "Search workspace knowledge with Dense/Keyword/Hybrid retrieval and reranker.",
      "input_schema": {},
      "output_schema": {},
      "enabled": true,
      "permission_scopes": ["rag:read"]
    }
  ]
}
```

### GET `/api/v1/tools/{tool_name}`

Status: production foundation

Required headers: `X-Workspace-Id`

Workspace: required

Purpose: returns a single tool's description, input schema, output schema, enabled flag, and permission scopes.

### POST `/api/v1/tools/{tool_name}/execute`

Status: production foundation

Required headers: `X-Workspace-Id`, optional `X-User-Id`

Workspace: required

Request:
```json
{
  "input": {
    "query": "automation RAG search",
    "collection_name": "docs_demo_collection",
    "search_mode": "hybrid",
    "final_top_k": 3
  }
}
```

Response:
```json
{
  "tool_name": "rag_search_tool",
  "success": true,
  "output": {
    "collection_name": "docs_demo_collection",
    "query": "automation RAG search",
    "search_mode": "hybrid",
    "items": []
  },
  "error": null,
  "latency_ms": 12
}
```

Builtin tools:
- `rag_search_tool`: calls the current Hybrid Search + Reranker flow.
- `file_search_tool`: queries `documents` / metadata in the current workspace.
- `create_task_tool`: creates a task in the current workspace.
- `get_task_status_tool`: reads task status in the current workspace.
- `current_runtime_tool`: returns current provider/search/upload settings and reads `CURRENT_RUNTIME.md` when available.
- `browser_tool`: executes safe mock browser actions through `MockBrowserProvider`.

### GET `/api/v1/tool-calls`

Status: production foundation

Required headers: `X-Workspace-Id`

Workspace: required

Query parameters:
- `tool_name`
- `agent_name`
- `success`
- `limit`

Response:
```json
{
  "items": [
    {
      "id": "uuid",
      "workspace_id": "demo-workspace",
      "agent_name": "ContentAgent",
      "tool_name": "current_runtime_tool",
      "tool_input": {
        "include_document": false
      },
      "tool_output": {
        "runtime": {
          "LLM_PROVIDER": "mock"
        }
      },
      "success": true,
      "error": null,
      "latency_ms": 3,
      "created_at": "2026-05-12T00:00:00Z"
    }
  ]
}
```

Tool observability table and fields:
- `tool_call_logs`
- `tool_name`
- `tool_input`
- `tool_output`
- `success`
- `latency_ms`

## Multi-Agent

Status: production foundation. Phase 15 implements fixed-chain Multi-Agent orchestration only. It does not implement autonomous planning, ReAct, Browser Agent, Playwright, OpenClaw, Selenium, or external platform automation.

Required headers for all Multi-Agent APIs: `X-Workspace-Id`, optional `X-User-Id`

Workspace: required. All run, message, and handoff queries are scoped by `workspace_id`.

Runtime tables:
- `agent_runs`
- `agent_messages`
- `agent_handoffs`

Registered AgentRegistry agents:
- `content_planner`
- `rag_agent`
- `content_agent`
- `review_agent`
- `runtime_agent`
- `tool_agent`

### GET `/api/v1/agents/registry`

Response:
```json
{
  "items": [
    {
      "name": "content_agent",
      "display_name": "Content Agent",
      "agent_type": "content_generation",
      "description": "ContentAgent wrapper.",
      "capabilities": ["content:generate"],
      "enabled": true,
      "metadata": {}
    }
  ]
}
```

### POST `/api/v1/multi-agent/runs`

Request:
```json
{
  "root_agent": "content_planner",
  "session_id": null,
  "input": {
    "topic": "AI automation operations",
    "platform": "tiktok",
    "style": "professional concise",
    "query": "ping",
    "collection_name": "phase15_multi_agent_demo"
  }
}
```

Response:
```json
{
  "id": "uuid",
  "workspace_id": "demo-workspace",
  "user_id": "demo-user",
  "session_id": null,
  "root_agent": "content_planner",
  "status": "pending",
  "input": {},
  "output": null,
  "error": null,
  "duration_ms": null
}
```

### GET `/api/v1/multi-agent/runs`

Query parameters:
- `status`
- `limit`

### GET `/api/v1/multi-agent/runs/{run_id}`

Returns a single run in the current workspace.

### POST `/api/v1/multi-agent/runs/{run_id}/execute-chain`

Request:
```json
{
  "chain_name": "content_planning",
  "input": {
    "topic": "AI automation operations",
    "platform": "tiktok",
    "style": "professional concise",
    "query": "ping"
  }
}
```

Response:
```json
{
  "run": {
    "id": "uuid",
    "status": "completed",
    "duration_ms": 120
  },
  "agents_involved": ["content_planner", "rag_agent", "content_agent", "review_agent"],
  "success": true,
  "error": null,
  "duration_ms": 120,
  "messages": [],
  "handoffs": []
}
```

The run output stores `agents_involved`, `handoff_trace`, and each agent's intermediate result.

### GET `/api/v1/multi-agent/runs/{run_id}/messages`

Returns `agent_messages` for the run.

### GET `/api/v1/multi-agent/runs/{run_id}/handoffs`

Returns `agent_handoffs` for the run.

## Planning

Status: production foundation. Phase 16 implements rule-based Agent Planning Foundation only. It does not implement autonomous AGI planning, tree-of-thought, recursive planning, infinite Agent loops, ReAct, Browser Agent, Playwright, OpenClaw, Selenium, or external platform automation.

Required headers: `X-Workspace-Id`, optional `X-User-Id`

Workspace: required.

Runtime tables:
- `plans`
- `plan_steps`
- `plan_reviews`

### POST `/api/v1/plans`

Request:
```json
{
  "root_goal": "Generate TikTok content for AI automation operations",
  "session_id": null,
  "planner_agent": "simple_planner",
  "metadata": {
    "query": "ping",
    "platform": "tiktok",
    "style": "professional concise"
  },
  "auto_create_steps": true
}
```

Response includes `plans` fields: `id`, `workspace_id`, `session_id`, `root_goal`, `planner_agent`, `status`, `metadata`, `created_at`, and `updated_at`.

### GET `/api/v1/plans`

Query parameters:
- `status`
- `limit`

### GET `/api/v1/plans/{plan_id}`

Returns one workspace-scoped plan.

### POST `/api/v1/plans/{plan_id}/execute`

Request:
```json
{
  "input": {
    "query": "ping"
  }
}
```

Response:
```json
{
  "plan": {
    "id": "uuid",
    "status": "completed"
  },
  "success": true,
  "status": "completed",
  "step_outputs": {},
  "review_result": "approved",
  "duration_ms": 120,
  "memory_trace": [],
  "steps": [],
  "reviews": []
}
```

Plan Execution Flow: `SimplePlannerAgent -> PlanStep -> AgentRegistry or ToolRegistry -> PlanReview`.

`PlanStep` records `status`, `duration_ms`, `error`, `input_payload`, and `output_payload`.

`PlanReview` records `reviewer_agent`, `review_result`, `score`, and `notes`.

### POST `/api/v1/plans/{plan_id}/cancel`

Marks the plan as `cancelled` and skips pending steps.

### GET `/api/v1/plans/{plan_id}/steps`

Returns `plan_steps` for the plan.

### GET `/api/v1/plans/{plan_id}/reviews`

Returns `plan_reviews` for the plan.

## Browser Adapter

Status: production foundation. Phase 17 implements Browser Automation Adapter Foundation only. It does not start a real browser and does not integrate Playwright, Selenium, OpenClaw, TikTok, YouTube, X, OCR, visual AI, or platform automation.

Required headers: `X-Workspace-Id`, optional `X-User-Id`

Workspace: required. `browser_sessions`, `browser_actions`, and `browser_action_logs` are always workspace-scoped.

Current provider state:

- `BROWSER_PROVIDER=mock`
- `BrowserProvider`
- `MockBrowserProvider`
- `PlaywrightBrowserProvider` placeholder only

Runtime tables:

- `browser_sessions`
- `browser_actions`
- `browser_action_logs`

### POST `/api/v1/browser/sessions`

Request:

```json
{
  "metadata": {
    "purpose": "swagger"
  }
}
```

### GET `/api/v1/browser/sessions`

Query parameters: `status`, `limit`.

### POST `/api/v1/browser/actions`

Request:

```json
{
  "session_id": "uuid",
  "action_type": "navigate",
  "target": "https://example.com",
  "input_payload": {
    "wait": "none"
  }
}
```

Supported `action_type` values: `navigate`, `click`, `type_text`, `scroll`, `screenshot`, `get_page_content`.

Response includes `duration_ms`, `status`, `error`, and `output_payload`.

### GET `/api/v1/browser/actions/{session_id}`

Returns `browser_actions` for one session in the current workspace.

### GET `/api/v1/browser/logs/{session_id}`

Returns `browser_action_logs` for one session in the current workspace.

### `browser_tool`

`browser_tool` can be called through the Tool API:

```json
{
  "input": {
    "action_type": "navigate",
    "target": "https://example.com",
    "input_payload": {
      "wait": "none"
    }
  }
}
```

The tool supports `navigate`, `click`, `type_text`, and `screenshot`, all through `MockBrowserProvider`.

## Phase 18 Browser API Update

Status: production foundation. Phase 18 adds `PlaywrightLocalProvider` with provider name `playwright_local` for bounded local headless Chromium execution checks. The default remains `BROWSER_PROVIDER=mock`.

Workspace: required. Sessions, actions, screenshots, and logs are always scoped by `X-Workspace-Id`.

Runtime settings:

- `BROWSER_PROVIDER=mock`
- `BROWSER_PROVIDER=playwright_local`
- `BROWSER_TIMEOUT_SECONDS=30.0`
- `BROWSER_HEADLESS=True`
- `BROWSER_TYPE=chromium`
- `BROWSER_VIEWPORT_WIDTH=1280`
- `BROWSER_VIEWPORT_HEIGHT=720`
- `BROWSER_SCREENSHOT_DIR=screenshots`

New and extended fields:

- `browser_id`
- `page_id`
- `provider_session_metadata`
- `selector`
- `target_url`
- `screenshot_path`
- `page_title`
- `get_page_content`

### POST `/api/v1/browser/actions`

Request JSON:

```json
{
  "session_id": "uuid",
  "action_type": "navigate",
  "target": "https://example.com",
  "selector": null,
  "text": null,
  "screenshot_name": null,
  "input_payload": {}
}
```

Supported action types:

- `navigate`
- `click`
- `type_text`
- `scroll`
- `screenshot`
- `get_page_content`

Core response fields:

```json
{
  "id": "uuid",
  "workspace_id": "demo-workspace",
  "session_id": "uuid",
  "action_type": "screenshot",
  "target": null,
  "selector": null,
  "target_url": "https://example.com",
  "screenshot_path": "screenshots/demo-workspace/session/example-home.png",
  "page_title": "Example Domain",
  "status": "completed",
  "error": null,
  "duration_ms": 120
}
```

### GET `/api/v1/browser/screenshot/{session_id}/{filename}`

Returns a PNG screenshot from the current workspace/session. `filename` must be a safe filename ending in `.png`.

Safety boundary:

- Allowed: `example.com`, local test pages, static `file://` pages.
- Not allowed: TikTok / YouTube / X, automatic login, cookie injection, fingerprint bypass, proxy pools, captcha automation, OCR, visual AI, autonomous browser planning, Browser Worker, or real platform automation.

## Phase 19 Remote Browser Worker API

Status: production foundation. Phase 19 implements Remote Browser Worker Foundation only: `RemoteBrowserProvider`, `BrowserWorkerClient`, Worker Registration, Worker Heartbeat, and Worker Runtime Mock. It does not deploy a real external worker.

Workspace: `/api/v1/browser-workers/*` requires `X-Workspace-Id`; mock runtime `/api/v1/browser-worker-runtime/*` is the worker protocol endpoint and does not require workspace headers.

Runtime settings:

- `BROWSER_PROVIDER=remote`
- `BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30.0`
- `BROWSER_WORKER_RETRY_COUNT=2`

Database tables:

- `browser_workers`
- `browser_worker_sessions`
- `browser_worker_actions`

Core fields:

- `remote_session_id`
- `remote_action_id`
- `worker_id`
- `worker_name`
- `base_url`
- `capabilities`

### POST `/api/v1/browser-workers/register`

Request:

```json
{
  "worker_name": "local-worker-1",
  "worker_type": "playwright",
  "base_url": "http://localhost:8000/api/v1/browser-worker-runtime",
  "capabilities": {
    "browser": "chromium",
    "screenshot": true,
    "page_content": true
  },
  "metadata": {}
}
```

Response includes `id`, `workspace_id`, `worker_name`, `worker_type`, `base_url`, `status`, `capabilities`, and `last_heartbeat_at`.

### POST `/api/v1/browser-workers/{worker_id}/heartbeat`

Request:

```json
{
  "status": "online",
  "capabilities": {
    "browser": "chromium",
    "screenshot": true
  },
  "metadata": {}
}
```

Supported `status` values: `online`, `offline`, `busy`, `error`.

### GET `/api/v1/browser-workers`

Supported query parameters:

- `status`
- `worker_type`
- `limit`

### Mock Worker Runtime

```http
GET /api/v1/browser-worker-runtime/health
POST /api/v1/browser-worker-runtime/sessions
POST /api/v1/browser-worker-runtime/actions
POST /api/v1/browser-worker-runtime/sessions/{session_id}/close
```

Mock action response example:

```json
{
  "success": true,
  "remote_action_id": "mock-remote-action-id",
  "message": "mock remote browser action success",
  "data": {
    "remote_session_id": "mock-remote-session-id",
    "action_type": "navigate",
    "target_url": "https://example.com",
    "page_title": "Mock Remote Browser"
  },
  "error": null
}
```

Boundary: the current Remote Worker layer is only a protocol foundation and in-project mock runtime. It does not implement TikTok / YouTube / X, account login, auto-publishing, proxy pools, fingerprint bypass, captcha automation, or autonomous browser agents.

## Phase 20 Real Browser Worker Service

Status: production foundation. Phase 20 upgrades the Phase 19 mock worker runtime into an independent `browser-worker` service while keeping the same safety boundary and workspace-scoped API registration flow.

API Server call chain:

```text
API Server
-> RemoteBrowserProvider
-> BrowserWorkerClient
-> http://browser-worker:9100
-> worker/main.py
-> worker/browser_worker/playwright_runtime.py
-> Playwright Chromium
```

Runtime settings:

- `BROWSER_PROVIDER=remote`
- `BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100`
- `BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30.0`
- `BROWSER_WORKER_RETRY_COUNT=2`
- `WORKER_TIMEOUT_SECONDS=30`
- `WORKER_SCREENSHOT_DIR=worker/screenshots`

Docker service:

- `browser-worker`
- Port: `9100`
- Screenshot path: `worker/screenshots/{workspace_id}/{remote_session_id}/{filename}.png`

Standalone worker endpoints:

```http
GET http://localhost:9100/health
POST http://localhost:9100/sessions
POST http://localhost:9100/actions
POST http://localhost:9100/sessions/{session_id}/close
```

Worker health response example:

```json
{
  "success": true,
  "worker_type": "playwright",
  "reachable": true,
  "capabilities": {
    "browser": "chromium",
    "headless": true,
    "screenshot": true,
    "page_content": true
  },
  "message": "browser worker reachable",
  "error": null
}
```

## Phase 21 Browser Worker Reliability API

Status: production foundation. Phase 21 adds reliability, capacity, recovery, and cleanup capabilities around Remote Browser Worker and the independent `browser-worker` service. All `/api/v1/browser-workers/*` endpoints and `/api/v1/browser/screenshots/cleanup` require `X-Workspace-Id`; `X-User-Id` is optional.

Key services and fields:

- `BrowserWorkerHealthService`
- `BrowserWorkerSelector`
- `BrowserSessionCleanupService`
- `ScreenshotCleanupService`
- `max_sessions`
- `active_sessions`
- `max_actions_per_minute`
- `current_load`
- `priority`
- `error_message`
- `last_seen`
- `retry_count`
- `max_retries`
- `BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS`
- `BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS`
- `BROWSER_SESSION_TIMEOUT_SECONDS`
- `BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS`
- `BROWSER_ACTION_TIMEOUT_SECONDS`
- `BROWSER_ACTION_RETRY_COUNT`
- `BROWSER_ACTION_RETRY_BACKOFF_SECONDS`
- `SCREENSHOT_RETENTION_DAYS`

### POST `/api/v1/browser-workers/register`

Phase 21 request extension:

```json
{
  "worker_name": "local-worker-1",
  "worker_type": "playwright",
  "base_url": "http://browser-worker:9100",
  "capabilities": {
    "browser": "chromium",
    "screenshot": true,
    "page_content": true
  },
  "metadata": {},
  "max_sessions": 2,
  "max_actions_per_minute": 60,
  "priority": 100
}
```

Response includes:

```json
{
  "id": "worker-id",
  "workspace_id": "demo-workspace",
  "worker_name": "local-worker-1",
  "worker_type": "playwright",
  "base_url": "http://browser-worker:9100",
  "status": "online",
  "capabilities": {
    "browser": "chromium"
  },
  "last_seen": "2026-05-13T10:00:00",
  "max_sessions": 2,
  "active_sessions": 0,
  "max_actions_per_minute": 60,
  "current_load": 0,
  "priority": 100,
  "error_message": null,
  "metadata": {}
}
```

### GET `/api/v1/browser-workers/health/summary`

Returns worker health summary and runs stale worker detection:

```json
{
  "workspace_id": "demo-workspace",
  "total_workers": 2,
  "online_workers": 1,
  "offline_workers": 1,
  "busy_workers": 0,
  "error_workers": 0,
  "stale_workers": 1,
  "available_workers": 1
}
```

### GET `/api/v1/browser-workers/available`

Returns workers assignable by `BrowserWorkerSelector`, ordered by `current_load`, `active_sessions`, and `priority`:

```json
{
  "items": [
    {
      "id": "worker-id",
      "worker_name": "local-worker-1",
      "status": "online",
      "active_sessions": 0,
      "max_sessions": 2,
      "current_load": 0,
      "priority": 100
    }
  ]
}
```

### POST `/api/v1/browser-workers/{worker_id}/mark-offline`

Manually marks a worker offline:

```json
{
  "error_message": "manual maintenance"
}
```

### POST `/api/v1/browser-workers/cleanup-sessions`

Runs manual session cleanup:

```json
{
  "session_timeout_seconds": 1800,
  "close_remote": false
}
```

Response:

```json
{
  "workspace_id": "demo-workspace",
  "stale_sessions": 1,
  "offline_worker_sessions": 0,
  "closed_sessions": 1,
  "failed_sessions": 0,
  "log_count": 1
}
```

### GET `/api/v1/browser-workers/{worker_id}/sessions`

Returns sessions assigned to a worker:

```json
{
  "items": [
    {
      "id": "worker-session-id",
      "workspace_id": "demo-workspace",
      "worker_id": "worker-id",
      "remote_session_id": "remote-session-id",
      "local_browser_session_id": "browser-session-id",
      "status": "active",
      "metadata": {}
    }
  ]
}
```

### POST `/api/v1/browser/screenshots/cleanup`

Cleans screenshots by workspace. Dry-run is the default:

```json
{
  "older_than_days": 7,
  "dry_run": true
}
```

Response:

```json
{
  "workspace_id": "demo-workspace",
  "root_dir": "screenshots;worker/screenshots",
  "older_than_days": 7,
  "dry_run": true,
  "matched_files": 2,
  "deleted_files": 0,
  "bytes_freed": 0
}
```

Boundary: Phase 21 does not provide TikTok / YouTube / X automation, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, OCR, visual AI, OpenClaw, real platform automation, or autonomous browser planning.

## Phase 22 Persistent Browser Profile API

Status: production foundation. Phase 22 adds Persistent Browser Profile Foundation for saving browser state and preparing future long-running sessions, manual takeover, and account-environment isolation. It does not perform login, inject cookies, configure fingerprints, or automate real platforms.

Core objects and fields:

- `browser_profiles`
- `BrowserProfileService`
- `profile_id`
- `profile_path`
- `persistent_context_enabled`
- `locked_by_session_id`
- `locked_at`
- `last_used_at`
- `launch_persistent_context`
- `BROWSER_PROFILE_ROOT`
- `WORKER_PROFILE_DIR`

### POST `/api/v1/browser/profiles`

Request:

```json
{
  "profile_name": "demo-profile",
  "profile_type": "persistent",
  "provider": "remote",
  "metadata": {
    "purpose": "manual takeover preparation"
  }
}
```

Response:

```json
{
  "id": "profile-id",
  "workspace_id": "demo-workspace",
  "user_id": "demo-user",
  "profile_name": "demo-profile",
  "profile_type": "persistent",
  "provider": "remote",
  "profile_path": "worker/profiles/demo-workspace/profile-id",
  "status": "available",
  "locked_by_session_id": null,
  "locked_at": null,
  "last_used_at": null,
  "metadata": {},
  "created_at": "2026-05-13T10:00:00Z",
  "updated_at": "2026-05-13T10:00:00Z"
}
```

### GET `/api/v1/browser/profiles`

Supported query parameters: `status`, `limit`.

### GET `/api/v1/browser/profiles/{profile_id}`

Returns one profile scoped by `X-Workspace-Id`.

### POST `/api/v1/browser/profiles/{profile_id}/lock`

Manually locks a profile. Session creation normally performs this automatically.

```json
{
  "session_id": "browser-session-id"
}
```

### POST `/api/v1/browser/profiles/{profile_id}/release`

Manually releases a profile. Session close normally performs this automatically.

```json
{
  "session_id": "browser-session-id"
}
```

### DELETE `/api/v1/browser/profiles/{profile_id}`

Logically deletes a profile. Locked profiles cannot be deleted.

### POST `/api/v1/browser/sessions`

Phase 22 request extension:

```json
{
  "profile_id": "profile-id",
  "use_persistent_profile": true,
  "metadata": {
    "scenario": "persistent-context-smoke"
  }
}
```

Response includes:

```json
{
  "id": "browser-session-id",
  "profile_id": "profile-id",
  "profile_path": "worker/profiles/demo-workspace/profile-id",
  "persistent_context_enabled": true,
  "status": "active"
}
```

### POST `/api/v1/browser/sessions/{session_id}/close`

Closes the browser session and releases the profile lock:

```json
{
  "id": "browser-session-id",
  "status": "closed",
  "profile_id": "profile-id",
  "persistent_context_enabled": true
}
```

Persistent Context Flow:

```text
POST /api/v1/browser/profiles
-> POST /api/v1/browser/sessions with profile_id
-> BrowserProfileService.lock_profile
-> RemoteBrowserProvider
-> browser-worker launch_persistent_context
-> worker/profiles/{workspace_id}/{profile_id}
-> POST /api/v1/browser/sessions/{session_id}/close
-> BrowserProfileService.release_profile
```

Boundary: Phase 22 does not support TikTok / YouTube / X, login, cookie injection, proxy pools, fingerprint bypass, captcha handling, or real platform automation.

Register worker request:

```json
{
  "worker_name": "browser-worker",
  "worker_type": "playwright",
  "base_url": "http://browser-worker:9100",
  "capabilities": {
    "browser": "chromium",
    "screenshot": true,
    "page_content": true
  },
  "metadata": {
    "phase": "20"
  }
}
```

Worker action request:

```json
{
  "remote_session_id": "worker-session-id",
  "action_type": "screenshot",
  "target": null,
  "input_payload": {
    "screenshot_name": "example-home"
  }
}
```

Boundary: Phase 20 does not support TikTok / YouTube / X, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha automation, OCR, visual AI, OpenClaw, autonomous browser agents, or production external worker fleet management.

### GET `/api/v1/observability/summary`

Status: Production foundation

Headers: `X-Workspace-Id`

Workspace: required

Response:

```json
{
  "pending_count": 1,
  "running_count": 0,
  "failed_count": 0,
  "completed_count": 3,
  "cancelled_count": 1,
  "timeout_count": 0,
  "avg_duration_ms": 128.5
}
```

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

## Phase 23 Browser Profile Health & Recovery API

Status: production foundation. Phase 23 strengthens Persistent Browser Profile stability, recovery, and lifecycle management. It still does not support TikTok / YouTube / X automation, account login, cookie injection, proxy pools, fingerprint bypass, captcha handling, or real platform automation.

Required headers: `X-Workspace-Id`; `X-User-Id` is recommended. All profile APIs are workspace-isolated and cannot read, recover, back up, or clean up profiles from another workspace.

Core tables and fields:

- `browser_profiles` adds `health_status`, `last_health_check_at`, `last_error`, `usage_count`, `corrupted_at`, `backup_path`, and `last_backup_at`.
- `browser_profile_usage_logs` records profile lifecycle events such as `lock`, `release`, `session_start`, `session_close`, `backup`, `restore`, `recovery`, `cleanup`, and `health_check`.
- `health_status` supports `healthy`, `warning`, `corrupted`, `stale`, and `deleted`.

Core services:

- `BrowserProfileHealthService`: profile health checks, warning/corrupted marking, stale lock recovery, profile path/runtime validation, usage count, usage logs, and health/summary.
- `BrowserProfileBackupService`: profile backup, list backups, restore backup, and backup retention.
- `BrowserProfileCleanupService`: deleted/corrupted/unused profile directory cleanup, dry-run by default.

Runtime settings:

```text
BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS=1800
BROWSER_PROFILE_BACKUP_ENABLED=True
BROWSER_PROFILE_MAX_BACKUPS=3
BROWSER_PROFILE_UNUSED_DAYS=30
BROWSER_PROFILE_BACKUP_ROOT=worker/profile_backups
```

### GET `/api/v1/browser/profiles/health/summary`

Returns profile health totals for the current workspace.

Response:

```json
{
  "workspace_id": "demo-workspace",
  "total_profiles": 3,
  "healthy_count": 1,
  "warning_count": 0,
  "corrupted_count": 1,
  "stale_count": 1,
  "deleted_count": 0
}
```

### POST `/api/v1/browser/profiles/{profile_id}/health-check`

Checks one profile path, lock state, and lifecycle status.

Response:

```json
{
  "healthy": true,
  "health_status": "healthy",
  "error": null,
  "profile": {
    "id": "profile-id",
    "health_status": "healthy",
    "usage_count": 1,
    "last_health_check_at": "2026-05-13T12:00:00Z",
    "last_error": null,
    "backup_path": null,
    "last_backup_at": null
  }
}
```

### POST `/api/v1/browser/profiles/recover-stale-locks`

Recovers stale profile locks held by timed-out locks, closed/failed sessions, or offline/error workers in the current workspace.

Response:

```json
{
  "workspace_id": "demo-workspace",
  "recovered_count": 1,
  "checked_count": 2,
  "recovered_profile_ids": ["profile-id"]
}
```

### POST `/api/v1/browser/profiles/{profile_id}/backup`

Creates a profile zip backup under `worker/profile_backups/{workspace_id}/{profile_id}`.

Response:

```json
{
  "workspace_id": "demo-workspace",
  "profile_id": "profile-id",
  "backup_path": "worker/profile_backups/demo-workspace/profile-id/profile-20260513T120000Z.zip",
  "success": true,
  "error": null,
  "retained_backups": 1
}
```

### GET `/api/v1/browser/profiles/{profile_id}/backups`

Lists retained profile zip backups.

### POST `/api/v1/browser/profiles/{profile_id}/restore`

Restores profile files from a selected backup zip.

Request:

```json
{
  "backup_path": "worker/profile_backups/demo-workspace/profile-id/profile-20260513T120000Z.zip"
}
```

### POST `/api/v1/browser/profiles/cleanup`

Cleans deleted/corrupted/unused profile directories. The default is `dry_run=true`.

Request:

```json
{
  "include_deleted": true,
  "include_corrupted": true,
  "include_unused": true,
  "dry_run": true
}
```

Response:

```json
{
  "workspace_id": "demo-workspace",
  "dry_run": true,
  "deleted_profiles": 1,
  "corrupted_profiles": 1,
  "unused_profiles": 0,
  "matched_profiles": 2,
  "removed_paths": 0,
  "bytes_freed": 0
}
```

### GET `/api/v1/browser/profiles/{profile_id}/usage-logs`

Returns profile usage logs.

Response:

```json
{
  "items": [
    {
      "id": "usage-log-id",
      "workspace_id": "demo-workspace",
      "profile_id": "profile-id",
      "session_id": "browser-session-id",
      "action": "recovery",
      "success": true,
      "error": null,
      "metadata": {
        "reason": "profile lock exceeded 1800s"
      },
      "created_at": "2026-05-13T12:00:00Z"
    }
  ]
}
```

## Phase 29 Worker Client Local Management API

Status: completed runtime foundation. These endpoints are exposed by the customer-machine `worker_client.runtime` service, not by the central AI Server OpenAPI.

Required local host: default `runtime_host: 127.0.0.1`, `runtime_port: 9100`.

- `GET /local/status`
  - response: local runtime state from `worker_client/status.py`, backed by `worker_client/runtime_state/status.json`.
  - fields: `worker_id`, `worker_name`, `workspace_id`, `server_url`, `runtime_running`, `heartbeat_running`, `registered`, `last_heartbeat_at`, `last_error`, `current_status`, `openclaw_enabled`, `browser_enabled`.
- `GET /local/health`
  - response: `Worker Runtime Manager` health with `runtime_running`, `heartbeat_running`, `host`, `port`, and `localhost_only`.
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`
- `GET /local/logs`
  - response: recent lines from `worker_client/logs/worker.log`.

Implementation files:

- `worker_client/runtime_manager.py`
- `worker_client/status.py`
- `worker_client/logging.py`
- `worker_client/local_api_client.py`
- `worker_client/runtime_state/status.json`
- `worker_client/logs/worker.log`

Packaging Scripts:

- `packaging/windows_start_worker.ps1`
- `packaging/mac_start_worker.sh`

Worker Console Foundation:

- `Desktop Runtime Placeholder` exists under `worker_client/desktop/`.
- Current state is `no GUI`; no Electron, no Tauri, no PySide, no system tray, no exe/dmg packaging.

## Phase 30 Worker Console Local Web API Usage

Worker Console frontend calls the local worker client API through `worker_console/src/api/localWorkerClient.ts`.

Config:

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

Used local endpoints:

- `GET /local/status`
- `GET /local/health`
- `GET /local/logs`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`

UI unreachable state: `Worker API unreachable`, `请确认 worker_client 是否启动`, `请确认端口是否为 9100`.

Phase 30 API doc marker: Worker Console GUI Foundation uses Vite, React, TypeScript, and Tailwind. Runtime Control is local-only. Current boundary: no exe / dmg.
## Phase 31: Worker Console Desktop Local API

Status: completed, local desktop shell capability. Scope name: Worker Console Desktop App Foundation.

`worker_console_desktop` does not add new AI Server APIs. It reuses the customer-machine `worker_client` Local API:

- `GET /local/status`
- `GET /local/health`
- `GET /local/logs`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`

Default configuration:

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
status_url=http://127.0.0.1:9100/local/status
tauri_config=worker_console_desktop/src-tauri/tauri.conf.json
src-tauri/tauri.conf.json
```

Unreachable-state text includes `Worker Runtime 未启动`.

Development commands:

```bash
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

Current boundary: no exe / dmg, no system tray, no auto update, and no formal installer.
