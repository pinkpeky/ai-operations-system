# AI Operations System Project Overview

Last updated: 2026-05-14

This is the entry point for `E:\ai-operations-system`. After Phase 10.5, `docs/` is the project Single Source of Truth. After Phase 27, this source of truth is also verified by runtime checks through `scripts/verify_docs_runtime.py`.

## Project Summary

AI Operations System is a backend-first AI automation platform. It combines task orchestration, Agentic RAG, workspace isolation, knowledge lifecycle management, hybrid retrieval, reranking, evaluation trace storage, content generation, file-based knowledge ingestion, task reliability observability, foundational internal Tool Calling, Agent Memory foundation, fixed-chain Multi-Agent foundation, Agent Planning Foundation, Browser Adapter Foundation, Playwright Local Provider Integration, Remote Browser Worker Foundation, Real Browser Worker Service, Browser Worker Reliability, Persistent Browser Profile Foundation, Browser Profile Health & Recovery, Human-in-the-loop Browser Control, Browser Worker UI Access Placeholder, Browser Worker Security & Access Control, Customer Machine Worker Bootstrap, and OpenClaw Worker Adapter Foundation.

The project is not a frontend dashboard. It is a backend foundation for future content agents, support agents, data analysis agents, tool-calling agents, browser automation, monitoring, and more advanced multi-agent workflows.

## Current Status

Phase 1 through Phase 28 are completed.

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
- Phase 12 Task Reliability & Observability with `task_events`, `task_logs`, `cancelled` / `timeout` status, task control APIs, and workspace-scoped summary.
- Phase 13 Tool Calling Foundation with `BaseTool`, `ToolRegistry`, builtin tools, `tool_call_logs`, tool execution APIs, and BaseAgent manual tool execution support.
- Phase 14 Memory Foundation with `conversation_sessions`, `conversation_messages`, `agent_memories`, `memory_operation_logs`, Memory API, BaseAgent memory hooks, and Agentic RAG memory trace.
- Phase 15 Multi-Agent Foundation with `AgentRegistry`, `agent_runs`, `agent_messages`, `agent_handoffs`, fixed Agent Chain execution, `ToolAgent`, and memory-aware run metadata.
- Phase 16 Agent Planning Foundation with `plans`, `plan_steps`, `plan_reviews`, `SimplePlannerAgent`, step execution, retry/skip state support, review records, and plan-level `memory_trace`.
- Phase 17 Browser Automation Adapter Foundation with `browser_sessions`, `browser_actions`, `browser_action_logs`, `BrowserProvider`, `MockBrowserProvider`, `PlaywrightBrowserProvider` placeholder, `BrowserService`, Browser APIs, and `browser_tool`.
- Phase 18 Playwright Local Provider Integration with `PlaywrightLocalProvider`, `BROWSER_PROVIDER=playwright_local`, real local Chromium execution, `browser_id`, `page_id`, `provider_session_metadata`, action runtime fields, `screenshot_path`, `page_title`, `selector`, `target_url`, Screenshot System, `GET /api/v1/browser/screenshot/{session_id}/{filename}`, and `browser_tool` support for `get_page_content`.
- Phase 19 Remote Browser Worker Foundation with `RemoteBrowserProvider`, `BrowserWorkerClient`, `browser_workers`, `browser_worker_sessions`, `browser_worker_actions`, Worker Registration, Worker Heartbeat, Worker Runtime Mock, `BROWSER_PROVIDER=remote`, `BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS`, and `BROWSER_WORKER_RETRY_COUNT`.
- Phase 20 Real Browser Worker Service with independent `browser-worker` container, `worker/main.py`, `worker/browser_worker/playwright_runtime.py`, Playwright Chromium runtime, `http://browser-worker:9100`, `BROWSER_WORKER_DEFAULT_URL`, and `worker/screenshots` storage.
- Phase 21 Browser Worker Reliability with `BrowserWorkerHealthService`, `BrowserWorkerSelector`, `BrowserSessionCleanupService`, `ScreenshotCleanupService`, worker capacity fields (`max_sessions`, `active_sessions`, `max_actions_per_minute`, `current_load`, `priority`, `error_message`, `last_seen`), action retry fields (`retry_count`, `max_retries`), stale worker detection, least loaded worker selection, session cleanup, action retry, and manual screenshot cleanup.
- Phase 22 Persistent Browser Profile Foundation with `browser_profiles`, `BrowserProfileService`, `profile_id`, `profile_path`, `persistent_context_enabled`, profile lock/release, `worker/profiles/{workspace_id}/{profile_id}`, and worker-side `launch_persistent_context`.
- Phase 23 Browser Profile Health & Recovery with `BrowserProfileHealthService`, `BrowserProfileBackupService`, `BrowserProfileCleanupService`, `browser_profile_usage_logs`, `health_status`, `usage_count`, `health/summary`, stale lock recovery, profile backup, restore, cleanup, and profile runtime health tracking.
- Phase 24 Human-in-the-loop Browser Control with `BrowserHumanControlService`, `browser_human_control_sessions`, `browser_human_control_events`, `human_control_status`, `human_control_session_id`, `paused_at`, `resumed_at`, session paused/resumed flow, worker metadata-level human-control endpoints, and `browser_tool` actions `request_human_control` / `complete_human_control`.
- Phase 25 Browser Worker UI Access Placeholder with `BrowserUIAccessService`, `browser_ui_access_sessions`, `access_token_hash`, placeholder URL generation, `remote_control_url`, `live_view_url`, `devtools_url=null`, token validation/revoke/expire APIs, worker `/ui-access/capabilities`, and `browser_tool` actions `create_ui_access` / `revoke_ui_access`.
- Phase 26 Browser Worker Security & Access Control with `BrowserWorkerAuthService`, `worker_secret_hash`, `api_key_hash`, `last_auth_at`, `auth_status`, `allowed_actions`, `allowed_domains`, signed worker request headers (`X-Worker-Signature`, `X-Worker-Timestamp`, `X-Worker-Nonce`), UI Access Scope fields (`scopes`, `one_time`, `used_at`, `revoked_reason`, `client_ip`, `user_agent`), `BrowserActionPolicyService`, `browser_security_audit_logs`, and security policy / audit APIs.
- Phase 27 Customer Machine Worker Bootstrap with `worker_client`, `worker_config.example.yaml`, local `worker_config.yaml`, local-only `worker_state.json`, CLI commands `python -m worker_client.cli register`, `heartbeat`, `serve`, and `start`, customer machine registration flow, heartbeat flow, local worker runtime, and compatibility with the existing Browser Worker protocol.
- Phase 28 OpenClaw Worker Adapter Foundation with `worker_client/openclaw`, `BaseOpenClawProvider`, `MockOpenClawProvider`, `OpenClawRuntime`, server-side `OpenClawWorkerClient`, `openclaw_tool`, `openclaw_action_logs`, OpenClaw mock worker runtime routes, and `/api/v1/openclaw/*` APIs.

Experimental capabilities:

- Local reranker provider is a placeholder interface. The active reranker is still mock.
- RAG Eval stores trace and manual score, but does not compute automatic metrics yet.
- Local Ollama providers are supported, but default Docker smoke tests use mock providers unless `.env` enables local providers.

Planned capabilities:

- Real reranker model integration.
- Real BM25 or external search engine.
- RAG metrics and batch evaluation.
- Advanced Tool Calling with autonomous planning, function calling, ReAct, and planner loops.
- Vector memory and graph memory.
- Autonomous memory planning and summarization with real LLM.
- Advanced Multi-Agent orchestration with autonomous planner, dynamic handoff policy, and ReAct-style loops.
- Real OpenClaw integration, Browser Agent, and platform-specific automation.
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

OpenClaw Worker Adapter Foundation:

```text
API Server / openclaw_tool
 -> OpenClawService
 -> BrowserWorkerSelector capability=openclaw
 -> OpenClawWorkerClient
 -> worker_client /openclaw/* mock runtime
 -> MockOpenClawProvider
 -> openclaw_action_logs + browser_security_audit_logs
```

Current OpenClaw boundary: `OPENCLAW_PROVIDER=mock`, `OPENCLAW_ENABLED=True`, and `OPENCLAW_ACTION_TIMEOUT_SECONDS=60.0`. The adapter is a placeholder for future OpenClaw execution. It does not call real OpenClaw, does not automate TikTok / YouTube / X, and does not implement login, cookie injection, proxy pools, fingerprint bypass, or captcha automation.

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

Task Reliability & Observability:

```text
Task API / Scheduler / TaskExecutor
 -> tasks.status: pending/running/retry/failed/completed/cancelled/timeout
 -> task_events lifecycle records
 -> task_logs structured records
 -> tasks.duration_ms
 -> GET /api/v1/observability/summary
```

Tool Calling Foundation:

```text
Agent or Tool API
 -> ToolRegistry
 -> BaseTool input validation
 -> builtin tool execute
 -> workspace-scoped business layer
 -> tool_call_logs
 -> tool result returned to Agent or API
```

Current builtin tools:

- `rag_search_tool`: calls current Hybrid Search + Reranker.
- `file_search_tool`: queries `documents` and metadata in the current workspace.
- `create_task_tool`: creates a task in the current workspace.
- `get_task_status_tool`: reads task status in the current workspace.
- `current_runtime_tool`: returns current runtime provider/search/upload settings and reads `CURRENT_RUNTIME.md` when available.
- `browser_tool`: executes safe browser actions through the configured BrowserProvider; default is `MockBrowserProvider`, while Phase 18 supports `PlaywrightLocalProvider` for bounded local Chromium tests.

Memory Foundation:

```text
Agent or API
 -> MemoryService
 -> conversation_sessions / conversation_messages
 -> PostgreSQL text search over agent_memories
 -> prompt memory context
 -> LLM response + memory_trace
```

Current memory tables:

- `conversation_sessions`
- `conversation_messages`
- `agent_memories`
- `memory_operation_logs`

Current memory APIs:

- `POST /api/v1/memory/sessions`
- `GET /api/v1/memory/sessions`
- `GET /api/v1/memory/sessions/{session_id}`
- `POST /api/v1/memory/messages`
- `GET /api/v1/memory/messages/{session_id}`
- `POST /api/v1/memory/memories`
- `GET /api/v1/memory/memories`
- `DELETE /api/v1/memory/memories/{memory_id}`

Multi-Agent Foundation:

```text
POST /api/v1/multi-agent/runs
 -> agent_runs
 -> fixed Agent Chain
    content_planner
    -> rag_agent
    -> content_agent
    -> review_agent
 -> agent_messages
 -> agent_handoffs
 -> run output + handoff_trace
```

Current registered agents:

- `content_planner`: lightweight mock planning agent.
- `rag_agent`: wrapper around `AgenticRAGOrchestrator`.
- `content_agent`: wrapper around `ContentAgent`.
- `review_agent`: lightweight mock review agent.
- `runtime_agent`: reads runtime information through `current_runtime_tool`.
- `tool_agent`: calls current `ToolRegistry` builtin tools.

Phase 15 intentionally implements a fixed Agent Chain, not autonomous planning, not ReAct, and not Browser Agent automation.

Agent Planning Foundation:

```text
POST /api/v1/plans
 -> SimplePlannerAgent
 -> plans
 -> plan_steps
 -> execute plan
    -> AgentRegistry or ToolRegistry
    -> step output / duration / error
 -> plan_reviews
 -> Plan Execution Flow result + memory_trace
```

Current planning steps are rule-based and bounded. Phase 16 supports plan creation, step execution, retry/skip state at the service layer, cancellation, review records, and workspace-scoped queries. It does not implement autonomous AGI planning, tree-of-thought, recursive planning, infinite Agent loops, ReAct, or Browser Agent automation.

Browser Automation Adapter Foundation:

```text
Browser API / browser_tool / plan step
 -> BrowserService
 -> BrowserProvider
 -> MockBrowserProvider
 -> browser_sessions / browser_actions / browser_action_logs
```

Phase 17 adds a provider abstraction for browser automation without starting a real browser. The active provider is `MockBrowserProvider`; `PlaywrightBrowserProvider` is a placeholder that returns clear non-execution responses. Browser actions are workspace-scoped, persisted with `duration_ms`, and logged in `browser_action_logs`. Planning can execute a step with `tool_name=browser_tool`, but this is still a bounded manual tool path, not autonomous browser planning.

Playwright Local Provider Integration:

```text
Browser API / browser_tool
 -> BrowserService
 -> PlaywrightLocalProvider
 -> local headless Chromium
 -> browser_actions runtime fields
 -> screenshots/{workspace_id}/{session_id}/{filename}.png
 -> browser_action_logs
```

Phase 18 keeps `BROWSER_PROVIDER=mock` as the default, but `BROWSER_PROVIDER=playwright_local` enables real local Chromium execution for bounded tests. Supported actions are `navigate`, `click`, `type_text`, `screenshot`, and `get_page_content`. Navigation is intentionally restricted to `example.com`, local test pages, and static `file://` URLs. This phase does not implement Browser Agent, autonomous browser planning, login automation, cookies, fingerprint bypass, OCR, visual AI, social platform automation, or remote Browser Worker execution.

Remote Browser Worker Foundation:

```text
AI Server
 -> RemoteBrowserProvider
 -> BrowserWorkerClient
 -> Browser Worker API
 -> Worker Runtime Mock
```

Phase 19 adds the remote browser worker protocol inside the same project. Workers can be registered, heartbeat can update `online` / `busy` / `error` status, and `BROWSER_PROVIDER=remote` dispatches browser actions through `BrowserWorkerClient`. The current worker runtime is a mock API under `/api/v1/browser-worker-runtime/*`; it does not start a real external worker and does not perform platform automation.

Real Browser Worker Service:

```text
API Server -> Worker
FastAPI API Server
 -> RemoteBrowserProvider
 -> BrowserWorkerClient
 -> http://browser-worker:9100
 -> worker/main.py
 -> worker/browser_worker/playwright_runtime.py
 -> Playwright Chromium
 -> worker/screenshots/{workspace_id}/{remote_session_id}/{filename}.png
```

Phase 20 upgrades the Phase 19 protocol from an in-process mock runtime to an independently runnable `browser-worker` FastAPI service. The worker exposes `GET /health`, `POST /sessions`, `POST /actions`, and `POST /sessions/{session_id}/close`. Docker Compose now runs a separate `browser-worker` container on port `9100`; API Server calls it through `BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100` after a worker is registered with that `base_url`.

The worker uses headless Playwright Chromium only. Supported actions are `navigate`, `click`, `type_text`, `scroll`, `screenshot`, and `get_page_content`. The safety boundary remains strict: only `example.com`, local test pages, and static file pages are allowed. Phase 20 still does not implement TikTok, YouTube, X, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha automation, OCR, visual AI, OpenClaw, or autonomous browser agents.

Browser Worker Reliability:

```text
RemoteBrowserProvider
 -> BrowserWorkerSelector
 -> least loaded worker with status=online and capacity available
 -> BrowserWorkerClient
 -> action timeout / retry / retry_logs
 -> browser_worker_actions.retry_count / max_retries
```

Phase 21 adds reliability and recovery foundations around the worker protocol. `BrowserWorkerHealthService` marks stale workers offline when heartbeat age exceeds `BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS`. `BrowserWorkerSelector` filters by `workspace_id`, `status=online`, capability, and capacity, then selects the least loaded worker using `current_load`, `active_sessions`, and `priority`. `BrowserSessionCleanupService` closes stale sessions or marks sessions failed when their worker is offline or in error. `ScreenshotCleanupService` supports manual, workspace-scoped screenshot cleanup with dry-run as the default.

New runtime knobs are `BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS`, `BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS`, `BROWSER_SESSION_TIMEOUT_SECONDS`, `BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS`, `BROWSER_ACTION_TIMEOUT_SECONDS`, `BROWSER_ACTION_RETRY_COUNT`, `BROWSER_ACTION_RETRY_BACKOFF_SECONDS`, and `SCREENSHOT_RETENTION_DAYS`. Phase 21 remains reliability infrastructure only: no TikTok, YouTube, X, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, OCR, visual AI, OpenClaw, or autonomous browser planning.

Persistent Browser Profile Foundation:

```text
BrowserProfileService
 -> browser_profiles
 -> Profile Lock
 -> BrowserSession(profile_id, profile_path, persistent_context_enabled)
 -> RemoteBrowserProvider
 -> browser-worker
 -> launch_persistent_context
 -> worker/profiles/{workspace_id}/{profile_id}
 -> Profile Release
```

Phase 22 adds `browser_profiles` and profile lifecycle APIs. Profiles can be created, listed, loaded, locked, released, and logically deleted. A profile can be locked by only one browser session at a time through `locked_by_session_id` and `locked_at`. When `POST /api/v1/browser/sessions` receives `profile_id` and `use_persistent_profile=true`, the API locks the profile, passes profile metadata to the worker, and releases the profile when `POST /api/v1/browser/sessions/{session_id}/close` is called. The worker uses Playwright `launch_persistent_context` only for profile-backed sessions and stores state under `worker/profiles/{workspace_id}/{profile_id}`.

Phase 22 does not inject cookies, perform login, configure browser fingerprints, bypass anti-bot checks, automate social platforms, or introduce real platform automation.

Browser Profile Health & Recovery:

```text
browser_profiles
 -> health_status / last_health_check_at / last_error
 -> usage_count / browser_profile_usage_logs
 -> BrowserProfileHealthService
 -> stale lock recovery
 -> BrowserProfileBackupService
 -> profile backup / restore
 -> BrowserProfileCleanupService
 -> cleanup deleted / corrupted / unused profiles
```

Phase 23 extends the persistent profile layer with health fields (`health_status`, `last_health_check_at`, `last_error`, `usage_count`, `corrupted_at`, `backup_path`, `last_backup_at`) and a `browser_profile_usage_logs` audit table. `BrowserProfileHealthService` validates profile paths, records health checks, summarizes profile health through `GET /api/v1/browser/profiles/health/summary`, marks warning/corrupted/stale profiles, increments usage count, and recovers stale locks. `BrowserProfileBackupService` stores zip backups under `worker/profile_backups/{workspace_id}/{profile_id}` and enforces `BROWSER_PROFILE_MAX_BACKUPS`. `BrowserProfileCleanupService` supports dry-run cleanup for deleted, corrupted, and unused profile directories.

New runtime knobs are `BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS`, `BROWSER_PROFILE_BACKUP_ENABLED`, `BROWSER_PROFILE_MAX_BACKUPS`, `BROWSER_PROFILE_UNUSED_DAYS`, and `BROWSER_PROFILE_BACKUP_ROOT`. Phase 23 still does not implement account login, cookie injection, browser fingerprint bypass, proxy pools, captcha handling, TikTok / YouTube / X automation, or autonomous browser planning.

Human-in-the-loop Browser Control:

```text
BrowserService active session
 -> BrowserHumanControlService.request_control
 -> browser_human_control_sessions status=requested
 -> browser_sessions status=paused
 -> approve/start
 -> worker metadata-level /human-control/start
 -> complete
 -> browser_sessions status=active
 -> browser_human_control_events
```

Phase 24 adds `browser_human_control_sessions` and `browser_human_control_events`, plus `browser_sessions.human_control_status`, `human_control_session_id`, `paused_at`, and `resumed_at`. `BrowserHumanControlService` manages request, approve, start, complete, cancel, expire, list, get, and event writing. While a browser session is paused, normal browser actions are rejected by the existing active-session guard; after `complete_control`, the session is resumed and actions can continue. The traceable lifecycle explicitly covers `session paused` and `session resumed`. `browser_tool` now supports `request_human_control` and `complete_human_control`, so planning steps can call `tool_name=browser_tool` with `action_type=request_human_control`.

The worker side exposes metadata-level `POST /human-control/start`, `POST /human-control/complete`, and `GET /human-control/status/{session_id}`. These routes do not implement VNC, noVNC, Chrome DevTools remote UI, account login, captcha handling, or platform automation; they only reserve the protocol boundary for future human takeover surfaces.

Browser Worker UI Access Placeholder:

```text
active human control session
 -> BrowserUIAccessService.create_access_session
 -> browser_ui_access_sessions
 -> access token hash stored in database
 -> plaintext token returned once
 -> placeholder URL:
    /ui/browser-control/{access_session_id}
    /ui/browser-live/{access_session_id}
 -> validate / revoke / expire
```

Phase 25 adds `browser_ui_access_sessions` and `BrowserUIAccessService`. It stores only `access_token_hash`, never the plaintext token, and the plaintext token is returned only by `POST /api/v1/browser/ui-access`. The generated `remote_control_url` and `live_view_url` are placeholder URL values such as `http://localhost:8000/ui/browser-control/{access_session_id}` and `http://localhost:8000/ui/browser-live/{access_session_id}`; `devtools_url` is currently `null`. `browser_tool` supports `create_ui_access` and `revoke_ui_access`.

Worker UI capabilities are declared through `GET /ui-access/capabilities` and the in-process mock runtime mirrors this at `GET /api/v1/browser-worker-runtime/ui-access/capabilities`. The response explicitly says `vnc=false`, `novnc=false`, `devtools=false`, and `placeholder=true`. Phase 25 does not implement real VNC, noVNC, Chrome DevTools remote UI, live browser video, platform login, captcha handling, cookie injection, proxy pools, fingerprint bypass, or TikTok / YouTube / X automation.

Browser Worker Security & Access Control:

```text
worker register
 -> generated worker_secret returned once
 -> worker_secret_hash / api_key_hash stored only as hashes
 -> BrowserWorkerClient signed worker request
 -> browser-worker validates X-Worker-Signature / X-Worker-Timestamp / X-Worker-Nonce
 -> BrowserActionPolicyService validates action/domain/profile/worker capability/UI scope
 -> browser_security_audit_logs records security decisions
```

Phase 26 adds `BrowserWorkerAuthService`, worker secret hashing, signed worker request support, worker auth status fields, UI Access Scope validation, `BrowserActionPolicyService`, and `BrowserSecurityAuditLog` / `browser_security_audit_logs`. Worker registration can return a plaintext `worker_secret` once, while the database stores `worker_secret_hash` and optional `api_key_hash`. Worker records now include `last_auth_at`, `auth_status`, `allowed_actions`, and `allowed_domains`. UI access records now include `scopes`, `one_time`, `used_at`, `revoked_reason`, `client_ip`, and `user_agent`.

Browser Action Policy defaults are intentionally narrow: `BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1`, `BROWSER_BLOCKED_DOMAINS=` and `BROWSER_ALLOW_EXTERNAL_DOMAINS=False`. Policy checks can block unsupported action types, disallowed domains, denied profile access, missing worker capability, or missing UI access scope. Security audit events cover worker registration, worker auth success/failure, UI token creation/validation/revoke/expiry, action blocked by policy, and profile access denial.

Phase 26 is a security foundation only. It does not implement real social-platform security, account login, cookie injection, proxy pools, fingerprint bypass, captcha automation, TikTok / YouTube / X automation, or production external identity enforcement.

Customer Machine Worker Bootstrap:

```text
Customer machine
 -> worker_client/worker_config.yaml
 -> python -m worker_client.cli register
 -> POST /api/v1/browser-workers/register
 -> worker_client/worker_state.json stores worker_id + worker_secret locally
 -> python -m worker_client.cli serve
 -> local worker runtime on port 9100
 -> python -m worker_client.cli heartbeat
 -> signed heartbeat with worker_secret
 -> AI Server RemoteBrowserProvider dispatches actions to the customer machine worker URL
```

Phase 27 adds the `worker_client` package so a real customer machine, Windows PC, or Mac can bootstrap as a Browser Worker without running the Docker `browser-worker` container. The client reads `worker_config.yaml` from a copy of `worker_config.example.yaml`, supports environment overrides, registers with AI Server, stores the one-time `worker_secret` only in local `worker_state.json`, sends heartbeat requests with the Phase 26 signing mechanism, and exposes a local Worker Runtime API compatible with `GET /health`, `POST /sessions`, `POST /actions`, `POST /sessions/{session_id}/close`, and `GET /ui-access/capabilities`.

The CLI commands are `python -m worker_client.cli register`, `python -m worker_client.cli heartbeat`, `python -m worker_client.cli serve`, and `python -m worker_client.cli start`. `start` reuses an existing worker state unless `--force-register` is passed. `worker_state.json` and local `worker_config.yaml` are ignored by Git and must not be committed.

Phase 27 is a bootstrap foundation only. Phase 28 adds a mock OpenClaw adapter on top of that worker protocol, but it still does not implement real OpenClaw integration, TikTok / YouTube / X automation, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha automation, or real platform automation.

## Project Structure

```text
app/
  api/            FastAPI route registration and endpoint modules.
  agents/         LLM client, base agent, and ContentAgent.
  browser/        Browser Adapter providers, service, repository, sessions, actions, and logs.
  core/           Settings, logging, errors, and workspace context.
  db/             PostgreSQL, Redis, and Qdrant connection helpers.
  file_pipeline/  File upload parsers, text cleaning, and ingestion service.
  middleware/     Workspace context middleware.
  memory/         Conversation sessions, messages, Agent Memory repositories, and MemoryService.
  multi_agent/    AgentRegistry, MultiAgentService, fixed chain orchestration, run/message/handoff repositories.
  openclaw/       Server-side OpenClawWorkerClient, schemas, repository, service, and action logs.
  planning/       SimplePlannerAgent, PlanningService, plan/step/review repositories.
  rag/            Embedding, chunking, vector store, retrieval, hybrid search, and Agentic RAG.
  reranker/       Reranker provider abstraction and mock/local providers.
  repositories/   Database access layer.
  schemas/        Pydantic request and response models.
  services/       Prompt manager, queues, document lifecycle, eval service, scheduler.
  tools/          BaseTool, ToolRegistry, builtin tools, and Tool Calling foundation.
  workers/        TaskExecutor and task handlers.
worker/
  main.py                         Standalone FastAPI Browser Worker entrypoint.
  browser_worker/config.py         Worker runtime configuration.
  browser_worker/runtime.py        Worker runtime interface.
  browser_worker/playwright_runtime.py  Headless Chromium implementation.
  browser_worker/schemas.py        Worker request/response schemas.
worker_client/
  config.py                        YAML/env config and local worker_state.json handling.
  registration.py                  AI Server worker registration client.
  heartbeat.py                     Signed heartbeat client and loop.
  runtime.py                       Customer machine Worker Runtime API.
  openclaw/                       Mock OpenClaw provider, schemas, and runtime routes.
  cli.py                           register / heartbeat / serve / start CLI.
  worker_config.example.yaml       Safe example config; copy to worker_config.yaml locally.
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
BROWSER_PROVIDER=mock
BROWSER_TIMEOUT_SECONDS=30.0
BROWSER_HEADLESS=True
BROWSER_TYPE=chromium
BROWSER_VIEWPORT_WIDTH=1280
BROWSER_VIEWPORT_HEIGHT=720
BROWSER_SCREENSHOT_DIR=screenshots
BROWSER_WORKER_AUTH_ENABLED=True
BROWSER_WORKER_AUTH_STRICT=False
BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1
BROWSER_BLOCKED_DOMAINS=
BROWSER_ALLOW_EXTERNAL_DOMAINS=False
BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30.0
BROWSER_WORKER_RETRY_COUNT=2
BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100
```

Task statuses:

```text
pending
running
retry
failed
completed
cancelled
timeout
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

Builtin tools:

- `rag_search_tool`
- `file_search_tool`
- `create_task_tool`
- `get_task_status_tool`
- `current_runtime_tool`
- `browser_tool`

Memory APIs:

- `POST /api/v1/memory/sessions`
- `POST /api/v1/memory/messages`
- `POST /api/v1/memory/memories`
- `GET /api/v1/memory/memories`

Multi-Agent APIs:

- `GET /api/v1/agents/registry`
- `POST /api/v1/multi-agent/runs`
- `GET /api/v1/multi-agent/runs`
- `GET /api/v1/multi-agent/runs/{run_id}`
- `POST /api/v1/multi-agent/runs/{run_id}/execute-chain`
- `GET /api/v1/multi-agent/runs/{run_id}/messages`
- `GET /api/v1/multi-agent/runs/{run_id}/handoffs`

Planning APIs:

- `POST /api/v1/plans`
- `GET /api/v1/plans`
- `GET /api/v1/plans/{plan_id}`
- `POST /api/v1/plans/{plan_id}/execute`
- `POST /api/v1/plans/{plan_id}/cancel`
- `GET /api/v1/plans/{plan_id}/steps`
- `GET /api/v1/plans/{plan_id}/reviews`

Browser APIs:

- `POST /api/v1/browser/sessions`
- `GET /api/v1/browser/sessions`
- `POST /api/v1/browser/actions`
- `GET /api/v1/browser/actions/{session_id}`
- `GET /api/v1/browser/screenshot/{session_id}/{filename}`
- `GET /api/v1/browser/logs/{session_id}`
- `POST /api/v1/browser-workers/register`
- `POST /api/v1/browser-workers/{worker_id}/heartbeat`
- `GET /api/v1/browser-workers`
- `GET /api/v1/browser-worker-runtime/health`
- `POST /api/v1/browser-worker-runtime/sessions`
- `POST /api/v1/browser-worker-runtime/actions`
- `POST /api/v1/browser-worker-runtime/sessions/{session_id}/close`
- `POST /api/v1/browser/ui-access`
- `GET /api/v1/browser/ui-access/{access_session_id}`
- `POST /api/v1/browser/ui-access/{access_session_id}/revoke`
- `POST /api/v1/browser/ui-access/expire`
- `GET /api/v1/browser/ui-access/{access_session_id}/validate`
- `GET /api/v1/browser/security/audit-logs`
- `POST /api/v1/browser/security/policy/check`
- `GET /api/v1/browser-worker-runtime/ui-access/capabilities`
- `GET http://localhost:9100/health`
- `POST http://localhost:9100/sessions`
- `POST http://localhost:9100/actions`
- `POST http://localhost:9100/sessions/{session_id}/close`
- `GET http://localhost:9100/ui-access/capabilities`
- `POST /api/v1/browser-workers/{worker_id}/rotate-secret`
- `POST /api/v1/browser-workers/{worker_id}/revoke`

Not supported in Phase 11:

- PPTX
- XLSX
- OCR
- Images

## Current Limitations

- Local reranker is still a placeholder interface.
- Keyword retrieval uses PostgreSQL `ILIKE` and simple keyword scoring.
- No Elasticsearch, OpenSearch, or real BM25 engine.
- Memory is a PostgreSQL text-search foundation only; no vector memory, graph memory, autonomous memory planning, or personality memory is implemented.
- No LLM-native function calling, autonomous planning, ReAct loop, or autonomous browser automation.
- Multi-Agent is currently a fixed-chain foundation only; it does not include dynamic planning, autonomous routing, or ReAct.
- Planning is currently rule-based through `SimplePlannerAgent`; it does not include autonomous AGI planning, tree-of-thought, recursive planning, infinite Agent loops, or ReAct.
- No Browser Agent.
- `browser_tool` can use `MockBrowserProvider` or `PlaywrightLocalProvider`, but only for manually requested bounded actions.
- `PlaywrightBrowserProvider` remains a placeholder; real execution is implemented separately in `PlaywrightLocalProvider`.
- `PlaywrightLocalProvider` only allows `example.com`, local test pages, and static file URLs.
- `RemoteBrowserProvider` currently calls only the in-project Worker Runtime Mock unless an operator explicitly registers another base URL for future experiments.
- `browser-worker` is an independent local Docker service, but production-grade external worker fleets, scheduling, autoscaling, and remote machine deployment are not implemented yet.
- Browser UI Access is a placeholder only: no real VNC, noVNC, Chrome DevTools remote UI, or live browser screen stream exists yet.
- Browser Worker Security is a foundation layer only: it adds worker secret hashes, signed request plumbing, UI Access Scope checks, Browser Action Policy, and audit logs, but it is not a full RBAC/JWT/OAuth or real platform account security system.
- Customer Machine Worker Bootstrap provides `worker_client` only; it does not ship a managed remote worker fleet, platform account automation, or a hosted customer-machine installer.
- OpenClaw is currently a mock adapter foundation only through `MockOpenClawProvider`; no real OpenClaw runtime is called.
- No Selenium, TikTok, YouTube, X, OCR, visual AI, login automation, cookie injection, fingerprint bypass, proxy pool, captcha automation, real external Browser Worker deployment, or real platform automation.
- No Grafana or Prometheus.
- No frontend observability dashboard.
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
3. Vector/graph memory and higher-quality memory summarization.
4. Tool Calling advanced planning, function calling compatibility, and permission controls.
5. Dynamic Multi-Agent orchestration and policy-driven handoff.
6. Real noVNC / DevTools UI access and production Browser Worker fleet management after the placeholder protocol and safety model are hardened.
7. Real OpenClaw Worker route after worker bootstrap, profile safety, and human takeover boundaries are production-hardened.
8. Harder security policy management for worker fleets, scoped browser profiles, and production identity integration.
9. External observability with Prometheus and Grafana.
10. Full authentication and authorization.

## Phase 29: Worker Client Packaging & Worker Console Foundation

Phase 29 is completed. It upgrades the customer-machine `worker_client` from a set of CLI scripts into a locally manageable runtime foundation. This is not a GUI phase; it is the base layer that a future Worker Console GUI can call.

Completed runtime foundation:

- `Worker Runtime Manager` in `worker_client/runtime_manager.py` controls `start_runtime`, `stop_runtime`, `restart_runtime`, `runtime_health`, `start_heartbeat`, `stop_heartbeat`, and `runtime_state`.
- `worker_client/status.py` manages local `worker_client/runtime_state/status.json` with `worker_id`, `worker_name`, `workspace_id`, `server_url`, `runtime_running`, `heartbeat_running`, `registered`, `last_heartbeat_at`, `last_error`, `current_status`, `openclaw_enabled`, and `browser_enabled`.
- `worker_client/logging.py` writes local logs to `worker_client/logs/worker.log` with simple rotation and worker secret redaction.
- `worker_client/runtime.py` exposes local management routes: `GET /local/status`, `GET /local/health`, `POST /local/runtime/start`, `POST /local/runtime/stop`, `POST /local/runtime/restart`, `POST /local/heartbeat/start`, `POST /local/heartbeat/stop`, and `GET /local/logs`.
- `worker_client/local_api_client.py` provides a Python client for future Worker Console Foundation integration.
- `Packaging Scripts` live under `packaging/`, including `packaging/windows_start_worker.ps1` and `packaging/mac_start_worker.sh`.
- `Desktop Runtime Placeholder` lives under `worker_client/desktop/` and documents future Tauri, Electron, PySide, system tray, auto start, Worker Console GUI, and embedded browser control routes.

Current Phase 29 limits:

- no GUI
- no system tray
- no Electron
- no Tauri
- no PySide
- no EXE / DMG packaging
- no embedded browser-control UI
- no TikTok, YouTube, X, login automation, cookie injection, fingerprint bypass, proxy pool, captcha automation, or real platform automation

## Phase 30: Worker Console GUI Foundation

Phase 30 is completed. `worker_console` is an independent Vite + React + TypeScript + Tailwind local Web GUI for customer-machine Worker management. It connects to `VITE_LOCAL_WORKER_API=http://127.0.0.1:9100` by default and calls the Worker Client Local API from Phase 29.

Completed Worker Console GUI Foundation:

- Dashboard for `worker_name`, `worker_id`, `workspace_id`, `server_url`, `registered`, `runtime_running`, `heartbeat_running`, `current_status`, `last_heartbeat_at`, and `last_error`.
- Runtime Control for `POST /local/runtime/start`, `POST /local/runtime/stop`, `POST /local/runtime/restart`, `POST /local/heartbeat/start`, and `POST /local/heartbeat/stop`.
- Logs view backed by `GET /local/logs`, with refresh and error highlighting.
- Connection Info for `server_url`, `worker_base_url`, `runtime_port`, `openclaw_enabled`, and `browser_enabled`.
- Frontend Local API client: `worker_console/src/api/localWorkerClient.ts`.
- Error state: `Worker API unreachable`, `请确认 worker_client 是否启动`, and `请确认端口是否为 9100`.

Phase 30 current boundary: local Web GUI Foundation only, no system tray, no auto update, no Electron, no Tauri, no PySide, no exe / dmg, no TikTok / YouTube / X automation, no login automation, no proxy pools, no fingerprint bypass, no captcha automation, and no real platform automation.

## Phase 31: Worker Console Desktop App Foundation

Phase 31 is completed. `worker_console_desktop` upgrades the Phase 30 web console into a Tauri desktop shell foundation while preserving the same local Worker API contract. It is a desktop app foundation, not a production installer release.

Completed Worker Console Desktop App Foundation:

- Desktop shell project: `worker_console_desktop`.
- Tauri configuration: `worker_console_desktop/src-tauri/tauri.conf.json`.
- React + Vite + TypeScript + Tailwind frontend reused from the Worker Console workflow.
- Default local Worker API: `VITE_LOCAL_WORKER_API=http://127.0.0.1:9100`.
- Default status check: `http://127.0.0.1:9100/local/status`.
- Desktop window shows Worker status, runtime state, heartbeat state, connection info, and logs.
- Runtime controls call `POST /local/runtime/start`, `POST /local/runtime/stop`, `POST /local/runtime/restart`, `POST /local/heartbeat/start`, and `POST /local/heartbeat/stop`.
- Local API client: `worker_console_desktop/src/api/localWorkerClient.ts`.
- Development command: `npm run tauri dev`.
- Frontend build command: `npm run build`.
- Worker API unreachable state explicitly says the Worker Runtime is not started, asks the operator to start `worker_client`, or to use the packaging scripts.
- UI text includes `Worker Runtime 未启动` for local runtime detection failures.

Current Phase 31 boundary:

- no exe / dmg
- no system tray
- no auto update
- no autostart
- no formal installer release
- no TikTok / YouTube / X automation
- no login automation
- no cookie injection
- no proxy pool
- no fingerprint bypass
- no captcha automation
- no real platform automation

Future Worker Console Desktop roadmap: tray / autostart / installer can be layered on top of this Tauri shell after Worker security, profile safety, and human-control boundaries remain stable.
