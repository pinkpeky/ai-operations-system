# Current Runtime

Last updated: 2026-05-19

This document records the current real runtime defaults for `E:\ai-operations-system`. Values are based on `app/core/config.py`, `.env.example`, and `docker-compose.yml`.

The repository currently has no committed `.env` file. Without local overrides, the application uses the defaults below.

## Commercial Operations Runtime

Phase 61A added the `commercial_operations` table, `CommercialOperationService`, and `/api/v1/commercial-operations` route group. These APIs are workspace-scoped and create reviewable plan outlines only.

Phase 61B adds `commercial_operation_links` and `/api/v1/commercial-operations/{operation_id}/links` so operators can attach evidence and handoff references to an operation. Supported link categories are `conversation`, `artifact`, `task_run`, `workflow_run`, `rag_document`, `knowledge_source`, `approval`, and `external`.

Phase 61C adds `commercial_operation_approvals` and `/api/v1/commercial-operations/{operation_id}/approvals` so operators can request, approve, reject, or cancel human approval for a specific operation plan step. Approval decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61D adds `commercial_operation_dry_runs` and `/api/v1/commercial-operations/{operation_id}/dry-runs` so operators can create, complete, fail, or cancel metadata-only dry-run records from approved approval gates. Dry-run decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61E adds `commercial_operation_content_drafts` and `/api/v1/commercial-operations/{operation_id}/content-drafts` so operators can create, edit, send for review, approve, reject, or archive per-channel content drafts. Draft decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61F adds `commercial_operation_asset_requests` and `/api/v1/commercial-operations/{operation_id}/asset-requests` so operators can create, edit, send for review, approve, reject, prepare, fail, or archive first-class asset requests linked to an operation and optionally a content draft. Asset request decisions are reflected back into `plan_outline` metadata for operator visibility.

Commercial operations still do not publish, execute OpenClaw actions, run Browser Worker actions, run ComfyUI jobs, control real accounts, or bypass approval.

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
| `BROWSER_RUNTIME_SCREENSHOT_DIR` | `storage/browser_screenshots` | Phase 34 remote browser runtime screenshot storage root. |
| `BROWSER_RUNTIME_SNAPSHOT_DIR` | `storage/browser_runtime_snapshots` | Phase 35A page/text/error/replay metadata snapshot storage root. |
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
| `OPENCLAW_PROVIDER` | `mock` | OpenClaw worker adapter provider. Current default is mock only. |
| `OPENCLAW_ENABLED` | `True` | Enables the OpenClaw adapter foundation APIs and tool. |
| `OPENCLAW_ACTION_TIMEOUT_SECONDS` | `60.0` | Timeout for OpenClaw worker runtime calls. |

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
| `openclaw_tool` | completed foundation | Calls the mock OpenClaw worker adapter through registered Browser Workers. |

All tool execution and tool call log APIs require `X-Workspace-Id`.

Current limitations:

- `browser_tool` is available and can use the configured BrowserProvider.
- `openclaw_tool` is available as a mock/placeholder worker adapter only; it does not call real OpenClaw.
- No Selenium or external API tools.
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
Phase 28 adds OpenClaw Worker Adapter Foundation: `worker_client/openclaw`, `BaseOpenClawProvider`, `MockOpenClawProvider`, `OpenClawRuntime`, server-side `OpenClawWorkerClient`, `openclaw_tool`, `openclaw_action_logs`, and `/api/v1/openclaw/*` APIs. It is mock/placeholder only and does not call real OpenClaw or perform platform automation.

Runtime setting:

```text
BROWSER_PROVIDER=mock
BROWSER_TIMEOUT_SECONDS=30.0
BROWSER_HEADLESS=True
BROWSER_TYPE=chromium
BROWSER_VIEWPORT_WIDTH=1280
BROWSER_VIEWPORT_HEIGHT=720
BROWSER_SCREENSHOT_DIR=screenshots
BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
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
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=True
OPENCLAW_ACTION_TIMEOUT_SECONDS=60.0
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
- `GET /api/v1/browser-worker-runtime/openclaw/health`
- `GET /api/v1/browser-worker-runtime/openclaw/capabilities`
- `POST /api/v1/browser-worker-runtime/openclaw/actions`
- `GET /api/v1/openclaw/health`
- `GET /api/v1/openclaw/capabilities`
- `POST /api/v1/openclaw/actions`

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

Phase 28 OpenClaw Worker Adapter runtime:

```text
worker_client/openclaw
BaseOpenClawProvider
MockOpenClawProvider
OpenClawRuntime
OpenClawWorkerClient
openclaw_tool
openclaw_action_logs
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=True
OPENCLAW_ACTION_TIMEOUT_SECONDS=60.0
```

OpenClaw flow:

```text
API Server / openclaw_tool
-> OpenClawService
-> BrowserWorkerSelector capability=openclaw
-> OpenClawWorkerClient
-> worker_client /openclaw/* mock runtime
-> openclaw_action_logs + browser_security_audit_logs
```

`worker_client/worker_config.example.yaml` defaults:

```yaml
server_url: http://localhost:8000
worker_name: local-windows-worker-1
worker_type: playwright
workspace_id: demo-workspace
worker_secret: null
worker_base_url: http://localhost:9100
runtime_host: 127.0.0.1
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
- `openclaw_action_logs`

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
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=true
OPENCLAW_ACTION_TIMEOUT_SECONDS=60
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
GET /api/v1/openclaw/health
GET /api/v1/openclaw/capabilities
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
BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
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
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=true
OPENCLAW_ACTION_TIMEOUT_SECONDS=60
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
BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
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
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=true
OPENCLAW_ACTION_TIMEOUT_SECONDS=60
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

## Phase 29 Worker Client Local Runtime

Current customer-machine Worker Client defaults:

```text
worker_client runtime_host=127.0.0.1
worker_client runtime_port=9100
worker_client status=worker_client/runtime_state/status.json
worker_client logs=worker_client/logs/worker.log
```

Completed Phase 29 runtime files:

- `Worker Runtime Manager`: `worker_client/runtime_manager.py`
- local status: `worker_client/status.py`
- local logging: `worker_client/logging.py`
- local API client: `worker_client/local_api_client.py`
- status file: `worker_client/runtime_state/status.json`
- log file: `worker_client/logs/worker.log`
- packaging scripts: `packaging/windows_start_worker.ps1`, `packaging/mac_start_worker.sh`
- desktop placeholder: `worker_client/desktop/README.md`

Local management API exposed by `worker_client.runtime`:

- `GET /local/status`
- `GET /local/health`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`
- `GET /local/logs`

Phase 29 is `Worker Console Foundation` only: no GUI, no Electron, no Tauri, no PySide, no system tray, no EXE/DMG packaging, and no real platform automation.

## Phase 30 Worker Console Runtime

Worker Console frontend defaults:

```text
worker_console stack=Vite + React + TypeScript + Tailwind
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
worker_console dev_url=http://localhost:5173
```

Runtime relationship:

- `worker_console` calls the local Worker Client API from Phase 29.
- Default local status URL: `http://127.0.0.1:9100/local/status`.
- Frontend client: `worker_console/src/api/localWorkerClient.ts`.
- If the API is down, the UI shows `Worker API unreachable`, `请确认 worker_client 是否启动`, and `请确认端口是否为 9100`.

Current boundary: Worker Console GUI Foundation only; no system tray, no auto update, no Electron, no Tauri, no PySide, no exe / dmg packaging.

## Phase 31 Worker Console Desktop Runtime

Worker Console Desktop defaults:

```text
worker_console_desktop stack=Tauri + React + Vite + TypeScript + Tailwind
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
worker_console_desktop dev_url=http://127.0.0.1:5174
worker_console_desktop status_url=http://127.0.0.1:9100/local/status
```

Runtime relationship:

- `worker_console_desktop` calls the same local Worker Client API as `worker_console`.
- Desktop local API client: `worker_console_desktop/src/api/localWorkerClient.ts`.
- Tauri config: `worker_console_desktop/src-tauri/tauri.conf.json`.
- Development command: `npm run tauri dev`.
- Frontend validation command: `npm run build`.
- If the local Worker API is down, the UI shows `Worker API unreachable`, `Worker Runtime 未启动`, `请先启动 worker_client`, and `packaging 脚本启动`.

Current boundary: Worker Console Desktop App Foundation only; no exe / dmg, no system tray, no auto update, no autostart, and no formal installer release.

## Phase 32 Worker Console System Tray & Desktop Runtime Foundation

Worker Console Desktop runtime defaults:

```text
worker_console_desktop stack=Tauri System Tray + React + Vite + TypeScript + Tailwind
localWorkerApi=http://127.0.0.1:9100
minimizeToTray=true
refreshIntervalMs=5000
desktop_runtime_config=worker_console_desktop/src-tauri/desktop-runtime.json
settings_example=worker_console_desktop/settings.example.json
```

Runtime behavior:

- System Tray menu: Show Console, Hide Window, Start Runtime, Stop Runtime, Restart Runtime, Start Heartbeat, Stop Heartbeat, Refresh Status, Quit.
- Minimize To Tray: closing the window hides it instead of exiting.
- Tray Runtime Control calls only local Worker Client API endpoints.
- Desktop Status Sync calls `GET /local/status` and `GET /local/health`.
- Tooltip fields: `worker_name`, `current_status`, `runtime_running`, `heartbeat_running`.
- Connection states shown in UI: connected, reconnecting, disconnected, online, offline, error.
- AutoStart Placeholder docs exist, but no real start-on-login registration is performed.

Current boundary: no formal installer, no exe / dmg, no real autostart registration, no auto-update, no remote shell, and no arbitrary command execution.

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

## Phase 34 Remote Browser Runtime

Remote Browser Runtime adds one runtime storage setting and keeps the existing browser safety boundaries.

```text
BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
```

Current runtime behavior:

- API Server dispatches browser runtime actions through `RemoteBrowserProvider`.
- Remote worker browser runtime lives under `worker_client/browser_runtime`.
- Worker runtime API uses `/browser/session/create`, `/browser/session/{session_id}/navigate`, `/browser/session/{session_id}/screenshot`, `/browser/session/{session_id}/page`, and `/browser/session/{session_id}/close`.
- Runtime sessions are stored in `browser_runtime_sessions`.
- Screenshots are stored locally under `storage/browser_screenshots`.
- Customer machines must install Playwright Chromium with `playwright install chromium`.

Current boundary: no stealth browser, no proxy rotation, no cookie injection, no captcha bypass, no TikTok / YouTube / X automation, no remote desktop streaming, and no DevTools remote control.

## Phase 35A Browser Runtime Observability & Replay

Phase 35A adds runtime observability storage and APIs. It does not add live streaming, VNC/noVNC, DevTools remote control, or replay re-execution.

Runtime setting:

```text
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
```

Runtime tables:

- `browser_runtime_events`
- `browser_runtime_snapshots`
- `browser_runtime_replays`

Runtime APIs:

- `GET /api/v1/browser-runtime/sessions/{session_id}/events`
- `GET /api/v1/browser-runtime/sessions/{session_id}/snapshots`
- `POST /api/v1/browser-runtime/sessions/{session_id}/replay`
- `GET /api/v1/browser-runtime/replays/{replay_id}`
- `GET /api/v1/browser-runtime/replays/{replay_id}/export`

Storage:

```text
storage/browser_runtime_snapshots/{workspace_id}/{session_id}/page-{snapshot_id}.html
storage/browser_runtime_snapshots/{workspace_id}/{session_id}/page-{snapshot_id}.txt
storage/browser_runtime_snapshots/{workspace_id}/{session_id}/error-{snapshot_id}.json
storage/browser_runtime_snapshots/{workspace_id}/{session_id}/replay-{replay_id}.json
```

Timeline events include `session_created`, `navigate_started`, `navigate_completed`, `screenshot_started`, `screenshot_completed`, `page_snapshot_captured`, `action_failed`, `session_closed`, and `replay_requested`.

Replay is metadata-only. It exports readable timeline and snapshot references; it does not re-run browser actions.

## Phase 35B Real Client Worker E2E Runtime Notes

Phase 35B adds no new service environment variable. It adds `scripts/validate_real_client_worker_e2e.py`, a validation script that checks whether a real customer-machine worker is online before executing browser actions.

Runtime facts:

```text
Expected remote worker capability: browser_runtime=true
Expected browser: chromium
Expected test domain: example.com
Screenshot directory: BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
Snapshot directory: BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
```

If `BROWSER_PROVIDER` is not `remote`, the script prints a WARNING only. The browser runtime API is still directly testable, but legacy browser action APIs may continue to use the configured provider.

If the configured `expected_worker_name` is not online, the script returns `SKIPPED` with exit code `2` and reason `real client worker not online`. This is intentional because Phase 35B is a validation plan and script, not a fabricated real-client E2E result.

## Phase 36 Admin Dashboard Runtime

Phase 36 adds a frontend-only Admin Dashboard Foundation. It does not add new backend environment variables.

Frontend runtime config:

```text
VITE_AI_SERVER_API=http://localhost:8000
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

Runtime facts:

- Project path: `admin_dashboard`
- API client: `admin_dashboard/src/api/client.ts`
- Default AI Server URL: `http://localhost:8000`
- Required headers: `X-Workspace-Id` and `X-User-Id`
- Stored local settings: `aiServerUrl`, `workspaceId`, `userId`
- Auto refresh default: 10000 ms
- Pages: Overview, Workers, Browser Runtime, Conversations, Tasks, OpenClaw, Audit Logs, RAG / Documents, Settings
- API modules: `workersApi`, `browserRuntimeApi`, `conversationsApi`, `tasksApi`, `openclawApi`, `auditApi`, `ragApi`

The dashboard is a read-only monitoring foundation. It has no login UI, no permission UI, no publishing business flow, no real social platform control, and no production-grade operations backend.

## Phase 37 Conversation Frontend Runtime

Phase 37 adds no production authentication layer and no real streaming transport. It adds frontend configuration and development CORS for Conversation Runtime UI integration.

Frontend runtime defaults:

```text
VITE_AI_SERVER_API=http://localhost:8000
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

Backend CORS runtime:

```text
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:5180,http://127.0.0.1:5180,tauri://localhost
```

Conversation frontend API coverage:

```text
POST /api/v1/conversations
GET /api/v1/conversations
GET /api/v1/conversations/{thread_id}
POST /api/v1/conversations/{thread_id}/messages
GET /api/v1/conversations/{thread_id}/messages
GET /api/v1/conversations/{thread_id}/events
POST /api/v1/conversations/{thread_id}/run
```

Current mode: Polling Event Timeline only. The implementation is not WebSocket, not SSE, and not a full ChatGPT UI.

## Phase 38 Runtime: Conversation Tool Execution Bridge

Current bridge mode:
- `ConversationToolRouter`: enabled.
- Routing mode: deterministic rule-based routing, not autonomous agent planning.
- Tool bridge events: `route_selected`, `tool_execution_started`, `tool_execution_completed`, `tool_execution_failed`, `agent_execution_started`, `agent_execution_completed`, `planning_execution_started`, `planning_execution_completed`, `bridge_fallback`, `bridge_error`.
- Run response fields: `route_name`, `selected_tool`, `events_created`, `success`, `summary`, `result_metadata`.
- Browser bridge: uses `browser_tool` composite flow for create session, navigate, screenshot, get page, and close session when browser runtime is available.
- OpenClaw bridge: mock only through `openclaw_tool`; no real OpenClaw and no real device execution.
- RAG bridge: requires `collection_name` from thread metadata or run input.
- Content bridge: calls `ContentAgent`.
- Planning bridge: calls `PlanningService` to create a plan and steps.

Current limitations: not WebSocket, not SSE, not an autonomous agent, not real OpenClaw, not ComfyUI, and not real platform publishing.

## Phase 39 Runtime: Conversation Approval Flow

Current approval mode:
- `conversation_approvals`: enabled.
- `ConversationApprovalService`: enabled for create / approve / reject / cancel / execute state flow.
- `ConversationRiskPolicy`: enabled for `low`, `medium`, and `high` risk classification.
- Run modes: `auto_safe`, `review_first`, `execute_after_approval`.
- Default run mode: `auto_safe`.
- Tool Execution Gate: medium/high risk actions remain pending until approval; approved actions are executed through `POST /api/v1/conversation-approvals/{approval_id}/execute`.

Approval API coverage:

```text
GET /api/v1/conversations/{thread_id}/approvals
GET /api/v1/conversation-approvals/{approval_id}
POST /api/v1/conversation-approvals/{approval_id}/approve
POST /api/v1/conversation-approvals/{approval_id}/reject
POST /api/v1/conversation-approvals/{approval_id}/cancel
POST /api/v1/conversation-approvals/{approval_id}/execute
```

Approval event coverage:

```text
approval_required
approval_created
approval_approved
approval_rejected
approval_cancelled
approval_expired
approval_executed
execution_blocked_pending_approval
execution_after_approval_started
execution_after_approval_completed
execution_after_approval_failed
```

Current limitations: this is not a full permission system, not WebSocket/SSE streaming, not real platform publishing, not real OpenClaw, and not autonomous agent execution.
## Phase 40 Runtime Addendum: Conversation Playbooks

Current Playbook runtime is enabled in the API server and uses the existing Conversation Runtime, ToolRegistry, ContentAgent, PlanningService, browser_tool, rag_search_tool, and openclaw_tool mock bridge.

Database tables:
- `conversation_playbooks`
- `conversation_playbook_runs`

API routes:
- `GET /api/v1/conversation-playbooks`
- `GET /api/v1/conversation-playbooks/{playbook_id}`
- `POST /api/v1/conversation-playbooks`
- `PATCH /api/v1/conversation-playbooks/{playbook_id}`
- `POST /api/v1/conversation-playbooks/{playbook_id}/run`
- `GET /api/v1/conversation-playbook-runs`
- `GET /api/v1/conversation-playbook-runs/{run_id}`
- `POST /api/v1/conversation-playbook-runs/{run_id}/cancel`

Conversation run supports `playbook_name`, `playbook_run_id`, and `playbook_status`. Playbook steps still respect `review_first`, `auto_safe`, and `execute_after_approval`.

Current defaults remain unchanged: no real OpenClaw, no real social-platform publishing, no proxy/fingerprint/captcha handling, and no full workflow editor.

## Phase 41 Runtime Addendum: Output Library

Current Output Library runtime is enabled in the API server and stores reusable execution outputs in `output_artifacts`.

Storage:
- `OUTPUT_ARTIFACT_DIR=storage/output_artifacts`
- Exported markdown/json/txt files use `storage/output_artifacts/{workspace_id}/{artifact_id}/`
- Screenshot and HTML snapshot artifacts reference existing file paths; large files are not copied.

API routes:
- `GET /api/v1/output-artifacts`
- `GET /api/v1/output-artifacts/{artifact_id}`
- `PATCH /api/v1/output-artifacts/{artifact_id}`
- `DELETE /api/v1/output-artifacts/{artifact_id}`
- `POST /api/v1/output-artifacts/from-message/{message_id}`
- `POST /api/v1/output-artifacts/from-playbook-run/{run_id}`
- `GET /api/v1/output-artifacts/{artifact_id}/export`

Events:
- `artifact_created`
- `artifact_exported`
- `artifact_deleted`
- `artifact_linked_to_playbook_run`

Current boundaries remain unchanged: no S3, no MinIO, no full DAM, no production-grade file manager, no real platform publishing, and no social-platform automation.
## Phase 42 Runtime Configuration

Task Orchestration defaults are now part of runtime config and docker-compose:

- `TASK_ORCHESTRATOR_ENABLED=true`
- `TASK_ORCHESTRATOR_POLL_INTERVAL_SECONDS=2.0`
- `TASK_ORCHESTRATOR_BATCH_SIZE=5`
- `TASK_RUN_DEFAULT_MAX_RETRIES=3`

The background executor is `BackgroundTaskExecutor`, started from FastAPI lifespan when enabled. It polls `task_runs` in-process and executes Conversation / Playbook work through `TaskOrchestratorService`. This is not Celery, not RabbitMQ, not Kubernetes, and not production HA.
## Phase 43 Runtime Configuration: Task Scheduler Persistence & Worker Recovery

Task Scheduler Persistence is enabled through the existing in-process `BackgroundTaskExecutor`; it remains a foundation, not Celery, not Kubernetes, and not production HA distributed queue.

| Key | Current default | Meaning |
| --- | --- | --- |
| `TASK_SCHEDULER_NAME` | `api-in-process-task-scheduler` | Stable scheduler identity used for `task_scheduler_state` and task lease ownership. |
| `TASK_LEASE_SECONDS` | `120` | Lease duration assigned to running `task_runs`. Expired lease is eligible for recovery. |
| `TASK_STUCK_TIMEOUT_SECONDS` | `300` | Heartbeat staleness threshold for stuck running task recovery. |
| `TASK_SCHEDULER_RECOVERY_INTERVAL_SECONDS` | `10.0` | Background recovery scan interval for scheduled, retrying, and stuck tasks. |

Runtime tables and fields:

- `task_scheduler_state` stores scheduler status, heartbeat, last scan, active task count, recovered task count, and metadata.
- `task_runs` now includes `lease_owner`, `lease_token`, `lease_expires_at`, `heartbeat_at`, `recovery_count`, `last_recovered_at`, `recovery_reason`, `failure_category`, `failure_reason`, `recoverable`, `suggested_action`, and `last_event_summary`.

Core APIs:

- `GET /api/v1/task-scheduler/health`
- `POST /api/v1/task-scheduler/scan`
- `GET /api/v1/task-runs/{task_run_id}/diagnostics`
- `POST /api/v1/task-runs/{task_run_id}/recover`

Recovery rules:

- `running` task with expired lease or stale heartbeat becomes `retrying` when retry budget remains, otherwise `failed`.
- `pending` task with `scheduled_at <= now` becomes `queued`.
- `retrying` task with retry delay elapsed becomes `queued`.
- `waiting_approval` is not auto-executed and must resume through approval flow.
- `completed`, `cancelled`, and `expired` tasks are not recovered.

Admin Dashboard now shows Scheduler Health, lease status, recoverable badge, diagnostics panel, and manual recover control. Worker Console Web/Desktop show simplified scheduler and task recovery status.

Runtime verifier marker: TASK_SCHEDULER_RECOVERY_INTERVAL_SECONDS=10.0

<!-- PHASE44_RUNTIME:START -->
## Phase 44 Output Artifact Pipeline Runtime

| Key | Current default | Meaning |
| --- | --- | --- |
| `OUTPUT_ARTIFACT_DIR` | `storage/output_artifacts` | Output Artifact text/export metadata root. |
| `OUTPUT_PACKAGE_DIR` | `storage/output_packages` | Package artifact and bundle metadata root. |
| `OUTPUT_EXPORT_DIR` | `storage/output_exports` | Exported markdown/html/json/txt/bundle output root. |

Phase 44 adds Artifact lineage, relationship graph, `artifact_relationships`, `ArtifactExportService`, `ArtifactPackagingService`, and `ArtifactRetentionService`. Exports are based only on existing artifacts; they do not re-run Browser Runtime, Playbook, Conversation, Task, or OpenClaw mock actions.

New APIs:

- `GET /api/v1/output-artifacts/{artifact_id}/lineage`
- `GET /api/v1/output-artifacts/{artifact_id}/relationships`
- `POST /api/v1/output-artifacts/{artifact_id}/export`
- `POST /api/v1/output-artifacts/{artifact_id}/package`
- `POST /api/v1/output-artifacts/cleanup/preview`

Current boundaries: not a full DAM, not a production object storage platform, no production S3 / MinIO / CDN, no real social platform publishing, no real OpenClaw, and no ComfyUI.
<!-- PHASE44_RUNTIME:END -->

<!-- PHASE45_RUNTIME:START -->
## Phase 45 Runtime: Workflow State & Agent Memory Foundation

Runtime database tables:

- `workflow_runs`
- `workflow_steps`
- `workflow_checkpoints`
- `agent_memory_snapshots`

Runtime service: `WorkflowStateService` is used by Conversation, Playbook, Task Orchestration, and Output Artifact lineage integration. It records `workflow_run_created`, `workflow_step_started`, `workflow_step_completed`, `workflow_checkpoint_created`, `workflow_paused`, `workflow_resumed`, and `memory_snapshot_created` events when a workflow is linked to a conversation thread.

Runtime API routes:

- `GET /api/v1/workflow-runs`
- `GET /api/v1/workflow-runs/{workflow_run_id}`
- `GET /api/v1/workflow-runs/{workflow_run_id}/steps`
- `GET /api/v1/workflow-runs/{workflow_run_id}/checkpoints`
- `POST /api/v1/workflow-runs/{workflow_run_id}/pause`
- `POST /api/v1/workflow-runs/{workflow_run_id}/resume`
- `GET /api/v1/workflow-runs/{workflow_run_id}/memory-snapshots`
- `GET /api/v1/agent-memory-snapshots`

Artifact lineage fields: `workflow_run_id`, `workflow_step_id`, `checkpoint_id`, and `memory_snapshot_id`.

Boundaries: not a full workflow builder, not ComfyUI, not WebSocket/SSE streaming, not real platform automation.
<!-- PHASE45_RUNTIME:END -->

<!-- PHASE46_RUNTIME:START -->
## Phase 46 Runtime: Workflow Graph Runtime & Conditional Execution

Runtime database tables:

- `workflow_graphs`
- `workflow_graph_nodes`
- `workflow_graph_edges`
- `workflow_replays`

Runtime services:

- `WorkflowExecutionPlanner` validates graphs, resolves entry nodes, performs topological traversal, detects cycles, plans next nodes, tracks dependency state, and exposes retry/fallback paths.
- `SafeConditionEvaluator` evaluates only safe condition expressions over `workflow.variables`, `workflow.status`, `step.output`, `artifact.metadata`, and `approval.status`. It supports `==`, `!=`, `and`, `or`, `in`, and `exists`, and does not use Python `eval`.
- `WorkflowGraphService` creates, lists, gets, and validates workflow graph definitions.
- `WorkflowStateService` records graph execution metadata on workflow runs and steps.

Runtime API routes:

- `GET /api/v1/workflow-graphs`
- `POST /api/v1/workflow-graphs`
- `GET /api/v1/workflow-graphs/{graph_id}`
- `POST /api/v1/workflow-graphs/{graph_id}/validate`
- `POST /api/v1/workflow-runs/{workflow_run_id}/replay`
- `GET /api/v1/workflow-runs/{workflow_run_id}/graph`
- `GET /api/v1/workflow-runs/{workflow_run_id}/planner`

Runtime fields:

- `workflow_runs.workflow_graph_id`
- `workflow_runs.graph_execution`
- `workflow_runs.current_node_key`
- `workflow_runs.planned_next_nodes`
- `workflow_runs.skipped_nodes`
- `workflow_runs.retry_state`
- `workflow_runs.fallback_state`
- `workflow_steps.node_key`
- `workflow_steps.parent_node_key`
- `workflow_steps.dependency_state`
- `output_artifacts.producing_node_key`
- `output_artifacts.replay_source`
- `output_artifacts.graph_lineage`
- `agent_memory_snapshots.node_key`

Boundaries: current replay is metadata-only and does not re-run actions. The runtime is not a visual DAG builder, not a distributed orchestration engine, not ComfyUI, not WebSocket/SSE streaming, and not real platform automation.
<!-- PHASE46_RUNTIME:END -->

<!-- PHASE47_RUNTIME:START -->
## Phase 47 Runtime: Workflow Template Registry & Versioning

Runtime database tables:

- `workflow_templates`
- `workflow_template_versions`
- `workflow_template_runs`

Runtime services:

- `WorkflowTemplateRegistryService` manages template listing, creation, immutable version creation, active version activation, validation, import/export, template runs, and built-in template seeding.
- `WorkflowTemplateCompatibilityService` checks required node types, input_schema, output_schema, graph definition validation, risk_level, runtime capabilities, warnings, errors, and missing capabilities.

Built-in template keys:

- `browser_screenshot_report_graph`
- `content_generation_graph`
- `rag_answer_graph`
- `approval_then_browser_graph`
- `openclaw_mock_inspect_graph`
- `task_retry_demo_graph`

Runtime API routes:

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

Runtime fields:

- `workflow_templates.template_key`
- `workflow_templates.current_version`
- `workflow_templates.latest_version`
- `workflow_template_versions.validation_status`
- `workflow_template_versions.compatibility`
- `task_runs.workflow_template_id`
- `task_runs.workflow_template_version_id`
- `task_runs.workflow_template_run_id`
- `output_artifacts.workflow_template_id`
- `output_artifacts.workflow_template_version_id`
- `output_artifacts.workflow_template_run_id`
- `agent_memory_snapshots.workflow_template_id`
- `agent_memory_snapshots.workflow_template_version_id`
- `agent_memory_snapshots.workflow_template_run_id`

Frontend clients:

- `admin_dashboard/src/api/workflowTemplateClient.ts`
- `worker_console/src/api/workflowTemplateClient.ts`
- `worker_console_desktop/src/api/workflowTemplateClient.ts`

Boundaries: Template Library is a registry and run foundation only. It is not a visual DAG builder, not a drag/drop graph editor, not ComfyUI, not WebSocket/SSE streaming, and not real platform automation.
<!-- PHASE47_RUNTIME:END -->

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

<!-- PHASE53_SYNC:BEGIN -->
## Phase 53: Release Smoke Test Matrix & Preflight Automation

Phase 53 adds release readiness orchestration on top of Phase 51 packaging and Phase 52 deployment profiles.

Runtime-facing additions:

- `release/smoke/smoke_matrix.json`
- `release/smoke/profile_matrix.json`
- `release/smoke/runtime_matrix.json`
- `scripts/release_preflight.py`
- `scripts/release_smoke_matrix.py`
- `scripts/generate_release_report.py`
- `scripts/check_migration_continuity.py`
- `scripts/check_runtime_hygiene.py`

The preflight runner coordinates pytest, docs verifier, release validator, frontend builds, Docker health, deployment verification, runtime hygiene, migration continuity, and smoke routes. The smoke matrix checks health, browser-worker summary, conversation playbooks, task runs, output artifacts, workflow templates, and workflow replay sessions.

Boundaries: this is not Kubernetes, Helm, Terraform, CI/CD SaaS, a real installer, code signing, an auto updater, production HA orchestration, ComfyUI, real OpenClaw, or real social media automation.
<!-- PHASE53_SYNC:END -->

<!-- PHASE54_SYNC:BEGIN -->
## Phase 54: Integration Branch & PR Chain Reconciliation

Phase 54 adds integration reconciliation on top of the Phase 43-53 stack. It introduces `docs/INTEGRATION_STRATEGY.md`, `docs/INTEGRATION_STATUS.md`, `release/integration/*`, `release/reports/pr_chain_inventory.json`, `scripts/analyze_pr_chain.py`, `scripts/integration_preflight.py`, `scripts/detect_integration_conflicts.py`, `scripts/check_api_frontend_drift.py`, and `scripts/generate_integration_report.py`.

The integration preflight coordinates release preflight, smoke matrix, docs verifier, migration continuity, runtime hygiene, release packaging validation, deployment verification, OpenAPI/frontend client drift checks, phase index consistency, PR chain inventory validation, and conflict surface detection.

Boundaries: Phase 54 does not add runtime features, does not merge PRs automatically, does not resolve conflicts automatically, and is not Kubernetes, Helm, Terraform, CI/CD SaaS, production HA orchestration, a real installer, code signing, or auto update.
<!-- PHASE54_SYNC:END -->

<!-- PHASE55_SYNC:BEGIN -->
## Phase 55: Mainline Integration & Release Candidate Merge Window

Phase 55 does not add runtime features. It adds Mainline Release Candidate preparation: `docs/MAINLINE_INTEGRATION_PLAN.md`, `docs/RELEASE_CANDIDATE_PROCESS.md`, `release/integration/release_candidate_model.json`, `scripts/mainline_readiness.py`, `scripts/simulate_mainline_merge.py`, `scripts/generate_superseded_pr_report.py`, and `scripts/generate_mainline_integration_report.py`.

The runtime remains smoke verified and integration preflight verified, but not production-ready. Phase 55 keeps `main` unchanged and prepares the manual RC decision package.
<!-- PHASE55_SYNC:END -->

## Docs Stabilization Sprint

This document is now indexed by `docs/PHASE_INDEX.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/SYSTEM_BOUNDARIES.md`, `docs/DOC_RENDER_QA.md`, and `docs/ARCHITECTURE_TIMELINE.md`.

The canonical project recovery state is: `main` is the Phase 55 accepted baseline after PR #17 merged the Phase 43-55 Combined Release Candidate. Phase 56 was reverted and is not active. Post-merge stabilization is tracked in `docs/POST_MERGE_STABILIZATION.md`. Current non-goals remain: no ComfyUI integration, no real social media publishing, no captcha bypass, no proxy pool, no Kubernetes/Helm/Terraform, no HA orchestration, and no production installer/signing.
