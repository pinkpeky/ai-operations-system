# Architecture

## Phase 28 OpenClaw Worker Adapter Foundation

Phase 28 adds a mock OpenClaw adapter on top of the Browser Worker protocol:

```text
API Server / openclaw_tool
-> OpenClawService
-> BrowserWorkerSelector capability=openclaw
-> OpenClawWorkerClient
-> worker_client /openclaw/* mock runtime
-> MockOpenClawProvider
-> openclaw_action_logs + browser_security_audit_logs
```

The server-side `app/openclaw/` package owns OpenClaw schemas, `OpenClawWorkerClient`, repository, and service logic. The customer-machine `worker_client/openclaw/` package owns `BaseOpenClawProvider`, `MockOpenClawProvider`, `OpenClawRuntime`, and worker runtime routes. The builtin `openclaw_tool` calls the same service path and records `tool_call_logs`.

Boundary: this is a placeholder foundation only. It does not call real OpenClaw, automate social platforms, log in, inject cookies, use proxy pools, bypass fingerprints, or automate captchas.

## Phase 20 Real Browser Worker Service

Phase 20 adds a real independent worker service on top of the Phase 19 Remote Browser Worker protocol. The current remote browser execution path is:

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

`browser-worker` is a standalone FastAPI service in Docker Compose and exposes port `9100`. It provides `GET /health`, `POST /sessions`, `POST /actions`, and `POST /sessions/{session_id}/close`. The API Server still registers workers through `POST /api/v1/browser-workers/register` using `base_url=http://browser-worker:9100`, then dispatches actions through `BrowserService` and the remote provider.

Safety boundary: only `example.com`, local test pages, and static file pages are supported. TikTok / YouTube / X automation, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, OCR, visual AI, OpenClaw, and autonomous browser agents are not implemented.

Last updated: 2026-05-12

This document describes the architecture that exists in the current codebase.

## Overview

```text
Client / Swagger / API caller
 -> FastAPI
 -> WorkspaceContextMiddleware
 -> Routes
 -> Services
 -> Repositories / Providers
 -> PostgreSQL / Redis / Qdrant / Ollama
```

Key boundaries:

- Scheduler scans tasks, transitions status, and enqueues work.
- TaskExecutor consumes queued tasks and dispatches handlers.
- RAG, LLM, Reranker, and File Upload logic live outside Scheduler core logic.
- Workspace isolation is enforced by middleware and workspace-aware queries.
- Docs are treated as Single Source of Truth and verified by runtime checks.

## Project Structure

```text
app/api/            FastAPI routes and endpoint modules.
app/agents/         LLM client, BaseAgent, and ContentAgent.
app/core/           Settings, errors, logging, workspace context.
app/db/             PostgreSQL, Redis, and Qdrant helpers.
app/file_pipeline/  File upload parsers, text cleaner, upload ingestion service.
app/middleware/     Workspace context middleware.
app/memory/         Conversation sessions, messages, Agent Memory repositories, and MemoryService.
app/multi_agent/    AgentRegistry, MultiAgentService, and run/message/handoff persistence.
app/planning/       SimplePlannerAgent, PlanningService, and plan/step/review persistence.
app/rag/            Embedding, chunking, vector store, retrieval, hybrid search, Agentic RAG.
app/reranker/       Reranker abstraction and mock/local providers.
app/repositories/   Database access layer.
app/schemas/        Pydantic models.
app/services/       Prompt manager, queue, lifecycle, eval, scheduler.
app/workers/        TaskExecutor and handlers.
scripts/            Runtime verification scripts.
docs/               Documentation SSOT.
```

## Data Stores

PostgreSQL tables:

- `tasks`
- `accounts`
- `publish_logs`
- `documents`
- `document_chunks`
- `collections_metadata`
- `users`
- `workspaces`
- `workspace_members`
- `api_keys`
- `rag_eval_runs`
- `rag_eval_items`
- `task_events`
- `task_logs`
- `tool_call_logs`
- `conversation_sessions`
- `conversation_messages`
- `agent_memories`
- `memory_operation_logs`

Qdrant stores chunk embeddings. Payloads include `document_id`, `source_id`, `version`, `workspace_id`, `user_id`, and `status`.

Redis stores task queue data.

Ollama is used by local providers for Mistral and bge-m3 when explicitly enabled.

## Workspace Isolation

Workspace-scoped requests require:

```http
X-Workspace-Id: <workspace id>
X-User-Id: <optional user id>
```

Rules:

- Document queries are workspace-filtered.
- Task queries are workspace-filtered.
- Collection queries are workspace-filtered.
- Dense retrieval filters Qdrant payload by workspace/status/source.
- Keyword retrieval filters PostgreSQL rows by workspace/status/source.
- Protected endpoints never default to global reads.

## Knowledge Lifecycle

```text
ingest text/file
 -> create document
 -> chunk text
 -> create document_chunks
 -> embed chunks
 -> upsert Qdrant points
 -> update lifecycle metadata
```

Statuses:

- `active`
- `outdated`
- `deleted`

Re-ingesting the same `source_id` marks the previous active document as `outdated` and creates a new version.

## File Upload Pipeline

```text
POST /api/v1/files/upload
 -> validate workspace
 -> validate file type and size
 -> save temp file
 -> compute SHA-256 file_hash
 -> duplicate check by file_hash + workspace_id + collection_name
 -> parse file text
 -> clean extracted text
 -> DocumentLifecycleService.ingest_text
 -> update file metadata
 -> cleanup temp file
```

Supported parsers:

- PDF via `pypdf`
- DOCX via `python-docx`
- CSV via `pandas`
- TXT and MD via UTF-8 text parser

Unsupported:

- PPTX
- XLSX
- OCR
- Images

Duplicate strategies:

- `skip`: return the existing active document.
- `force_reingest`: reuse the source and let lifecycle versioning create a new version.

## RAG Query Architecture

```text
query
 -> dense retrieval
 -> keyword retrieval
 -> merge by chunk id
 -> dense_score / keyword_score / hybrid_score
 -> reranker
 -> top_n context
 -> prompt assembly
 -> LLM
 -> answer + trace
```

Modes:

- `dense`
- `keyword`
- `hybrid`

Defaults:

```text
DEFAULT_SEARCH_MODE=hybrid
DENSE_TOP_K=20
KEYWORD_TOP_K=20
FINAL_TOP_K=5
```

## Reranker

Providers:

- `MockRerankerProvider`
- `LocalRerankerProvider`

Default:

```text
RERANKER_PROVIDER=mock
```

The mock reranker uses deterministic query-token overlap. The local reranker provider is a placeholder interface.

## Agentic RAG Trace

When `debug=true`, `POST /api/v1/agentic-rag/query` returns:

- `query`
- `workspace_id`
- `collection_name`
- `search_mode`
- `dense_results_count`
- `keyword_results_count`
- `merged_results_count`
- `final_results_count`
- `dense_scores`
- `keyword_scores`
- `hybrid_scores`
- `retrieval_before_rerank`
- `reranked_chunks`
- `rerank_scores`
- `retrieval_after_rerank`
- `final_prompt`
- `final_answer`
- `llm_provider`
- `llm_model`
- `embedding_provider`
- `embedding_model_name`
- `reranker_provider`
- `reranker_model`
- `latency_ms`
- `session_id`
- `recent_messages_count`
- `retrieved_memories_count`
- `recent_messages`
- `retrieved_memories`
- `memory_trace`

## Memory Foundation

Phase 14 adds a workspace-scoped memory foundation without vector memory, graph memory, or autonomous planning.

```text
Memory API / BaseAgent / Agentic RAG
 -> MemoryService
 -> ConversationRepository / AgentMemoryRepository
 -> PostgreSQL tables
 -> recent messages + text-matched memories
 -> prompt assembly
 -> memory_trace
```

Tables:

- `conversation_sessions`: workspace/user scoped conversation containers.
- `conversation_messages`: ordered messages with `system`, `user`, `assistant`, or `tool` roles.
- `agent_memories`: Agent memory entries with `short_term`, `long_term`, `task_memory`, or `retrieval_memory` types.
- `memory_operation_logs`: operation latency, success/error, workspace, session, agent, and memory type logs.

Memory retrieval:

- Recent conversation is loaded by `session_id`.
- Agent memories are searched with PostgreSQL text matching on `agent_memories.content`.
- All reads and writes require `workspace_id`.
- Agentic RAG combines memory context with RAG context before LLM prompt assembly.

## Docs Runtime Verification

```text
python scripts/verify_docs_runtime.py
 -> Settings defaults
 -> docker-compose environment
 -> FastAPI OpenAPI schema
 -> CURRENT_RUNTIME
 -> PROJECT_OVERVIEW
 -> zh/en API_REFERENCE
 -> PASS / WARNING / ERROR
```

The verifier prevents documentation drift after runtime or API changes.

## Boundaries

- No real reranker model is wired.
- No Elasticsearch or OpenSearch.
- No OCR.
- No PPTX, XLSX, or image parsing.
- No vector memory or graph memory.
- No autonomous memory planning.
- No full RBAC, JWT, or OAuth.
- No frontend dashboard.
- No Browser Agent, OpenClaw, or Playwright.

## Task Reliability & Observability

Phase 12 adds a reliability and observability layer around the task system without changing Scheduler core responsibility.

```text
Task API
 -> create/cancel/retry/query
 -> tasks
 -> task_events
 -> task_logs

Scheduler
 -> scan pending/retry
 -> enqueue
 -> minimal stale running timeout adaptation

TaskExecutor
 -> skip cancelled
 -> started event/log
 -> handler execution
 -> completed/failed/retry_scheduled/timeout event/log
 -> duration_ms
```

New tables:

- `task_events`
- `task_logs`

Task statuses:

- `pending`
- `running`
- `retry`
- `failed`
- `completed`
- `cancelled`
- `timeout`

Observability APIs:

- `POST /api/v1/tasks/{task_id}/cancel`
- `POST /api/v1/tasks/{task_id}/retry`
- `GET /api/v1/tasks/{task_id}/events`
- `GET /api/v1/tasks/{task_id}/logs`
- `GET /api/v1/observability/summary`

## Tool Calling Foundation

Phase 13 adds an internal Tool Calling foundation. It does not connect browser automation, external APIs, or autonomous planning.

```text
API / Agent
 -> ToolRegistry
 -> BaseTool.validate_input
 -> builtin tool execute
 -> workspace-scoped repository/service
 -> tool_call_logs
 -> tool result
 -> optional LLM response
```

Core directories:

- `app/tools/base/`: `BaseTool`, `ToolExecutionContext`, `ToolExecutionRecord`.
- `app/tools/registry/`: `ToolRegistry` and default builtin tool registration.
- `app/tools/builtin/`: current builtin tools.
- `app/api/routes/tools.py`: tool list, execute, and log APIs.
- `app/repositories/tool_call_repository.py`: `tool_call_logs` read/write layer.

Current builtin tools:

- `rag_search_tool`
- `file_search_tool`
- `create_task_tool`
- `get_task_status_tool`
- `current_runtime_tool`

`BaseAgent` supports:

- `available_tools`
- `tool_call_trace`
- `execute_tool()`

Current limitations:

- No LLM-native function calling.
- No ReAct.
- No Planner.
- No Browser Agent / OpenClaw / Playwright / Selenium.

## Multi-Agent Foundation

Phase 15 adds a fixed-chain Multi-Agent foundation. It introduces orchestration records and a registry without implementing autonomous planning or browser automation.

```text
API
 -> AgentRegistry
 -> MultiAgentService
 -> agent_runs
 -> content_planner
 -> rag_agent
 -> content_agent
 -> review_agent
 -> agent_messages
 -> agent_handoffs
 -> run output with agents_involved + handoff_trace
```

Core directories:

- `app/multi_agent/services/`: `AgentRegistry` and `MultiAgentService`.
- `app/multi_agent/repositories/`: `AgentRunRepository`.
- `app/api/routes/multi_agent.py`: run, chain, message, and handoff APIs.
- `app/schemas/multi_agent.py`: request and response schemas.

Tables:

- `agent_runs`
- `agent_messages`
- `agent_handoffs`

Registered agents:

- `content_planner`: deterministic mock planner.
- `rag_agent`: wraps `AgenticRAGOrchestrator`.
- `content_agent`: wraps `ContentAgent`.
- `review_agent`: deterministic mock reviewer.
- `runtime_agent`: calls `current_runtime_tool`.
- `tool_agent`: calls current `ToolRegistry` builtin tools.

Fixed chain:

```text
content_planner -> rag_agent -> content_agent -> review_agent
```

Memory integration:

- `agent_runs.session_id` stores the conversation session reference when provided.
- `rag_agent` and `content_agent` can reuse the existing Phase 14 Memory Foundation.
- The response exposes messages, handoffs, `agents_involved`, and `handoff_trace`.

Current limitations:

- No autonomous planner.
- No dynamic handoff policy.
- No ReAct.
- No Browser Agent / OpenClaw / Playwright / Selenium.

## Browser Automation Adapter Foundation

Phase 17 adds a provider-based Browser Adapter layer without real browser execution.

Flow:

```text
Browser API / browser_tool / Planning tool step
 -> BrowserService
 -> BrowserProvider
 -> MockBrowserProvider
 -> browser_sessions / browser_actions / browser_action_logs
```

Core modules:

- `app/browser/providers/base.py`: `BrowserProvider` interface.
- `app/browser/providers/mock_browser_provider.py`: deterministic mock provider.
- `app/browser/providers/playwright_browser_provider.py`: placeholder only.
- `app/browser/services/browser_service.py`: session/action execution and observability.
- `app/browser/repositories/browser_repository.py`: workspace-scoped persistence.
- `app/tools/builtin/browser_tool.py`: safe manual browser tool.
- `app/api/routes/browser.py`: Browser API.

Tables:

- `browser_sessions`
- `browser_actions`
- `browser_action_logs`

Current boundaries:

- `BROWSER_PROVIDER=mock` by default.
- `MockBrowserProvider` never starts a browser.
- `PlaywrightBrowserProvider` is a placeholder and does not install or call Playwright.
- Planning can execute `tool_name=browser_tool`, but there is no autonomous browser planning.
- No Browser Agent, OpenClaw, Selenium, OCR, visual AI, real login flow, or platform automation.

## Playwright Local Provider Integration

Phase 18 adds real local Chromium execution on top of the Browser Adapter abstraction. It is still bounded execution, not a Browser Agent.

```text
Browser API / browser_tool
 -> BrowserService
 -> BrowserProvider switch
 -> PlaywrightLocalProvider
 -> headless Chromium
 -> browser_actions: selector / target_url / screenshot_path / page_title
 -> screenshots/{workspace_id}/{session_id}/{filename}.png
 -> browser_action_logs
```

Core modules:

- `app/browser/providers/playwright_provider.py`: `PlaywrightLocalProvider`, provider name `playwright_local`.
- `app/browser/services/browser_service.py`: switches between `mock` and `playwright_local` through `BROWSER_PROVIDER`.
- `app/api/routes/browser.py`: adds `GET /api/v1/browser/screenshot/{session_id}/{filename}`.
- `app/tools/builtin/browser_tool.py`: supports `navigate`, `click`, `type_text`, `screenshot`, and `get_page_content`.

Runtime fields:

- `browser_sessions.browser_id`
- `browser_sessions.page_id`
- `browser_sessions.provider_session_metadata`
- `browser_actions.selector`
- `browser_actions.target_url`
- `browser_actions.screenshot_path`
- `browser_actions.page_title`

Safety boundary:

- Default is `BROWSER_PROVIDER=mock`.
- `BROWSER_PROVIDER=playwright_local` only allows `example.com`, local test pages, and static `file://` pages.
- No social platform automation, automatic login, cookie injection, fingerprint bypass, proxy pools, captcha automation, OCR, visual AI, autonomous browser planning, Browser Worker, or real platform automation.

## Remote Browser Worker Foundation

Phase 19 establishes the Remote Browser Worker protocol so the AI Server can eventually dispatch browser actions to separate worker machines. This phase implements the protocol, client, provider, worker registration/heartbeat, and in-project mock runtime only.

```text
AI Server
 -> RemoteBrowserProvider
 -> BrowserWorkerClient
 -> Browser Worker API
 -> Worker Runtime Mock
```

Core modules:

- `app/browser/remote/client/browser_worker_client.py`: `BrowserWorkerClient`.
- `app/browser/providers/remote_browser_provider.py`: `RemoteBrowserProvider`.
- `app/browser/remote/services/browser_worker_repository.py`: worker/session/action persistence.
- `app/browser/remote/services/browser_worker_service.py`: registration, heartbeat, and listing service.
- `app/api/routes/browser_workers.py`: worker management API and mock runtime API.

Database tables:

- `browser_workers`
- `browser_worker_sessions`
- `browser_worker_actions`

Remote Action Dispatch Flow:

```text
BrowserService creates browser_actions
 -> RemoteBrowserProvider reads provider_session_metadata
 -> BrowserWorkerClient POST /actions
 -> browser_worker_actions stores remote_action_id / response_payload
 -> BrowserService completes browser_actions
 -> browser_action_logs records worker_id / worker_name / remote_action_id
```

Boundary:

- Current worker runtime is mock and does not start a real browser.
- No real external worker deployment.
- No TikTok / YouTube / X, login, auto-publishing, cookie injection, fingerprint bypass, proxy pools, captcha automation, or autonomous browser agent.

## Agent Planning Foundation

Phase 16 adds a bounded Planning layer above AgentRegistry and ToolRegistry. It upgrades fixed chain execution into a stored plan with observable steps and reviews, without implementing autonomous AGI planning or recursive loops.

```text
User goal
 -> SimplePlannerAgent
 -> plans
 -> plan_steps
 -> PlanningService.execute_plan
 -> AgentRegistry or ToolRegistry
 -> step output / duration_ms / error
 -> plan_reviews
 -> final plan status + memory_trace
```

Core directories:

- `app/planning/services/`: `SimplePlannerAgent` and `PlanningService`.
- `app/planning/repositories/`: `PlanRepository`.
- `app/api/routes/planning.py`: plan, execute, cancel, steps, and reviews APIs.
- `app/schemas/planning.py`: Planning API schemas.

Tables:

- `plans`
- `plan_steps`
- `plan_reviews`

Plan status:

- `pending`
- `planning`
- `executing`
- `completed`
- `failed`
- `cancelled`

PlanStep status:

- `pending`
- `running`
- `completed`
- `failed`
- `skipped`

Planning integrates with:

- `AgentRegistry` for agent steps.
- `ToolRegistry` for tool steps.
- Memory Foundation through `session_id` and planning `memory_trace`.

Current limitations:

- Rule-based planner only.
- No autonomous AGI planner.
- No tree-of-thought.
- No recursive planning.
- No infinite Agent loop.
- No ReAct.
- No Browser Agent / OpenClaw / Playwright / Selenium.
## Phase 21 Browser Worker Reliability

Browser Worker Reliability wraps `RemoteBrowserProvider` and `BrowserWorkerClient` with recovery and scheduling foundations for future multi-worker execution, Chrome Profile support, and account-environment isolation.

Core components:

- `BrowserWorkerHealthService`: checks `last_seen` / `last_heartbeat_at`, marks stale workers `offline`, and records `error_message`.
- `BrowserWorkerSelector`: filters by `workspace_id`, `status=online`, capability, and `active_sessions < max_sessions`, then selects the least loaded worker.
- `BrowserSessionCleanupService`: closes stale sessions, marks sessions failed when the worker is offline/error, and writes browser logs.
- `ScreenshotCleanupService`: cleans `screenshots` and `worker/screenshots` by workspace and age, with dry-run as the default.

Worker selection flow:

```text
create browser session
-> RemoteBrowserProvider
-> BrowserWorkerSelector
-> online + capability + capacity
-> least loaded worker
-> BrowserWorkerClient
-> browser-worker
```

Action retry flow:

```text
browser action
-> BrowserWorkerClient
-> timeout / retry / backoff
-> retry_logs
-> browser_worker_actions.retry_count / max_retries
```

This phase still does not include real platform automation, login, cookies, proxies, fingerprinting, captcha handling, OCR, visual AI, or autonomous browser planning.

## Phase 22 Persistent Browser Profile Foundation

Phase 22 adds persistent browser profile metadata and lock management around the Browser Worker stack. It prepares the system for future account-environment isolation and long-running browser sessions while keeping the current safety boundary intact.

Core components:

- `browser_profiles`: stores `profile_name`, `profile_type`, `provider`, `profile_path`, `status`, `locked_by_session_id`, `locked_at`, and `last_used_at`.
- `BrowserProfileService`: creates, lists, loads, locks, releases, marks corrupted, and logically deletes profiles under workspace isolation.
- `browser_sessions.profile_id`, `browser_sessions.profile_path`, and `browser_sessions.persistent_context_enabled`: bind a session to a profile-backed runtime.
- `worker/browser_worker/playwright_runtime.py`: uses Playwright `launch_persistent_context` only when a session explicitly requests a persistent profile.

Profile lock / release flow:

```text
POST /api/v1/browser/profiles
-> BrowserProfileService.create_profile
-> POST /api/v1/browser/sessions with profile_id + use_persistent_profile=true
-> BrowserProfileService.lock_profile
-> BrowserService passes profile metadata to RemoteBrowserProvider
-> browser-worker launches persistent context
-> POST /api/v1/browser/sessions/{session_id}/close
-> BrowserProfileService.release_profile
```

Persistent context flow:

```text
browser_sessions.profile_id
-> provider_session_metadata.profile_id/profile_path/use_persistent_profile
-> BrowserWorkerClient /sessions
-> worker/browser_worker/playwright_runtime.py
-> launch_persistent_context
-> worker/profiles/{workspace_id}/{profile_id}
```

This phase does not implement login, cookie injection, browser fingerprinting, proxies, captcha handling, social platform automation, or autonomous browser planning.

## Phase 23 Browser Profile Health & Recovery

Phase 23 builds health, recovery, backup, cleanup, and usage-log capabilities on top of the Phase 22 Persistent Browser Profile layer. The purpose is to make long-lived browser profiles observable and recoverable when a session fails, a worker goes offline, a profile path is damaged, or profile files become stale.

Core data:

- `browser_profiles.health_status`: `healthy`, `warning`, `corrupted`, `stale`, `deleted`.
- `browser_profiles.last_health_check_at`, `last_error`, `usage_count`, `corrupted_at`, `backup_path`, and `last_backup_at`.
- `browser_profile_usage_logs`: profile lifecycle audit records for troubleshooting and recovery.

Service layering:

```text
Browser Profile APIs
-> BrowserProfileHealthService
   -> check_profile_health / recover_stale_locks / summarize_profiles
-> BrowserProfileBackupService
   -> create_backup / list_backups / restore_backup
-> BrowserProfileCleanupService
   -> cleanup_deleted_profiles / cleanup_corrupted_profiles / cleanup_unused_profiles
-> browser_profile_usage_logs
```

Stale lock recovery flow:

```text
locked browser_profile
-> check locked_at timeout
-> check locking browser_session status
-> check worker session and worker status
-> release locked_by_session_id
-> set profile status=available
-> set health_status=stale
-> write browser_profile_usage_logs action=recovery
```

Profile backup flow:

```text
POST /api/v1/browser/profiles/{profile_id}/backup
-> validate profile_path under BROWSER_PROFILE_ROOT
-> zip profile directory
-> worker/profile_backups/{workspace_id}/{profile_id}
-> update backup_path / last_backup_at
-> enforce BROWSER_PROFILE_MAX_BACKUPS
-> write usage log action=backup
```

Profile cleanup flow:

```text
POST /api/v1/browser/profiles/cleanup
-> select deleted / corrupted / unused profiles in current workspace
-> dry-run by default
-> remove profile directory only when inside profile root
-> write usage log action=cleanup
```

New settings: `BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS`, `BROWSER_PROFILE_BACKUP_ENABLED`, `BROWSER_PROFILE_MAX_BACKUPS`, `BROWSER_PROFILE_UNUSED_DAYS`, and `BROWSER_PROFILE_BACKUP_ROOT`.

The safety boundary remains unchanged: no account login, cookie injection, proxy pools, fingerprint bypass, captcha handling, real platform automation, TikTok / YouTube / X automation, or autonomous browser planning.

## Phase 24 Human-in-the-loop Browser Control

Phase 24 adds a backend human-control protocol for browser automation. It lets automation pause a browser session, record that manual work is needed, keep the worker/profile session alive, and resume later when the manual step is marked complete.

Core data:

- `browser_human_control_sessions`: stores `browser_session_id`, `profile_id`, `worker_id`, `status`, `reason`, requester/approver fields, timestamps, expiry, and metadata.
- `browser_human_control_events`: records `requested`, `approved`, `started`, `completed`, `cancelled`, `expired`, `timeout`, and `note` events.
- `browser_sessions.human_control_status`, `human_control_session_id`, `paused_at`, and `resumed_at`: bind the browser session to the current human-control state.

Pause / resume flow:

```text
POST /api/v1/browser/human-control/request
-> BrowserHumanControlService.request_control
-> browser_human_control_sessions status=requested
-> browser_sessions status=paused
-> browser_human_control_events requested
-> approve/start
-> worker metadata-level /human-control/start
-> complete
-> browser_sessions status=active
-> browser_human_control_events completed
```

Tool integration:

```text
browser_tool action_type=request_human_control
-> BrowserHumanControlService.request_control

browser_tool action_type=complete_human_control
-> BrowserHumanControlService.complete_control
```

While the browser session is paused, normal browser actions are rejected by the existing active-session guard. After completion, the session is resumed and subsequent actions can continue.

Worker integration is metadata-level only:

- `POST /human-control/start`
- `POST /human-control/complete`
- `GET /human-control/status/{session_id}`

This phase does not implement VNC, noVNC, Chrome DevTools remote UI, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha automation, TikTok / YouTube / X automation, or real platform automation.

## Phase 25 Browser Worker UI Access Placeholder

Phase 25 adds a placeholder access layer for future human remote browser UI control. It creates the backend contract, token handling, and URL placeholders, but it does not expose a real remote desktop or browser stream.

Core data:

- `browser_ui_access_sessions`: stores `browser_session_id`, `human_control_session_id`, `worker_id`, `access_token_hash`, `remote_control_url`, `live_view_url`, `devtools_url`, status, expiry, and metadata.
- `BrowserUIAccessService`: creates, reads, revokes, expires, generates tokens, and validates tokens.
- `BROWSER_UI_ACCESS_TIMEOUT_SECONDS`: controls token/session expiry.

Token flow:

```text
POST /api/v1/browser/ui-access
-> generate plaintext token
-> store access_token_hash
-> return plaintext token once
-> validate with /validate?token=TOKEN
-> revoke or expire
```

Human Control integration:

```text
human control status=active
-> BrowserUIAccessService.create_access_session
-> placeholder URL generation
-> browser_tool create_ui_access / revoke_ui_access
```

Worker capabilities:

```text
GET /ui-access/capabilities
-> vnc=false
-> novnc=false
-> devtools=false
-> placeholder=true
```

The generated URLs are placeholders only:

- `remote_control_url`: `http://localhost:8000/ui/browser-control/{access_session_id}`
- `live_view_url`: `http://localhost:8000/ui/browser-live/{access_session_id}`
- `devtools_url`: `null`

Phase 25 does not implement VNC, noVNC, Chrome DevTools remote UI, live browser video, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha automation, TikTok / YouTube / X automation, or real platform automation.

## Phase 26 Browser Worker Security & Access Control

Phase 26 adds basic security boundaries across Browser Worker, UI Access, Browser Profile, and Browser Action. It is backend security infrastructure, not a complete identity system and not a real social-platform account security implementation.

### Worker Secret / Signed Request

```text
POST /api/v1/browser-workers/register
 -> generate worker_secret
 -> plaintext returned once
 -> store worker_secret_hash only
 -> BrowserWorkerClient.sign_request
 -> X-Worker-Signature / X-Worker-Timestamp / X-Worker-Nonce
 -> browser-worker verify_signature
```

`BrowserWorkerAuthService` handles secret generation, hashing, verification, request signing, and signature verification. `browser_workers` now includes `worker_secret_hash`, `api_key_hash`, `last_auth_at`, `auth_status`, `allowed_actions`, and `allowed_domains`.

### UI Access Scope

`browser_ui_access_sessions` now includes `scopes`, `one_time`, `used_at`, `revoked_reason`, `client_ip`, and `user_agent`. Token validation checks token value, expiry, scope, and one-time state, then writes security audit records.

### Browser Action Policy

`BrowserActionPolicyService` validates:

- Supported action type.
- Navigate target under `BROWSER_ALLOWED_DOMAINS`.
- Profile/session workspace ownership.
- Worker `allowed_actions`.
- Worker capability.
- UI access scope.

The default policy is `BROWSER_ALLOW_EXTERNAL_DOMAINS=False`, allowing only `example.com`, `localhost`, and `127.0.0.1`.

### Security Audit

`BrowserSecurityAuditLog` / `browser_security_audit_logs` stores worker registration, worker auth success/failed, UI token created/validated/revoked/expired, action blocked by policy, and profile access denied events.

Phase 26 does not implement TikTok / YouTube / X automation, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha handling, real platform automation, or complete RBAC/JWT/OAuth.

## Phase 27 Customer Machine Worker Bootstrap

Phase 27 adds a customer-machine bootstrap package named `worker_client`. It lets a Windows PC, Mac, or customer-owned machine register with the AI Server and expose the same Browser Worker protocol used by the Docker `browser-worker` service.

```text
customer machine
 -> worker_client/worker_config.yaml
 -> python -m worker_client.cli register
 -> AI Server /api/v1/browser-workers/register
 -> worker_client/worker_state.json
 -> python -m worker_client.cli serve
 -> local worker runtime
 -> python -m worker_client.cli heartbeat
 -> AI Server heartbeat and signed request flow
```

Main modules:

- `worker_client/config.py`: YAML loading, env overrides, local `worker_state.json` read/write, and secret redaction.
- `worker_client/registration.py`: registration flow against `POST /api/v1/browser-workers/register`.
- `worker_client/heartbeat.py`: heartbeat flow against `POST /api/v1/browser-workers/{worker_id}/heartbeat` with `X-Worker-Secret` and signed Phase 26 headers.
- `worker_client/runtime.py`: local worker runtime compatible with `/health`, `/sessions`, `/actions`, `/sessions/{session_id}/close`, and `/ui-access/capabilities`.
- `worker_client/cli.py`: `python -m worker_client.cli register`, `heartbeat`, `serve`, and `start`.
- `worker_client/worker_config.example.yaml`: safe template copied locally to `worker_config.yaml`.

Security boundary:

- `worker_config.yaml` and `worker_state.json` are local-only and ignored by Git.
- The plaintext `worker_secret` is returned once by the server and stored only in customer-machine `worker_state.json`.
- Phase 27 does not add OpenClaw integration, browser account login, cookie injection, proxy pools, fingerprint bypass, captcha handling, social-platform automation, or a hosted worker fleet.

## Phase 29 Worker Runtime Manager Architecture

`worker_client/runtime_manager.py` is the local control layer for customer-machine workers. It coordinates runtime lifecycle, heartbeat thread, runtime health, and `runtime_state`. Local state is written through `worker_client/status.py` to `worker_client/runtime_state/status.json`; local logs are written through `worker_client/logging.py` to `worker_client/logs/worker.log` with secret redaction. `worker_client/local_api_client.py` is the future Worker Console Foundation client.

Local management API exposed by `worker_client/runtime.py`: `GET /local/status`, `GET /local/health`, `POST /local/runtime/start`, `POST /local/runtime/stop`, `POST /local/runtime/restart`, `POST /local/heartbeat/start`, `POST /local/heartbeat/stop`, `GET /local/logs`.

`Desktop Runtime Placeholder` lives in `worker_client/desktop/`; Phase 29 has no GUI, no Electron, no Tauri, no PySide, no system tray, and no exe/dmg packaging.

## Phase 30 Worker Console GUI Foundation

`worker_console` is an independent local Web GUI project built with Vite, React, TypeScript, and Tailwind. It is not served by the central API container. Operators run it locally during worker-machine operation.

Architecture:

```text
Worker Console Web UI
↓
worker_console/src/api/localWorkerClient.ts
↓
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
↓
worker_client.runtime /local/* API
↓
Worker Runtime Manager
```

Pages: Dashboard, Runtime Control, Logs, Connection Info. Current boundary: no system tray, no auto update, no Electron, no Tauri, no PySide, no exe / dmg.
## Phase 31: Worker Console Desktop Architecture

`worker_console_desktop` is the Tauri desktop shell foundation. It runs on the customer machine and calls the `worker_client` Local API on `http://127.0.0.1:9100`.

Flow:

```text
Tauri Window
↓
React Worker Console UI
↓
worker_console_desktop/src/api/localWorkerClient.ts
↓
worker_client local API
↓
runtime_manager / status / logging
```

The desktop app only displays status/logs and sends runtime/heartbeat control requests. It does not include a system tray, autostart, auto update, formal installer, or real platform automation.

## Phase 32: System Tray Desktop Runtime Architecture

After Phase 32, the desktop runtime architecture is:

```text
Tauri System Tray
↓
tray-control event
↓
React Desktop Console
↓
localWorkerClient.ts
↓
worker_client Local API
↓
runtime_manager / heartbeat / status / logging
```

The close-window event is intercepted by Tauri. When `minimize_to_tray=true`, the window is hidden instead of exiting the process. Tray Runtime Control uses only the local HTTP API for runtime / heartbeat control; it does not execute shell commands or remote commands.

Desktop Status Sync periodically calls `GET /local/status` and `GET /local/health`, then updates the tray tooltip through a Tauri command.

## Phase 33 Conversation Runtime Architecture

Flow:

```text
user message
-> ConversationService
-> MemoryService lightweight lookup
-> PlanningService plan placeholder
-> ToolRegistry / ContentAgent / OpenClaw mock routing
-> assistant response
-> conversation_events polling timeline
```

Core files:

- `app/models/conversation.py`
- `app/schemas/conversation.py`
- `app/conversation/repositories/conversation_repository.py`
- `app/conversation/services/conversation_service.py`
- `app/api/routes/conversations.py`
- `worker_console/src/api/conversationClient.ts`
- `worker_console_desktop/src/api/conversationClient.ts`

Conversation Runtime does not replace Memory Foundation. It reuses `conversation_messages` by adding nullable `thread_id`; Phase 14 Memory session messages continue to use nullable-compatible `session_id`.

## Phase 34 Remote Browser Runtime Architecture

Remote Browser Runtime Foundation adds a real dispatch path from AI Server to customer-machine Worker:

```text
AI Server
-> BrowserRuntimeSessionService
-> RemoteBrowserProvider
-> BrowserWorkerSelector
-> BrowserWorkerClient
-> worker_client/browser_runtime
-> Playwright Chromium
-> storage/browser_screenshots
```

Core files:

- `app/models/browser_runtime.py` for `browser_runtime_sessions`
- `app/browser/services/browser_runtime_session_service.py`
- `app/browser/providers/remote_provider.py`
- `worker_client/browser_runtime/runtime.py`
- `worker_client/browser_runtime/session_manager.py`
- `worker_client/browser_runtime/playwright_provider.py`
- `worker_client/browser_runtime/schemas.py`

Worker Runtime API:

- `/browser/session/create`
- `/browser/session/{session_id}/navigate`
- `/browser/session/{session_id}/screenshot`
- `/browser/session/{session_id}/page`
- `/browser/session/{session_id}/close`

The runtime supports basic Chromium create / navigate / screenshot / page content / close. It does not support stealth browser, proxy rotation, cookie injection, login cloning, captcha bypass, remote desktop streaming, or DevTools remote control.

## Phase 35B Real Client Worker E2E Validation Architecture

Phase 35B adds validation capability rather than new runtime execution primitives.

```text
validate_real_client_worker_e2e.py
-> API health
-> worker health summary
-> available workers
-> expected_worker_name online check
-> browser runtime create / navigate / screenshot / page / close
-> JSON summary
```

If `expected_worker_name` is unavailable, the validator returns `SKIPPED` and does not call browser runtime action APIs. This preserves the distinction between validation readiness and a real customer-machine E2E result.

## Phase 35A: Browser Runtime Observability & Replay

```text
BrowserRuntimeSessionService
 -> BrowserRuntimeObservabilityService
 -> browser_runtime_events
 -> browser_runtime_snapshots
 -> browser_runtime_replays
 -> storage/browser_runtime_snapshots/{workspace_id}/{session_id}
 -> Worker Console Timeline / Snapshots / Replay metadata
```

Timeline Event Flow:

- create session -> `session_created`
- navigate -> `navigate_started` / `navigate_completed` / `action_failed`
- screenshot -> `screenshot_started` / `screenshot_completed`
- get page -> `page_snapshot_captured`
- close -> `session_closed`
- replay -> `replay_requested`

Snapshot Storage saves page HTML, page TXT, error JSON, and replay JSON. Screenshots still use `storage/browser_screenshots`. Replay Metadata Flow exports readable metadata only; it does not re-run browser actions. Failure Debug records action_type, target/url, worker_id, error, duration_ms, last known URL, and last page title.

Boundary: Phase 35A is not live stream, not VNC/noVNC, not DevTools remote control, and not replay re-execution. It does not implement real platform automation.

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
## Phase 38: Conversation Tool Execution Bridge Architecture

Completed: `ConversationToolRouter` owns the Routing Rules and maps a user message to Browser Bridge, OpenClaw mock bridge, RAG bridge, Content bridge, Planning bridge, or fallback. `ConversationService.run_conversation_turn` records `route_selected`, `tool_execution_started`, `tool_execution_completed`, `agent_execution_started`, `planning_execution_started`, `bridge_fallback`, `bridge_error`, and returns `route_name`, `selected_tool`, `events_created`, `success`, `summary`, and `result_metadata`.

Boundaries: this is not autonomous agent, not WebSocket, not SSE, no real platform publishing, no real OpenClaw, and no ComfyUI.

## Phase 39: Conversation Approval Flow Architecture

Phase 39 adds an approval gate between Conversation Runtime and the Tool Execution Bridge:

```text
user message
-> ConversationToolRouter
-> ConversationRiskPolicy
-> conversation_approvals
-> pending approvals panel
-> approve / reject / cancel
-> execute_after_approval
-> Tool Execution Gate
-> Tool / Agent / Planning
-> conversation_events
```

Core components:

- `ConversationRiskPolicy`: assigns `risk_level` from route/tool/action.
- `ConversationApprovalService`: owns `approval_status` transitions.
- `conversation_approvals`: stores `proposed_action` and `proposed_payload` so unreviewed actions do not execute directly.
- Tool Execution Gate: `auto_safe` executes low risk only; `review_first` creates approval for every route; `execute_after_approval` executes approved approval only.
- Frontends: Admin Dashboard, Worker Console, and Worker Console Desktop show a pending approvals panel.

Boundaries: this is not a full permission system, not WebSocket/SSE, and does not implement real platform publishing, login, captcha, proxy, fingerprint bypass, real OpenClaw, or ComfyUI.
## Phase 40: Conversation Playbook Architecture

Conversation Runtime now has three layers:

1. `ConversationToolRouter`: one-off rule-based routing.
2. `ConversationApprovalService` / `ConversationRiskPolicy`: review and safety gate.
3. `ConversationPlaybookService` / `ConversationPlaybookExecutor`: reusable template execution.

Playbook Run Flow:

`conversation_playbooks` -> `conversation_playbook_runs` -> step executor -> existing Tool / Agent / Planning bridge -> approval gate when needed -> `conversation_events` timeline -> assistant message.

Step details do not use a separate table in this phase. They are stored in `conversation_playbook_runs.output_payload.steps` with `step_index`, `step_type`, `status`, `input`, `output`, `error`, and `duration_ms`.

This is not a full workflow builder and not an autonomous agent. It is a Playbook Foundation.

## Phase 41 Output Library Architecture

Output Library sits after Conversation / Playbook / Tool execution:

```text
Conversation / Playbook / Tool / Browser Runtime
-> OutputArtifactService
-> output_artifacts
-> storage/output_artifacts/{workspace_id}/{artifact_id}/
-> Admin Dashboard / Worker Console / Desktop preview and export
```

`output_artifacts` is workspace-scoped and can link to `thread_id` and `playbook_run_id`. File artifacts such as screenshots and HTML snapshots keep `file_path` references and metadata instead of copying large files. Text artifacts such as `content_draft`, `rag_answer`, `report`, and `plan` can store bounded content directly.

Playbook artifact generation:
- `content_generation` -> `content_draft`
- `browser_screenshot_report` -> `screenshot` + `report`
- `rag_answer` -> `rag_answer`
- `trend_research_draft` -> `report` + `content_draft`
- `openclaw_mock_device_check` -> `json`

This is not a full DAM, not S3 / MinIO, and not production publishing asset management.
## Phase 42: Task Orchestration & Background Execution

This phase adds the Task Orchestration foundation: `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, and `TaskRetryPolicy`. Conversation / Playbook runs can use `execution_mode=background`, then `/api/v1/task-runs` exposes queued, running, waiting_approval, retrying, completed, failed, cancelled, expired state plus timeline events. `scheduled_at` supports scheduled runs; retry uses exponential backoff; approval resume continues to enforce the Phase 39 Approval Gate; Output Library artifacts are linked by `task_run_id`.

Boundary: this is an in-process queue, not Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue. It does not implement real publishing, real OpenClaw, ComfyUI, CAPTCHA handling, proxies, or fingerprint bypass.
## Phase 43: Task Scheduler Persistence & Worker Recovery (Completed)

Completed: Task Scheduler Persistence, `task_scheduler_state`, Task Lease fields on `task_runs`, `TaskRecoveryService`, Scheduler Health API, manual recovery API, Failed Diagnostics, and frontend scheduler health panels.

Task Lease: running task runs receive `lease_owner`, `lease_token`, `lease_expires_at`, and `heartbeat_at`. Expired lease and stale heartbeat are recoverable through scan or manual recover.

Recovery rules: running + expired lease or stale heartbeat -> retrying if retry budget remains, otherwise failed; pending scheduled due -> queued; retrying delay elapsed -> queued; waiting_approval is not auto-executed; completed/cancelled/expired are not recovered.

Admin Dashboard now shows Scheduler Health, lease status, recoverable badge, diagnostics panel, scheduled due indicator, and manual recover. Worker Console and Worker Console Desktop show simplified Task recovery state.

Boundary: this remains an in-process scheduler foundation, not Celery, not Kubernetes, and not production HA distributed queue.

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
## Phase 46 Architecture: Workflow Graph Runtime

Phase 46 adds `workflow_graphs`, `workflow_graph_nodes`, `workflow_graph_edges`, `workflow_replays`, `WorkflowExecutionPlanner`, and `SafeConditionEvaluator` above the Phase 45 Workflow State layer. Graph runtime supports Conditional Execution, dependency resolution, Retry/Fallback Path planning, and Replay Foundation metadata while preserving boundaries: not a visual DAG builder, not distributed orchestration engine, and not ComfyUI.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47: Workflow Template Registry & Versioning

Architecture now includes `workflow_templates`, `workflow_template_versions`, and `workflow_template_runs`. `WorkflowTemplateRegistryService` and `WorkflowTemplateCompatibilityService` turn Workflow Graph Runtime definitions into reusable templates. Built-in templates include `browser_screenshot_report_graph`, `content_generation_graph`, `rag_answer_graph`, `approval_then_browser_graph`, `openclaw_mock_inspect_graph`, and `task_retry_demo_graph`. Template runs link `workflow_template_id`, `workflow_template_version_id`, and `workflow_template_run_id` while preserving approval and risk gates.

Boundary: this is not a visual DAG builder, does not connect ComfyUI, and does not perform real platform automation.
<!-- PHASE47_SYNC:END -->
