# AI Operations System Project Overview

Last updated: 2026-05-15

This is the entry point for `E:\ai-operations-system`. After Phase 10.5, `docs/` is the project Single Source of Truth. After Phase 44, this source of truth is also verified by runtime checks through `scripts/verify_docs_runtime.py`.

## Project Summary

AI Operations System is a backend-first AI automation platform. It combines task orchestration, Agentic RAG, workspace isolation, knowledge lifecycle management, hybrid retrieval, reranking, evaluation trace storage, content generation, file-based knowledge ingestion, task reliability observability, foundational internal Tool Calling, Agent Memory foundation, fixed-chain Multi-Agent foundation, Agent Planning Foundation, Browser Adapter Foundation, Playwright Local Provider Integration, Remote Browser Worker Foundation, Real Browser Worker Service, Browser Worker Reliability, Persistent Browser Profile Foundation, Browser Profile Health & Recovery, Human-in-the-loop Browser Control, Browser Worker UI Access Placeholder, Browser Worker Security & Access Control, Customer Machine Worker Bootstrap, OpenClaw Worker Adapter Foundation, Remote Browser Runtime Foundation, Real Client Worker E2E Validation Plan, Browser Runtime Observability & Replay, Task Scheduler Persistence & Worker Recovery, and Output Artifact Pipeline & Export System.

The project is not a frontend dashboard. It is a backend foundation for future content agents, support agents, data analysis agents, tool-calling agents, browser automation, monitoring, and more advanced multi-agent workflows.

## Current Status

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate and after post-merge stabilization landed. PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after verification. PR #16 was accepted into the Phase 54 branch before PR #17 merged to `main`. Phase 56 was reverted and is not active. Phase 56A-56D readiness work has landed on `main`, adding CI gates, required-check documentation, release readiness artifacts, and scheduled server Docker smoke. Phase 57A-57D, Phase 58A-58E, and Phase 59A have also landed on `main`, adding the Admin Dashboard Run Cockpit, guarded cockpit actions, operator controls, deep links, refresh UX, Playbooks context, Output Library context handoff, Phase 58 closeout, and Run Cockpit search density.

The current next branch is `codex/phase-59-run-cockpit-workflow-handoff`, scoped to carrying `workflow_run_id` context from Run Cockpit into Workflows and Replay Center with linked workflow/runtime summary context.

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
- Phase 34 Remote Browser Runtime Foundation with `browser_runtime_sessions`, `BrowserRuntimeSessionService`, `app/browser/providers/remote_provider.py`, `worker_client/browser_runtime`, Browser Session Lifecycle, `storage/browser_screenshots`, Browser Sessions Panel, and `playwright install chromium` customer-worker setup.
- Phase 35B Real Client Worker E2E Validation Plan with `scripts/validate_real_client_worker_e2e.py`, explicit `SKIPPED` behavior when the real client worker is not online, Swagger validation flow, Worker Console validation checklist, and network safety guidance for Tailscale/VPN/LAN.
- Phase 35A Browser Runtime Observability & Replay with `browser_runtime_events`, `browser_runtime_snapshots`, `browser_runtime_replays`, `BrowserRuntimeObservabilityService`, Timeline Event Flow, Snapshot Storage, Replay Metadata Flow, Failure Debug, and Worker Console timeline/snapshot/replay panels.

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
- Browser Runtime Replay is metadata-only. It exports timeline/snapshot manifests but does not re-execute browser actions and is not live streaming, VNC, noVNC, or DevTools remote control.
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

## Phase 32: Worker Console System Tray & Desktop Runtime Foundation

Phase 32 is completed. `worker_console_desktop` now moves from a desktop shell foundation to a desktop runtime foundation with Tauri System Tray support, minimize-to-tray behavior, local runtime controls, and desktop status sync.

Completed Desktop Runtime Foundation:

- System Tray menu in `worker_console_desktop/src-tauri/src/main.rs`.
- Tray menu entries: Show Console, Hide Window, Start Runtime, Stop Runtime, Restart Runtime, Start Heartbeat, Stop Heartbeat, Refresh Status, and Quit.
- Minimize To Tray is enabled by default through `worker_console_desktop/src-tauri/desktop-runtime.json` with `minimize_to_tray=true`.
- Closing the desktop window hides it to the tray; Quit is the only tray menu item that exits the process.
- Tray Runtime Control emits local frontend events and the React app calls only the local Worker Client API.
- Desktop Status Sync calls `GET /local/status` and `GET /local/health` on a configurable interval.
- Tray tooltip shows `worker_name`, `current_status`, `runtime_running`, and `heartbeat_running`.
- Desktop settings live in `worker_console_desktop/src/settings.ts` and `worker_console_desktop/settings.example.json`.
- Desktop setting fields: `localWorkerApi`, `minimizeToTray`, and `refreshIntervalMs`.
- Logs panel now supports auto refresh, manual refresh, error highlight, clear display, and last updated time. Clear display only clears the frontend view and does not delete log files.
- AutoStart Placeholder docs live under `worker_console_desktop/autostart/`.
- Tauri Security stays minimal: no shell plugin, no filesystem-wide plugin, no process plugin, no arbitrary shell, and no remote command execution.

Current Phase 32 boundary:

- no formal installer
- no exe / dmg release
- no real autostart registration
- no auto-update
- no remote shell
- no arbitrary command execution
- no TikTok / YouTube / X automation
- no login automation
- no cookie injection
- no proxy pool
- no fingerprint bypass
- no captcha automation
- no real platform automation

## Phase 33: Conversation Runtime Foundation

Phase 33 is completed. It adds the first real Conversation Runtime layer so a frontend can send one sentence, persist it in a conversation thread, run bounded rule-based routing, and poll an event timeline.

Completed runtime components:

- Database tables and model layer: `conversation_threads`, `conversation_events`, and an extended `conversation_messages.thread_id` column. `conversation_messages.session_id` is nullable so Phase 14 Memory sessions and Phase 33 threads can share the message table without breaking old Memory APIs.
- Service layer: `ConversationService` in `app/conversation/services/conversation_service.py` with `create_thread`, `list_threads`, `get_thread`, `append_message`, `append_event`, `run_conversation_turn`, and `archive_thread`.
- API layer: `POST /api/v1/conversations`, `GET /api/v1/conversations`, `GET /api/v1/conversations/{thread_id}`, `POST /api/v1/conversations/{thread_id}/messages`, `GET /api/v1/conversations/{thread_id}/messages`, `GET /api/v1/conversations/{thread_id}/events`, and `POST /api/v1/conversations/{thread_id}/run`.
- Event timeline records `message_received`, `planning_started`, `plan_created`, `agent_started`, `tool_called`, `worker_action_started`, `worker_action_completed`, `assistant_response`, and `error` events.
- Rule-based routing only: messages containing search/browser/open-page keywords call `browser_tool`; messages containing content/copy/generate keywords call `ContentAgent`; messages containing `OpenClaw` call `openclaw_tool` mock.
- Worker Console Chat Panel Foundation in both `worker_console` and `worker_console_desktop`, including input box, Send button, Message list, Event Timeline, Refresh events, planning/tool/worker status display, and `conversationClient.ts`.
- Event feed is polling via `GET /api/v1/conversations/{thread_id}/events`. WebSocket and SSE are placeholders only and are not implemented.

Current Phase 33 boundaries:

- no TikTok / YouTube / X automation
- no login automation, cookie injection, proxy pool, fingerprint bypass, or captcha automation
- no real platform automation
- no real OpenClaw runtime
- no ComfyUI
- no real WebSocket or SSE streaming
- no Scheduler, TaskExecutor, Workspace Isolation, or Hybrid Search core logic changes

## Phase 34: Remote Browser Runtime Foundation

Phase 34 is completed. It upgrades the browser path from mock/local-only execution to a real Remote Browser Runtime foundation where the AI Server dispatches browser sessions and actions to a registered customer-machine worker.

Completed runtime components:

- Database model and migration for `browser_runtime_sessions`.
- Service layer: `BrowserRuntimeSessionService` manages create, get, navigate, screenshot, page fetch, close, activity updates, and stale status handling.
- Provider layer: `app/browser/providers/remote_provider.py` selects a healthy remote worker and calls the worker runtime through `BrowserWorkerClient`.
- Worker runtime layer: `worker_client/browser_runtime` implements the Playwright-backed runtime, session manager, schemas, and browser provider.
- Worker Runtime API: `/browser/session/create`, `/browser/session/{session_id}/navigate`, `/browser/session/{session_id}/screenshot`, `/browser/session/{session_id}/page`, and `/browser/session/{session_id}/close`.
- API Server routes: `/api/v1/browser-runtime/sessions`, `/api/v1/browser-runtime/sessions/{session_id}`, `/api/v1/browser-runtime/sessions/{session_id}/navigate`, `/api/v1/browser-runtime/sessions/{session_id}/screenshot`, `/api/v1/browser-runtime/sessions/{session_id}/page`, and `/api/v1/browser-runtime/sessions/{session_id}/close`.
- Browser Session Lifecycle: create remote session, persist local runtime session, navigate, capture screenshot, fetch page title/content, close remote session, and close local record.
- Screenshot Storage: runtime screenshots are saved under `storage/browser_screenshots` and configured by `BROWSER_RUNTIME_SCREENSHOT_DIR`.
- Worker Console Browser Sessions Panel: `worker_console` and `worker_console_desktop` now list active runtime sessions and can close them.
- Customer worker setup now explicitly includes `playwright install chromium`.

Current Phase 34 boundaries:

- no stealth browser
- no anti-detect browser
- no proxy rotation
- no cookie injection
- no captcha bypass
- no TikTok / YouTube / X automation
- no persistent login cloning
- no remote desktop streaming
- no DevTools remote control
- no OpenClaw real device
- no ComfyUI

## Phase 35A: Browser Runtime Observability & Replay

Phase 35A is completed. It adds observability and replay metadata around the Phase 34 Remote Browser Runtime. It does not require a real customer-machine worker; Docker `browser-worker` can be used for validation.

Completed runtime components:

- Database model and migration for `browser_runtime_events`, `browser_runtime_snapshots`, and `browser_runtime_replays`.
- Service layer: `BrowserRuntimeObservabilityService` supports event append, page snapshot capture, screenshot snapshot capture, error snapshot capture, event listing, snapshot listing, replay creation, and replay JSON export.
- Timeline Event Flow: create session writes `session_created`; navigate writes `navigate_started` / `navigate_completed` / `action_failed`; screenshot writes `screenshot_started` / `screenshot_completed`; page fetch writes `page_snapshot_captured`; close writes `session_closed`; replay creation writes `replay_requested`.
- Snapshot Storage: page HTML/text snapshots are stored under `storage/browser_runtime_snapshots/{workspace_id}/{session_id}/`; screenshots continue to use `storage/browser_screenshots`.
- Replay Metadata Flow: `browser_runtime_replays.replay_steps` stores readable timeline metadata and snapshot references. Replay is metadata-only and does not re-run browser actions.
- Failure Debug: failed actions write `action_failed` events and `snapshot_type=error` records with action type, target/url, worker id, error, duration, last known URL, and last page title when available.
- API routes: `GET /api/v1/browser-runtime/sessions/{session_id}/events`, `GET /api/v1/browser-runtime/sessions/{session_id}/snapshots`, `POST /api/v1/browser-runtime/sessions/{session_id}/replay`, `GET /api/v1/browser-runtime/replays/{replay_id}`, and `GET /api/v1/browser-runtime/replays/{replay_id}/export`.
- Worker Console Timeline: `worker_console` and `worker_console_desktop` Browser Sessions Panel now includes Timeline, Screenshot history, Page snapshots, Replay metadata, Refresh events, and Refresh snapshots.

Phase 35A boundaries:

- metadata-only replay, not browser action re-execution
- not live stream
- not VNC
- not noVNC
- not DevTools remote control
- no TikTok / YouTube / X automation
- no login automation, cookie injection, proxy pool, fingerprint bypass, captcha automation, or real platform automation

## Phase 35B: Real Client Worker E2E Validation Plan

Phase 35B is completed as a validation plan and script. It does not claim that a real customer machine was available during implementation.

Completed validation assets:

- `scripts/validate_real_client_worker_e2e.py`
- `docs/zh/REAL_CLIENT_WORKER_E2E.md`
- `docs/en/REAL_CLIENT_WORKER_E2E.md`
- pytest coverage for script behavior and documentation coverage
- docs verifier coverage for the new docs and script

The script validates:

- API health
- worker health summary
- available workers
- `expected_worker_name` online and available
- browser runtime session create
- navigate to `https://example.com`
- screenshot metadata
- page title/content
- close session

If the real customer-machine worker is unavailable, the script returns `SKIPPED` and reason `real client worker not online`; it does not execute browser actions and does not fabricate a successful E2E result.

Swagger validation flow:

1. `GET /api/v1/health`
2. `GET /api/v1/browser-workers/health/summary`
3. `GET /api/v1/browser-workers/available`
4. `POST /api/v1/browser-runtime/sessions`
5. `POST /api/v1/browser-runtime/sessions/{session_id}/navigate`
6. `POST /api/v1/browser-runtime/sessions/{session_id}/screenshot`
7. `GET /api/v1/browser-runtime/sessions/{session_id}/page`
8. `POST /api/v1/browser-runtime/sessions/{session_id}/close`

Worker Console validation checklist includes Web Console status/log checks and Desktop Console `npm run tauri dev` when Rust/MSVC is ready.

Security reminder: do not expose port 9100 to the public internet. Prefer Tailscale, VPN, or a trusted LAN.

## Phase 36: Server Admin Dashboard Foundation

Phase 36 is completed. It adds `admin_dashboard`, a standalone Vite + React + TypeScript + Tailwind Server Admin Dashboard Foundation for read-only monitoring of the AI Operations System.

Completed dashboard architecture:

- Admin Dashboard Foundation project: `admin_dashboard`.
- API client: `admin_dashboard/src/api/client.ts`.
- Runtime config: `VITE_AI_SERVER_API=http://localhost:8000`, `VITE_WORKSPACE_ID=demo-workspace`, `VITE_USER_ID=demo-user`.
- API modules: `workersApi`, `browserRuntimeApi`, `conversationsApi`, `tasksApi`, `openclawApi`, `auditApi`, and `ragApi`.
- Required headers: `X-Workspace-Id` and `X-User-Id`.
- Pages: Overview, Workers, Browser Runtime, Conversations, Tasks, OpenClaw, Audit Logs, RAG / Documents, and Settings.
- Auto refresh: Overview, Workers, and Browser Runtime refresh every 10 seconds; logs, events, and snapshots are manually refreshed.
- Browser Runtime page can create metadata-only replay records for debugging. It does not re-execute browser actions.

Admin Dashboard page map:

- Overview shows API health, Worker online/offline, Browser runtime session count, Task summary, Conversation count, OpenClaw mock status, and Recent errors.
- Workers shows registered browser workers, available workers, health summary, capabilities, capacity, heartbeat, and auth status.
- Browser Runtime shows sessions, Timeline events, Snapshots, and Replay metadata.
- Conversations shows conversation threads, messages, and polling events, and labels Conversation Runtime as a foundation.
- Tasks shows task list, events, logs, and payload summary in read-only mode.
- OpenClaw shows health, capabilities, and mock status only.
- Audit Logs shows browser security audit logs and basic event_type / success / target_type filtering.
- RAG / Documents shows embedding health, documents, collection metadata, and a simple hybrid search form.
- Settings stores `aiServerUrl`, `workspaceId`, and `userId` in localStorage.

Current Phase 36 boundaries:

- read-only monitoring foundation
- no login UI
- no permission UI
- no publishing business flow
- no real social platform control
- no production-grade operations backend
- no TikTok / YouTube / X automation
- no auto login, cookie injection, proxy pool, fingerprint bypass, captcha automation, or real platform automation

## Phase 37: Conversation Runtime Frontend Integration

Phase 37 is completed. It connects the Phase 33 Conversation Runtime to the Server Admin Dashboard, Worker Console Web, and Worker Console Desktop so operators can create conversation threads, send messages, run a conversation turn, and inspect a polling event timeline from the frontends.

Completed frontend architecture:

- Admin Dashboard Conversation page: create thread, thread list, thread detail, message list, event timeline, send message, run conversation, refresh messages, and refresh events.
- Admin Dashboard client: `admin_dashboard/src/api/conversationClient.ts` with `createThread`, `listThreads`, `getThread`, `sendMessage`, `listMessages`, `listEvents`, and `runConversation`.
- Worker Console Chat Panel: AI Server URL, Workspace ID, User ID, create thread, send and run, AI Server connected / disconnected / unreachable state, latest assistant message, and Polling Event Timeline.
- Desktop Chat Panel: same foundation as Worker Console Web; native Tauri validation still depends on customer-machine Rust/MSVC setup.
- Polling Event Timeline: frontends call `GET /api/v1/conversations/{thread_id}/events` manually or every 5 seconds. The UI shows `event_type`, `message`, `created_at`, and `payload JSON`.
- Development CORS: backend config `CORS_ALLOWED_ORIGINS` allows local dashboard, console, desktop, and `tauri://localhost` origins for development.

Current boundaries: this is not WebSocket, not SSE, and not a full ChatGPT UI. It does not implement real platform automation, real OpenClaw, ComfyUI, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, or publishing workflows.

## Phase 38: Conversation Runtime Tool Execution Bridge

Phase 38 is completed. Conversation Runtime now has a deterministic Tool Execution Bridge that turns one user message into a bounded route, executes the selected internal capability, writes readable events, and returns structured run metadata.

Completed:
- `ConversationToolRouter` in `app/conversation/tool_router.py` performs rule-based routing and returns `route_name`, `selected_tool`, `reason`, `confidence`, `tool_input`, and fallback route metadata.
- Routing Rules cover browser/search/page/screenshot requests, OpenClaw mock requests, RAG / knowledge-base search, background task creation, content generation, and planning / step decomposition.
- Browser Bridge Flow maps “open page and screenshot” to `browser_tool` composite execution: create runtime session, navigate, screenshot, get page metadata, and close session when possible.
- OpenClaw Mock Bridge Flow maps OpenClaw/device/app messages to `openclaw_tool` with `mock_inspect`; this remains mock-only and never calls real OpenClaw or real devices.
- RAG bridge calls `rag_search_tool` when `collection_name` is present; without a collection it returns a clear fallback message instead of silently searching the wrong knowledge base.
- Content bridge calls `ContentAgent` and stores `title`, `description`, `tags`, `cta`, and `raw_response` in `result_metadata`.
- Planning bridge calls `PlanningService`, creates a plan, returns `plan_id`, `steps`, and status, and does not execute real platform publishing.
- Conversation events now include `route_selected`, `tool_execution_started`, `tool_execution_completed`, `tool_execution_failed`, `agent_execution_started`, `agent_execution_completed`, `planning_execution_started`, `planning_execution_completed`, `bridge_fallback`, and `bridge_error`.
- `POST /api/v1/conversations/{thread_id}/run` now returns `user_message_id`, `assistant_message_id`, `route_name`, `selected_tool`, `events_created`, `success`, `summary`, and `result_metadata` while keeping the legacy `route`, `events`, and `output` fields.
- Admin Dashboard, Worker Console, and Worker Console Desktop show route selected, selected tool, tool status, result summary, event timeline, and full metadata panel.

Current boundaries: this is not autonomous agent planning, not WebSocket, not SSE, and not real platform automation. It does not implement TikTok / YouTube / X automation, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, real OpenClaw, ComfyUI, or publishing workflows.

## Phase 39: Conversation Execution Review & Approval Flow

Phase 39 is completed. Conversation Runtime now has an execution review gate before risky tool actions run. The goal is to prevent a single sentence from directly triggering medium/high risk Browser, OpenClaw, account/profile, upload, publish, or future platform actions.

Completed:
- Added `conversation_approvals` with `route_name`, `selected_tool`, `risk_level`, `approval_status`, `proposed_action`, `proposed_payload`, reviewer fields, timestamps, and metadata.
- Added `ConversationApprovalService` for `create_approval`, `approve`, `reject`, `cancel`, `expire_pending`, and `mark_executed`.
- Added `ConversationRiskPolicy` with low / medium / high risk classification.
- Added run modes: `auto_safe`, `review_first`, and `execute_after_approval`.
- Added Tool Execution Gate: low risk can run under `auto_safe`; medium/high risk creates a pending approval unless explicitly approved and executed.
- Added approval events: `approval_required`, `approval_created`, `approval_approved`, `approval_rejected`, `approval_cancelled`, `approval_expired`, `approval_executed`, `execution_blocked_pending_approval`, `execution_after_approval_started`, `execution_after_approval_completed`, and `execution_after_approval_failed`.
- Added approval APIs under `/api/v1/conversations/{thread_id}/approvals` and `/api/v1/conversation-approvals/{approval_id}`.
- Admin Dashboard, Worker Console, and Worker Console Desktop now show a pending approvals panel with proposed action preview, proposed payload JSON, risk badge, approve / reject / cancel buttons, and execute approved action button.

Risk policy:
- `low`: content generation, RAG search, and planning create-only actions.
- `medium`: browser navigate / screenshot / get page and OpenClaw mock inspect.
- `high`: browser click, form input, upload, publish, account/profile actions, real OpenClaw actions, and future social platform actions.

Current boundaries: this is not a full permission system, not WebSocket, not SSE, not real platform publishing, and not an autonomous agent. It does not implement TikTok / YouTube / X automation, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, real OpenClaw, or ComfyUI.
## Phase 40: Conversation Execution Templates & Playbooks

Status: completed.

Phase 40 adds Conversation Playbooks as reusable execution templates on top of the Phase 38 Tool Bridge and Phase 39 Approval Flow. The implemented database tables are `conversation_playbooks` and `conversation_playbook_runs`; step details are stored in `conversation_playbook_runs.output_payload.steps` rather than a separate step table.

Built-in Playbooks:
- `browser_search_summary`: browser page open/content collection/summary foundation.
- `browser_screenshot_report`: browser open/screenshot/title-content report foundation.
- `rag_answer`: knowledge-base retrieval answer foundation.
- `content_generation`: title, description, hashtags, and CTA generation.
- `trend_research_draft`: simulated trend research plan plus draft; no social-platform automation.
- `openclaw_mock_device_check`: mock OpenClaw device check only.

Runtime components:
- `ConversationPlaybookService` manages playbook listing, creation, updates, disabling, runs, and cancellation.
- `ConversationPlaybookExecutor` executes step types `message`, `route`, `tool`, `agent`, `planning`, `approval`, and `summarize`.
- Approval integration keeps Playbook medium/high risk steps behind the Phase 39 gate.
- Run modes continue to use `auto_safe`, `review_first`, and `execute_after_approval`.
- Medium/high risk Playbook steps create approvals through the Phase 39 gate; Playbooks do not bypass approval.
- Frontends now include a Playbook selector, Playbook Runs list, Step Timeline, and approval-aware execution controls.

Current limitation: this is not a full workflow builder, not autonomous agent planning, not WebSocket/SSE streaming, and not real social-media publishing.

## Phase 41: Playbook Run Artifacts & Output Library

Status: completed.

Phase 41 adds an Output Library foundation so reusable results from Conversation, Playbook, Tool, Browser Runtime, RAG, ContentAgent, Planning, and OpenClaw mock flows can be saved, viewed, reused, and exported.

Completed:
- Added `output_artifacts` for workspace-scoped artifacts linked to `thread_id` and optional `playbook_run_id`.
- Added `OutputArtifactService` with create, list, get, update, soft delete, export, create from Playbook Run, create from Conversation message, and create from Browser Runtime snapshot.
- Added artifact events: `artifact_created`, `artifact_exported`, `artifact_deleted`, and `artifact_linked_to_playbook_run`.
- Playbook completion automatically creates artifacts. Examples: `content_generation` creates a `content_draft`; `browser_screenshot_report` creates `screenshot` and `report`; `rag_answer` creates `rag_answer`; planning creates `plan`; OpenClaw mock creates `json`.
- Frontends now include Output Library panels. Admin Dashboard has an Output Library page; Conversation pages support Save as Artifact, generated artifacts, preview, and Export markdown.
- Export formats: markdown, json, and txt. File artifacts keep `file_path` metadata and do not copy large screenshots.

Artifact types: `text`, `markdown`, `json`, `screenshot`, `html_snapshot`, `report`, `plan`, `rag_answer`, `content_draft`.

Source types: `conversation`, `playbook`, `tool`, `browser_runtime`, `rag`, `content_agent`, `planning`, `openclaw_mock`.

Storage: exported files are written under `storage/output_artifacts/{workspace_id}/{artifact_id}/`. The system does not use S3 or MinIO.

Current limitation: this is not a full DAM, not a production file manager, not cloud storage, not real publishing asset management, and not a complete material management system.
## Phase 42: Task Orchestration & Background Execution

Phase 42 is completed. The system now has `task_runs` and `task_run_events` as a dedicated background execution timeline for Conversation and Playbook work. `TaskOrchestratorService` creates, queues, starts, completes, fails, retries, cancels, schedules, and resumes task runs. `BackgroundTaskExecutor` is a lightweight in-process polling loop started by FastAPI when `TASK_ORCHESTRATOR_ENABLED=true`. `TaskRetryPolicy` provides exponential backoff and keeps approval rejected / validation errors non-retryable.

Conversation Runtime now supports `execution_mode=immediate|background|scheduled`; background responses include `task_run_id`, `task_status`, and `execution_mode`. Scheduled Tasks use `scheduled_at`. Waiting approval runs pause as `waiting_approval` and resume only after Phase 39 approval is approved. Output Library now stores `task_run_id` on artifacts for Artifact linkage.

Current limits: this is not Celery, not RabbitMQ, not Kubernetes scheduler, and not production HA distributed queue. It does not add TikTok / YouTube / X automation, real publishing, login, CAPTCHA handling, proxy rotation, fingerprint bypass, real OpenClaw, or ComfyUI.

Phase 42 marker: Approval resume is supported for approved waiting_approval task runs.
## Phase 43: Task Scheduler Persistence & Worker Recovery

Phase 43 is completed. It strengthens Phase 42 Background Execution with Task Scheduler Persistence, Task Lease ownership, scheduler heartbeat, recovery scans, Failed Diagnostics, and Admin Dashboard scheduler health.

Completed capabilities:

- `task_scheduler_state` records scheduler status, heartbeat, last scan, active task count, recovered task count, and metadata.
- `task_runs` now records `lease_owner`, `lease_token`, `lease_expires_at`, `heartbeat_at`, `recovery_count`, `last_recovered_at`, `recovery_reason`, `failure_category`, `failure_reason`, `recoverable`, `suggested_action`, and `last_event_summary`.
- `TaskRecoveryService` supports scheduled task recovery, retrying task recovery, expired lease recovery, stuck task recovery, manual recover, executor degraded state, and scheduler health.
- `BackgroundTaskExecutor` now heartbeats scheduler state, runs startup recovery, periodically scans scheduled/retrying/stuck tasks, assigns leases to running tasks, and releases owned leases on shutdown best effort.
- APIs: `GET /api/v1/task-scheduler/health`, `POST /api/v1/task-scheduler/scan`, `GET /api/v1/task-runs/{task_run_id}/diagnostics`, and `POST /api/v1/task-runs/{task_run_id}/recover`.
- Admin Dashboard shows Scheduler Health, lease status, recoverable badge, diagnostics panel, scheduled due indicator, and manual recover button. Worker Console Web/Desktop show simplified task recovery state.

Recovery rules: running + expired lease or stale heartbeat -> retrying if retry budget remains, otherwise failed; pending scheduled due -> queued; retrying delay elapsed -> queued; waiting_approval is not auto-executed; completed/cancelled/expired are not recovered.

Boundary: this remains an in-process scheduler foundation. It is not Celery, not RabbitMQ, not Kubernetes scheduler, and not production HA distributed queue. It does not implement TikTok / YouTube / X automation, real publishing, login, CAPTCHA, proxy/fingerprint bypass, real OpenClaw, or ComfyUI.

<!-- PHASE44:START -->
## Phase 44 Output Artifact Pipeline & Export System

Phase 44 extends the Output Library into an Output Artifact Pipeline & Export System. It adds Artifact lineage, `artifact_relationships`, `ArtifactExportService`, `ArtifactPackagingService`, `ArtifactRetentionService`, package/export APIs, relationship graph lookup, `bundle.zip` generation, retention preview, and the Admin Dashboard Artifact Explorer. This phase preserves the boundary that the project is not a full DAM and not a production object storage platform.
<!-- PHASE44:END -->

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
- Output Artifact lineage now supports `workflow_run_id`, `workflow_step_id`, `checkpoint_id`, and `memory_snapshot_id` so artifacts can be traced back to workflow state. Workflow lineage is available in artifact detail and workflow panels.
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
## Phase 46: Workflow Graph Runtime & Conditional Execution

Status: completed.

Phase 46 upgrades Workflow State from a linear foundation into Workflow Graph Runtime & Conditional Execution. It adds `workflow_graphs`, `workflow_graph_nodes`, `workflow_graph_edges`, and `workflow_replays`, plus `WorkflowExecutionPlanner` and `SafeConditionEvaluator` for safe graph validation, dependency resolution, conditional routing, retry/fallback planning, and replay metadata.

Completed scope:

- Workflow Graph Runtime stores graph definitions, node configuration, edge conditions, entry node, graph version, retry policy, timeout metadata, and execution mode.
- Conditional Execution supports safe expressions over `workflow.variables`, `workflow.status`, `step.output`, `artifact.metadata`, and `approval.status` with `==`, `!=`, `and`, `or`, `in`, and `exists`; it does not use Python `eval`.
- `workflow_runs` now records graph execution metadata: `workflow_graph_id`, `graph_execution`, `current_node_key`, `planned_next_nodes`, `skipped_nodes`, `retry_state`, and `fallback_state`.
- `workflow_steps` now records `node_key`, `parent_node_key`, and `dependency_state` so step execution can be traced to graph nodes.
- Output Artifact lineage adds `producing_node_key`, `replay_source`, and `graph_lineage`; Agent Memory Snapshots can record `node_key`.
- Replay Foundation creates `workflow_replays` metadata from checkpoints; it does not re-execute browser, OpenClaw, tool, or task actions.
- Admin Dashboard adds a Workflow Graphs view with graph summary, node list, edge list, planner result, conditional routing result, Retry/Fallback Path, retry path, fallback path, and replay panel.
- Worker Console and Worker Console Desktop show a simplified graph execution panel with current node, planned next nodes, skipped nodes, retry/fallback state, and replay status.

Boundaries: Phase 46 is not a visual DAG builder, not a drag/drop graph editor, not distributed orchestration engine, not a distributed orchestration engine, not Kubernetes/Celery orchestration, not WebSocket/SSE streaming, and not ComfyUI. It does not add TikTok / YouTube / X automation, real platform publishing, automatic login, CAPTCHA automation, proxy pools, fingerprint bypass, or real OpenClaw.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47: Workflow Template Registry & Versioning

Status: completed.

Phase 47 upgrades the Phase 46 Workflow Graph Runtime into a reusable Workflow Template Registry & Versioning foundation. It adds `workflow_templates`, `workflow_template_versions`, and `workflow_template_runs`, plus `WorkflowTemplateRegistryService` and `WorkflowTemplateCompatibilityService` for template registration, immutable versions, validation, compatibility checks, import/export, and template runs.

Built-in templates:

- `browser_screenshot_report_graph`: open URL, screenshot, page snapshot, and report artifact.
- `content_generation_graph`: generate title, description, hashtags, CTA, and content artifact.
- `rag_answer_graph`: retrieve docs, summarize answer, and create RAG artifact.
- `approval_then_browser_graph`: approval gate, browser action, and artifact package.
- `openclaw_mock_inspect_graph`: mock inspect and JSON artifact only.
- `task_retry_demo_graph`: simulated failure, retry route, and fallback summary.

Versioning and registry flow:

- `template_key` is workspace-unique.
- `current_version` is the default active version; `latest_version` tracks the newest version.
- `workflow_template_versions.validation_status` stores `pending`, `valid`, or `invalid`.
- `compatibility` records supported node-type checks, schema checks, graph validation, runtime capability warnings, and missing capabilities.
- Versions are not overwritten; a new graph definition creates a new version.
- Template runs create `workflow_template_run_id` and link to `workflow_run_id` without bypassing approval or risk gates.

Integration:

- Conversation run supports `workflow_template_key`.
- Task Runs, Output Artifacts, and Agent Memory Snapshots can record `workflow_template_id`, `workflow_template_version_id`, and `workflow_template_run_id`.
- Admin Dashboard adds a Template Library with template detail, Version list, Validation result, Compatibility result, Import / Export JSON, Run template, and Template runs.
- Worker Console and Worker Console Desktop add a simplified Template Library entry for selecting, running, and checking template runs.

API coverage:

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

Boundaries: Phase 47 is not a visual DAG builder, not a drag/drop workflow editor, not WebSocket/SSE streaming, and not ComfyUI. It does not add TikTok / YouTube / X automation, real platform publishing, automatic login, CAPTCHA automation, proxy pools, fingerprint bypass, or real OpenClaw.
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

<!-- PHASE53_SYNC:BEGIN -->
## Phase 53: Release Smoke Test Matrix & Preflight Automation

Phase 53 adds a unified Release Smoke Matrix and Preflight System. It introduces `release/smoke/` with `smoke_matrix.json`, `profile_matrix.json`, `runtime_matrix.json`, and smoke documentation. It also adds `scripts/release_preflight.py`, `scripts/release_smoke_matrix.py`, `scripts/generate_release_report.py`, `scripts/check_migration_continuity.py`, and `scripts/check_runtime_hygiene.py`.

Capabilities:

- Unified preflight runner for pytest, docs verifier, release packaging validation, migration continuity, runtime hygiene, frontend builds, Docker health, deployment verification, and smoke routes.
- Smoke orchestrator for grouped execution and partial failure reporting.
- Release readiness report generation under ignored local QA output.
- Migration continuity checks for Alembic revision chain, unique revisions, single root/head, and downgrade functions.
- Runtime hygiene checks for committed `.env`, rendered PDFs, `runtime_state`, logs, `node_modules`, storage runtime artifacts, and generated release bundles.
- Frontend Release Readiness / Diagnostics help in Admin Dashboard, Worker Console, and Desktop Console.

Boundaries: Phase 53 is an Integration Candidate readiness layer. It is not Kubernetes, Helm, Terraform, CI/CD SaaS, a real installer, code signing, an auto updater, production HA orchestration, ComfyUI, real OpenClaw, or real social media automation.

Keywords: Phase 53; Release Smoke Test Matrix; Preflight Automation; release/smoke; release_preflight.py; release_smoke_matrix.py; generate_release_report.py; check_migration_continuity.py; check_runtime_hygiene.py; runtime hygiene; migration continuity; smoke routes; release readiness.
<!-- PHASE53_SYNC:END -->

<!-- PHASE54_SYNC:BEGIN -->
## Phase 54: Integration Branch & PR Chain Reconciliation

Phase 54 adds the Integration Candidate reconciliation layer. It introduces `docs/INTEGRATION_STRATEGY.md`, `docs/INTEGRATION_STATUS.md`, `release/integration/`, `release/reports/pr_chain_inventory.json`, `scripts/analyze_pr_chain.py`, `scripts/integration_preflight.py`, `scripts/detect_integration_conflicts.py`, `scripts/check_api_frontend_drift.py`, and `scripts/generate_integration_report.py`.

The phase reconciles the Phase 43-53 PR chain, dependency order, conflict surfaces, OpenAPI/frontend client drift, deployment profile drift, release readiness, migration continuity, runtime hygiene, smoke matrix, and docs verifier status.

Boundaries: Phase 54 does not add runtime features, does not automatically merge PRs, does not resolve conflicts automatically, and is not Kubernetes, Helm, Terraform, CI/CD SaaS, a production HA orchestrator, a real installer, code signing, auto update, ComfyUI, real OpenClaw, or real social media automation.

Keywords: Phase 54; Integration Branch & PR Chain Reconciliation; INTEGRATION_STRATEGY.md; INTEGRATION_STATUS.md; integration_preflight.py; detect_integration_conflicts.py; check_api_frontend_drift.py; PR chain; conflict surface; integration readiness report.
<!-- PHASE54_SYNC:END -->

<!-- PHASE55_SYNC:BEGIN -->
## Phase 55: Mainline Integration & Release Candidate Merge Window

Phase 55 adds Mainline Integration and Release Candidate preparation. It introduces `docs/MAINLINE_INTEGRATION_PLAN.md`, `docs/RELEASE_CANDIDATE_PROCESS.md`, `release/integration/release_candidate_model.json`, `scripts/mainline_readiness.py`, `scripts/simulate_mainline_merge.py`, `scripts/generate_superseded_pr_report.py`, and `scripts/generate_mainline_integration_report.py`.

The phase prepares a controlled Release Candidate merge window for the Phase 43-54 integration candidate stack. It does not merge into `main`, does not add runtime features, and does not declare the system production-ready.

Boundaries: Phase 55 is not a production release, not a production installer, not code signing, not an auto updater, not Kubernetes, not HA orchestration, not real OpenClaw, and not real social automation.

Keywords: Phase 55; Mainline Integration; Release Candidate; MAINLINE_INTEGRATION_PLAN.md; RELEASE_CANDIDATE_PROCESS.md; mainline_readiness.py; simulate_mainline_merge.py; superseded PR; mainline integration report.
<!-- PHASE55_SYNC:END -->

## Docs Stabilization Sprint

This document is now indexed by `docs/PHASE_INDEX.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/SYSTEM_BOUNDARIES.md`, `docs/DOC_RENDER_QA.md`, and `docs/ARCHITECTURE_TIMELINE.md`.

The canonical project recovery state is: `main` is the Phase 55 stable baseline after PR #17 and post-merge stabilization, PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`, PR #1 and PR #15 are closed as superseded, and Phase 56 remains reverted and inactive. Current non-goals remain: no ComfyUI integration, no real social media publishing, no captcha bypass, no proxy pool, no Kubernetes/Helm/Terraform, no HA orchestration, and no production installer/signing.
