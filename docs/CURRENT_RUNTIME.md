# Current Runtime

Last updated: 2026-05-13

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
| `LOCAL_RERANKER_BASE_URL` | `http://host.docker.internal:11434` | Placeholder local reranker endpoint. |
| `LOCAL_RERANKER_MODEL` | `local-reranker-model` | Placeholder local reranker model name. |
| `BROWSER_PROVIDER` | `mock` | Default Browser Adapter provider. Does not start a real browser. |
| `BROWSER_TIMEOUT_SECONDS` | `30.0` | Browser action timeout for Playwright local mode. |
| `BROWSER_HEADLESS` | `True` | Runs Chromium headless in Playwright local mode. |
| `BROWSER_TYPE` | `chromium` | Browser type used by Playwright local mode. |
| `BROWSER_VIEWPORT_WIDTH` | `1280` | Default browser viewport width. |
| `BROWSER_VIEWPORT_HEIGHT` | `720` | Default browser viewport height. |
| `BROWSER_SCREENSHOT_DIR` | `screenshots` | Host/container screenshot storage root. |
| `BROWSER_PROFILE_ROOT` | `worker/profiles` | API-side profile path root stored on `browser_profiles.profile_path`. |
| `BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS` | `1800` | Stale profile lock recovery threshold. |
| `BROWSER_PROFILE_BACKUP_ENABLED` | `True` | Enables profile zip backup APIs. |
| `BROWSER_PROFILE_MAX_BACKUPS` | `3` | Maximum retained backups per profile. |
| `BROWSER_PROFILE_UNUSED_DAYS` | `30` | Unused profile cleanup age threshold. |
| `BROWSER_PROFILE_BACKUP_ROOT` | `worker/profile_backups` | Profile backup zip storage root. |
| `BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS` | `900` | Human-in-the-loop browser control timeout. |
| `BROWSER_UI_ACCESS_TIMEOUT_SECONDS` | `900` | Browser UI Access Placeholder token expiry timeout. |
| `BROWSER_WORKER_AUTH_ENABLED` | `True` | Enables Browser Worker signed-request authentication plumbing. |
| `BROWSER_WORKER_AUTH_STRICT` | `False` | Local development mode accepts unsigned worker runtime calls when no shared secret is configured. |
| `BROWSER_ALLOWED_DOMAINS` | `example.com,localhost,127.0.0.1` | Default allowed browser navigation domains. |
| `BROWSER_BLOCKED_DOMAINS` | `` | Optional blocked browser navigation domains. |
| `BROWSER_ALLOW_EXTERNAL_DOMAINS` | `False` | Default policy blocks arbitrary external browser navigation. |
| `BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS` | `30.0` | Remote Browser Worker client timeout. |
| `BROWSER_WORKER_RETRY_COUNT` | `2` | Remote Browser Worker client retry count. |
| `BROWSER_WORKER_DEFAULT_URL` | `http://browser-worker:9100` | Default Docker network URL for the independent Phase 20 `browser-worker` service. |
| `BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS` | `60` | Worker heartbeat staleness threshold. |
| `BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS` | `30` | Intended worker health monitor interval. |
| `BROWSER_SESSION_TIMEOUT_SECONDS` | `1800` | Browser session stale timeout used by cleanup. |
| `BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS` | `300` | Intended browser session cleanup interval. |
| `BROWSER_ACTION_TIMEOUT_SECONDS` | `60.0` | Remote browser action timeout. |
| `BROWSER_ACTION_RETRY_COUNT` | `2` | Remote browser action retry count. |
| `BROWSER_ACTION_RETRY_BACKOFF_SECONDS` | `2.0` | Remote browser action retry backoff seconds. |
| `SCREENSHOT_RETENTION_DAYS` | `7` | Default screenshot cleanup retention. |

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

## Task Reliability Runtime

Phase 12 does not add new environment variables. It adds runtime tables and APIs:

- `task_events`
- `task_logs`
- `tasks.duration_ms`
- `POST /api/v1/tasks/{task_id}/cancel`
- `POST /api/v1/tasks/{task_id}/retry`
- `GET /api/v1/tasks/{task_id}/events`
- `GET /api/v1/tasks/{task_id}/logs`
- `GET /api/v1/observability/summary`

Supported task status values:

```text
pending
running
retry
failed
completed
cancelled
timeout
```

All task control, events, logs, and summary APIs require `X-Workspace-Id`.

## Tool Calling Runtime

Phase 13 does not add new environment variables. Tool Calling is enabled through code-level builtin registration.

Runtime table:

- `tool_call_logs`

Core APIs:

- `GET /api/v1/tools`
- `GET /api/v1/tools/{tool_name}`
- `POST /api/v1/tools/{tool_name}/execute`
- `GET /api/v1/tool-calls`

Builtin tools:

| Tool | Status | Scope |
| --- | --- | --- |
| `rag_search_tool` | completed | Calls current Hybrid Search + Reranker. |
| `file_search_tool` | completed | Queries `documents` metadata inside the current workspace. |
| `create_task_tool` | completed | Creates a task in the current workspace. |
| `get_task_status_tool` | completed | Reads task status in the current workspace. |
| `current_runtime_tool` | completed | Returns provider/search/upload settings and reads `CURRENT_RUNTIME.md` when available. |

All tool execution and tool call log APIs require `X-Workspace-Id`.

Current limitations:

- `browser_tool` is available and can use the configured BrowserProvider.
- No OpenClaw, Selenium, or external API tools.
- No autonomous planner, ReAct loop, or LLM-native function calling.
- Tool enable/disable and permission scopes exist at Registry level, but no management API or full RBAC is implemented yet.

## Memory Runtime

Phase 14 does not add new environment variables. Memory is enabled through the backend service and database tables.

Runtime tables:

- `conversation_sessions`
- `conversation_messages`
- `agent_memories`
- `memory_operation_logs`

Core APIs:

- `POST /api/v1/memory/sessions`
- `GET /api/v1/memory/sessions`
- `GET /api/v1/memory/sessions/{session_id}`
- `POST /api/v1/memory/messages`
- `GET /api/v1/memory/messages/{session_id}`
- `POST /api/v1/memory/memories`
- `GET /api/v1/memory/memories`
- `DELETE /api/v1/memory/memories/{memory_id}`

Supported message roles:

```text
system
user
assistant
tool
```

Supported memory types:

```text
short_term
long_term
task_memory
retrieval_memory
```

Current memory retrieval uses PostgreSQL text matching over `agent_memories.content`. Agentic RAG `debug=true` now returns `session_id`, `recent_messages_count`, `retrieved_memories_count`, `recent_messages`, `retrieved_memories`, and `memory_trace`.

Current limitations:

- No vector memory.
- No graph memory.
- No autonomous memory planning.
- No personality memory.
- `summarize_session` is a lightweight deterministic text summary and does not call an LLM.

## Multi-Agent Runtime

Phase 15 does not add new environment variables. Multi-Agent is enabled through code-level `AgentRegistry` registration and database-backed run tracking.

Runtime tables:

- `agent_runs`
- `agent_messages`
- `agent_handoffs`

Core APIs:

- `GET /api/v1/agents/registry`
- `POST /api/v1/multi-agent/runs`
- `GET /api/v1/multi-agent/runs`
- `GET /api/v1/multi-agent/runs/{run_id}`
- `POST /api/v1/multi-agent/runs/{run_id}/execute-chain`
- `GET /api/v1/multi-agent/runs/{run_id}/messages`
- `GET /api/v1/multi-agent/runs/{run_id}/handoffs`

Registered agents:

| Agent | Status | Runtime role |
| --- | --- | --- |
| `content_planner` | completed foundation | Lightweight mock planner for content chain inputs. |
| `rag_agent` | completed foundation | Wraps `AgenticRAGOrchestrator`. |
| `content_agent` | completed foundation | Wraps `ContentAgent`. |
| `review_agent` | completed foundation | Lightweight mock reviewer. |
| `runtime_agent` | completed foundation | Reads runtime information through `current_runtime_tool`. |
| `tool_agent` | completed foundation | Calls existing `ToolRegistry` builtin tools. |

Current fixed Agent Chain:

```text
content_planner
-> rag_agent
-> content_agent
-> review_agent
```

All Multi-Agent APIs require `X-Workspace-Id`. `X-User-Id` is optional and is stored on `agent_runs.user_id` when provided.

Current limitations:

- No autonomous planner.
- No ReAct loop.
- No Browser Agent.
- No Playwright, OpenClaw, Selenium, or external platform automation.
- Agent enable/disable is currently code-level registry state, not a management API.

## Planning Runtime

Phase 16 does not add new environment variables. Planning is enabled through `SimplePlannerAgent`, `PlanningService`, `AgentRegistry`, and `ToolRegistry`.

Runtime tables:

- `plans`
- `plan_steps`
- `plan_reviews`

Core APIs:

- `POST /api/v1/plans`
- `GET /api/v1/plans`
- `GET /api/v1/plans/{plan_id}`
- `POST /api/v1/plans/{plan_id}/execute`
- `POST /api/v1/plans/{plan_id}/cancel`
- `GET /api/v1/plans/{plan_id}/steps`
- `GET /api/v1/plans/{plan_id}/reviews`

Supported plan status values:

```text
pending
planning
executing
completed
failed
cancelled
```

Supported plan step status values:

```text
pending
running
completed
failed
skipped
```

Current Plan Execution Flow:

```text
SimplePlannerAgent
-> plans / plan_steps
-> AgentRegistry or ToolRegistry
-> step output / duration_ms / error
-> plan_reviews
-> plan status + memory_trace
```

Current limitations:

- Planning is rule-based only.
- No autonomous AGI planner.
- No tree-of-thought.
- No recursive planning.
- No infinite Agent loop.
- No ReAct.
- No Browser Agent, Playwright, OpenClaw, Selenium, or external platform automation.

## Browser Runtime

Phase 17 adds Browser Automation Adapter Foundation. Phase 18 adds `PlaywrightLocalProvider` for bounded local Chromium execution.
Phase 19 adds `RemoteBrowserProvider` and the in-project Remote Browser Worker mock runtime.
Phase 20 adds a real independent `browser-worker` FastAPI service backed by Playwright Chromium.
Phase 21 adds Browser Worker Reliability: health monitoring, capacity tracking, least loaded worker selection, stale session cleanup, action retry, and manual screenshot cleanup.
Phase 22 adds Persistent Browser Profile Foundation: `browser_profiles`, profile lock/release, session profile binding, and worker-side `launch_persistent_context`.
Phase 23 adds Browser Profile Health & Recovery: `BrowserProfileHealthService`, `BrowserProfileBackupService`, `BrowserProfileCleanupService`, `browser_profile_usage_logs`, health fields, `health/summary`, stale lock recovery, profile backup, and profile cleanup.
Phase 24 adds Human-in-the-loop Browser Control: `BrowserHumanControlService`, `browser_human_control_sessions`, `browser_human_control_events`, session paused/resumed fields, worker metadata-level `/human-control/*` routes, and `browser_tool` actions `request_human_control` / `complete_human_control`.
Phase 25 adds Browser Worker UI Access Placeholder: `BrowserUIAccessService`, `browser_ui_access_sessions`, access token hash storage, placeholder URL generation, `/ui-access/capabilities`, and `browser_tool` actions `create_ui_access` / `revoke_ui_access`. It does not provide real VNC, noVNC, DevTools UI, live browser video, login, captcha handling, or platform automation.
Phase 26 adds Browser Worker Security & Access Control: `BrowserWorkerAuthService`, signed worker request headers, worker secret hash storage, UI Access Scope validation, `BrowserActionPolicyService`, `BrowserSecurityAuditLog`, and `browser_security_audit_logs`. It does not provide real social-platform account security, login, proxy, fingerprint, captcha, or platform automation.
Phase 27 adds Customer Machine Worker Bootstrap through the local `worker_client` package. It does not add new API Server environment variables; it adds customer-machine config, CLI, registration, heartbeat, and local runtime behavior.

Runtime setting:

```text
BROWSER_PROVIDER=mock
BROWSER_TIMEOUT_SECONDS=30.0
BROWSER_HEADLESS=True
BROWSER_TYPE=chromium
BROWSER_VIEWPORT_WIDTH=1280
BROWSER_VIEWPORT_HEIGHT=720
BROWSER_SCREENSHOT_DIR=screenshots
BROWSER_PROFILE_ROOT=worker/profiles
BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS=1800
BROWSER_PROFILE_BACKUP_ENABLED=True
BROWSER_PROFILE_MAX_BACKUPS=3
BROWSER_PROFILE_UNUSED_DAYS=30
BROWSER_PROFILE_BACKUP_ROOT=worker/profile_backups
BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS=900
BROWSER_UI_ACCESS_TIMEOUT_SECONDS=900
BROWSER_WORKER_AUTH_ENABLED=True
BROWSER_WORKER_AUTH_STRICT=False
BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1
BROWSER_BLOCKED_DOMAINS=
BROWSER_ALLOW_EXTERNAL_DOMAINS=False
BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30.0
BROWSER_WORKER_RETRY_COUNT=2
BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100
BROWSER_WORKER_AUTH_ENABLED=true
BROWSER_WORKER_AUTH_STRICT=false
BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1
BROWSER_BLOCKED_DOMAINS=
BROWSER_ALLOW_EXTERNAL_DOMAINS=false
BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS=60
BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS=30
BROWSER_SESSION_TIMEOUT_SECONDS=1800
BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS=300
BROWSER_ACTION_TIMEOUT_SECONDS=60.0
BROWSER_ACTION_RETRY_COUNT=2
BROWSER_ACTION_RETRY_BACKOFF_SECONDS=2.0
SCREENSHOT_RETENTION_DAYS=7
```

Phase 20 worker service runtime:

```text
WORKER_HOST=0.0.0.0
WORKER_PORT=9100
WORKER_TIMEOUT_SECONDS=30
WORKER_HEADLESS=true
WORKER_BROWSER_TYPE=chromium
WORKER_SCREENSHOT_DIR=worker/screenshots
WORKER_PROFILE_DIR=worker/profiles
WORKER_VIEWPORT_WIDTH=1280
WORKER_VIEWPORT_HEIGHT=720
BROWSER_WORKER_PORT=9100
```

Runtime tables:

- `browser_sessions`
- `browser_actions`
- `browser_action_logs`
- `browser_profiles`
- `browser_profile_usage_logs`

Core APIs:

- `POST /api/v1/browser/sessions`
- `POST /api/v1/browser/sessions/{session_id}/close`
- `POST /api/v1/browser/profiles`
- `GET /api/v1/browser/profiles`
- `POST /api/v1/browser/profiles/recover-stale-locks`
- `POST /api/v1/browser/profiles/cleanup`
- `GET /api/v1/browser/profiles/health/summary`
- `GET /api/v1/browser/profiles/{profile_id}`
- `POST /api/v1/browser/profiles/{profile_id}/health-check`
- `POST /api/v1/browser/profiles/{profile_id}/backup`
- `GET /api/v1/browser/profiles/{profile_id}/backups`
- `POST /api/v1/browser/profiles/{profile_id}/restore`
- `GET /api/v1/browser/profiles/{profile_id}/usage-logs`
- `POST /api/v1/browser/profiles/{profile_id}/lock`
- `POST /api/v1/browser/profiles/{profile_id}/release`
- `DELETE /api/v1/browser/profiles/{profile_id}`
- `POST /api/v1/browser/human-control/request`
- `GET /api/v1/browser/human-control`
- `GET /api/v1/browser/human-control/{control_session_id}`
- `POST /api/v1/browser/human-control/{control_session_id}/approve`
- `POST /api/v1/browser/human-control/{control_session_id}/start`
- `POST /api/v1/browser/human-control/{control_session_id}/complete`
- `POST /api/v1/browser/human-control/{control_session_id}/cancel`
- `GET /api/v1/browser/human-control/{control_session_id}/events`
- `POST /api/v1/browser/ui-access`
- `GET /api/v1/browser/ui-access/{access_session_id}`
- `POST /api/v1/browser/ui-access/{access_session_id}/revoke`
- `POST /api/v1/browser/ui-access/expire`
- `GET /api/v1/browser/ui-access/{access_session_id}/validate`
- `GET /api/v1/browser/sessions`
- `POST /api/v1/browser/actions`
- `GET /api/v1/browser/actions/{session_id}`
- `GET /api/v1/browser/screenshot/{session_id}/{filename}`
- `GET /api/v1/browser/logs/{session_id}`
- `POST /api/v1/browser-workers/register`
- `POST /api/v1/browser-workers/{worker_id}/heartbeat`
- `GET /api/v1/browser-workers`
- `GET /api/v1/browser-workers/health/summary`
- `GET /api/v1/browser-workers/available`
- `POST /api/v1/browser-workers/{worker_id}/mark-offline`
- `POST /api/v1/browser-workers/cleanup-sessions`
- `GET /api/v1/browser-workers/{worker_id}/sessions`
- `POST /api/v1/browser/screenshots/cleanup`
- `GET /api/v1/browser-worker-runtime/health`
- `POST /api/v1/browser-worker-runtime/sessions`
- `POST /api/v1/browser-worker-runtime/actions`
- `POST /api/v1/browser-worker-runtime/sessions/{session_id}/close`
- `POST /api/v1/browser-worker-runtime/human-control/start`
- `POST /api/v1/browser-worker-runtime/human-control/complete`
- `GET /api/v1/browser-worker-runtime/human-control/status/{session_id}`
- `GET /api/v1/browser-worker-runtime/ui-access/capabilities`

Current browser provider state:

- `MockBrowserProvider` is completed and active by default.
- `PlaywrightBrowserProvider` is a placeholder only.
- `PlaywrightLocalProvider` is completed for local Chromium smoke tests through `BROWSER_PROVIDER=playwright_local`.
- `RemoteBrowserProvider` is completed as a protocol foundation through `BROWSER_PROVIDER=remote`.
- `BrowserWorkerClient` dispatches to registered worker `base_url` values.
- `Worker Runtime Mock` is available inside this API process at `/api/v1/browser-worker-runtime`.
- `browser_tool` can execute `navigate`, `click`, `type_text`, `screenshot`, `get_page_content`, `request_human_control`, `complete_human_control`, `create_ui_access`, and `revoke_ui_access` through the configured provider/services.
- Planning steps can target `tool_name=browser_tool`.

Playwright local runtime fields:

- `browser_sessions.browser_id`
- `browser_sessions.page_id`
- `browser_sessions.profile_id`
- `browser_sessions.profile_path`
- `browser_sessions.persistent_context_enabled`
- `browser_sessions.provider_session_metadata`
- `browser_actions.selector`
- `browser_actions.target_url`
- `browser_actions.screenshot_path`
- `browser_actions.page_title`

Screenshot System:

```text
screenshots/{workspace_id}/{session_id}/{filename}.png
```

Persistent Profile System:

```text
browser_profiles
-> profile_id / profile_path
-> Profile Lock by locked_by_session_id
-> BrowserSession persistent_context_enabled=true
-> browser-worker launch_persistent_context
-> worker/profiles/{workspace_id}/{profile_id}
-> Profile Release on session close
```

Phase 23 health fields:

```text
health_status
last_health_check_at
last_error
usage_count
corrupted_at
backup_path
last_backup_at
browser_profile_usage_logs
```

Phase 23 services:

```text
BrowserProfileHealthService
BrowserProfileBackupService
BrowserProfileCleanupService
stale lock recovery
profile backup
profile cleanup
```

Phase 24 human control fields:

```text
browser_human_control_sessions
browser_human_control_events
human_control_status
human_control_session_id
paused_at
resumed_at
```

Phase 24 service and actions:

```text
BrowserHumanControlService
request_human_control
complete_human_control
BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS
```

Phase 25 UI access fields:

```text
browser_ui_access_sessions
access_token_hash
scopes
one_time
used_at
revoked_reason
client_ip
user_agent
remote_control_url
live_view_url
devtools_url
BROWSER_UI_ACCESS_TIMEOUT_SECONDS
```

Phase 25 service and actions:

```text
BrowserUIAccessService
create_ui_access
revoke_ui_access
access token hash
placeholder URL
```

Phase 26 Browser Worker Security fields:

```text
worker_secret_hash
api_key_hash
last_auth_at
auth_status
allowed_actions
allowed_domains
browser_security_audit_logs
BrowserSecurityAuditLog
```

Phase 26 services and policy:

```text
BrowserWorkerAuthService
signed worker request
X-Worker-Signature
X-Worker-Timestamp
X-Worker-Nonce
BrowserActionPolicyService
UI Access Scope
BROWSER_WORKER_AUTH_ENABLED=True
BROWSER_WORKER_AUTH_STRICT=False
BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1
BROWSER_BLOCKED_DOMAINS=
BROWSER_ALLOW_EXTERNAL_DOMAINS=False
```

Phase 27 Worker Client runtime:

```text
worker_client
worker_config.example.yaml
worker_config.yaml
worker_state.json
python -m worker_client.cli register
python -m worker_client.cli heartbeat
python -m worker_client.cli serve
python -m worker_client.cli start
registration flow
heartbeat flow
local worker runtime
```

`worker_client/worker_config.example.yaml` defaults:

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
```

Security note: `worker_state.json` stores the customer-machine plaintext `worker_secret` locally because the server returns it only once. It is ignored by Git and must not be committed or printed in logs. The client sends heartbeat with `X-Worker-Secret` plus signed request headers from Phase 26.

Profile status values:

```text
available
locked
disabled
corrupted
deleted
```

Profile health status values:

```text
healthy
warning
corrupted
stale
deleted
```

Playwright safety boundary:

- Allowed: `example.com`, local test pages, static `file://` URLs.
- Not allowed: TikTok, YouTube, X, automatic login, cookie injection, fingerprint bypass, proxy pools, captcha automation, OCR, visual AI, autonomous browser planning, or remote Browser Worker execution.

Remote Browser Worker tables:

- `browser_workers`
- `browser_worker_sessions`
- `browser_worker_actions`

Phase 21 worker reliability fields:

- `browser_workers.max_sessions`
- `browser_workers.active_sessions`
- `browser_workers.max_actions_per_minute`
- `browser_workers.current_load`
- `browser_workers.priority`
- `browser_workers.error_message`
- `browser_workers.last_heartbeat_at` is exposed as `last_seen`
- `browser_worker_actions.retry_count`
- `browser_worker_actions.max_retries`

Reliability services:

- `BrowserWorkerHealthService`
- `BrowserWorkerSelector`
- `BrowserSessionCleanupService`
- `ScreenshotCleanupService`

Selection flow:

```text
workspace_id
-> online workers
-> capability filter
-> active_sessions < max_sessions
-> least loaded worker by current_load / active_sessions / priority
```

Cleanup flow:

```text
stale worker -> offline + error_message
stale session -> closed
offline/error worker session -> failed
screenshot cleanup -> dry_run by default
```

Remote Browser Worker status values:

```text
online
offline
busy
error
```

Remote mode:

```env
BROWSER_PROVIDER=remote
BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30
BROWSER_WORKER_RETRY_COUNT=2
BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100
BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS=60
BROWSER_ACTION_TIMEOUT_SECONDS=60
BROWSER_ACTION_RETRY_COUNT=2
BROWSER_ACTION_RETRY_BACKOFF_SECONDS=2
SCREENSHOT_RETENTION_DAYS=7
```

Real Browser Worker Service:

```text
API Server
-> RemoteBrowserProvider
-> BrowserWorkerClient
-> http://browser-worker:9100
-> worker/main.py
-> worker/browser_worker/playwright_runtime.py
-> Playwright Chromium
-> worker/screenshots/{workspace_id}/{remote_session_id}/{filename}.png
```

The worker exposes:

```http
GET http://localhost:9100/health
POST http://localhost:9100/sessions
POST http://localhost:9100/actions
POST http://localhost:9100/sessions/{session_id}/close
```

The API Server still uses the database-backed registration flow. Register the worker with:

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

Remote worker safety boundary:

- Current runtime now includes an independent local Docker `browser-worker` service.
- The old in-process mock worker runtime remains available for protocol tests.
- Production external worker fleets, worker scheduling, autoscaling, and remote machine deployment are not included.
- No TikTok, YouTube, X, automatic login, cookie injection, fingerprint bypass, proxy pool, captcha automation, OCR, visual AI, or autonomous browser planning.

Current limitations:

- Real browser execution is limited to `PlaywrightLocalProvider` and bounded test pages.
- No Selenium, OpenClaw, TikTok, YouTube, X, OCR, visual AI, login automation, or real platform automation.
- No autonomous browser agent or browser planning loop.

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
GET /api/v1/observability/summary
GET /api/v1/tools
GET /api/v1/tool-calls
POST /api/v1/memory/sessions
POST /api/v1/memory/messages
POST /api/v1/memory/memories
GET /api/v1/agents/registry
POST /api/v1/multi-agent/runs
POST /api/v1/multi-agent/runs/{run_id}/execute-chain
POST /api/v1/plans
POST /api/v1/plans/{plan_id}/execute
GET /api/v1/plans/{plan_id}/steps
GET /api/v1/plans/{plan_id}/reviews
GET http://localhost:9100/health
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
BROWSER_PROVIDER=mock
BROWSER_TIMEOUT_SECONDS=30.0
BROWSER_HEADLESS=True
BROWSER_TYPE=chromium
BROWSER_VIEWPORT_WIDTH=1280
BROWSER_VIEWPORT_HEIGHT=720
BROWSER_SCREENSHOT_DIR=screenshots
BROWSER_PROFILE_ROOT=worker/profiles
BROWSER_WORKER_AUTH_ENABLED=true
BROWSER_WORKER_AUTH_STRICT=false
BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1
BROWSER_BLOCKED_DOMAINS=
BROWSER_ALLOW_EXTERNAL_DOMAINS=false
BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30
BROWSER_WORKER_RETRY_COUNT=2
BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100
BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS=60
BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS=30
BROWSER_SESSION_TIMEOUT_SECONDS=1800
BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS=300
BROWSER_ACTION_TIMEOUT_SECONDS=60
BROWSER_ACTION_RETRY_COUNT=2
BROWSER_ACTION_RETRY_BACKOFF_SECONDS=2
SCREENSHOT_RETENTION_DAYS=7
```

Restart:

```powershell
docker compose up --build -d
```

To test Playwright local mode:

```env
BROWSER_PROVIDER=playwright_local
BROWSER_TIMEOUT_SECONDS=30
BROWSER_HEADLESS=true
BROWSER_TYPE=chromium
BROWSER_VIEWPORT_WIDTH=1280
BROWSER_VIEWPORT_HEIGHT=720
BROWSER_SCREENSHOT_DIR=screenshots
BROWSER_PROFILE_ROOT=worker/profiles
```

Restart with Docker Compose and smoke test `POST /api/v1/browser/sessions`, `POST /api/v1/browser/actions` with `navigate` to `https://example.com`, `screenshot`, `get_page_content`, and `GET /api/v1/browser/screenshot/{session_id}/{filename}`.

## Switching Back to Mock

```env
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
BROWSER_PROVIDER=mock
BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30
BROWSER_WORKER_RETRY_COUNT=2
BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100
BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS=60
BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS=30
BROWSER_SESSION_TIMEOUT_SECONDS=1800
BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS=300
BROWSER_ACTION_TIMEOUT_SECONDS=60
BROWSER_ACTION_RETRY_COUNT=2
BROWSER_ACTION_RETRY_BACKOFF_SECONDS=2
SCREENSHOT_RETENTION_DAYS=7
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
