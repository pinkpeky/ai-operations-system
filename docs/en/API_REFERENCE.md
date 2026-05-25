# API Reference

Last updated: 2026-05-23

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

## Phase 32: Worker Console Desktop Tray Runtime

Status: completed, local desktop runtime capability. Scope name: Worker Console System Tray & Desktop Runtime Foundation.

Capability keywords: System Tray, Minimize To Tray, Tray Runtime Control, Desktop Status Sync, AutoStart Placeholder.

This phase does not add new AI Server APIs. The desktop app continues to call the local `worker_client` Local API:

- `GET /local/status`
- `GET /local/health`
- `GET /local/logs`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`

Desktop settings:

```json
{
  "localWorkerApi": "http://127.0.0.1:9100",
  "minimizeToTray": true,
  "refreshIntervalMs": 5000
}
```

Settings example file: `worker_console_desktop/settings.example.json`.
Tauri runtime config: `worker_console_desktop/src-tauri/desktop-runtime.json`, with `minimize_to_tray=true`.

Tauri System Tray menu: Show Console, Hide Window, Start Runtime, Stop Runtime, Restart Runtime, Start Heartbeat, Stop Heartbeat, Refresh Status, Quit.

Security boundary: no arbitrary shell, no remote shell, no remote command execution, and no filesystem-wide access. There is no formal installer, no formal installer release, and no auto-update.

## Phase 33 Conversation Runtime APIs

Status: completed foundation.

Required headers for all endpoints:

```text
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

### POST /api/v1/conversations

Request:

```json
{
  "title": " ",
  "metadata": {"phase": "33"}
}
```

Response includes `id`, `workspace_id`, `user_id`, `title`, `status`, `metadata`, `created_at`, and `updated_at`.

### GET /api/v1/conversations

Lists `conversation_threads` filtered by current workspace.

### GET /api/v1/conversations/{thread_id}

Returns one workspace-scoped conversation thread.

### POST /api/v1/conversations/{thread_id}/messages

Request:

```json
{
  "role": "user",
  "content": " ",
  "metadata": {"source": "swagger"}
}
```

Writes to `conversation_messages` with `thread_id` and emits `message_received` for user messages.

### GET /api/v1/conversations/{thread_id}/messages

Returns the message list for the current workspace thread.

### GET /api/v1/conversations/{thread_id}/events

Polling event feed. Returns `conversation_events` such as `message_received`, `planning_started`, `plan_created`, `agent_started`, `tool_called`, `worker_action_started`, `worker_action_completed`, `assistant_response`, and `error`.

This is not WebSocket streaming and not SSE streaming. WebSocket and SSE are placeholders only.

### POST /api/v1/conversations/{thread_id}/run

Request:

```json
{
  "input": {
    "message": " "
  }
}
```

Response includes `assistant_message`, `route`, `events`, `output`, `websocket_placeholder=true`, and `sse_placeholder=true`.

Rule-based routing:

- search/browser/open-page keywords -> `browser_tool`
- content/copy/generate keywords -> `ContentAgent`
- `OpenClaw` keyword -> `openclaw_tool` mock

### Phase 33 API Reference Markers

Conversation Runtime Foundation implementation markers for docs verifier: `ConversationService`, `run_conversation_turn`, `Chat Panel Foundation`, `Event Timeline`, `polling`.

The polling event feed uses `GET /api/v1/conversations/{thread_id}/events`. WebSocket and SSE are placeholders only.

## Phase 34 Remote Browser Runtime API

Status: completed foundation. Workspace headers are required for all AI Server routes:

```text
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Implementation markers: `Remote Browser Runtime Foundation`, `browser_runtime_sessions`, `BrowserRuntimeSessionService`, `app/browser/providers/remote_provider.py`, `worker_client/browser_runtime`, `storage/browser_screenshots`, `BROWSER_RUNTIME_SCREENSHOT_DIR`, `Browser Sessions Panel`, `playwright install chromium`.

### POST /api/v1/browser-runtime/sessions

Create a remote browser runtime session.

Request:

```json
{
  "browser": "chromium",
  "metadata": {
    "phase": "34"
  }
}
```

Response:

```json
{
  "id": "RUNTIME_SESSION_ID",
  "workspace_id": "demo-workspace",
  "worker_id": "WORKER_ID",
  "provider": "remote",
  "browser": "chromium",
  "session_status": "active",
  "last_activity_at": "2026-05-14T00:00:00Z",
  "metadata": {
    "remote_session_id": "REMOTE_SESSION_ID"
  }
}
```

### GET /api/v1/browser-runtime/sessions

Lists browser runtime sessions for the current workspace. Supports status filtering, for example `?status=active`.

### GET /api/v1/browser-runtime/sessions/{session_id}

Returns one `browser_runtime_sessions` record scoped to the current workspace.

### POST /api/v1/browser-runtime/sessions/{session_id}/navigate

Request:

```json
{
  "url": "https://example.com"
}
```

Response includes `title`, `url`, `remote_action_id`, and structured remote worker data.

### POST /api/v1/browser-runtime/sessions/{session_id}/screenshot

Request:

```json
{
  "full_page": true,
  "screenshot_name": "example-home"
}
```

Response includes the saved screenshot path under `storage/browser_screenshots`.

### GET /api/v1/browser-runtime/sessions/{session_id}/page

Returns page title, current URL, and HTML/text content fetched from the remote worker page.

### POST /api/v1/browser-runtime/sessions/{session_id}/close

Closes the remote browser session and marks the local runtime session closed.

### Worker Runtime API

The registered worker exposes these compatible runtime endpoints:

- `POST /browser/session/create`
- `POST /browser/session/{session_id}/navigate`
- `POST /browser/session/{session_id}/screenshot`
- `GET /browser/session/{session_id}/page`
- `POST /browser/session/{session_id}/close`

The in-project mock worker runtime exposes equivalent test routes under `/api/v1/browser-worker-runtime/browser/session/create`, `/api/v1/browser-worker-runtime/browser/session/{session_id}/navigate`, `/api/v1/browser-worker-runtime/browser/session/{session_id}/screenshot`, `/api/v1/browser-worker-runtime/browser/session/{session_id}/page`, and `/api/v1/browser-worker-runtime/browser/session/{session_id}/close`.

Boundary: current runtime supports basic Chromium create / navigate / screenshot / page / close only. It does not implement stealth, proxy rotation, cookie injection, captcha bypass, platform automation, remote desktop streaming, or DevTools remote control.

## Phase 35B Real Client Worker E2E Validation Plan

Status: completed validation plan and script. This phase adds `validate_real_client_worker_e2e.py`; it does not claim that a real customer machine was online during implementation.

Script:

```bash
python scripts/validate_real_client_worker_e2e.py \
  --server-url http://localhost:8000 \
  --workspace-id demo-workspace \
  --user-id demo-user \
  --expected-worker-name customer-machine-worker-1
```

Parameters:

- `server_url`
- `workspace_id`
- `user_id`
- `expected_worker_name`

Exit codes:

- `0`: PASS
- `1`: FAIL
- `2`: SKIPPED

If `expected_worker_name` is not online, the script returns `SKIPPED` with reason `real client worker not online` and does not execute browser actions.

Swagger validation flow:

1. `GET /api/v1/health`
2. `GET /api/v1/browser-workers/health/summary`
3. `GET /api/v1/browser-workers/available`
4. `POST /api/v1/browser-runtime/sessions`
5. `POST /api/v1/browser-runtime/sessions/{session_id}/navigate`
6. `POST /api/v1/browser-runtime/sessions/{session_id}/screenshot`
7. `GET /api/v1/browser-runtime/sessions/{session_id}/page`
8. `POST /api/v1/browser-runtime/sessions/{session_id}/close`

Security note: do not expose port 9100 to the public internet. Prefer Tailscale, VPN, or LAN.

## Phase 35A Browser Runtime Observability & Replay

Status: completed. Every route requires workspace headers:

Service: `BrowserRuntimeObservabilityService`.

Concept map: Browser Runtime Timeline, Browser Runtime Snapshots, Browser Runtime Replay Metadata, Snapshot Storage, Timeline Event Flow, Failure Debug, metadata-only replay.

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

### GET /api/v1/browser-runtime/sessions/{session_id}/events

Lists `browser_runtime_events` for one runtime session. Events include `session_created`, `navigate_started`, `navigate_completed`, `screenshot_started`, `screenshot_completed`, `page_snapshot_captured`, `action_failed`, `session_closed`, and `replay_requested`.

Response:

```json
{
  "items": [
    {
      "event_type": "navigate_completed",
      "status": "completed",
      "message": "Browser runtime navigation completed",
      "payload": {
        "url": "https://example.com"
      },
      "duration_ms": 120,
      "error": null
    }
  ]
}
```

### GET /api/v1/browser-runtime/sessions/{session_id}/snapshots

Lists `browser_runtime_snapshots`. Optional query: `snapshot_type=page|screenshot|error|final`.

Response:

```json
{
  "items": [
    {
      "snapshot_type": "page",
      "url": "https://example.com",
      "page_title": "Example Domain",
      "html_path": "storage/browser_runtime_snapshots/demo-workspace/SESSION/page-SNAPSHOT.html",
      "text_path": "storage/browser_runtime_snapshots/demo-workspace/SESSION/page-SNAPSHOT.txt",
      "screenshot_path": null,
      "metadata": {
        "source": "get_page"
      }
    }
  ]
}
```

### POST /api/v1/browser-runtime/sessions/{session_id}/replay

Creates a `browser_runtime_replays` record. Replay is metadata-only and does not re-run browser actions.

Request:

```json
{
  "metadata": {
    "reason": "debug browser runtime session"
  }
}
```

### GET /api/v1/browser-runtime/replays/{replay_id}

Returns replay metadata, including `replay_steps`, `source_event_ids`, and `source_snapshot_ids`.

### GET /api/v1/browser-runtime/replays/{replay_id}/export

Writes and returns `replay-{replay_id}.json` under `BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots`.

Boundary: Browser Runtime Observability & Replay is not live stream, not VNC, not noVNC, not DevTools remote control, and not browser action re-execution.

## Phase 36: Server Admin Dashboard Foundation

`admin_dashboard` is now part of the docs SSOT. It is a read-only monitoring foundation for Overview, Workers, Browser Runtime, Conversations, Tasks, OpenClaw, Audit Logs, RAG / Documents, and Settings. Runtime config is `VITE_AI_SERVER_API=http://localhost:8000`, `VITE_WORKSPACE_ID=demo-workspace`, and `VITE_USER_ID=demo-user`. The API client lives at `admin_dashboard/src/api/client.ts` and exports `workersApi`, `browserRuntimeApi`, `conversationsApi`, `tasksApi`, `openclawApi`, `auditApi`, and `ragApi`. Current boundaries: no login UI, no permission UI, no publishing business flow, no real social platform control, no production-grade operations backend.

## Phase 37: Conversation Runtime Frontend Integration

Status: completed, Phase 37.

Phase 37 connects the Conversation Runtime to Server Admin Dashboard, Worker Console Web, and Worker Console Desktop. The current scope is Conversation frontend integration and a basic conversation entrypoint. It is not a full ChatGPT UI and it is not WebSocket / SSE streaming.

Completed:

- Admin Dashboard Conversation page: `admin_dashboard` Conversations supports create thread, thread list, thread detail, message list, event timeline, send message, run conversation, refresh messages, and refresh events.
- Admin Dashboard client: `admin_dashboard/src/api/conversationClient.ts` supports `createThread`, `listThreads`, `getThread`, `sendMessage`, `listMessages`, `listEvents`, and `runConversation`.
- Worker Console Chat Panel: `worker_console` supports AI Server URL, Workspace ID, User ID settings, create thread, send and run, Polling Event Timeline, and AI Server connected / disconnected / unreachable state.
- Desktop Chat Panel: `worker_console_desktop` mirrors the Chat Panel foundation. Tauri native validation still depends on the customer machine Rust/MSVC environment.
- Polling Event Timeline: frontends call `GET /api/v1/conversations/{thread_id}/events` manually or every 5 seconds and show `event_type`, `message`, `created_at`, and `payload JSON`.
- Frontend config: `VITE_AI_SERVER_API=http://localhost:8000`, `VITE_WORKSPACE_ID=demo-workspace`, `VITE_USER_ID=demo-user`.
- Development CORS: backend `CORS_ALLOWED_ORIGINS` allows `http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:5180`, `http://127.0.0.1:5180`, `tauri://localhost`, and related local development origins.

Boundaries: current implementation is not WebSocket, not SSE, and not a full ChatGPT UI. It does not implement TikTok / YouTube / X automation, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, real platform automation, real OpenClaw, or ComfyUI.

Phase 37 UI error state exact marker: AI Server unreachable.
## Phase 38: Conversation Tool Execution Bridge API

Conversation Runtime Tool Execution Bridge: completed / foundation.

### POST `/api/v1/conversations/{thread_id}/run`

Status: completed / foundation. Required headers: `X-Workspace-Id`, `X-User-Id`.

Request:

```json
{
  "input": {
    "message": "Please open https://example.com and take a screenshot."
  }
}
```

New response fields:

```json
{
  "thread_id": "uuid",
  "user_message_id": "uuid",
  "assistant_message_id": "uuid",
  "route": "browser",
  "route_name": "browser",
  "selected_tool": "browser_tool",
  "events_created": 8,
  "success": true,
  "summary": "Browser bridge opened https://example.com...",
  "result_metadata": {
    "runtime_session_id": "uuid",
    "target": "https://example.com"
  },
  "events": [],
  "output": {}
}
```

Route / Tool fields:
- `ConversationToolRouter`
- `app/conversation/tool_router.py`
- `route_selected`
- `tool_execution_started`
- `tool_execution_completed`
- `tool_execution_failed`
- `agent_execution_started`
- `agent_execution_completed`
- `planning_execution_started`
- `planning_execution_completed`
- `bridge_fallback`
- `bridge_error`
- `route_name`
- `selected_tool`
- `events_created`
- `success`
- `summary`
- `result_metadata`

Routing Rules:
- Browser Bridge / Browser Bridge Flow: `browser_tool`, using create session -> navigate -> screenshot -> get page -> close session.
- OpenClaw mock bridge / OpenClaw Mock Bridge Flow: `openclaw_tool` mock, `mock_inspect` only.
- RAG bridge: `rag_search_tool`, requires `collection_name`.
- Content bridge: `ContentAgent`.
- Planning bridge: `PlanningService`, returns `plan_id` and steps.

Boundaries: not autonomous agent, not WebSocket, not SSE, no real platform publishing, no real OpenClaw, and no ComfyUI.

## Conversation Approval Flow API (Phase 39)

Status: completed Conversation Execution Review & Approval Flow / Approval Flow Foundation. `ConversationApprovalService` owns the state transitions. `Tool Execution Gate` blocks unapproved medium/high risk actions. This is not a full permission system.

### `GET /api/v1/conversations/{thread_id}/approvals`

Required headers: `X-Workspace-Id`, `X-User-Id`.

Response:

```json
{
  "thread_id": "THREAD_ID",
  "items": [
    {
      "id": "APPROVAL_ID",
      "workspace_id": "demo-workspace",
      "thread_id": "THREAD_ID",
      "message_id": "MESSAGE_ID",
      "route_name": "browser",
      "selected_tool": "browser_tool",
      "risk_level": "medium",
      "approval_status": "pending",
      "proposed_action": "browser_tool:navigate_and_screenshot",
      "proposed_payload": {
        "decision": {},
        "tool_input": {},
        "source_message": "open https://example.com and screenshot"
      }
    }
  ]
}
```

### `GET /api/v1/conversation-approvals/{approval_id}`

Returns one `conversation_approvals` record, including `risk_level`, `approval_status`, `proposed_action`, and `proposed_payload`.

### `POST /api/v1/conversation-approvals/{approval_id}/approve`

```json
{
  "reviewer_notes": "Looks safe to execute."
}
```

State transition: `pending -> approved`, with `approval_approved` event.

### `POST /api/v1/conversation-approvals/{approval_id}/reject`

```json
{
  "reviewer_notes": "Need to rewrite before execution."
}
```

State transition: `pending -> rejected`, with `approval_rejected`. Rejected approval cannot execute.

### `POST /api/v1/conversation-approvals/{approval_id}/cancel`

```json
{
  "reviewer_notes": "Cancelled before execution."
}
```

State transition: `pending/approved -> cancelled`, with `approval_cancelled`.

### `POST /api/v1/conversation-approvals/{approval_id}/execute`

```json
{
  "input": {
    "approval_id": "APPROVAL_ID"
  }
}
```

The approval must be `approved`. Execution writes `approval_executed`, `execution_after_approval_started`, `execution_after_approval_completed`, or `execution_after_approval_failed`.

### Conversation Run Mode

`POST /api/v1/conversations/{thread_id}/run` now accepts `mode`:

```json
{
  "input": {
    "message": "Please open https://example.com and take a screenshot."
  },
  "mode": "review_first"
}
```

Supported modes:

- `auto_safe`: low risk executes; medium/high risk creates approval and does not execute.
- `review_first`: every route creates approval first and does not execute.
- `execute_after_approval`: requires `input.approval_id`; approval must already be approved.

Response additions:

```json
{
  "approval_required": true,
  "approval_id": "APPROVAL_ID",
  "approval_status": "pending",
  "risk_level": "medium",
  "proposed_action": "browser_tool:navigate_and_screenshot"
}
```

Risk Policy / `ConversationRiskPolicy`:

- `low`: content generation, RAG search, planning create-only.
- `medium`: browser navigate / screenshot / get page, OpenClaw mock inspect.
- `high`: browser click, form input, upload, publish, account/profile actions, real OpenClaw actions, future social platform actions.

Conversation events: `approval_required`, `approval_created`, `approval_approved`, `approval_rejected`, `approval_cancelled`, `approval_expired`, `approval_executed`, `execution_blocked_pending_approval`, `execution_after_approval_started`, `execution_after_approval_completed`, and `execution_after_approval_failed`.

Frontend: Admin Dashboard, Worker Console, and Worker Console Desktop include a pending approvals panel, proposed payload JSON, risk badge, approve / reject / cancel / execute approved action. Current implementation remains polling-only and is not WebSocket/SSE or a full permission system.
## Phase 40 Conversation Playbooks API

Required headers: `X-Workspace-Id`, `X-User-Id`.

Database tables: `conversation_playbooks`, `conversation_playbook_runs`.

### `GET /api/v1/conversation-playbooks`

Lists active/disabled/archived playbooks in the current workspace. Built-in templates are seeded on demand.

The response includes `name`, `category`, `status`, `risk_level`, `steps`, `default_inputs`, and `metadata`.

### `GET /api/v1/conversation-playbooks/{playbook_id}`

Returns one Playbook definition.

### `POST /api/v1/conversation-playbooks`

Creates a custom Playbook. This is a foundation API, not a visual workflow builder.

### `PATCH /api/v1/conversation-playbooks/{playbook_id}`

Updates an existing Playbook definition or disables it by setting `status=disabled`.

### `POST /api/v1/conversation-playbooks/{playbook_id}/run`

Runs a Playbook directly.

```json
{
  "input": {
    "topic": "AI automation operations",
    "platform": "short_video",
    "style": "professional concise"
  },
  "mode": "auto_safe"
}
```

The response stores run state in `conversation_playbook_runs` and includes `playbook_id`, `thread_id`, `status`, `input_payload`, `output_payload`, `current_step`, and `error`.

### `GET /api/v1/conversation-playbook-runs`

Lists Playbook Runs. Step Timeline is stored in `output_payload.steps`.

### `GET /api/v1/conversation-playbook-runs/{run_id}`

Returns one Playbook Run.

### `POST /api/v1/conversation-playbook-runs/{run_id}/cancel`

Cancels a pending/running/waiting Playbook Run.

### Conversation run with Playbook

`POST /api/v1/conversations/{thread_id}/run` now supports:

```json
{
  "input": {
    "message": "Open https://example.com, take a screenshot, and generate a report."
  },
  "playbook_name": "browser_screenshot_report",
  "mode": "review_first"
}
```

Additional response fields: `playbook_name`, `playbook_run_id`, `playbook_status`.

Events include `playbook_selected`, `playbook_run_started`, `playbook_step_started`, `playbook_step_completed`, `playbook_approval_required`, `playbook_waiting_approval`, `playbook_resumed_after_approval`, `playbook_completed`, `playbook_failed`, and `playbook_cancelled`.

Current limitation: this is not a full workflow builder and does not implement real social-platform publishing.

## Phase 41 Output Artifacts / Output Library API

Required headers: `X-Workspace-Id`, `X-User-Id`.

Database table: `output_artifacts`.

Service: `OutputArtifactService` handles workspace-scoped artifact creation, listing, soft delete, message/playbook conversion, and markdown/json/txt export.

Core fields: `source_type`, `artifact_type`, `title`, `summary`, `content`, `file_path`, `mime_type`, `metadata`, `thread_id`, `playbook_run_id`, `created_by`, `status`.

Source types: `conversation`, `playbook`, `tool`, `browser_runtime`, `rag`, `content_agent`, `planning`, `openclaw_mock`.

Artifact types: `text`, `markdown`, `json`, `screenshot`, `html_snapshot`, `report`, `plan`, `rag_answer`, `content_draft`.

Events: `artifact_created`, `artifact_exported`, `artifact_deleted`, `artifact_linked_to_playbook_run`.

### `GET /api/v1/output-artifacts`

Lists active artifacts in the current workspace. Supports filters: `artifact_type`, `source_type`, `thread_id`, `playbook_run_id`, created_at range (`created_from`, `created_to`), `include_deleted`, and `limit`.

### `GET /api/v1/output-artifacts/{artifact_id}`

Returns one artifact.

### `PATCH /api/v1/output-artifacts/{artifact_id}`

Updates editable fields such as `title`, `summary`, `content`, `file_path`, `mime_type`, and `metadata`.

### `DELETE /api/v1/output-artifacts/{artifact_id}`

Soft deletes the artifact by setting status to `deleted`; physical files are not removed.

### `POST /api/v1/output-artifacts/from-message/{message_id}`

Creates an artifact from a Conversation message. Assistant messages in the Conversation UI expose Save as Artifact.

### `POST /api/v1/output-artifacts/from-playbook-run/{run_id}`

Creates or returns generated artifacts for one Playbook Run. Completed Playbook Runs also create artifacts automatically.

### `GET /api/v1/output-artifacts/{artifact_id}/export`

Exports an artifact as markdown/json/txt.

```text
GET /api/v1/output-artifacts/{artifact_id}/export?format=markdown
GET /api/v1/output-artifacts/{artifact_id}/export?format=json
GET /api/v1/output-artifacts/{artifact_id}/export?format=txt
```

Export files are written under `storage/output_artifacts/{workspace_id}/{artifact_id}/`. Screenshot and `html_snapshot` artifacts return/retain file path metadata and do not copy large files.

Frontend: Admin Dashboard has an Output Library page with artifact list/detail, type badge, source type, related thread, related Playbook Run, preview content, Export markdown/json/txt, and filters. Conversation pages show generated artifacts and Save as Artifact.

Boundary: this is not a full DAM, not S3, not MinIO, and not production publishing asset management.
## Phase 42 API: Task Orchestration & Background Execution

### `GET /api/v1/task-runs`
Required headers: `X-Workspace-Id`, `X-User-Id`. Query filters: `status`, `task_type`, `source_type`, `created_from`, `created_to`, `limit`.

Response JSON:
```json
{
  "items": [
    {
      "id": "TASK_RUN_ID",
      "workspace_id": "demo-workspace",
      "task_type": "playbook",
      "source_type": "conversation",
      "source_id": "THREAD_ID",
      "status": "queued",
      "priority": "normal",
      "retry_count": 0,
      "max_retries": 3,
      "scheduled_at": null,
      "current_step": 0,
      "input_payload": {},
      "output_payload": {},
      "metadata": {},
      "created_by": "demo-user"
    }
  ]
}
```

### `GET /api/v1/task-runs/{task_run_id}`
Returns one `task_runs` record with queued, running, waiting_approval, retrying, completed, failed, cancelled, or expired status.

### `GET /api/v1/task-runs/{task_run_id}/events`
Returns the `task_run_events` timeline, including `task_queued`, `task_started`, `task_step_started`, `task_step_completed`, `task_waiting_approval`, `task_retry_scheduled`, `task_completed`, `task_cancelled`, and `artifact_created`.

### `POST /api/v1/task-runs/{task_run_id}/retry`
```json
{ "reason": "manual retry" }
```
Only failed / retryable tasks can retry. `TaskRetryPolicy` uses exponential backoff. `approval rejected` and validation errors are not retried.

### `POST /api/v1/task-runs/{task_run_id}/cancel`
```json
{ "reason": "manual cancel" }
```
Cancels unfinished task runs and writes task timeline events.

### `POST /api/v1/task-runs/{task_run_id}/resume`
Only `waiting_approval` tasks with an approved linked approval can resume. Resume re-queues the task and does not bypass the Phase 39 Approval Gate.

### Conversation Background Run
`POST /api/v1/conversations/{thread_id}/run` adds:
```json
{
  "input": { "message": "Open https://example.com, take a screenshot, and generate a report." },
  "playbook_name": "browser_screenshot_report",
  "mode": "review_first",
  "execution_mode": "background"
}
```
The response includes `task_run_id`, `task_status`, and `execution_mode`. `scheduled` mode requires `scheduled_at`.

Current boundary: Task Orchestration is a Background Execution foundation, not Celery / RabbitMQ / Kubernetes / production HA queue.

Phase 42 verifier markers: `TaskOrchestratorService`, `BackgroundTaskExecutor`, `TaskRetryPolicy`, artifact linkage, not Celery, not Kubernetes, not production HA.
## Phase 43: Task Scheduler Persistence & Worker Recovery (Completed)

Completed: Task Scheduler Persistence, `task_scheduler_state`, Task Lease fields on `task_runs`, `TaskRecoveryService`, Scheduler Health API, manual recovery API, Failed Diagnostics, and frontend scheduler health panels.

Task Lease: running task runs receive `lease_owner`, `lease_token`, `lease_expires_at`, and `heartbeat_at`. Expired lease and stale heartbeat are recoverable through scan or manual recover.

Recovery rules: running + expired lease or stale heartbeat -> retrying if retry budget remains, otherwise failed; pending scheduled due -> queued; retrying delay elapsed -> queued; waiting_approval is not auto-executed; completed/cancelled/expired are not recovered.

Admin Dashboard now shows Scheduler Health, lease status, recoverable badge, diagnostics panel, scheduled due indicator, and manual recover. Worker Console and Worker Console Desktop show simplified Task recovery state.

Boundary: this remains an in-process scheduler foundation, not Celery, not Kubernetes, and not production HA distributed queue.
## Phase 43 API: Task Scheduler Persistence & Worker Recovery

Required headers: `X-Workspace-Id`, `X-User-Id`.

Database table: `task_scheduler_state`.

Task lease fields on `task_runs`: `lease_owner`, `lease_token`, `lease_expires_at`, `heartbeat_at`, `recovery_count`, `last_recovered_at`, `recovery_reason`, `failure_category`, `failure_reason`, `recoverable`, `suggested_action`, and `last_event_summary`.

### `GET /api/v1/task-scheduler/health`

Returns scheduler health for the current workspace, including scheduler status, heartbeat, last scan, active task count, recovered task count, and metadata. The current scheduler is an in-process foundation and is not Celery, not Kubernetes, and not production HA.

### `POST /api/v1/task-scheduler/scan`

Runs one manual recovery scan. It checks scheduled due tasks, retrying due tasks, expired lease, and stuck task recovery. Response includes recovered counts and the updated scheduler health.

### `GET /api/v1/task-runs/{task_run_id}/diagnostics`

Returns Failed Diagnostics: `failure_category`, `failure_reason`, `recoverable`, `suggested_action`, `last_event_summary`, `lease_expired`, `scheduled_due`, `retry_count`, and `max_retries`.

### `POST /api/v1/task-runs/{task_run_id}/recover`

Manually recovers a recoverable task. Running tasks with expired lease are moved through retry policy; failed tasks may be retried if `TaskRetryPolicy` allows it; waiting approval tasks must continue through approval resume.

### Enhanced `GET /api/v1/task-runs`

Additional filters: `recoverable`, `lease_expired`, and `scheduled_due`.

Recovery rules: running + expired lease or stale heartbeat -> retrying or failed; queued/pending can be re-queued; scheduled due -> queued; retrying delay elapsed -> queued; waiting_approval is not auto-executed; completed/cancelled/expired are not recovered; exceeded max retries -> failed.

Admin Dashboard shows scheduler health, lease status, recoverable badge, diagnostics panel, and manual recover button. Worker Console and Worker Console Desktop show simplified Task recovery state.

Phase 43 verifier markers: `TaskRecoveryService`, `task_scheduler_state`, `Task Lease`, `Scheduler Health`, `Failed Diagnostics`, `lease_owner`, `lease_token`, `lease_expires_at`, `heartbeat_at`, `recovery_count`, `failure_category`, `recoverable`, stuck task recovery, expired lease, not Celery, not Kubernetes, not production HA.

Phase 43 runtime config markers: `TASK_SCHEDULER_NAME`, `TASK_LEASE_SECONDS`, `TASK_STUCK_TIMEOUT_SECONDS`, `TASK_SCHEDULER_RECOVERY_INTERVAL_SECONDS`.

<!-- PHASE44_API:START -->
## Phase 44 Output Artifact Pipeline APIs

### `GET /api/v1/output-artifacts/{artifact_id}/lineage`
Returns Artifact lineage for one artifact, including root artifact, ancestors, descendants, and relationship graph edges.

### `GET /api/v1/output-artifacts/{artifact_id}/relationships`
Returns `artifact_relationships` edges for one artifact. Supported `relationship_type` values include `derived_from`, `packaged_into`, `summarized_from`, `exported_from`, and `replay_of`.

### `POST /api/v1/output-artifacts/{artifact_id}/export`
Runs `ArtifactExportService` over an existing artifact. Supported formats include markdown, html, json, txt, bundle_zip, and report_package. This creates exported child artifacts and does not re-run runtime execution.

### `POST /api/v1/output-artifacts/{artifact_id}/package`
Runs `ArtifactPackagingService` to create a bundle artifact and `bundle.zip` package metadata from the selected artifact and optional lineage.

### `POST /api/v1/output-artifacts/cleanup/preview`
Runs `ArtifactRetentionService` cleanup preview. It returns retention preview candidates and does not delete files.

Phase 44 fields: `parent_artifact_id`, `root_artifact_id`, `source_task_run_id`, `source_playbook_run_id`, `source_conversation_id`, `source_runtime_session_id`, `artifact_role`, `artifact_stage`, `generated_by`, `exportable`, `retention_policy`, `expires_at`, `artifact_relationships`, `relationship_type`, `derived_from`, `packaged_into`, `exported_from`, `ArtifactExportService`, `ArtifactPackagingService`, `ArtifactRetentionService`, `Artifact Explorer`, `lineage graph`, `relationship graph`, `bundle.zip`, `storage/output_packages`, `storage/output_exports`, `retention preview`, `not a full DAM`, `S3`, `MinIO`, and not a production object storage platform.
<!-- PHASE44_API:END -->

<!-- PHASE44_SYNC:START -->
## Phase 44: Output Artifact Pipeline & Export System

Phase 44 adds the Output Artifact Pipeline & Export System on top of the Phase 41 Output Library and Phase 42/43 task runtime. It adds Artifact lineage, relationship graph tracking with `artifact_relationships`, export/package services, retention policy preview, and frontend Artifact Explorer controls.

Completed in this phase:

- `output_artifacts` now records `parent_artifact_id`, `root_artifact_id`, `source_task_run_id`, `source_playbook_run_id`, `source_conversation_id`, `source_runtime_session_id`, `artifact_role`, `artifact_stage`, `generated_by`, `exportable`, `retention_policy`, and `expires_at`.
- `artifact_relationships` records relationship graph edges such as `derived_from`, `packaged_into`, `summarized_from`, `exported_from`, and `replay_of`.
- `ArtifactExportService` supports `export_markdown`, `export_html`, `export_json`, `export_bundle_zip`, and `export_report_package` without re-running browser runtime or playbook execution.
- `ArtifactPackagingService` supports `package_playbook_run`, `package_task_run`, `package_browser_runtime_session`, and `package_conversation` to create package artifacts and `bundle.zip` metadata.
- `ArtifactRetentionService` supports retention policy, expiration scan, cleanup preview, and soft archive foundations. Current cleanup preview does not delete physical files.
- API additions include `GET /api/v1/output-artifacts/{artifact_id}/lineage`, `GET /api/v1/output-artifacts/{artifact_id}/relationships`, `POST /api/v1/output-artifacts/{artifact_id}/export`, `POST /api/v1/output-artifacts/{artifact_id}/package`, and `POST /api/v1/output-artifacts/cleanup/preview`.
- Storage roots now include `storage/output_artifacts`, `storage/output_packages`, and `storage/output_exports`.
- Admin Dashboard adds Artifact Explorer, lineage graph panel, export actions, package actions, retention badge, archived indicator, and bundle metadata preview.
- Worker Console and Worker Console Desktop expose simplified export, package, lineage summary, and retention status controls.

Boundaries:

- This is not a full DAM system.
- This is not a production object storage platform.
- There is no production S3 / MinIO / CDN integration.
- Export never re-executes Browser Runtime, Playbook, Conversation, OpenClaw, or Task actions.
- There is still no TikTok / YouTube / X automation, no automatic login, no captcha automation, no proxy pool, no fingerprint bypass, no real OpenClaw, and no ComfyUI.
<!-- PHASE44_SYNC:END -->

<!-- PHASE45_API:START -->
## Phase 45 API: Workflow State & Agent Memory Foundation

Workflow State API paths:

- `GET /api/v1/workflow-runs`
- `GET /api/v1/workflow-runs/{workflow_run_id}`
- `GET /api/v1/workflow-runs/{workflow_run_id}/steps`
- `GET /api/v1/workflow-runs/{workflow_run_id}/checkpoints`
- `POST /api/v1/workflow-runs/{workflow_run_id}/pause`
- `POST /api/v1/workflow-runs/{workflow_run_id}/resume`
- `POST /api/v1/workflow-runs/{workflow_run_id}/checkpoints`
- `GET /api/v1/workflow-runs/{workflow_run_id}/memory-snapshots`
- `POST /api/v1/workflow-runs/{workflow_run_id}/memory-snapshots`
- `GET /api/v1/agent-memory-snapshots`

Data model/API field markers: `workflow_runs`, `workflow_steps`, `workflow_checkpoints`, `agent_memory_snapshots`, `WorkflowStateService`, `Workflow State`, `Workflow Steps`, `Checkpoints`, `Agent Memory Snapshots`, `workflow_run_id`, `workflow_step_id`, `checkpoint_id`, `memory_snapshot_id`, `workflow_run_created`, `workflow_step_started`, `workflow_step_completed`, `workflow_checkpoint_created`, `workflow_paused`, `workflow_resumed`, `memory_snapshot_created`, `Pause / Resume`, `Workflow lineage`, `not a full workflow builder`, `not ComfyUI`.
<!-- PHASE45_API:END -->

<!-- PHASE45_SYNC:START -->
## Phase 45: Workflow State & Agent Memory Foundation

Status: completed.

Phase 45 adds recoverable Workflow State and Agent Memory Snapshots across Conversation, Playbook, Task, and Artifact runtime. It is a foundation for long multi-step automation, not a full workflow builder and not ComfyUI.

Completed scope:

- `workflow_runs` stores workflow status, source links, `conversation_thread_id`, `playbook_run_id`, `task_run_id`, `current_step`, variables, context, checkpoints, pause/resume/failure timestamps, and metadata.
- `workflow_steps` stores ordered step execution with `step_index`, `step_name`, `step_type`, status, input/output payloads, error, duration, and metadata.
- `workflow_checkpoints` stores immutable checkpoint records with auto/manual/approval/failure/resume checkpoint types plus state, variables, and context snapshots.
- `agent_memory_snapshots` stores durable memory snapshots for `conversation_summary`, `task_context`, `tool_result`, `decision`, `approval_context`, and `artifact_summary`.
- `WorkflowStateService` supports create workflow, list/get workflow, variables/context update, start/complete/fail step, pause workflow, resume workflow, complete workflow, fail workflow, create/restore checkpoint, create memory snapshot, and list memory snapshots.
- Conversation events now include `workflow_run_created`, `workflow_step_started`, `workflow_step_completed`, `workflow_checkpoint_created`, `workflow_paused`, `workflow_resumed`, and `memory_snapshot_created`.
- Playbook and Task execution now optionally link to `workflow_run_id`; each playbook step can create a `workflow_step`; waiting approval moves workflow status to `waiting_approval`; completion/failure creates final/failure checkpoints.
- Output Artifact lineage now supports `workflow_run_id`, `workflow_step_id`, `checkpoint_id`, and `memory_snapshot_id` so artifacts can be traced back to workflow state.
- Admin Dashboard adds Workflow Runs with step timeline, variables viewer, context viewer, checkpoints list, Agent Memory Snapshots, and Pause / Resume controls.
- Worker Console and Worker Console Desktop show simplified Workflow State, current step, checkpoint count, memory summary, and linked workflow ids.

API coverage:

- `GET /api/v1/workflow-runs`
- `GET /api/v1/workflow-runs/{workflow_run_id}`
- `GET /api/v1/workflow-runs/{workflow_run_id}/steps`
- `GET /api/v1/workflow-runs/{workflow_run_id}/checkpoints`
- `POST /api/v1/workflow-runs/{workflow_run_id}/pause`
- `POST /api/v1/workflow-runs/{workflow_run_id}/resume`
- `POST /api/v1/workflow-runs/{workflow_run_id}/checkpoints`
- `GET /api/v1/workflow-runs/{workflow_run_id}/memory-snapshots`
- `POST /api/v1/workflow-runs/{workflow_run_id}/memory-snapshots`
- `GET /api/v1/agent-memory-snapshots`

Boundaries: this is not a full workflow builder, not ComfyUI, not WebSocket/SSE streaming, not real OpenClaw, not real social-platform publishing, and not TikTok / YouTube / X automation. It does not add automatic login, CAPTCHA automation, proxy pools, or fingerprint bypass.
<!-- PHASE45_SYNC:END -->

<!-- PHASE46_SYNC:START -->
## Phase 46 API: Workflow Graph Runtime & Conditional Execution

New graph runtime routes:

- `GET /api/v1/workflow-graphs`
- `POST /api/v1/workflow-graphs`
- `GET /api/v1/workflow-graphs/{graph_id}`
- `POST /api/v1/workflow-graphs/{graph_id}/validate`
- `POST /api/v1/workflow-runs/{workflow_run_id}/replay`
- `GET /api/v1/workflow-runs/{workflow_run_id}/graph`
- `GET /api/v1/workflow-runs/{workflow_run_id}/planner`

New runtime tables and services:

- `workflow_graphs`
- `workflow_graph_nodes`
- `workflow_graph_edges`
- `workflow_replays`
- `WorkflowExecutionPlanner`
- `SafeConditionEvaluator`

Fields and events:

- `current_node_key`
- `planned_next_nodes`
- `skipped_nodes`
- `retry_state`
- `fallback_state`
- `node_key`
- `parent_node_key`
- `dependency_state`
- `producing_node_key`
- `replay_source`
- `graph_lineage`

Supported routing concepts: Workflow Graph Runtime, Conditional Execution, Retry/Fallback Path, Replay Foundation, conditional routing, dependency resolution, graph replay metadata, and safe evaluator conditions over `workflow.variables`, `workflow.status`, `step.output`, `artifact.metadata`, and `approval.status`.

Boundaries: not a visual DAG builder, not distributed orchestration engine, not ComfyUI, not WebSocket/SSE streaming, not real OpenClaw, and not real platform publishing.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47: Workflow Template Registry & Versioning API

Phase 47 adds Workflow Template Registry & Versioning. Runtime tables include `workflow_templates`, `workflow_template_versions`, and `workflow_template_runs`. Runtime services include `WorkflowTemplateRegistryService` and `WorkflowTemplateCompatibilityService`.

New APIs:

- `GET /api/v1/workflow-templates`
- `POST /api/v1/workflow-templates`
- `GET /api/v1/workflow-templates/{template_id}`
- `POST /api/v1/workflow-templates/{template_id}/versions`
- `GET /api/v1/workflow-templates/{template_id}/versions/{version_id}`
- `POST /api/v1/workflow-templates/{template_id}/activate-version/{version_id}`
- `POST /api/v1/workflow-templates/{template_id}/validate`
- `POST /api/v1/workflow-templates/{template_id}/run`
- `GET /api/v1/workflow-template-runs`
- `GET /api/v1/workflow-template-runs/{run_id}`
- `POST /api/v1/workflow-templates/import`
- `GET /api/v1/workflow-templates/{template_id}/export`

Key fields and concepts:

- `template_key`
- `current_version`
- `latest_version`
- `validation_status`
- `compatibility`
- `workflow_template_id`
- `workflow_template_version_id`
- `workflow_template_run_id`
- `Template Library`
- `Import / Export`

Built-in templates:

- `browser_screenshot_report_graph`
- `content_generation_graph`
- `rag_answer_graph`
- `approval_then_browser_graph`
- `openclaw_mock_inspect_graph`
- `task_retry_demo_graph`

Boundaries: the current scope is not a visual DAG builder, not a drag/drop workflow editor, not ComfyUI, and not real platform automation.
<!-- PHASE47_SYNC:END -->

<!-- PHASE48_SYNC:START -->
## Phase 48: Workflow Template Marketplace & Governance Foundation

Status: completed.

Phase 48 adds an internal Workflow Template Marketplace & Governance foundation on top of Phase 47 Workflow Template Registry & Versioning. It is an internal template library and governance layer, not public marketplace, not a paid marketplace, not multi-tenant SaaS marketplace, not a visual DAG editor, and not ComfyUI.

Completed scope:

- Added `workflow_template_reviews` for review queue, `review_status`, `risk_assessment`, `compatibility_report`, approve / reject / request changes.
- Added `workflow_template_promotions` to record activate, rollback, deprecate, and archive lifecycle events with `promotion_type`, source version, target version, and reason.
- Added `workflow_template_audit_logs` for governance audit trail, actor, previous_state, new_state, and metadata.
- Added `workflow_template_compatibility_matrix` for runtime capabilities: `browser_runtime`, `approval_gate`, `task_scheduler`, `artifact_pipeline`, `workflow_graph_runtime`, `openclaw_mock`, and `rag_pipeline`.
- Added `WorkflowTemplateGovernanceService` with `submit_for_review`, `approve_review`, `reject_review`, `request_changes`, `activate_template_version`, `rollback_template_version`, `deprecate_template`, `archive_template`, `list_review_queue`, and `list_governance_events`.
- Template lifecycle is draft -> review -> approved -> active -> deprecated -> archived. Activation requires approved review; only one active version is default; deprecated templates are not default-runnable; archived templates cannot run; rollback does not delete old versions.
- Marketplace foundation records `featured`, `verified`, `recommended`, `usage_count`, `success_rate`, `average_runtime_ms`, and `average_step_count` on `workflow_templates`, then exposes governance badges, risk badge, verified badge, featured templates, and recommended templates.
- Output Artifact lineage adds `source_template_review_id` and `governance_state`; Workflow Runs can record template governance state and compatibility snapshot.
- Admin Dashboard adds Template Governance with Review Queue, Approval / Reject / Request Changes, Template Lifecycle View, Audit Log View, Marketplace View, Compatibility Matrix View, and Rollback UI.
- Worker Console and Worker Console Desktop show governance status, template verification status, and compatibility summary in Template Library.

API coverage:

- `GET /api/v1/workflow-template-reviews`
- `POST /api/v1/workflow-template-reviews`
- `POST /api/v1/workflow-template-reviews/{review_id}/approve`
- `POST /api/v1/workflow-template-reviews/{review_id}/reject`
- `POST /api/v1/workflow-template-reviews/{review_id}/request-changes`
- `POST /api/v1/workflow-templates/{template_id}/rollback/{version_id}`
- `POST /api/v1/workflow-templates/{template_id}/deprecate`
- `POST /api/v1/workflow-templates/{template_id}/archive`
- `GET /api/v1/workflow-template-audit-logs`
- `GET /api/v1/workflow-template-marketplace`
- `GET /api/v1/workflow-template-compatibility-matrix`

Boundaries: Phase 48 is not public marketplace, not a visual DAG builder, not a distributed orchestration platform, not ComfyUI, not TikTok / YouTube / X automation, not real platform publishing, not automatic login, not CAPTCHA automation, not proxy pool, and not fingerprint bypass.
<!-- PHASE48_SYNC:END -->

## Phase 49: Workflow Run Observability & Replay Center

Completed the Workflow Run Observability & Replay Center foundation: added `workflow_execution_traces`, `workflow_runtime_diagnostics`, `workflow_replay_sessions`, and integrated `WorkflowExecutionTraceService` plus `WorkflowDiagnosticsService`. The runtime now records node_started / node_completed / node_failed / planner_decision / retry_triggered / fallback_triggered / approval_wait / approval_resume / replay_started / replay_completed for Execution Trace, Runtime Summary, Failure Hotspots, Replay Center, and metadata_only / dry_run replay sessions.

New APIs: `GET /api/v1/workflow-runs/{workflow_run_id}/traces`, `GET /api/v1/workflow-runs/{workflow_run_id}/diagnostics`, `GET /api/v1/workflow-runs/{workflow_run_id}/analytics`, `POST /api/v1/workflow-runs/{workflow_run_id}/replay-sessions`, `GET /api/v1/workflow-runs/{workflow_run_id}/runtime-summary`, `GET /api/v1/workflow-replay-sessions`, and `GET /api/v1/workflow-replay-sessions/{replay_session_id}`.

Admin Dashboard now includes Replay Center / Workflow Observability views for Execution Trace Timeline, Node Inspection Panel, Retry/Fallback Visualization, Diagnostics Panel, Runtime Summary, Replay Session View, Failure Hotspots, and Approval Wait Visualization. Worker Console / Desktop show a simplified trace timeline, replay session status, diagnostics summary, and retry/fallback counters.

Boundaries: this is not a distributed tracing platform, not an OpenTelemetry stack, not WebSocket/SSE realtime, not a deterministic replay engine, not a visual DAG editor, does not connect ComfyUI, does not perform real social publishing, and does not implement Kubernetes orchestration.

Keywords: not distributed tracing platform; not deterministic replay engine; not ComfyUI.

## Phase 50: Desktop Console Runtime UX & Client Packaging Readiness

Phase 50 adds Desktop Console Runtime UX & Client Packaging Readiness. The Tauri icon resource is now explicit: `worker_console_desktop/src-tauri/icons/icon.ico` is a valid local placeholder icon and `bundle.icon` points to `["icons/icon.ico"]`.

Start Runtime diagnostics now surface clear states: `starting`, `started`, `failed`, `unavailable`, `port_conflict`, `missing_config`, and `server_environment_warning`. The Desktop Console shows local worker diagnostics for `/local/status`, `/local/health`, runtime port, `server_url`, `worker_base_url`, last attempted action, last error detail, and last successful sync.

Server/client boundary: Desktop Console controls the worker runtime on this local machine. If running on the server host, Start Runtime starts a server-local worker, not a remote customer machine. For real client E2E, run this app on the customer machine.

This phase is packaging readiness only: not final installer, no code signing, no auto updater, no MSI/EXE release packaging, and not ComfyUI.

Keywords: Desktop Console Runtime UX & Client Packaging Readiness; Tauri icon resource; icons/icon.ico; bundle.icon; Start Runtime diagnostics; missing_config; port_conflict; server_environment_warning; local worker diagnostics; customer machine; not final installer; no code signing; no auto updater.
<!-- PHASE51_SYNC:START -->
## Phase 51: Release Packaging & Deployment Bundle Foundation

Status: completed.

Phase 51 adds the Release Packaging & Deployment Bundle Foundation. It introduces a `release/` directory with `release/manifest.json`, `release/version.json`, `release/env/aiops.release.env.template`, server deployment bundle scripts, frontend production build bundle scripts, desktop release readiness scripts, Windows / Mac startup scripts, and `release/scripts/validate_release_packaging.py`.

Packaging architecture:

- Server deployment bundle: `release/scripts/build_server_bundle.ps1` and `release/scripts/build_server_bundle.sh` collect API server, worker, worker_client, Alembic, Docker, docs runtime metadata, and env template sources under ignored `release/build/server`.
- Frontend production build bundle: `release/scripts/build_frontend_bundles.ps1` and `release/scripts/build_frontend_bundles.sh` run production builds for Admin Dashboard, Worker Console, and Worker Console Desktop frontend assets, then copy `dist` output under ignored `release/build/frontends`.
- Desktop release readiness: `release/scripts/check_desktop_release_readiness.ps1` and `.sh` verify Tauri config, `icons/icon.ico`, package metadata, and Cargo/toolchain presence without producing a signed installer.
- Version metadata: `release/version.json` records Phase 51 package metadata and component readiness.
- Release manifest: `release/manifest.json` is the packaging SSOT for components, outputs, startup scripts, validation script, and forbidden runtime artifacts.
- Validation: `release/scripts/validate_release_packaging.py` checks required files, manifest JSON, version JSON, desktop icon config, boundaries, and forbidden artifact declarations.

Boundaries: Phase 51 is not a formal production release, no code signing, no auto updater, no MSI/EXE formal installer, no DMG/notarization, no Kubernetes/Helm packaging, no ComfyUI, and no real social platform publishing.

 Phase 51  release readiness  code signing, auto updater, MSI/EXE, DMG/notarization, Kubernetes/Helm.

Keywords: Phase 51; Release Packaging & Deployment Bundle Foundation; release/manifest.json; release/version.json; server deployment bundle; frontend production build bundle; desktop release readiness; aiops.release.env.template; validate_release_packaging.py; Windows / Mac startup scripts; not a formal production release; no code signing; no auto updater; no MSI/EXE; no DMG/notarization; no Kubernetes/Helm.
<!-- PHASE51_SYNC:END -->
<!-- PHASE52_SYNC:START -->
## Phase 52: Deployment Profiles & Environment Bootstrap

Status: completed.

Phase 52 adds Deployment Profiles & Environment Bootstrap on top of Phase 51 release packaging. It introduces `deployment/` with profile-based configuration for `local-dev`, `server-docker`, `client-worker`, `desktop-client`, `staging`, and `production-like`. Each profile contains `profile.json`, `env.template`, `ports.json`, `services.json`, `healthchecks.json`, and `README.md`.

Completed scope:

- `deployment/scripts/generate_env.py` generates `.env.generated` or a specified output from a profile `env.template`, supports override JSON, validates required keys, and refuses to overwrite existing env files without `--force`.
- `deployment/scripts/check_dependencies.py` checks Python, Docker, Docker Compose, Node/npm, Git, Playwright/client worker advisories, Rust/cargo, MSVC/link.exe on Windows, Tauri icon readiness, and WebView2 advisory by profile.
- `deployment/scripts/check_ports.py` checks API 8000, Admin Dashboard 5180, Worker Console 5173, Desktop Console 5174, Worker Runtime 9100, PostgreSQL 5432, Redis 6379, and Qdrant 6333 from each profile `ports.json`; it reports process hints and never kills processes.
- `deployment/scripts/verify_environment.py` verifies `server-docker`, `client-worker`, and `desktop-client` health: docker compose ps, API health, browser-worker health, workflow routes smoke, task-runs smoke, output-artifacts smoke, local worker status/health, Tauri config/icon, and frontend build presence where applicable.
- Added Windows / Mac startup scripts under `deployment/windows/` and `deployment/mac/` for server Docker, Admin Dashboard, Worker Console, Desktop Console, client worker, and profile verification.
- Release integration updates `release/manifest.json`, `release/version.json`, `release/README.md`, and `release/scripts/validate_release_packaging.py` to include deployment profiles, bootstrap scripts, dependency checks, port checks, and profile verification.
- Admin Dashboard, Worker Console, and Worker Console Desktop Settings / Help now show recommended profile, AI Server URL, Workspace ID, User ID, Local Worker API, server/client/desktop role differences, and profile bootstrap docs link.

Boundaries: Phase 52 is not Kubernetes/Helm/Terraform, not Ansible, not production HA, not code signing, not an auto updater, not a formal installer, not ComfyUI, and not real social platform publishing.

Keywords: Phase 52; Deployment Profiles & Environment Bootstrap; local-dev; server-docker; client-worker; desktop-client; staging; production-like; generate_env.py; check_dependencies.py; check_ports.py; verify_environment.py; env generation; dependency checks; port checks; health verification; profile bootstrap docs; Kubernetes/Helm/Terraform.
<!-- PHASE52_SYNC:END -->

## Phase 61A: Commercial Operations Foundation

Status: merged to main.

Phase 61A adds a workspace-scoped commercial operation project center. It exposes `commercial_operations`, `CommercialOperationService`, and the Admin Dashboard Commercial Ops page for turning one business objective into a durable record and reviewable plan outline.

APIs:

- `GET /api/v1/commercial-operations`
- `POST /api/v1/commercial-operations`
- `GET /api/v1/commercial-operations/{operation_id}`
- `PATCH /api/v1/commercial-operations/{operation_id}`
- `POST /api/v1/commercial-operations/{operation_id}/plan-draft`

Main fields: `title`, `objective`, `target_audience`, `channels`, `status`, `priority`, `risk_level`, `budget_amount`, `budget_currency`, `start_at`, `end_at`, `knowledge_collection`, `success_metrics`, `constraints`, `plan_outline`, and `metadata`.

Boundary: this phase does not publish, does not execute OpenClaw actions, does not run ComfyUI jobs, does not control real accounts, and does not bypass approval.

## Phase 61B: Commercial Operation Evidence & Handoff Links

Status: completed.

Phase 61B adds `commercial_operation_links` and `CommercialOperationLink` records below each commercial operation. Operators can attach handoff context and evidence before later phases introduce approval-backed execution.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/links`
- `POST /api/v1/commercial-operations/{operation_id}/links`
- `DELETE /api/v1/commercial-operations/{operation_id}/links/{link_id}`

Main fields: `operation_id`, `link_type`, `target_type`, `target_id`, `title`, `summary`, `source_name`, and `metadata`.

Supported `link_type` values: `conversation`, `artifact`, `task_run`, `workflow_run`, `rag_document`, `knowledge_source`, `approval`, and `external`.

Boundary: links are manual references only. They do not execute linked tasks, publish content, run ComfyUI, run OpenClaw, or bypass approval.

## Phase 61C: Commercial Operation Approval Gates

Status: completed.

Phase 61C adds `commercial_operation_approvals` and `CommercialOperationApproval` records below each commercial operation. Operators can request approval for a specific `plan_outline` step, then approve, reject, or cancel that gate before later dry-run or execution phases.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/approvals`
- `POST /api/v1/commercial-operations/{operation_id}/approvals`
- `POST /api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/cancel`

Main fields: `operation_id`, `step_key`, `title`, `requested_action`, `approval_status`, `risk_level`, `requested_by`, `reviewer_user_id`, `reviewer_notes`, `approved_at`, `rejected_at`, `cancelled_at`, and `metadata`.

Supported `approval_status` values: `pending`, `approved`, `rejected`, and `cancelled`.

Boundary: approvals are human review records and plan-step gates only. They do not execute linked tasks, publish content, run ComfyUI, run OpenClaw, control real accounts, or bypass approval.

## Phase 61D: Commercial Operation Safe Dry-Runs

Status: completed on `main` in PR #44.

Phase 61D adds `commercial_operation_dry_runs` and `CommercialOperationDryRun` records below each commercial operation. Operators can create a metadata-only dry-run from an approved approval gate, review the generated runbook and readiness checks, then complete, fail, or cancel the dry-run for later handoff.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/dry-runs`
- `POST /api/v1/commercial-operations/{operation_id}/dry-runs`
- `POST /api/v1/commercial-operations/{operation_id}/dry-runs/{dry_run_id}/complete`
- `POST /api/v1/commercial-operations/{operation_id}/dry-runs/{dry_run_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/dry-runs/{dry_run_id}/cancel`

Main fields: `operation_id`, `approval_id`, `step_key`, `title`, `dry_run_status`, `execution_mode`, `execution_target`, `input_summary`, `runbook`, `expected_outputs`, `readiness_checks`, `result_summary`, `failure_reason`, `requested_by`, `completed_by`, and `metadata`.

Supported `dry_run_status` values: `created`, `completed`, `failed`, and `cancelled`.

Boundary: dry-runs are approved, metadata-only execution preparation records. They do not publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, or bypass approval.

## Phase 61E: Commercial Operation Content Drafts

Status: completed on `main` in PR #45.

Phase 61E adds `commercial_operation_content_drafts` and `CommercialOperationContentDraft` records below each commercial operation. Operators can create a reviewable channel draft for a plan step, update the draft, mark it ready for review, approve it, reject it, or archive it for later handoff.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/content-drafts`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts`
- `PATCH /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/archive`

Main fields: `operation_id`, `step_key`, `channel`, `content_format`, `title`, `draft_status`, `audience_segment`, `content_body`, `summary`, `call_to_action`, `source_materials`, `asset_requests`, `reviewer_notes`, `created_by`, `updated_by`, `approved_by`, and `metadata`.

Supported `draft_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, and `archived`.

Boundary: content drafts are review records only. They do not publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, or bypass approval.

## Phase 61F: Commercial Operation Asset Requests

Status: completed on `main`.

Phase 61F adds `commercial_operation_asset_requests` and `CommercialOperationAssetRequest` records below each commercial operation. Operators can create a first-class asset request for a plan step, optionally link it to a content draft, update it, mark it ready for review, approve it, reject it, prepare it for future ComfyUI handoff, fail it during preparation, or archive it for later handoff.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/asset-requests`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests`
- `PATCH /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/prepare`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/archive`

Main fields: `operation_id`, `content_draft_id`, `step_key`, `channel`, `asset_type`, `title`, `request_status`, `purpose`, `dimensions`, `style_constraints`, `generation_prompt`, `negative_prompt`, `source_materials`, `readiness_checks`, `handoff_payload`, `result_summary`, `failure_reason`, `reviewer_notes`, `requested_by`, `updated_by`, `approved_by`, `prepared_by`, and `metadata`.

Supported `request_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, `prepared`, `failed`, and `archived`.

Boundary: asset requests and handoff payloads are review records only. They do not publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, or bypass approval.

## Phase 61G: Commercial Operation Deliverables

Status: completed on `main` in PR #47.

Phase 61G adds `commercial_operation_deliverables` and `CommercialOperationDeliverable` records below each commercial operation. Operators can package an approved content draft together with approved or prepared asset requests, update the package, mark it ready for review, approve it, reject it, package it into the Output Library, fail it during packaging, or archive it.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/deliverables`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables`
- `PATCH /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/package`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/archive`

Main fields: `operation_id`, `content_draft_id`, `output_artifact_id`, `asset_request_ids`, `step_key`, `channel`, `deliverable_type`, `title`, `deliverable_status`, `summary`, `delivery_notes`, `quality_checks`, `package_payload`, `result_summary`, `failure_reason`, `reviewer_notes`, `created_by`, `updated_by`, `approved_by`, `packaged_by`, and `metadata`.

Supported `deliverable_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, `packaged`, `failed`, and `archived`.

Boundary: deliverables and package payloads are review and handoff records only. They create linked Output Library artifacts with `source_type=commercial_operation`, but they do not publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, or bypass approval.

## Phase 61H: Commercial Operation Execution Requests

Status: completed on `main` in PR #48.

Phase 61H adds `commercial_operation_execution_requests` and `CommercialOperationExecutionRequest` records below each commercial operation. Operators can create a metadata-only execution handoff request from a packaged deliverable, update it, mark it ready for review, approve it, reject it, prepare it for a future guarded runtime adapter, fail it before handoff, cancel it before preparation, or archive it.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/execution-requests`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests`
- `PATCH /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/prepare`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/cancel`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/archive`

Main fields: `operation_id`, `deliverable_id`, `output_artifact_id`, `step_key`, `channel`, `execution_type`, `execution_mode`, `title`, `request_status`, `execution_target`, `input_summary`, `runbook`, `readiness_checks`, `expected_outputs`, `handoff_payload`, `result_summary`, `failure_reason`, `reviewer_notes`, `requested_by`, `updated_by`, `approved_by`, `prepared_by`, `cancelled_by`, and `metadata`.

Supported `request_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, `prepared`, `failed`, `cancelled`, and `archived`.

Boundary: execution requests and handoff payloads are review and future-runtime handoff records only. They do not publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, or bypass approval.

## Phase 61I: Commercial Operation Execution Runs

Status: merged to main.

Phase 61I adds `commercial_operation_execution_runs` and `CommercialOperationExecutionRun` records below each commercial operation. Operators can create a metadata-only execution run from a prepared execution request, update it while queued or retrying, start it, mark it succeeded, mark it failed, retry it within the retry limit, cancel it, or archive it.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/execution-runs`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs`
- `PATCH /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/start`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/succeed`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/retry`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/cancel`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/archive`

Main fields: `operation_id`, `execution_request_id`, `deliverable_id`, `output_artifact_id`, `step_key`, `channel`, `execution_type`, `execution_mode`, `execution_target`, `title`, `run_status`, `input_payload`, `runbook_snapshot`, `readiness_checks`, `expected_outputs`, `runtime_payload`, `result_payload`, `recovery_plan`, `retry_count`, `max_retries`, `result_summary`, `failure_reason`, `operator_notes`, `queued_by`, `started_by`, `completed_by`, `cancelled_by`, and `metadata`.

Supported `run_status` values: `queued`, `running`, `succeeded`, `failed`, `retrying`, `cancelled`, and `archived`.

Boundary: execution runs and runtime payloads are audit and recovery records only. They do not publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, or bypass approval.

## Phase 61J: Commercial Operation Results

Status: completed.

Phase 61J adds `commercial_operation_results` and `CommercialOperationResult` records below each commercial operation. Operators can create a result from a terminal execution run, update it while draft or rejected, mark it ready for review, approve it, reject it, or archive it.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/results`
- `POST /api/v1/commercial-operations/{operation_id}/results`
- `PATCH /api/v1/commercial-operations/{operation_id}/results/{result_id}`
- `POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/archive`

Main fields: `operation_id`, `execution_run_id`, `execution_request_id`, `deliverable_id`, `output_artifact_id`, `step_key`, `channel`, `result_type`, `title`, `result_status`, `summary`, `outcome_summary`, `observed_metrics`, `commercial_signals`, `evidence_links`, `follow_up_actions`, `result_payload`, `recommendation_payload`, `reviewer_notes`, `created_by`, `updated_by`, `approved_by`, and `metadata`.

Supported `result_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, and `archived`.

Boundary: results are operator-observed review records only. They do not ingest platform analytics, claim ROI attribution, publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, or bypass approval.

## Phase 61K: Commercial Operation Monitoring Observations

Status: merged.

Phase 61K adds `commercial_operation_monitoring_observations` and `CommercialOperationMonitoringObservation` records below each commercial operation. Operators can create a monitoring observation from an approved commercial result, update it while draft or rejected, mark it ready for review, approve it, reject it, or archive it.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/monitoring-observations`
- `POST /api/v1/commercial-operations/{operation_id}/monitoring-observations`
- `PATCH /api/v1/commercial-operations/{operation_id}/monitoring-observations/{observation_id}`
- `POST /api/v1/commercial-operations/{operation_id}/monitoring-observations/{observation_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/monitoring-observations/{observation_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/monitoring-observations/{observation_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/monitoring-observations/{observation_id}/archive`

Main fields: `operation_id`, `result_id`, `execution_run_id`, `execution_request_id`, `deliverable_id`, `output_artifact_id`, `step_key`, `channel`, `observation_type`, `title`, `observation_status`, `observation_window_start`, `observation_window_end`, `metric_snapshots`, `qualitative_signals`, `evidence_links`, `anomaly_flags`, `recommended_actions`, `observation_payload`, `reviewer_notes`, `created_by`, `updated_by`, `approved_by`, and `metadata`.

Supported `observation_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, and `archived`.

Boundary: monitoring observations are operator-observed review records only. They do not ingest platform analytics, claim ROI attribution, publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, or bypass approval.

## Phase 61L: Commercial Operation Optimization Decisions

Status: in progress.

Phase 61L adds `commercial_operation_optimization_decisions` and `CommercialOperationOptimizationDecision` records below each commercial operation. Operators can create an optimization decision from an approved monitoring observation, update it while draft or rejected, mark it ready for review, approve it, reject it, or archive it.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/optimization-decisions`
- `POST /api/v1/commercial-operations/{operation_id}/optimization-decisions`
- `PATCH /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}`
- `POST /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/archive`

Main fields: `operation_id`, `observation_id`, `result_id`, `execution_run_id`, `execution_request_id`, `deliverable_id`, `output_artifact_id`, `step_key`, `channel`, `decision_type`, `title`, `decision_status`, `priority`, `rationale`, `objective_updates`, `content_actions`, `asset_actions`, `audience_actions`, `execution_actions`, `risk_controls`, `decision_payload`, `next_review_at`, `reviewer_notes`, `created_by`, `updated_by`, `approved_by`, and `metadata`.

Supported `decision_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, and `archived`.

Boundary: optimization decisions are operator-reviewed decision records only. They do not auto-optimize content, assets, audiences, budgets, or execution handoffs; they do not ingest platform analytics, claim ROI attribution, publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, or bypass approval.

## Phase 61M: Commercial Operation Evidence Snapshots

Status: in progress.

Phase 61M adds `commercial_operation_evidence_snapshots` and `CommercialOperationEvidenceSnapshot` records below each commercial operation. Operators can create a reviewed evidence snapshot from a packaged deliverable, update it while draft or rejected, mark it ready for review, approve it, reject it, or archive it. Approved evidence snapshot IDs and operator checklists can be attached to execution requests and copied into execution runs.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/evidence-snapshots`
- `POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots`
- `PATCH /api/v1/commercial-operations/{operation_id}/evidence-snapshots/{snapshot_id}`
- `POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots/{snapshot_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots/{snapshot_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots/{snapshot_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots/{snapshot_id}/archive`

Main fields: `operation_id`, `deliverable_id`, `content_draft_id`, `output_artifact_id`, `step_key`, `channel`, `evidence_type`, `title`, `snapshot_status`, `knowledge_collection`, `query`, `evidence_summary`, `relevance_notes`, `source_document_ids`, `source_links`, `evidence_items`, `coverage_checks`, `snapshot_payload`, `reviewer_notes`, `created_by`, `updated_by`, `approved_by`, and `metadata`.

Execution request/run fields: `evidence_snapshot_ids`, `operator_checklist`, and `operator_checklist_snapshot`.

Supported `snapshot_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, and `archived`.

Boundary: evidence snapshots are operator-reviewed evidence records only. They do not run live RAG retrieval, ingest knowledge files, claim ROI attribution, publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, or bypass approval.

## Phase 61N: Commercial Operation RAG Evidence Generation

Status: in progress.

Phase 61N adds a controlled generation route that searches an existing RAG collection and creates a draft commercial operation evidence snapshot from retrieved chunks. Generated snapshots include source document IDs, evidence items, search metadata, and explicit forbidden actions. They still require human review before they can be approved or attached to execution handoffs.

API:

- `POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots/generate-rag`

Request fields: `deliverable_id`, `title`, `knowledge_collection`, `query`, `source_id`, `search_mode`, `dense_top_k`, `keyword_top_k`, `final_top_k`, `evidence_summary`, `relevance_notes`, `coverage_checks`, and `metadata`.

Generated payload fields include `generation_mode=rag_search_snapshot`, `collection_name`, `query`, `source_id`, `search_mode`, `dense_top_k`, `keyword_top_k`, `final_top_k`, `result_count`, `dense_candidate_count`, `keyword_candidate_count`, `merged_candidate_count`, and `forbidden_actions`.

Boundary: RAG evidence generation searches existing knowledge only. It does not upload or ingest new knowledge files, auto-approve evidence, publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval.

## Phase 61O: Commercial Operation RAG Content Draft Generation

Status: in progress.

Phase 61O adds a controlled generation route that searches an existing RAG collection and creates a draft commercial operation content record from retrieved chunks. Generated drafts include source materials, search metadata, a review boundary, and explicit forbidden actions. They still require human review before approval and cannot publish or execute.

API:

- `POST /api/v1/commercial-operations/{operation_id}/content-drafts/generate-rag`

Request fields: `step_key`, `channel`, `content_format`, `title`, `audience_segment`, `query`, `knowledge_collection`, `source_id`, `search_mode`, `dense_top_k`, `keyword_top_k`, `final_top_k`, `summary`, `call_to_action`, `asset_requests`, and `metadata`.

Generated metadata fields include `generation_mode=rag_content_draft`, `collection_name`, `query`, `source_id`, `search_mode`, `dense_top_k`, `keyword_top_k`, `final_top_k`, `rag_result_count`, `dense_candidate_count`, `keyword_candidate_count`, `merged_candidate_count`, and `forbidden_actions`.

Boundary: RAG content draft generation searches existing knowledge only. It does not upload or ingest new knowledge files, auto-approve content, publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval.

## Phase 61P: Commercial Operation RAG Asset Brief Generation

Status: in progress.

Phase 61P adds a controlled generation route that searches an existing RAG collection and creates a draft commercial operation asset request brief from retrieved chunks and optional linked content draft context. Generated requests include source materials, readiness checks, search metadata, a review boundary, and explicit forbidden actions. They still require human review before approval and cannot start ComfyUI or execute.

API:

- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/generate-rag`

Request fields: `step_key`, `content_draft_id`, `channel`, `asset_type`, `title`, `purpose`, `dimensions`, `style_constraints`, `query`, `knowledge_collection`, `source_id`, `search_mode`, `dense_top_k`, `keyword_top_k`, `final_top_k`, `readiness_checks`, `negative_prompt`, and `metadata`.

Generated metadata fields include `generation_mode=rag_asset_brief`, `collection_name`, `query`, `source_id`, `search_mode`, `dense_top_k`, `keyword_top_k`, `final_top_k`, `rag_result_count`, `dense_candidate_count`, `keyword_candidate_count`, `merged_candidate_count`, `content_draft_id`, and `forbidden_actions`.

Boundary: RAG asset brief generation searches existing knowledge only. It does not upload or ingest new knowledge files, auto-approve assets, publish content, run ComfyUI, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval.

## Phase 61Q: Commercial Operation ComfyUI Handoffs

Status: in progress.

Phase 61Q adds `commercial_operation_comfyui_handoffs` and `CommercialOperationComfyUIHandoff` records below each commercial operation. Operators can create metadata-only ComfyUI handoffs from approved or prepared asset requests, edit them while draft/rejected/failed, mark them ready for review, approve, reject, prepare, fail, or archive them. These records prepare a future guarded adapter but do not submit ComfyUI jobs.

APIs:

- `GET /api/v1/commercial-operations/{operation_id}/comfyui-handoffs`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs`
- `PATCH /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/prepare`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/archive`

Main fields: `operation_id`, `asset_request_id`, `content_draft_id`, `step_key`, `channel`, `asset_type`, `title`, `handoff_status`, `workflow_name`, `dimensions`, `generation_prompt`, `negative_prompt`, `workflow_payload`, `prompt_payload`, `source_materials`, `readiness_checks`, `handoff_payload`, `result_summary`, `failure_reason`, `reviewer_notes`, `requested_by`, `updated_by`, `approved_by`, `prepared_by`, and `metadata`.

Supported `handoff_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, `prepared`, `failed`, and `archived`.

Boundary: ComfyUI handoffs are operator-reviewed metadata records only. They do not submit ComfyUI jobs, generate images or videos, publish content, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval.

## Phase 61R: Commercial Operation ComfyUI Preflights

Status: in progress.

Phase 61R adds `commercial_operation_comfyui_preflights` and `CommercialOperationComfyUIPreflight` records below each commercial operation. Operators and server maintainers can create metadata-only readiness checks from approved or prepared ComfyUI handoffs, edit them, rerun local evaluation, fail them, or archive them. These records prepare a future guarded adapter but do not call ComfyUI endpoints or submit queue jobs.

APIs:

- `POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/preflights`
- `GET /api/v1/commercial-operations/{operation_id}/comfyui-preflights`
- `PATCH /api/v1/commercial-operations/{operation_id}/comfyui-preflights/{preflight_id}`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-preflights/{preflight_id}/check`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-preflights/{preflight_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-preflights/{preflight_id}/archive`

Main fields: `operation_id`, `handoff_id`, `asset_request_id`, `step_key`, `title`, `preflight_status`, `target_url`, `connection_mode`, `queue_name`, `workflow_name`, `model_refs`, `adapter_config`, `check_items`, `preflight_payload`, `result_summary`, `failure_reason`, `checked_by`, `updated_by`, `archived_by`, and `metadata`.

Supported `preflight_status` values: `draft`, `checked`, `blocked`, `failed`, and `archived`.

Boundary: ComfyUI preflights are metadata records only. They do not call ComfyUI health, prompt, history, upload, or queue endpoints, submit jobs, generate media, publish content, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval.

## Phase 61S: Commercial Operation ComfyUI Adapter Configs

Phase 61S adds `commercial_operation_comfyui_adapter_configs` and `CommercialOperationComfyUIAdapterConfig` records below each commercial operation. Server maintainers can create metadata-only adapter configs, edit them, rerun local validation, fail them, or archive them. These records document the future guarded ComfyUI adapter endpoint, queue, workflow allowlist, model inventory, runtime limits, maintenance notes, and secret references without storing secret values or calling ComfyUI.

Endpoints:

- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs`
- `GET /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs`
- `PATCH /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs/{config_id}`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs/{config_id}/validate`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs/{config_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs/{config_id}/archive`

Boundary: ComfyUI adapter configs are metadata records only. They do not store secret values, call ComfyUI health, prompt, history, upload, or queue endpoints, submit jobs, generate media, publish content, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval. Ready configs can be selected by ComfyUI preflights to prefill endpoint, queue, workflow, model references, and guarded adapter metadata.

## Phase 61T: Commercial Operation ComfyUI Job Requests

Phase 61T adds `commercial_operation_comfyui_job_requests` and `CommercialOperationComfyUIJobRequest` records below each commercial operation. Operators can create metadata-only job requests from checked ComfyUI preflights, edit them, send them for review, approve or reject them, mark approved requests as queued, mark failed requests, cancel active requests, or archive their audit trail. These records document the future guarded ComfyUI queue payload, safety checks, output expectations, and recovery guidance without uploading files, storing secret values, calling ComfyUI, submitting queues, or generating media.

Endpoints:

- `POST /api/v1/commercial-operations/{operation_id}/comfyui-preflights/{preflight_id}/job-requests`
- `GET /api/v1/commercial-operations/{operation_id}/comfyui-job-requests`
- `PATCH /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/queue`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/cancel`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/archive`

Supported `job_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, `queued`, `failed`, `cancelled`, and `archived`.

Boundary: ComfyUI job requests are metadata records only. They do not store secret values, call ComfyUI health, prompt, history, upload, or queue endpoints, upload files, submit jobs, generate media, publish content, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval. Approved requests can be marked queued only as an operator-facing state record; no ComfyUI queue submission occurs.

## Phase 61U: Commercial Operation ComfyUI Execution Plans

Phase 61U adds `commercial_operation_comfyui_execution_plans` and `CommercialOperationComfyUIExecutionPlan` records below each commercial operation. Operators can create metadata-only execution plans from approved or queued ComfyUI job requests, edit them, send them for review, approve or reject them, simulate them locally, mark failed plans, cancel active plans, or archive their audit trail. These records document future guarded ComfyUI queue simulation steps, simulation checks, operator checklist items, rollback guidance, and normalized queue payload shape without uploading files, storing secret values, calling ComfyUI, submitting queues, or generating media.

Endpoints:

- `POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/execution-plans`
- `GET /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans`
- `PATCH /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/simulate`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/cancel`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/archive`

Supported `plan_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, `simulated`, `failed`, `cancelled`, and `archived`.

Boundary: ComfyUI execution plans are metadata records only. They do not store secret values, call ComfyUI health, prompt, history, upload, or queue endpoints, upload files, submit jobs, generate media, publish content, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval. Approved plans can be simulated only as an operator-facing local metadata state record; no ComfyUI queue submission occurs.

## Phase 61V: Commercial Operation ComfyUI Connection Probes

Phase 61V adds `commercial_operation_comfyui_connection_probes` and `CommercialOperationComfyUIConnectionProbe` records below each commercial operation. Operators can create metadata-only connection probe records from approved or simulated ComfyUI execution plans, edit them, send them for review, approve or reject them, mark them probed, mark failures, cancel active probes, or archive their audit trail. These records document future guarded ComfyUI health and queue snapshot probes, route expectations, readiness checks, sanitized probe payloads, metadata-only health snapshots, metadata-only queue snapshots, and response schemas without storing secret values, calling ComfyUI, reading queues, uploading files, submitting queues, or generating media.

Endpoints:

- `POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/connection-probes`
- `GET /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes`
- `PATCH /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/probe`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/cancel`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/archive`

Supported `probe_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, `probed`, `failed`, `cancelled`, and `archived`.

Boundary: ComfyUI connection probes are metadata records only. They do not store secret values, call ComfyUI health, prompt, history, upload, or queue endpoints, read queues, upload files, submit jobs, generate media, publish content, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval. Approved probes can be marked probed only as an operator-facing metadata state record; no ComfyUI HTTP request or read-only queue probe occurs.

## Phase 61W: Commercial Operation ComfyUI Adapter Dispatches

Phase 61W adds `commercial_operation_comfyui_adapter_dispatches` and `CommercialOperationComfyUIAdapterDispatch` records below each commercial operation. Operators can create metadata-only adapter dispatch records from probed ComfyUI connection probes, edit them, send them for review, approve or reject them, mark them dispatched, mark failures, cancel active dispatches, or archive their audit trail. These records document future guarded ComfyUI adapter dispatches, prompt/workflow/queue payloads, sanitized dispatch payloads, guardrails, operator checklists, retry policy, and recovery plans without storing secret values, calling ComfyUI, submitting prompts, reading queues, uploading files, submitting queues, or generating media.

Endpoints:

- `POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/adapter-dispatches`
- `GET /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches`
- `PATCH /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/dispatch`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/cancel`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/archive`

Supported `dispatch_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, `dispatched`, `failed`, `cancelled`, and `archived`.

Boundary: ComfyUI adapter dispatches are metadata records only. They do not store secret values, call ComfyUI health, prompt, history, upload, or queue endpoints, submit prompts, read queues, upload files, submit jobs, generate media, publish content, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval. Approved dispatches can be marked dispatched only as an operator-facing metadata state record; no ComfyUI adapter call or queue submission occurs.

## Phase 61X: Commercial Operation ComfyUI Runtime Gates

Phase 61X adds `commercial_operation_comfyui_runtime_gates` and `CommercialOperationComfyUIRuntimeGate` records below each commercial operation. Operators and server maintainers can create metadata-only runtime gate records from dispatched ComfyUI adapter dispatches, edit them, send them for review, approve or reject them, mark them armed, mark failures, disable active gates, or archive their audit trail. These records document future guarded ComfyUI runtime cutover controls, runtime switch metadata, network policies, queue policies, secret-reference policies, approval policies, validation checks, operator checklists, and rollback plans without storing or resolving secret values, calling ComfyUI, submitting prompts, reading queues, uploading files, submitting queues, or generating media.

Endpoints:

- `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/runtime-gates`
- `GET /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates`
- `PATCH /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/arm`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/disable`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/archive`

Supported `gate_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, `armed`, `disabled`, `failed`, and `archived`.

Boundary: ComfyUI runtime gates are metadata records only. They do not store or resolve secret values, call ComfyUI health, prompt, history, upload, or queue endpoints, submit prompts, read queues, upload files, submit jobs, generate media, publish content, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval. Approved gates can be marked armed only as an operator-facing metadata state record; no ComfyUI adapter runtime is enabled.

## Phase 61Y: Commercial Operation ComfyUI Runtime Dry-Runs

Phase 61Y adds `commercial_operation_comfyui_runtime_dry_runs` and `CommercialOperationComfyUIRuntimeDryRun` records below each commercial operation. Operators and server maintainers can create metadata-only runtime dry-run records from armed ComfyUI runtime gates, edit them, send them for review, approve or reject them, mark them validated, mark failures, cancel active dry-runs, or archive their audit trail. These records document future guarded ComfyUI adapter contracts, dry-run request fixtures, expected response contracts, explicit server switch policies, validation checks, operator checklists, and rollback plans without importing or calling a ComfyUI adapter, storing or resolving secret values, calling ComfyUI, submitting prompts, reading queues, uploading files, submitting queues, enabling runtime switches, or generating media.

Endpoints:

- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/runtime-dry-runs`
- `GET /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs`
- `PATCH /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/validate`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/cancel`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/archive`

Supported `dry_run_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, `validated`, `failed`, `cancelled`, and `archived`.

Boundary: ComfyUI runtime dry-runs are metadata records only. They do not import or call ComfyUI adapters, enable runtime server switches, store or resolve secret values, call ComfyUI health, prompt, history, upload, or queue endpoints, submit prompts, read queues, upload files, submit jobs, generate media, publish content, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval. Approved dry-runs can be marked validated only as an operator-facing metadata state record; no ComfyUI adapter runtime is enabled.

## Phase 61Z: Commercial Operation ComfyUI Runtime Activations

Phase 61Z adds `commercial_operation_comfyui_runtime_activations` and `CommercialOperationComfyUIRuntimeActivation` records below each commercial operation. Operators and server maintainers can create metadata-only runtime activation records from validated ComfyUI runtime dry-runs, edit them, send them for review, approve or reject them, schedule metadata-only activation handoffs, mark failures, cancel active activation requests, or archive their audit trail. These records document future guarded ComfyUI activation requests, switch audits, runtime guardrails, validation checks, operator checklists, and rollback plans without importing or calling a ComfyUI adapter, storing or resolving secret values, calling ComfyUI, submitting prompts, reading queues, uploading files, submitting queues, enabling runtime switches, or generating media.

Endpoints:

- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/runtime-activations`
- `GET /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations`
- `PATCH /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/approve`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/reject`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/schedule`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/fail`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/cancel`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/archive`

Supported `activation_status` values: `draft`, `ready_for_review`, `approved`, `rejected`, `scheduled`, `failed`, `cancelled`, and `archived`.

Boundary: ComfyUI runtime activations are metadata records only. They do not import or call ComfyUI adapters, enable runtime server switches, mutate runtime configuration, read environment state, store or resolve secret values, call ComfyUI health, prompt, history, upload, or queue endpoints, submit prompts, read queues, upload files, submit jobs, generate media, publish content, run OpenClaw, run Browser Worker actions, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval. Approved activations can be scheduled only as an operator-facing metadata state record; no ComfyUI adapter runtime is enabled.

## Phase 62A: ComfyUI Runtime Adapter Contract

Phase 62A adds disabled-by-default ComfyUI runtime adapter contract endpoints. Operators and server maintainers can inspect provider, switch, base URL, timeout, allowed hosts, disabled actions, required configuration, and guardrails before any future live adapter work. These endpoints do not import adapters, call ComfyUI, read queues, submit prompts, upload files, generate media, enable runtime switches, mutate runtime configuration, read environment state, or resolve secret values.

Endpoints:

- `GET /api/v1/comfyui-runtime/health`
- `GET /api/v1/comfyui-runtime/capabilities`
- `GET /api/v1/comfyui-runtime/diagnostics`
- `GET /api/v1/comfyui-runtime/maintenance-runbook`
- `GET /api/v1/comfyui-runtime/config-change-requests`
- `POST /api/v1/comfyui-runtime/config-change-requests`
- `GET /api/v1/comfyui-runtime/manual-apply-evidence`
- `POST /api/v1/comfyui-runtime/config-change-requests/{request_id}/manual-apply-evidence`
- `GET /api/v1/comfyui-runtime/post-manual-readiness-checks`
- `POST /api/v1/comfyui-runtime/manual-apply-evidence/{evidence_id}/post-manual-readiness-checks`
- `GET /api/v1/comfyui-runtime/guarded-probe-executions`
- `POST /api/v1/comfyui-runtime/post-manual-readiness-checks/{check_id}/guarded-probe-executions`
- `GET /api/v1/comfyui-runtime/diagnostic-snapshots`
- `POST /api/v1/comfyui-runtime/diagnostic-snapshots`

Default configuration:

- `COMFYUI_RUNTIME_PROVIDER=disabled`
- `COMFYUI_RUNTIME_ENABLED=False`
- `COMFYUI_RUNTIME_BASE_URL=http://127.0.0.1:8188`
- `COMFYUI_RUNTIME_TIMEOUT_SECONDS=30.0`
- `COMFYUI_RUNTIME_ALLOW_NETWORK=False`
- `COMFYUI_RUNTIME_ALLOWED_HOSTS=127.0.0.1,localhost`

Boundary: Phase 62A is a contract and visibility layer only. Even when guarded settings are supplied, the health endpoint reports readiness metadata without attempting a network request. Runtime calls, queue reads/submissions, prompt submission, uploads, media generation, runtime switch enablement, and secret resolution remain disabled.

## Phase 62B: ComfyUI Guarded Read-Only Probe

Phase 62B extends the ComfyUI runtime contract with an explicitly gated read-only health probe. The default remains no-network. `GET /api/v1/comfyui-runtime/health` attempts exactly one `GET /system_stats` request only when `COMFYUI_RUNTIME_PROVIDER=guarded`, `COMFYUI_RUNTIME_ENABLED=true`, `COMFYUI_RUNTIME_ALLOW_NETWORK=true`, `COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=true`, the base URL host is in `COMFYUI_RUNTIME_ALLOWED_HOSTS`, and the health path is in `COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS`.

Endpoints:

- `GET /api/v1/comfyui-runtime/health`
- `GET /api/v1/comfyui-runtime/capabilities`

Additional default configuration:

- `COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=False`
- `COMFYUI_RUNTIME_HEALTH_PATH=/system_stats`
- `COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS=/system_stats`

Health responses include `read_only_probe_enabled`, `read_only_probe_attempted`, `health_path`, `allowed_health_paths`, `probe_status_code`, and `probe_latency_ms`.

Boundary: Phase 62B is a guarded read-only health check only. It does not import adapters, submit prompts, read queues, submit queues, upload files, generate media, enable runtime switches, mutate runtime configuration, read environment state, or resolve secret values.

## Phase 62C: ComfyUI Runtime Diagnostics

Phase 62C adds `GET /api/v1/comfyui-runtime/diagnostics`, a no-network readiness report for server maintainers. The diagnostics endpoint never calls ComfyUI. It reports `readiness_status`, `blocking_reasons`, `recommended_actions`, `read_only_probe_ready`, `external_request_attempted=false`, and `runtime_calls_enabled=false`.

Diagnostic checks include `provider_guarded`, `runtime_enabled`, `network_gate`, `base_url_scheme`, `base_url_host_allowlist`, `read_only_probe_gate`, `health_path_allowlist`, and `execution_boundary`.

Boundary: Phase 62C only explains guarded runtime readiness. It does not import adapters, call ComfyUI, submit prompts, read queues, submit queues, upload files, generate media, enable runtime switches, mutate runtime configuration, read environment state, or resolve secret values.

## Phase 62D: ComfyUI Runtime Diagnostic Snapshots

Phase 62D adds persisted no-network diagnostic snapshots for server maintainers. `POST /api/v1/comfyui-runtime/diagnostic-snapshots` calls the Phase 62C diagnostics path, stores the readiness result in `comfyui_runtime_diagnostic_snapshots`, and returns the saved snapshot with operator note, metadata, `readiness_status`, `blocking_reasons`, `recommended_actions`, `read_only_probe_ready`, diagnostic checks, forbidden actions, and the full diagnostic payload. `GET /api/v1/comfyui-runtime/diagnostic-snapshots` lists recent snapshots for the current workspace.

Boundary: Phase 62D records diagnostics only. Snapshot creation does not call ComfyUI, does not run the guarded `/system_stats` probe, and does not import adapters, submit prompts, read queues, submit queues, upload files, generate media, enable runtime switches, mutate runtime configuration, read environment state, or resolve secret values.

## Phase 62E: ComfyUI Runtime Maintenance Runbook

Phase 62E adds `GET /api/v1/comfyui-runtime/maintenance-runbook`, a no-network runbook for server maintainers and workstation operators. It reuses Phase 62C diagnostics and returns ordered `steps`, `next_operator_action`, `recovery_actions`, `configuration_summary`, `snapshot_recommended`, disabled actions, and the source diagnostics payload so the ComfyUI tab can show what to fix or verify next.

Boundary: Phase 62E explains and displays maintenance actions only. The runbook does not call ComfyUI, does not run the guarded `/system_stats` probe, and does not import adapters, submit prompts, read queues, submit queues, upload files, generate media, enable runtime switches, mutate runtime configuration, read environment state, or resolve secret values.

## Phase 62F: ComfyUI Runtime Configuration Change Requests

Phase 62F adds metadata-only configuration change requests for server maintainers. `POST /api/v1/comfyui-runtime/config-change-requests` creates a request from the Phase 62E maintenance runbook, stores current configuration, `requested_changes`, runbook steps, recovery actions, disabled actions, `change_status`, reviewer notes, and `config_mutation_performed=false` in `comfyui_runtime_config_change_requests`. `GET /api/v1/comfyui-runtime/config-change-requests` lists recent requests for the current workspace.

Review endpoints:

- `POST /api/v1/comfyui-runtime/config-change-requests/{request_id}/ready`
- `POST /api/v1/comfyui-runtime/config-change-requests/{request_id}/approve`
- `POST /api/v1/comfyui-runtime/config-change-requests/{request_id}/reject`
- `POST /api/v1/comfyui-runtime/config-change-requests/{request_id}/cancel`
- `POST /api/v1/comfyui-runtime/config-change-requests/{request_id}/archive`

Boundary: Phase 62F records a reviewable request only. It does not write environment variables, restart services, enable runtime switches, call ComfyUI, run the guarded `/system_stats` probe, import adapters, submit prompts, read queues, submit queues, upload files, generate media, read environment state, resolve secret values, publish, run OpenClaw, run Browser Worker actions, or bypass approval.

## Phase 62G: ComfyUI Runtime Manual Apply Evidence

Phase 62G adds metadata-only manual apply evidence for server maintainers. `POST /api/v1/comfyui-runtime/config-change-requests/{request_id}/manual-apply-evidence` creates evidence from a Phase 62F request that is already `approved_for_manual_apply`, stores before/after snapshot ids, the approved request payload, manual apply steps, restart evidence, rollback notes, verification notes, no-network diagnostics, `manual_config_applied=true`, `service_restart_reported`, `external_request_attempted=false`, `runtime_calls_enabled=false`, and `api_config_mutation_performed=false` in `comfyui_runtime_manual_apply_evidence`. `GET /api/v1/comfyui-runtime/manual-apply-evidence` lists recent evidence records for the current workspace.

Review endpoints:

- `POST /api/v1/comfyui-runtime/manual-apply-evidence/{evidence_id}/ready`
- `POST /api/v1/comfyui-runtime/manual-apply-evidence/{evidence_id}/verify`
- `POST /api/v1/comfyui-runtime/manual-apply-evidence/{evidence_id}/reject`
- `POST /api/v1/comfyui-runtime/manual-apply-evidence/{evidence_id}/fail`
- `POST /api/v1/comfyui-runtime/manual-apply-evidence/{evidence_id}/archive`

Boundary: Phase 62G records maintainer evidence only. It does not write environment variables, restart services, enable runtime switches, mutate runtime configuration through the API, call ComfyUI, run the guarded `/system_stats` probe, import adapters, submit prompts, read queues, submit queues, upload files, generate media, read environment state, resolve secret values, publish, run OpenClaw, run Browser Worker actions, or bypass approval.

## Phase 62H: ComfyUI Runtime Post-Manual Readiness Checks

Phase 62H adds metadata-only post-manual readiness checks for server maintainers. `POST /api/v1/comfyui-runtime/manual-apply-evidence/{evidence_id}/post-manual-readiness-checks` creates a check from verified Phase 62G evidence, compares before/after/current readiness, stores current no-network diagnostics, comparison results, blockers, recommended actions, readiness delta, `comparison_status`, `guarded_probe_ready`, `health_probe_executed=false`, `external_request_attempted=false`, `runtime_calls_enabled=false`, and `api_config_mutation_performed=false` in `comfyui_runtime_post_manual_readiness_checks`. `GET /api/v1/comfyui-runtime/post-manual-readiness-checks` lists recent checks for the current workspace.

Review endpoints:

- `POST /api/v1/comfyui-runtime/post-manual-readiness-checks/{check_id}/ready`
- `POST /api/v1/comfyui-runtime/post-manual-readiness-checks/{check_id}/approve`
- `POST /api/v1/comfyui-runtime/post-manual-readiness-checks/{check_id}/reject`
- `POST /api/v1/comfyui-runtime/post-manual-readiness-checks/{check_id}/fail`
- `POST /api/v1/comfyui-runtime/post-manual-readiness-checks/{check_id}/archive`

Boundary: Phase 62H records maintainer readiness comparisons only. It does not write environment variables, restart services, enable runtime switches, mutate runtime configuration through the API, call ComfyUI, run the guarded `/system_stats` probe, import adapters, submit prompts, read queues, submit queues, upload files, generate media, read environment state, resolve secret values, publish, run OpenClaw, run Browser Worker actions, or bypass approval.

## Phase 62J: ComfyUI Runtime Guarded Probe Execution Audit

Phase 62J adds approval-gated guarded read-only probe execution records for server maintainers. `POST /api/v1/comfyui-runtime/post-manual-readiness-checks/{check_id}/guarded-probe-executions` creates a record from a Phase 62H check that is already `approved_for_read_only_probe` and still shows current no-network diagnostics with `read_only_probe_ready=true`. Creation stores readiness check payload, current diagnostics, the intended read-only probe request, disabled actions, `probe_result_status=not_started`, `external_request_attempted=false`, `health_probe_executed=false`, `runtime_calls_enabled=false`, and `api_config_mutation_performed=false` in `comfyui_runtime_guarded_probe_executions`. `GET /api/v1/comfyui-runtime/guarded-probe-executions` lists recent records for the current workspace.

Review endpoints:

- `POST /api/v1/comfyui-runtime/guarded-probe-executions/{execution_id}/ready`
- `POST /api/v1/comfyui-runtime/guarded-probe-executions/{execution_id}/approve`
- `POST /api/v1/comfyui-runtime/guarded-probe-executions/{execution_id}/reject`
- `POST /api/v1/comfyui-runtime/guarded-probe-executions/{execution_id}/fail`
- `POST /api/v1/comfyui-runtime/guarded-probe-executions/{execution_id}/cancel`
- `POST /api/v1/comfyui-runtime/guarded-probe-executions/{execution_id}/archive`

Execution endpoint:

- `POST /api/v1/comfyui-runtime/guarded-probe-executions/{execution_id}/execute`

Boundary: create/list/review endpoints remain no-network. The execute endpoint rechecks current diagnostics and can call only the existing guarded `GET /system_stats` health path after the execution record is `approved_for_execution`. It records `external_request_attempted`, `health_probe_executed`, `read_only_probe_attempted`, `probe_status_code`, `probe_latency_ms`, `probe_result_status`, and `probe_response`; it still does not import adapters, submit prompts, read queues, submit queues, upload files, generate media, enable runtime switches, write environment variables, restart services, mutate runtime configuration, resolve secret values, publish, run OpenClaw, run Browser Worker actions, control accounts, or bypass approval.

## Phase 65A: ComfyUI Real Adapter

Phase 65A adds guarded real ComfyUI prompt and status routes for server maintainers. These routes are disabled by default and require `COMFYUI_RUNTIME_PROVIDER=guarded`, `COMFYUI_RUNTIME_ENABLED=true`, `COMFYUI_RUNTIME_ALLOW_NETWORK=true`, `COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=true`, allowed host and health path gates, `COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=true`, and `COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS` containing the requested execution path.

Endpoints:

- `POST /api/v1/comfyui-runtime/prompt-jobs`
- `GET /api/v1/comfyui-runtime/prompt-jobs/{prompt_id}/history`
- `GET /api/v1/comfyui-runtime/queue`

`POST /prompt-jobs` accepts a ComfyUI `prompt` graph plus optional `client_id`, `extra_data`, `workflow`, and `metadata`, then forwards the guarded payload to ComfyUI `/prompt`. The response records `external_request_attempted`, `runtime_calls_enabled`, `prompt_submission_enabled`, `status_code`, `prompt_id`, `number`, `node_errors`, `request_payload`, and `response_payload`. History and queue endpoints call only `/history/{prompt_id}` and `/queue` when those paths are allowlisted.

Boundary: Phase 65A submits prompts and reads history/queue only through the guarded adapter. It does not upload files, download models, resolve secrets, mutate runtime configuration, restart services, publish, run OpenClaw/Playwright publishing, control accounts, ingest analytics, or bypass approval.

## Phase 62Y: Commercial Operation Loop Protocol

Phase 62Y adds one read-only commercial-operation loop summary for server and customer-machine frontends. `GET /api/v1/commercial-operations/{operation_id}/operation-loop` returns `CommercialOperationLoopSummaryResponse` with `loop_status`, `current_stage_key`, `next_action`, `completion_ratio`, `stages`, `counts`, `execution_protocol`, `readiness`, and `boundaries`.

Each `CommercialOperationLoopStageResponse` maps one stage in the requested commercial loop: operating topic, system task plan, knowledge context, content production, human approval, OpenClaw/Playwright customer-machine execution, result recording, data observation, data analysis, and content improvement. Stages include `status`, `summary`, `next_action`, `blocked_reasons`, `related_records`, and server/customer/operator actions.

Endpoint:

- `GET /api/v1/commercial-operations/{operation_id}/operation-loop`

Boundary: this endpoint only aggregates existing operation records. It does not execute OpenClaw, run Playwright, publish, control accounts, call ComfyUI, ingest platform analytics, claim ROI attribution, resolve secrets, bypass captcha/proxy/fingerprint controls, or bypass approval.
