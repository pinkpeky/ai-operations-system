# Deployment

## Phase 28 OpenClaw Adapter Smoke Test

Current OpenClaw runtime is mock only:

```env
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=true
OPENCLAW_ACTION_TIMEOUT_SECONDS=60
```

Docker / local smoke flow:

1. Start the API stack with `docker compose up --build -d`.
2. Start or register a worker that advertises `"openclaw": true` in capabilities.
3. Call `GET /api/v1/openclaw/health` with `X-Workspace-Id`.
4. Call `GET /api/v1/openclaw/capabilities`.
5. Call `POST /api/v1/openclaw/actions` with a mock action such as `mock_inspect`.
6. Confirm `openclaw_action_logs`, `tool_call_logs` when using `openclaw_tool`, and `browser_security_audit_logs`.

Boundary: this does not call real OpenClaw and must not be used for TikTok / YouTube / X, login, cookies, proxy pools, fingerprint bypass, captcha automation, or real platform automation.

## Phase 20 browser-worker Startup and Verification

Docker Compose now includes an independent service:

```text
browser-worker
  command: uvicorn worker.main:app --host 0.0.0.0 --port 9100
  port: 9100
  runtime: worker/browser_worker/playwright_runtime.py
  screenshots: worker/screenshots
```

Start:

```powershell
docker compose up --build -d
```

Worker health:

```powershell
Invoke-RestMethod http://localhost:9100/health
```

API Server to worker smoke flow:

1. Set or confirm `BROWSER_PROVIDER=remote`.
2. Register the worker with Docker network `base_url=http://browser-worker:9100`.
3. Create a browser session.
4. Run `navigate` against `https://example.com`.
5. Run `screenshot` and `get_page_content`.

Phase 20 still does not support social platform automation, login, cookies, proxies, fingerprint bypass, captcha automation, OCR, visual AI, or OpenClaw.

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

Task reliability and observability:

```http
POST /api/v1/tasks
POST /api/v1/tasks/{task_id}/cancel
POST /api/v1/tasks/{task_id}/retry
GET /api/v1/tasks/{task_id}/events
GET /api/v1/tasks/{task_id}/logs
GET /api/v1/observability/summary
```

Summary smoke test:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri http://localhost:8000/api/v1/observability/summary `
  -Headers @{ "X-Workspace-Id" = "demo-workspace" }
```

## Tool Calling Smoke Test

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri http://localhost:8000/api/v1/tools `
  -Headers @{ "X-Workspace-Id" = "demo-workspace" }

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/tools/current_runtime_tool/execute `
  -Headers @{ "X-Workspace-Id" = "demo-workspace" } `
  -ContentType application/json `
  -Body '{ "input": { "include_document": false } }'

Invoke-RestMethod `
  -Method Get `
  -Uri http://localhost:8000/api/v1/tool-calls `
  -Headers @{ "X-Workspace-Id" = "demo-workspace" }
```

Current Tool Calling does not include Browser Agent, OpenClaw, Playwright, Selenium, autonomous planning, or external API tools.

## Memory Smoke Test

Create a session:

```powershell
$headers = @{ "X-Workspace-Id" = "demo-workspace"; "X-User-Id" = "demo-user" }
$session = Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/memory/sessions `
  -Headers $headers `
  -ContentType application/json `
  -Body '{ "title": "Phase 14 memory smoke", "metadata": { "phase": "14" } }'
```

Append a message:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/memory/messages `
  -Headers $headers `
  -ContentType application/json `
  -Body (@{
    session_id = $session.id
    role = "user"
    content = "Remember that I care about Agentic RAG memory_trace."
    metadata = @{ turn = 1 }
  } | ConvertTo-Json)
```

Save an Agent Memory:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/memory/memories `
  -Headers $headers `
  -ContentType application/json `
  -Body '{ "agent_name": "AgenticRAGOrchestrator", "memory_type": "long_term", "content": "User cares about Agentic RAG memory_trace.", "importance_score": 0.8 }'
```

Verify Agentic RAG memory trace:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/agentic-rag/query `
  -Headers $headers `
  -ContentType application/json `
  -Body (@{
    query = "How does memory_trace help debugging?"
    collection_name = "phase14_memory_demo"
    top_k = 3
    debug = $true
    session_id = $session.id
  } | ConvertTo-Json)
```

Expected debug fields include `session_id`, `recent_messages_count`, `retrieved_memories_count`, and `memory_trace`.

## Phase 15 Multi-Agent Smoke Test

Use mock providers and a lightweight query such as `ping` when the target collection has not been ingested yet.

```powershell
$headers = @{ "X-Workspace-Id" = "demo-workspace"; "X-User-Id" = "demo-user" }

Invoke-RestMethod `
  -Method Get `
  -Uri http://localhost:8000/api/v1/agents/registry `
  -Headers $headers

$run = Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/multi-agent/runs `
  -Headers $headers `
  -ContentType application/json `
  -Body '{
    "root_agent": "content_planner",
    "input": {
      "topic": "AI automation operations",
      "platform": "tiktok",
      "style": "professional concise",
      "query": "ping",
      "collection_name": "phase15_multi_agent_demo"
    }
  }'

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/v1/multi-agent/runs/$($run.id)/execute-chain" `
  -Headers $headers `
  -ContentType application/json `
  -Body '{ "chain_name": "content_planning" }'

Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/v1/multi-agent/runs/$($run.id)/messages" `
  -Headers $headers

Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/v1/multi-agent/runs/$($run.id)/handoffs" `
  -Headers $headers
```

Expected output contains `agents_involved`, `agent_messages`, `agent_handoffs`, and `handoff_trace`.

## Phase 16 Planning Smoke Test

```powershell
$headers = @{ "X-Workspace-Id" = "demo-workspace"; "X-User-Id" = "demo-user" }

$plan = Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/plans `
  -Headers $headers `
  -ContentType application/json `
  -Body '{
    "root_goal": "Generate TikTok content for AI automation operations",
    "planner_agent": "simple_planner",
    "metadata": {
      "query": "ping",
      "platform": "tiktok",
      "style": "professional concise"
    }
  }'

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/v1/plans/$($plan.id)/execute" `
  -Headers $headers `
  -ContentType application/json `
  -Body '{ "input": { "query": "ping" } }'

Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/v1/plans/$($plan.id)/steps" `
  -Headers $headers

Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/v1/plans/$($plan.id)/reviews" `
  -Headers $headers
```

Expected output contains `plans`, `plan_steps`, `plan_reviews`, `PlanStep.duration_ms`, and planning `memory_trace`.

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

## Browser Adapter Smoke Test

Phase 17 uses `BROWSER_PROVIDER=mock` by default. No real browser is started.

Create a session:

```http
POST /api/v1/browser/sessions
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

```json
{
  "metadata": {
    "purpose": "deployment-smoke"
  }
}
```

Execute an action:

```http
POST /api/v1/browser/actions
X-Workspace-Id: demo-workspace
```

```json
{
  "session_id": "uuid-from-create-session",
  "action_type": "navigate",
  "target": "https://example.com",
  "input_payload": {
    "wait": "none"
  }
}
```

Verify:

```http
GET /api/v1/browser/actions/{session_id}
GET /api/v1/browser/logs/{session_id}
POST /api/v1/tools/browser_tool/execute
```

Browser deployment limitations:

- `MockBrowserProvider` only.
- `PlaywrightBrowserProvider` placeholder only.
- No Playwright/Selenium installation.

## Playwright Local Provider Smoke Test

Phase 18 supports `PlaywrightLocalProvider`. The Docker image installs Playwright Python and Chromium:

```text
python -m playwright install --with-deps chromium
```

Enable it:

```powershell
$env:BROWSER_PROVIDER="playwright_local"
docker compose up --build -d
```

Recommended smoke test:

```http
POST /api/v1/browser/sessions
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

```json
{
  "metadata": {
    "test": "phase18"
  }
}
```

```http
POST /api/v1/browser/actions
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

```json
{
  "session_id": "SESSION_ID",
  "action_type": "navigate",
  "target": "https://example.com"
}
```

Screenshot:

```json
{
  "session_id": "SESSION_ID",
  "action_type": "screenshot",
  "screenshot_name": "example-home"
}
```

Read screenshot:

```http
GET /api/v1/browser/screenshot/{session_id}/example-home.png
X-Workspace-Id: demo-workspace
```

Safety boundary:

- Test only `example.com`, local pages, and static `file://` pages.
- No TikTok / YouTube / X, login automation, cookie injection, fingerprint bypass, proxy pools, captcha automation, OCR, visual AI, or Browser Worker.

## Remote Browser Worker Smoke Test

Phase 19 does not enable the remote provider by default. To verify Remote Browser Worker Foundation:

```powershell
$env:BROWSER_PROVIDER="remote"
docker compose up --build -d
```

Register the in-project mock worker runtime:

```http
POST /api/v1/browser-workers/register
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

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

Heartbeat:

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

Remote action:

```json
{
  "session_id": "SESSION_ID",
  "action_type": "navigate",
  "target": "https://example.com"
}
```

Mock runtime health:

```http
GET /api/v1/browser-worker-runtime/health
```

Note: this is only the in-project mock runtime, not a real external Browser Worker deployment. It does not start a real browser or perform platform automation.
- No platform automation, OCR, visual AI, or real login flow.
## Phase 21 Worker Reliability Deployment

New environment variables:

```env
BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS=60
BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS=30
BROWSER_SESSION_TIMEOUT_SECONDS=1800
BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS=300
BROWSER_ACTION_TIMEOUT_SECONDS=60
BROWSER_ACTION_RETRY_COUNT=2
BROWSER_ACTION_RETRY_BACKOFF_SECONDS=2
SCREENSHOT_RETENTION_DAYS=7
```

Docker Compose mounts these screenshot directories into the API container:

```text
./screenshots:/app/screenshots
./worker/screenshots:/app/worker/screenshots
```

This allows `ScreenshotCleanupService` to cover both API screenshots and independent `browser-worker` screenshots.

Deployment smoke test:

```powershell
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Swagger verification:

- `GET /api/v1/browser-workers/health/summary`
- `GET /api/v1/browser-workers/available`
- `POST /api/v1/browser-workers/{worker_id}/mark-offline`
- `POST /api/v1/browser-workers/cleanup-sessions`
- `POST /api/v1/browser/screenshots/cleanup`

This phase validates worker reliability only. It does not enable TikTok / YouTube / X automation, login, proxies, fingerprint bypass, captcha handling, or real platform automation.

## Phase 22 Persistent Browser Profile Deployment

Phase 22 adds profile persistence for browser sessions. The API stores profile metadata in PostgreSQL and passes profile hints to the configured browser provider. The independent `browser-worker` stores persistent context files under `worker/profiles/{workspace_id}/{profile_id}`.

## Phase 23 Browser Profile Health & Recovery Deployment

Phase 23 requires the API service to expose these runtime settings:

```env
BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS=1800
BROWSER_PROFILE_BACKUP_ENABLED=true
BROWSER_PROFILE_MAX_BACKUPS=3
BROWSER_PROFILE_UNUSED_DAYS=30
BROWSER_PROFILE_BACKUP_ROOT=worker/profile_backups
```

Docker Compose mounts `./worker/profile_backups:/app/worker/profile_backups` for the API service. Profile backups are zip files grouped by `workspace_id/profile_id`. `browser_profiles.profile_path` must stay under `BROWSER_PROFILE_ROOT`; health checks mark missing or out-of-root paths as corrupted.

Post-deploy smoke test:

```powershell
docker compose up --build -d
python -m pytest tests/test_profile_health.py tests/test_profile_recovery.py tests/test_profile_backup.py tests/test_profile_cleanup.py tests/test_profile_usage_logs.py
python scripts/verify_docs_runtime.py
```

Swagger verification:

- `GET /api/v1/browser/profiles/health/summary`
- `POST /api/v1/browser/profiles/{profile_id}/health-check`
- `POST /api/v1/browser/profiles/recover-stale-locks`
- `POST /api/v1/browser/profiles/{profile_id}/backup`
- `GET /api/v1/browser/profiles/{profile_id}/backups`
- `POST /api/v1/browser/profiles/{profile_id}/restore`
- `POST /api/v1/browser/profiles/cleanup`
- `GET /api/v1/browser/profiles/{profile_id}/usage-logs`

Production migration notes:

- Put the backup directory on a persistent volume and include it in server backup policy.
- `dry_run=true` is the default for profile cleanup; inspect `matched_profiles` and `bytes_freed` before real deletion.
- If a worker is offline or a session is stale, run `recover-stale-locks` before creating a new profile-backed session.
- This phase does not add social-platform automation, login, cookie injection, proxy pools, fingerprint bypass, or captcha handling.

Environment variables:

```env
BROWSER_PROFILE_ROOT=worker/profiles
WORKER_PROFILE_DIR=worker/profiles
```

Docker Compose mounts the profile directory so API metadata and worker runtime paths stay consistent:

```text
./worker/profiles:/app/worker/profiles
```

Smoke test:

```powershell
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Swagger verification:

- `POST /api/v1/browser/profiles`
- `GET /api/v1/browser/profiles`
- `POST /api/v1/browser/sessions` with `profile_id` and `use_persistent_profile=true`
- `POST /api/v1/browser/actions` with `navigate` to `https://example.com`
- `POST /api/v1/browser/actions` with `screenshot`
- `POST /api/v1/browser/sessions/{session_id}/close`

Expected behavior:

- The profile becomes `locked` while the session is active.
- The worker uses `launch_persistent_context` for that session.
- Closing the session releases the profile and updates `last_used_at`.
- The same profile can be reused after release.

Boundary: this deployment does not enable TikTok / YouTube / X automation, login, cookie injection, proxy pools, fingerprint bypass, captcha handling, or real platform automation.

## Phase 24 Human-in-the-loop Browser Control Deployment

Phase 24 is API-server first. It adds database-backed human-control state, browser-session pause/resume fields, and metadata-level worker endpoints. It does not require VNC, noVNC, Chrome DevTools remote UI, or a real manual-control surface.

Runtime setting:

```env
BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS=900
```

Docker Compose passes the setting to the API service. The independent `browser-worker` exposes metadata-level routes:

```text
POST /human-control/start
POST /human-control/complete
GET /human-control/status/{session_id}
```

Deployment smoke test:

```powershell
docker compose up --build -d
python -m pytest tests/test_browser_human_control.py tests/test_human_control_state_flow.py tests/test_human_control_api.py tests/test_browser_session_pause_resume.py tests/test_browser_tool_human_control.py
python scripts/verify_docs_runtime.py
```

Swagger verification:

- `POST /api/v1/browser/human-control/request`
- `POST /api/v1/browser/human-control/{control_session_id}/approve`
- `POST /api/v1/browser/human-control/{control_session_id}/start`
- `POST /api/v1/browser/human-control/{control_session_id}/complete`
- `GET /api/v1/browser/human-control/{control_session_id}/events`
- `POST /api/v1/tools/browser_tool/execute` with `action_type=request_human_control`
- `POST /api/v1/tools/browser_tool/execute` with `action_type=complete_human_control`

Expected behavior:

- Requesting human control sets the browser session to `paused`.
- Regular browser actions fail while the session is paused.
- Completing human control restores the browser session to `active`.
- The associated profile and worker session stay reserved during the human-control window.

Boundary: Phase 24 does not implement VNC, noVNC, Chrome DevTools remote UI, platform login, captcha handling, cookie injection, proxy pools, fingerprint bypass, or real social-platform automation.

## Phase 25 Browser Worker UI Access Placeholder Deployment

Phase 25 is a backend placeholder. It adds `browser_ui_access_sessions`, token hash validation, placeholder URLs, and worker capability reporting. It does not start a VNC/noVNC/DevTools service.

Runtime setting:

```env
BROWSER_UI_ACCESS_TIMEOUT_SECONDS=900
```

Worker capability endpoint:

```text
GET http://localhost:9100/ui-access/capabilities
```

Expected response:

```json
{
  "vnc": false,
  "novnc": false,
  "devtools": false,
  "placeholder": true
}
```

Deployment smoke test:

```powershell
docker compose up --build -d
python -m pytest tests/test_browser_ui_access.py tests/test_ui_access_token.py tests/test_ui_access_api.py tests/test_human_control_ui_access.py tests/test_browser_tool_ui_access.py
python scripts/verify_docs_runtime.py
```

Swagger verification:

- `POST /api/v1/browser/ui-access`
- `GET /api/v1/browser/ui-access/{access_session_id}`
- `GET /api/v1/browser/ui-access/{access_session_id}/validate?token=TOKEN`
- `POST /api/v1/browser/ui-access/{access_session_id}/revoke`
- `POST /api/v1/browser/ui-access/expire`
- `GET /api/v1/browser-worker-runtime/ui-access/capabilities`
- `POST /api/v1/tools/browser_tool/execute` with `action_type=create_ui_access`
- `POST /api/v1/tools/browser_tool/execute` with `action_type=revoke_ui_access`

Expected behavior:

- The create API returns the plaintext token once.
- Later read APIs return `access_token=null`.
- Token validation succeeds before revoke/expiry and fails after revoke/expiry.
- Generated `remote_control_url` and `live_view_url` are placeholder URLs only.

Boundary: this deployment does not enable real VNC, noVNC, DevTools UI, live browser video, platform login, captcha handling, cookie injection, proxy pools, fingerprint bypass, TikTok / YouTube / X, or real platform automation.

## Phase 26 Browser Worker Security & Access Control Deployment

Phase 26 does not require a new external service. It depends on the API Server, the database migration, the existing `browser-worker` service, and these runtime settings:

```env
BROWSER_WORKER_AUTH_ENABLED=true
BROWSER_WORKER_AUTH_STRICT=false
BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1
BROWSER_BLOCKED_DOMAINS=
BROWSER_ALLOW_EXTERNAL_DOMAINS=false
```

Local Docker keeps `BROWSER_WORKER_AUTH_STRICT=false`, so smoke tests are not blocked when the worker runtime has no shared secret configured. The API Server stores only `worker_secret_hash`; plaintext `worker_secret` is returned once by register/rotate responses. In the same API process, `BrowserWorkerClient` signs requests when the one-time secret is still cached. Production hardening should distribute the worker secret to the Worker service and enable strict mode.

Deployment verification:

```powershell
python -m pytest tests/test_browser_worker_auth.py tests/test_worker_signed_requests.py tests/test_ui_access_scopes.py tests/test_browser_action_policy.py tests/test_browser_security_audit_logs.py
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Swagger smoke:

- `POST /api/v1/browser-workers/register`, confirm the response contains one-time `worker_secret`.
- `POST /api/v1/browser-workers/{worker_id}/heartbeat`, optionally with `X-Worker-Secret`.
- `POST /api/v1/browser-workers/{worker_id}/rotate-secret`.
- `POST /api/v1/browser/security/policy/check`, where `https://example.com` is allowed and `https://not-allowed.example.org` is blocked.
- `POST /api/v1/browser/ui-access` with `scopes` and `one_time`.
- `GET /api/v1/browser/ui-access/{id}/validate?token=TOKEN&scope=view`.
- `GET /api/v1/browser/security/audit-logs`.

Boundary: Phase 26 does not implement real platform account security, TikTok / YouTube / X automation, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha handling, or complete RBAC/JWT/OAuth.

## Phase 27 Customer Machine Worker Bootstrap Deployment

Phase 27 adds a local `worker_client` package for customer-owned machines. It does not require a new API Server container. The Docker `browser-worker` service remains supported, and customer machines use the same registration, heartbeat, and worker runtime protocol.

Manual customer-machine setup:

```powershell
Copy-Item worker_client\worker_config.example.yaml worker_client\worker_config.yaml
# Edit server_url, workspace_id, worker_name, worker_base_url, and runtime_port.
python -m worker_client.cli register
python -m worker_client.cli serve
python -m worker_client.cli heartbeat
```

Single-process bootstrap:

```powershell
python -m worker_client.cli start
python -m worker_client.cli start --force-register
```

When using a non-default config path, pass the global option before the command:

```powershell
python -m worker_client.cli --config C:\path\worker_config.yaml register
python -m worker_client.cli --config C:\path\worker_config.yaml heartbeat --once
python -m worker_client.cli --config C:\path\worker_config.yaml serve --host 0.0.0.0 --port 9100
python -m worker_client.cli --config C:\path\worker_config.yaml start
```

Deployment verification:

```powershell
python -m pytest tests/test_worker_client_config.py tests/test_worker_client_registration.py tests/test_worker_client_heartbeat.py tests/test_worker_client_cli.py tests/test_worker_client_runtime_compatibility.py
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Security notes:

- `worker_client/worker_config.yaml` and `worker_client/worker_state.json` are local-only and ignored by Git.
- `worker_state.json` stores the one-time plaintext `worker_secret`; do not commit, print, or paste it into docs.
- The heartbeat flow sends `X-Worker-Secret` plus Phase 26 signed request headers.

Boundary: Phase 27 is Customer Machine Worker Bootstrap only. It does not implement OpenClaw integration, TikTok / YouTube / X automation, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha handling, or real platform automation.

## Phase 29 Worker Client Packaging

Windows:

```powershell
copy worker_client\worker_config.example.yaml worker_client\worker_config.yaml
.\packaging\windows_install_requirements.ps1
.\packaging\windows_register_worker.ps1
.\packaging\windows_start_worker.ps1
```

Mac:

```bash
cp worker_client/worker_config.example.yaml worker_client/worker_config.yaml
bash packaging/mac_install_requirements.sh
bash packaging/mac_register_worker.sh
bash packaging/mac_start_worker.sh
```

Local verification:

```text
GET http://127.0.0.1:9100/local/status
GET http://127.0.0.1:9100/local/health
GET http://127.0.0.1:9100/local/logs
```

Scripts include `packaging/windows_start_worker.ps1` and `packaging/mac_start_worker.sh`. Runtime writes `worker_client/runtime_state/status.json` and `worker_client/logs/worker.log`; both are ignored by Git. This is Worker Console Foundation only: no GUI, no exe/dmg packaging.

## Phase 30 Worker Console Deployment

Local development:

```powershell
python -m worker_client.cli start
cd worker_console
npm install
npm run dev
```

Open `http://localhost:5173`. The console uses `VITE_LOCAL_WORKER_API=http://127.0.0.1:9100`. Build with `npm run build`.

This is Web GUI Foundation only: no system tray, no auto update, no Electron, no Tauri, no PySide, no exe / dmg packaging.
## Phase 31: Worker Console Desktop Local Run

The desktop app still depends on the local customer-machine Worker API. Start `worker_client` first:

```bash
python -m worker_client.cli start
```

Then start the Tauri desktop shell:

```bash
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

Default connection:

```text
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

If the machine lacks Rust or Tauri platform dependencies, use `npm run build` for frontend validation and inspect `worker_console_desktop/src-tauri/tauri.conf.json`. This phase does not ship a formal exe / dmg, system tray, or auto update.

## Phase 32: System Tray Desktop Run

The run mode is still development mode:

```bash
python -m worker_client.cli start
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

This phase has System Tray and Minimize To Tray support, but still has no formal installer, no exe / dmg release, no real autostart registration, and no auto-update.

Configuration files:

- `worker_console_desktop/settings.example.json`
- `worker_console_desktop/src-tauri/desktop-runtime.json`
- `worker_console_desktop/autostart/README.md`

Security note: tray menu actions only trigger the local Worker API. They do not execute shell commands or remote commands.

## Phase 33 Runtime Notes

Conversation Runtime adds no new environment variable. It depends on the existing workspace headers and existing provider defaults.

Current defaults remain:

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
BROWSER_PROVIDER=mock
OPENCLAW_PROVIDER=mock
```

Conversation APIs require:

```text
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Worker Console chat clients use:

```text
VITE_AI_SERVER_API=http://localhost:8000/api/v1
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

Event feed mode: polling only through `GET /api/v1/conversations/{thread_id}/events`. WebSocket and SSE are placeholders only.

## Phase 34 Remote Browser Runtime Deployment

Deployment requirements:

- API Server must expose `BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots`.
- `docker-compose.yml` mounts `./storage:/app/storage` so runtime screenshots survive container restarts.
- Remote customer-machine workers must run the Worker Runtime API from `worker_client/runtime.py`.
- Customer machines that execute the real browser runtime must run `playwright install chromium`.
- Registered workers should include capabilities such as `{"browser_runtime": true, "browser": "chromium"}`.

Smoke test sequence:

1. Register or heartbeat an online worker.
2. `POST /api/v1/browser-runtime/sessions`
3. `POST /api/v1/browser-runtime/sessions/{session_id}/navigate`
4. `POST /api/v1/browser-runtime/sessions/{session_id}/screenshot`
5. `GET /api/v1/browser-runtime/sessions/{session_id}/page`
6. `POST /api/v1/browser-runtime/sessions/{session_id}/close`

Current deployment boundary: no stealth browser, no proxy, no login persistence, no cookie injection, no captcha bypass, no remote desktop stream, and no real platform automation.

## Phase 35B Real Client Worker E2E Deployment Check

Run after AI Server is online:

```bash
python scripts/validate_real_client_worker_e2e.py \
  --server-url http://localhost:8000 \
  --workspace-id demo-workspace \
  --user-id demo-user \
  --expected-worker-name customer-machine-worker-1
```

Expected result before a real customer machine is connected: `SKIPPED` with reason `real client worker not online`.

Expected result when the customer machine worker is online: `PASS`, with screenshot metadata under `storage/browser_screenshots`.

Do not expose customer-machine port 9100 to the public internet. Use Tailscale, VPN, or LAN routing.

## Phase 35A Browser Runtime Observability Smoke Test

Docker verification:

```powershell
docker compose up --build -d
```

Swagger / API flow:

1. `GET /api/v1/health`
2. `POST /api/v1/browser-runtime/sessions`
3. `POST /api/v1/browser-runtime/sessions/{session_id}/navigate`
4. `POST /api/v1/browser-runtime/sessions/{session_id}/screenshot`
5. `GET /api/v1/browser-runtime/sessions/{session_id}/page`
6. `GET /api/v1/browser-runtime/sessions/{session_id}/events`
7. `GET /api/v1/browser-runtime/sessions/{session_id}/snapshots`
8. `POST /api/v1/browser-runtime/sessions/{session_id}/replay`
9. `GET /api/v1/browser-runtime/replays/{replay_id}/export`
10. `POST /api/v1/browser-runtime/sessions/{session_id}/close`

Runtime directories:

```text
BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
```

Replay is currently metadata-only replay. It does not re-run browser actions and is not live stream, VNC/noVNC, or DevTools remote control.

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
## Phase 38 Deployment Verification

Conversation Tool Execution Bridge does not add a separate service. After deployment, create a conversation and call `POST /api/v1/conversations/{thread_id}/run`. Verify `route_name`, `selected_tool`, `events_created`, `success`, `summary`, and `result_metadata`, then call `GET /api/v1/conversations/{thread_id}/events` to inspect `route_selected`, `tool_execution_started`, `tool_execution_completed`, `agent_execution_started`, and `planning_execution_started`.

Boundaries: not autonomous agent, not WebSocket, not SSE, no real platform publishing, no real OpenClaw, and no ComfyUI.

## Phase 39 Deployment Verification

After deployment, verify the Approval Flow:

1. `POST /api/v1/conversations` to create a thread.
2. `POST /api/v1/conversations/{thread_id}/run` with `mode=review_first`.
3. `GET /api/v1/conversations/{thread_id}/approvals` and confirm `approval_status=pending`.
4. `POST /api/v1/conversation-approvals/{approval_id}/approve`.
5. `POST /api/v1/conversation-approvals/{approval_id}/execute`.
6. Repeating execute should return an error to prevent duplicate execution.

No extra environment variable is required. The flow depends on the `conversation_approvals` migration. Run Alembic before serving the updated Admin Dashboard / Worker Console assets. This is not a full permission system and not real platform publishing.
## Phase 40 Deployment Smoke Test: Conversation Playbooks

Recommended post-deploy checks:

1. `GET /api/v1/conversation-playbooks`
2. `POST /api/v1/conversation-playbooks/{playbook_id}/run`, starting with `content_generation`
3. `POST /api/v1/conversations/{thread_id}/run` with `playbook_name=browser_screenshot_report` and `mode=review_first`
4. Approve the generated approval
5. `POST /api/v1/conversation-approvals/{approval_id}/execute`
6. `GET /api/v1/conversation-playbook-runs`

If a browser Playbook stops at `waiting_approval`, that is expected. Medium/high risk steps must not execute before approval.

## Phase 41 Deployment Addendum

Output Library requires the API container to write `OUTPUT_ARTIFACT_DIR=storage/output_artifacts`. This phase exports markdown/json/txt to local disk; screenshots and HTML snapshots keep existing path references. There is no S3 / MinIO integration, no full DAM, and no production publishing asset management.
## Phase 42: Task Orchestration & Background Execution

This phase adds the Task Orchestration foundation: `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, and `TaskRetryPolicy`. Conversation / Playbook runs can use `execution_mode=background`, then `/api/v1/task-runs` exposes queued, running, waiting_approval, retrying, completed, failed, cancelled, expired state plus timeline events. `scheduled_at` supports scheduled runs; retry uses exponential backoff; approval resume continues to enforce the Phase 39 Approval Gate; Output Library artifacts are linked by `task_run_id`.

Boundary: this is an in-process queue, not Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue. It does not implement real publishing, real OpenClaw, ComfyUI, CAPTCHA handling, proxies, or fingerprint bypass.
