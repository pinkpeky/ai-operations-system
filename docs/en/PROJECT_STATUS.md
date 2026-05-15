# Project Status

## Phase 36: Server Admin Dashboard Foundation

Status: completed.

Phase 36 adds `admin_dashboard`, a standalone Vite + React + TypeScript + Tailwind Admin Dashboard Foundation for read-only monitoring of AI Server, Browser Workers, Browser Runtime, Timeline, Snapshots, Replay metadata, Tasks, Conversation Runtime, OpenClaw mock, Audit Logs, and RAG / Documents.

Completed:

- `admin_dashboard/package.json`
- `admin_dashboard/src/main.tsx`
- `admin_dashboard/src/styles.css`
- `admin_dashboard/src/api/client.ts`
- `docs/zh/ADMIN_DASHBOARD.md`
- `docs/en/ADMIN_DASHBOARD.md`

Pages: Overview, Workers, Browser Runtime, Conversations, Tasks, OpenClaw, Audit Logs, RAG / Documents, Settings.

API modules: `workersApi`, `browserRuntimeApi`, `conversationsApi`, `tasksApi`, `openclawApi`, `auditApi`, `ragApi`.

Runtime config: `VITE_AI_SERVER_API=http://localhost:8000`, `VITE_WORKSPACE_ID=demo-workspace`, `VITE_USER_ID=demo-user`.

Boundary: read-only monitoring foundation, no login UI, no permission UI, no publishing business flow, no real social platform control, no production-grade operations backend.

Last updated: 2026-05-14

This document summarizes the current engineering status of `E:\ai-operations-system`.

## Overall Status

Phase 1 through Phase 28 are complete.

The system currently includes:

- FastAPI.
- PostgreSQL, Redis, Qdrant, and Docker Compose.
- SQLAlchemy ORM and Alembic migrations.
- Redis Queue, Scheduler, TaskExecutor, and task handlers.
- LLM Client Layer.
- Ollama Mistral local LLM integration.
- Embedding Pipeline.
- Ollama bge-m3 local embedding integration.
- Knowledge Lifecycle Management.
- Workspace, user, and API key isolation foundation.
- Agentic RAG Orchestrator.
- ContentAgent.
- RAG Eval and Debug Trace.
- Reranker Provider Layer.
- Hybrid Search.
- File Upload Pipeline.
- Docs Runtime Verification.
- Task Reliability & Observability.
- Tool Calling Foundation.
- Memory Foundation.
- Multi-Agent Foundation.
- Agent Planning Foundation.
- Browser Automation Adapter Foundation.
- Playwright Local Provider Integration.
- Remote Browser Worker Foundation.
- Real Browser Worker Service.
- Browser Worker Reliability.
- Persistent Browser Profile Foundation.
- Browser Profile Health & Recovery.
- Human-in-the-loop Browser Control.
- Browser Worker UI Access Placeholder.
- Browser Worker Security & Access Control.
- Customer Machine Worker Bootstrap.
- OpenClaw Worker Adapter Foundation.

## Completed Phases

| Phase | Status | Summary |
| --- | --- | --- |
| Phase 1 | Complete | Docker, PostgreSQL, Redis, Qdrant, FastAPI, health check. |
| Phase 2 | Complete | ORM, task system, Redis queue, Scheduler, Task API. |
| Phase 2.5 | Complete | LLM client, mock/local/server providers, prompt manager. |
| Phase 3 | Complete | Embedding pipeline and Qdrant collection layer. |
| Phase 3.5 | Complete | RAG quality improvements, score normalization, collection health, debug API. |
| Phase 4 | Complete | Single Agentic RAG orchestrator. |
| Phase 4.5 | Complete | Agentic RAG task execution handler. |
| Phase 4.6 | Complete | Ollama Mistral local LLM integration. |
| Phase 5 | Complete | BaseAgent and ContentAgent. |
| Phase 6 | Complete | Knowledge lifecycle with document versioning and active-only retrieval. |
| Phase 6.5 | Complete | Workspace/user/API key isolation foundation. |
| Phase 7 | Complete | Ollama bge-m3 real embedding support. |
| Phase 8 | Complete | RAG eval runs/items and trace persistence. |
| Phase 9 | Complete | Reranker provider layer. |
| Phase 10 | Complete | Hybrid Search: Dense + Keyword -> Merge -> Rerank -> LLM. |
| Phase 10.5 | Complete | Bilingual docs system and docs SSOT. |
| Phase 11 | Complete | File Upload Pipeline and Docs Runtime Verification. |
| Phase 12 | Complete | Task Reliability & Observability with task_events, task_logs, cancel/retry, timeout, duration_ms, and summary API. |
| Phase 13 | Complete | Tool Calling Foundation with BaseTool, ToolRegistry, builtin tools, tool_call_logs, Tool API, and manual Agent tool calls. |
| Phase 14 | Complete | Memory Foundation with conversation_sessions, conversation_messages, agent_memories, memory_operation_logs, Memory API, BaseAgent memory hooks, and Agentic RAG memory_trace. |
| Phase 15 | Complete | Multi-Agent Foundation with AgentRegistry, agent_runs, agent_messages, agent_handoffs, fixed Agent Chain execution, ToolAgent, and memory-aware run metadata. |
| Phase 16 | Complete | Agent Planning Foundation with plans, plan_steps, plan_reviews, SimplePlannerAgent, bounded Plan Execution Flow, step duration/error tracking, cancellation, and planning memory_trace. |
| Phase 17 | Complete | Browser Automation Adapter Foundation with browser_sessions, browser_actions, browser_action_logs, BrowserProvider, MockBrowserProvider, PlaywrightBrowserProvider placeholder, BrowserService, browser_tool, and Browser APIs. |
| Phase 18 | Complete | Playwright Local Provider Integration with `PlaywrightLocalProvider`, `BROWSER_PROVIDER=playwright_local`, local headless Chromium, `browser_id`, `page_id`, `provider_session_metadata`, `selector`, `target_url`, `screenshot_path`, `page_title`, Screenshot System, and `get_page_content`. |
| Phase 19 | Complete | Remote Browser Worker Foundation with `RemoteBrowserProvider`, `BrowserWorkerClient`, `browser_workers`, `browser_worker_sessions`, `browser_worker_actions`, Worker Registration, Worker Heartbeat, Worker Runtime Mock, and `BROWSER_PROVIDER=remote`. |
| Phase 20 | Complete | Real Browser Worker Service with independent `browser-worker` Docker service, `worker/main.py`, `worker/browser_worker/playwright_runtime.py`, Playwright Chromium, `http://browser-worker:9100`, and `worker/screenshots`. |
| Phase 21 | Complete | Browser Worker Reliability with `BrowserWorkerHealthService`, `BrowserWorkerSelector`, `BrowserSessionCleanupService`, `ScreenshotCleanupService`, capacity fields, least loaded worker selection, action retry, and screenshot cleanup. |
| Phase 22 | Complete | Persistent Browser Profile Foundation with `browser_profiles`, `BrowserProfileService`, Profile Lock / Profile Release, `profile_id`, `profile_path`, `persistent_context_enabled`, `launch_persistent_context`, and `worker/profiles`. |
| Phase 23 | Complete | Browser Profile Health & Recovery with `BrowserProfileHealthService`, `BrowserProfileBackupService`, `BrowserProfileCleanupService`, `browser_profile_usage_logs`, `health_status`, `usage_count`, `health/summary`, stale lock recovery, profile backup, and profile cleanup. |
| Phase 24 | Complete | Human-in-the-loop Browser Control with `BrowserHumanControlService`, `browser_human_control_sessions`, `browser_human_control_events`, session paused/resumed flow, `request_human_control`, and `complete_human_control`. |
| Phase 25 | Complete | Browser Worker UI Access Placeholder with `BrowserUIAccessService`, `browser_ui_access_sessions`, `access_token_hash`, placeholder URL generation, token validate/revoke/expire, `/ui-access/capabilities`, `create_ui_access`, and `revoke_ui_access`. |
| Phase 26 | Complete | Browser Worker Security & Access Control with `BrowserWorkerAuthService`, `worker_secret_hash`, signed worker request headers, UI Access Scope, `BrowserActionPolicyService`, and `browser_security_audit_logs`. |
| Phase 27 | Complete | Customer Machine Worker Bootstrap with `worker_client`, `worker_config.example.yaml`, local `worker_config.yaml`, local-only `worker_state.json`, CLI register/heartbeat/serve/start, registration flow, heartbeat flow, and local worker runtime. |
| Phase 28 | Complete | OpenClaw Worker Adapter Foundation with `worker_client/openclaw`, `MockOpenClawProvider`, `OpenClawRuntime`, server-side `OpenClawWorkerClient`, `openclaw_tool`, `openclaw_action_logs`, and mock `/openclaw/*` runtime routes. |

## Phase 28 Summary

OpenClaw Worker Adapter Foundation:

- Adds `worker_client/openclaw/` with `BaseOpenClawProvider`, `MockOpenClawProvider`, `OpenClawRuntime`, and action schemas.
- Adds worker_client runtime routes: `GET /openclaw/health`, `GET /openclaw/capabilities`, and `POST /openclaw/actions`.
- Adds server-side `app/openclaw/` with `OpenClawWorkerClient`, schemas, repository, and service.
- Adds `openclaw_action_logs`.
- Adds `GET /api/v1/openclaw/health`, `GET /api/v1/openclaw/capabilities`, and `POST /api/v1/openclaw/actions`.
- Adds builtin `openclaw_tool`, which writes `tool_call_logs`, `openclaw_action_logs`, and `browser_security_audit_logs`.
- Adds `OPENCLAW_PROVIDER=mock`, `OPENCLAW_ENABLED=true`, and `OPENCLAW_ACTION_TIMEOUT_SECONDS=60`.

Boundary: Phase 28 is an adapter foundation only. It does not call real OpenClaw, integrate TikTok / YouTube / X, perform account login, auto-publish, automate captchas, use proxy pools, bypass fingerprints, or run real platform automation.

## Phase 11 Summary

File Upload:

- Adds `app/file_pipeline/`.
- Supports PDF, DOCX, TXT, MD, and CSV.
- Adds `POST /api/v1/files/upload`.
- Uses multipart/form-data.
- Saves a temp file, computes `file_hash`, parses text, cleans text, and calls DocumentLifecycle ingest.
- Writes `documents`, `document_chunks`, and Qdrant points.
- Stores file metadata: `filename`, `file_type`, `file_size`, `file_hash`, `ingest_status`, `ingest_error`, and `chunk_count`.
- Supports duplicate detection by `file_hash + workspace_id`.
- Supports `duplicate_strategy=skip` and `duplicate_strategy=force_reingest`.

Docs Runtime Verification:

- Adds `scripts/verify_docs_runtime.py`.
- Adds `docs/zh/DOCS_RUNTIME_VERIFICATION.md`.
- Adds `docs/en/DOCS_RUNTIME_VERIFICATION.md`.
- Checks config, docker-compose, OpenAPI routes, runtime docs, overview docs, API reference, and phase status.
- Outputs `PASS`, `WARNING`, and `ERROR`.

## Phase 12 Summary

Task Reliability & Observability:

- Adds `task_events` for task lifecycle events.
- Adds `task_logs` for structured task logs.
- Adds `tasks.duration_ms`.
- Extends task status values to `pending`, `running`, `retry`, `failed`, `completed`, `cancelled`, and `timeout`.
- Adds `POST /api/v1/tasks/{task_id}/cancel`.
- Adds `POST /api/v1/tasks/{task_id}/retry`.
- Adds `GET /api/v1/tasks/{task_id}/events`.
- Adds `GET /api/v1/tasks/{task_id}/logs`.
- Adds `GET /api/v1/observability/summary`.
- TaskExecutor records started/completed/failed/retry_scheduled/cancelled_skipped/timeout events and logs.
- Scheduler only receives minimal timeout-state adaptation.
- Agent / RAG / LLM logs include provider, model, latency_ms, error, workspace_id, and task_id when available.

## Phase 13 Summary

Tool Calling Foundation:
- Added `app/tools/` with `base`, `registry`, and `builtin`.
- Added `BaseTool` with `name`, `description`, `input_schema`, `output_schema`, and `execute()`.
- Added `ToolRegistry` with `register_tool`, `get_tool`, `list_tools`, and `validate_tool_input`.
- Registry includes enable/disable flags, permission scope placeholders, and workspace isolation hooks.
- Added `tool_call_logs` with `workspace_id`, `agent_name`, `tool_name`, `tool_input`, `tool_output`, `success`, `error`, `latency_ms`.
- Added APIs: `GET /api/v1/tools`, `GET /api/v1/tools/{tool_name}`, `POST /api/v1/tools/{tool_name}/execute`, and `GET /api/v1/tool-calls`.
- Builtin tools: `rag_search_tool`, `file_search_tool`, `create_task_tool`, `get_task_status_tool`, `current_runtime_tool`.
- `BaseAgent` now supports `available_tools`, `tool_call_trace`, and `execute_tool()`.
- This phase does not implement Browser Agent, OpenClaw, Playwright, Selenium, autonomous planning, ReAct, or Multi-Agent orchestration.

## Phase 14 Summary

Memory Foundation:
- Added `app/memory/` with repositories and `MemoryService`.
- Added `conversation_sessions`, `conversation_messages`, `agent_memories`, and `memory_operation_logs`.
- Added APIs: `POST /api/v1/memory/sessions`, `GET /api/v1/memory/sessions`, `GET /api/v1/memory/sessions/{session_id}`, `POST /api/v1/memory/messages`, `GET /api/v1/memory/messages/{session_id}`, `POST /api/v1/memory/memories`, `GET /api/v1/memory/memories`, and `DELETE /api/v1/memory/memories/{memory_id}`.
- Current memory retrieval uses PostgreSQL text search, scoped by workspace.
- `BaseAgent` now supports `session_id`, `memory_context`, `load_memory()`, `save_memory()`, and `memory_trace`.
- Agentic RAG debug trace now includes `session_id`, `recent_messages_count`, `retrieved_memories_count`, `recent_messages`, `retrieved_memories`, and `memory_trace`.
- This phase does not implement vector memory, graph memory, personality memory, or autonomous memory planning.

## Phase 15 Summary

Multi-Agent Foundation:
- Added `app/multi_agent/` with `AgentRegistry`, `MultiAgentService`, and `AgentRunRepository`.
- Added `agent_runs`, `agent_messages`, and `agent_handoffs`.
- Added APIs: `GET /api/v1/agents/registry`, `POST /api/v1/multi-agent/runs`, `GET /api/v1/multi-agent/runs`, `GET /api/v1/multi-agent/runs/{run_id}`, `POST /api/v1/multi-agent/runs/{run_id}/execute-chain`, `GET /api/v1/multi-agent/runs/{run_id}/messages`, and `GET /api/v1/multi-agent/runs/{run_id}/handoffs`.
- Registered agents: `content_planner`, `rag_agent`, `content_agent`, `review_agent`, `runtime_agent`, and `tool_agent`.
- The fixed Agent Chain is `content_planner -> rag_agent -> content_agent -> review_agent`.
- `ToolAgent` can call existing builtin tools through `ToolRegistry`: `rag_search_tool`, `file_search_tool`, `create_task_tool`, `get_task_status_tool`, and `current_runtime_tool`.
- Run output includes `agents_involved`, message history, handoff records, and `handoff_trace`.
- Memory integration supports `session_id`, recent messages, and memory context where the underlying Agent or Agentic RAG path already supports memory.
- This phase does not implement autonomous planning, ReAct, Browser Agent, Playwright, OpenClaw, Selenium, or external platform automation.

## Phase 16 Summary

Agent Planning Foundation:
- Added `app/planning/` with repositories and services.
- Added `plans`, `plan_steps`, and `plan_reviews`.
- Added `SimplePlannerAgent`, a rule-based planner that emits a bounded plan for content/RAG/review workflows.
- Added APIs: `POST /api/v1/plans`, `GET /api/v1/plans`, `GET /api/v1/plans/{plan_id}`, `POST /api/v1/plans/{plan_id}/execute`, `POST /api/v1/plans/{plan_id}/cancel`, `GET /api/v1/plans/{plan_id}/steps`, and `GET /api/v1/plans/{plan_id}/reviews`.
- Plan Execution Flow: plan -> steps -> AgentRegistry or ToolRegistry -> step output/duration/error -> review -> final status.
- Step execution stores `duration_ms`, `error`, and status. Service-level retry and skip are available for steps.
- Planning supports `session_id` and returns `memory_trace`.
- This phase does not implement autonomous AGI planning, tree-of-thought, recursive planning, infinite Agent loops, ReAct, Browser Agent, Playwright, OpenClaw, Selenium, or external platform automation.

## Phase 17 Summary

Browser Automation Adapter Foundation:

- Added `app/browser/` with providers, repositories, and services.
- Added runtime tables: `browser_sessions`, `browser_actions`, and `browser_action_logs`.
- Added `BrowserProvider` interface with `create_session`, `close_session`, `navigate`, `click`, `type_text`, `scroll`, `screenshot`, and `get_page_content`.
- Added `MockBrowserProvider`, the active default provider. It never starts a real browser.
- Added `PlaywrightBrowserProvider` as a placeholder only. It returns clear non-execution responses.
- Added `BrowserService` with workspace-scoped session creation, action execution, session/action listing, log listing, `duration_ms`, and error recording.
- Added APIs: `POST /api/v1/browser/sessions`, `GET /api/v1/browser/sessions`, `POST /api/v1/browser/actions`, `GET /api/v1/browser/actions/{session_id}`, and `GET /api/v1/browser/logs/{session_id}`.
- Added builtin `browser_tool` for `navigate`, `click`, `type_text`, and `screenshot`.
- Planning can execute a step with `tool_name=browser_tool`.
- This phase does not implement Browser Agent, autonomous browser planning, Playwright execution, Selenium, OpenClaw, OCR, visual AI, TikTok, YouTube, X, or real platform automation.

## Phase 18 Summary

Playwright Local Provider Integration:

- Added `app/browser/providers/playwright_provider.py` with `PlaywrightLocalProvider`, provider name `playwright_local`.
- Implemented `create_session`, `close_session`, `navigate`, `click`, `type_text`, `screenshot`, and `get_page_content`.
- Extended `BrowserSession` with `browser_id`, `page_id`, and `provider_session_metadata`.
- Extended `BrowserAction` with `selector`, `target_url`, `screenshot_path`, and `page_title`.
- Added Screenshot System: `screenshots/{workspace_id}/{session_id}/{filename}.png`.
- Added `GET /api/v1/browser/screenshot/{session_id}/{filename}`.
- Extended `browser_tool` with `get_page_content` while preserving `tool_call_logs`.
- Updated Docker image setup to install Playwright Python and Chromium only.

Phase 18 safety boundary:

- Default remains `BROWSER_PROVIDER=mock`.
- `BROWSER_PROVIDER=playwright_local` only allows `example.com`, local test pages, and static `file://` pages.
- No TikTok / YouTube / X automation.
- No automatic login, cookie injection, fingerprint bypass, proxy pools, or captcha automation.
- No OCR, visual AI, autonomous browser planning, Browser Worker, or real platform automation.

## Phase 19 Summary

Remote Browser Worker Foundation:

- Added `app/browser/remote/` with `client`, `schemas`, and `services`.
- Added `BrowserWorkerClient` with `create_session`, `close_session`, `execute_action`, and `health_check`.
- Added `RemoteBrowserProvider`, provider name `remote`, which dispatches browser actions through registered worker `base_url` values.
- Added runtime tables: `browser_workers`, `browser_worker_sessions`, and `browser_worker_actions`.
- Added APIs: `POST /api/v1/browser-workers/register`, `POST /api/v1/browser-workers/{worker_id}/heartbeat`, and `GET /api/v1/browser-workers`.
- Added mock worker runtime: `GET /api/v1/browser-worker-runtime/health`, `POST /api/v1/browser-worker-runtime/sessions`, `POST /api/v1/browser-worker-runtime/actions`, and `POST /api/v1/browser-worker-runtime/sessions/{session_id}/close`.
- `BrowserService` supports `BROWSER_PROVIDER=remote`.
- `browser_tool` still executes through `BrowserService`, so remote provider mode preserves `tool_call_logs` and `browser_action_logs`.

Phase 19 explicitly does not include:

- Real external Worker deployment.
- TikTok / YouTube / X automation.
- Account login, auto-publishing, cookie injection, fingerprint bypass, proxy pools, or captcha automation.
- Autonomous browser agents.

## Phase 20 Summary

Real Browser Worker Service:

- Added the standalone `worker/` FastAPI service package.
- Added `worker/main.py` with `GET /health`, `POST /sessions`, `POST /actions`, and `POST /sessions/{session_id}/close`.
- Added `worker/browser_worker/playwright_runtime.py` for headless Playwright Chromium execution.
- Docker Compose now runs an independent `browser-worker` service on port `9100`.
- API Server calls `RemoteBrowserProvider -> BrowserWorkerClient -> http://browser-worker:9100`.
- Added `BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100`.
- Screenshots are saved under `worker/screenshots/{workspace_id}/{remote_session_id}/{filename}.png`.

Phase 20 explicitly does not include:

- TikTok / YouTube / X automation.
- Account login, cookie injection, proxy pools, fingerprint bypass, captcha automation, OCR, visual AI, OpenClaw, or autonomous browser agents.
- Production external worker fleet management, scheduling, or autoscaling.

## Phase 21 Summary

Browser Worker Reliability:

- Added `BrowserWorkerHealthService` for stale worker detection, `offline` marking, `last_seen`, and `error_message`.
- Added `BrowserWorkerSelector` for workspace-scoped, capability-aware, least loaded worker selection.
- Added capacity fields on `browser_workers`: `max_sessions`, `active_sessions`, `max_actions_per_minute`, `current_load`, and `priority`.
- Added retry fields on `browser_worker_actions`: `retry_count` and `max_retries`.
- Added `BrowserSessionCleanupService` for stale sessions and worker offline/error recovery.
- Added `ScreenshotCleanupService` for manual workspace-scoped screenshot cleanup with dry-run by default.
- Added reliability APIs for health summary, available workers, manual offline marking, session cleanup, worker sessions, and screenshot cleanup.

Phase 21 explicitly does not include:

- TikTok / YouTube / X automation.
- Account login, cookie injection, proxy pools, fingerprint bypass, captcha automation, OCR, visual AI, OpenClaw, real platform automation, or autonomous browser planning.

## Phase 22 Summary

Persistent Browser Profile Foundation:

- Added `browser_profiles` for persistent browser state lifecycle metadata.
- Added `BrowserProfileService` for create/list/get/lock/release/mark corrupted/delete/get available profile flows.
- Added `profile_id`, `profile_path`, and `persistent_context_enabled` to `browser_sessions`.
- Extended `POST /api/v1/browser/sessions` with `profile_id` and `use_persistent_profile=true`.
- Added `POST /api/v1/browser/sessions/{session_id}/close` to close a session and release the profile lock.
- Added worker-side Playwright `launch_persistent_context` support for profile-backed sessions.
- Stores profile data under `worker/profiles/{workspace_id}/{profile_id}`.

Phase 22 explicitly does not include:

- TikTok / YouTube / X automation.
- Account login, cookie injection, proxy pools, fingerprint bypass, captcha automation, real social platform automation, or OpenClaw.

## Current Defaults

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
BROWSER_PROVIDER=mock
```

Supported local models:

- `LOCAL_LLM_MODEL=mistral`
- `LOCAL_EMBEDDING_MODEL=bge-m3`

Upload defaults:

```text
MAX_UPLOAD_FILE_SIZE_MB=20
UPLOAD_TEMP_DIR=/tmp/aiops_uploads
ALLOWED_FILE_TYPES=pdf,docx,txt,md,csv
```

## Production Foundation

- Health checks.
- Task creation, querying, queueing, execution, and retry.
- Text RAG ingest/search.
- File upload ingest.
- Knowledge lifecycle: active, outdated, deleted.
- Workspace-level data isolation.
- API key hash storage with one-time plaintext return.
- Dense, keyword, and hybrid search.
- Mock reranker.
- Agentic RAG debug trace.
- RAG eval run/item storage.
- ContentAgent.

## Experimental

- Local Ollama LLM and embedding providers.
- Local reranker provider placeholder.
- RAG eval trace and manual scoring without automatic metrics.

## Planned

- Real reranker integration.
- Real BM25 or external search engine.
- Vector memory and graph memory.
- Advanced Tool Calling planner / function calling / ReAct.
- Advanced Multi-Agent orchestration with autonomous planning and dynamic handoff policy.
- Browser Agent / OpenClaw / Playwright.
- Grafana / Prometheus.
- Full RBAC / JWT / OAuth.

## Phase 24 Summary

Human-in-the-loop Browser Control:

- Added `browser_human_control_sessions` and `browser_human_control_events`.
- Extended `browser_sessions` with `human_control_status`, `human_control_session_id`, `paused_at`, and `resumed_at`.
- Added `BrowserHumanControlService` for request, approve, start, complete, cancel, expire, list, get, and event recording.
- Added browser human-control APIs and worker metadata-level `/human-control/*` endpoints.
- Added `browser_tool` actions `request_human_control` and `complete_human_control`.

Phase 24 explicitly does not include VNC, noVNC, Chrome DevTools remote UI, platform login, captcha handling, social-platform automation, proxies, cookie injection, or fingerprint bypass.

## Phase 25 Summary

Browser Worker UI Access Placeholder:

- Added `browser_ui_access_sessions`.
- Added `BrowserUIAccessService` for create, get, revoke, expire, token generation, and token validation.
- Stored only `access_token_hash`; plaintext token is returned only once by create.
- Added placeholder `remote_control_url`, `live_view_url`, and `devtools_url=null`.
- Added API routes for create, get, revoke, expire, and validate.
- Added worker `/ui-access/capabilities` with `vnc=false`, `novnc=false`, `devtools=false`, `placeholder=true`.
- Added `browser_tool` actions `create_ui_access` and `revoke_ui_access`.

Phase 25 explicitly does not include real VNC, noVNC, Chrome DevTools remote UI, live browser video, platform login, captcha handling, social-platform automation, proxies, cookie injection, or fingerprint bypass.

## Phase 26 Summary

Browser Worker Security & Access Control:

- Extended `browser_workers` with `worker_secret_hash`, `api_key_hash`, `last_auth_at`, `auth_status`, `allowed_actions`, and `allowed_domains`.
- Added `BrowserWorkerAuthService` for worker secret generation, hashing, verification, request signing, and signature verification.
- Added signed worker request headers: `X-Worker-Signature`, `X-Worker-Timestamp`, `X-Worker-Nonce`, and request body hash validation.
- Extended worker runtime auth so `/sessions`, `/actions`, and `/sessions/{session_id}/close` can require signed requests; `/health` stays unauthenticated.
- Extended `browser_ui_access_sessions` with `scopes`, `one_time`, `used_at`, `revoked_reason`, `client_ip`, and `user_agent`.
- Added UI Access Scope validation for `view`, `control`, `screenshot`, and `devtools_placeholder`.
- Added `BrowserActionPolicyService` for action type, target domain, profile access, worker capability, and UI scope checks.
- Added `BrowserSecurityAuditLog` and `browser_security_audit_logs` for worker auth, UI token, policy block, and profile access audit records.
- Added APIs for worker secret rotation, worker revoke, security audit logs, and browser policy checks.

Phase 26 explicitly does not implement real social-platform account security, TikTok / YouTube / X automation, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha handling, or full RBAC/JWT/OAuth.

## Phase 27 Summary

Customer Machine Worker Bootstrap:

- Added `worker_client/` as a standalone customer-machine bootstrap package.
- Added `worker_client/worker_config.example.yaml`; operators copy it to `worker_config.yaml`.
- Added YAML config loading with environment overrides.
- Added local `worker_state.json` persistence for `worker_id` and one-time `worker_secret`; this file is ignored by Git.
- Added CLI commands: `python -m worker_client.cli register`, `heartbeat`, `serve`, and `start`.
- Registration calls `POST /api/v1/browser-workers/register` and stores returned `worker_id` / `worker_secret` locally.
- Heartbeat reads `worker_state.json`, uses `worker_secret`, and sends Phase 26 signed headers.
- Local runtime server exposes `GET /health`, `POST /sessions`, `POST /actions`, `POST /sessions/{session_id}/close`, and `GET /ui-access/capabilities`.
- Runtime reuses the existing Playwright Worker schema/runtime contract so customer-machine workers and Docker `browser-worker` use the same protocol.

Phase 27 explicitly does not implement OpenClaw integration, TikTok / YouTube / X automation, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha handling, or real platform automation.

## Current Limitations

- PDF parsing only extracts embedded text. No OCR.
- PPTX, XLSX, and image parsing are not supported.
- Keyword retrieval uses PostgreSQL `ILIKE` and simple scoring.
- Local reranker is still a placeholder.
- No Elasticsearch, OpenSearch, or real BM25.
- No full authentication system.
- No frontend dashboard.

## Required Verification

Every phase must finish with:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Docs are considered synchronized only when the docs verifier returns `SUMMARY: PASS`.

## Phase 29 Worker Client Packaging & Worker Console Foundation

Completed:

- Added `Worker Runtime Manager` in `worker_client/runtime_manager.py` with `start_runtime`, `stop_runtime`, `restart_runtime`, `runtime_health`, `start_heartbeat`, `stop_heartbeat`, and `runtime_state`.
- Added local status in `worker_client/status.py`; runtime writes `worker_client/runtime_state/status.json` with `worker_id`, `worker_name`, `workspace_id`, `server_url`, `runtime_running`, `heartbeat_running`, `registered`, `last_heartbeat_at`, `last_error`, `current_status`, `openclaw_enabled`, and `browser_enabled`.
- Added local logging in `worker_client/logging.py`; logs go to `worker_client/logs/worker.log` with simple rotation and secret redaction.
- Extended `worker_client/runtime.py` with local management API: `GET /local/status`, `GET /local/health`, `POST /local/runtime/start`, `POST /local/runtime/stop`, `POST /local/runtime/restart`, `POST /local/heartbeat/start`, `POST /local/heartbeat/stop`, and `GET /local/logs`.
- Added `worker_client/local_api_client.py` as the Python client for future Worker Console Foundation / GUI work.
- Added Packaging Scripts such as `packaging/windows_start_worker.ps1` and `packaging/mac_start_worker.sh`.
- Added `Desktop Runtime Placeholder` in `worker_client/desktop/README.md` and `placeholder.py`.

Explicitly not included: GUI, system tray, Electron, Tauri, PySide, exe/dmg packaging, real remote browser screen, real platform automation, TikTok / YouTube / X automation, login automation, cookie injection, fingerprint bypass, proxy pools, or captcha automation.

## Phase 30 Worker Console GUI Foundation

Completed:

- Added `worker_console` as an independent frontend project using Vite, React, TypeScript, and Tailwind.
- Default local API: `VITE_LOCAL_WORKER_API=http://127.0.0.1:9100`.
- Added Dashboard, Runtime Control, Logs, and Connection Info sections.
- Added `worker_console/src/api/localWorkerClient.ts` with `getStatus`, `getHealth`, `getLogs`, `startRuntime`, `stopRuntime`, `restartRuntime`, `startHeartbeat`, and `stopHeartbeat`.
- When the local API is unavailable, the UI shows `Worker API unreachable`, `请确认 worker_client 是否启动`, and `请确认端口是否为 9100`.

Explicitly not included: system tray, auto update, Electron, Tauri, PySide, no exe / dmg, TikTok / YouTube / X automation, login automation, cookie injection, proxy pools, fingerprint bypass, captcha automation, or real platform automation.
## Phase 31: Worker Console Desktop App Foundation

Status: completed.

This phase adds `worker_console_desktop`, a Tauri + React + Vite + TypeScript + Tailwind desktop shell foundation for the local Worker Console. The desktop app defaults to `VITE_LOCAL_WORKER_API=http://127.0.0.1:9100` and calls the Phase 29 Local API for Worker status, runtime state, heartbeat state, connection info, and logs.

Key files:

- `worker_console_desktop/package.json`
- `worker_console_desktop/src/api/localWorkerClient.ts`
- `worker_console_desktop/src/main.tsx`
- `worker_console_desktop/src-tauri/tauri.conf.json`
- `worker_console_desktop/src-tauri/src/main.rs`

Development commands:

```bash
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

Boundary: no formal installer, no exe / dmg, no system tray, no auto update, no autostart, and no real platform automation.

## Phase 32: Worker Console System Tray & Desktop Runtime Foundation

Status: completed.

This phase upgrades `worker_console_desktop` into a desktop runtime foundation with Tauri System Tray, Minimize To Tray, Tray Runtime Control, Desktop Status Sync, and AutoStart Placeholder documentation.

Completed:

- System Tray integration in `worker_console_desktop/src-tauri/src/main.rs`.
- Tray menu: Show Console, Hide Window, Start Runtime, Stop Runtime, Restart Runtime, Start Heartbeat, Stop Heartbeat, Refresh Status, Quit.
- `worker_console_desktop/src-tauri/desktop-runtime.json` defaults `minimize_to_tray=true`.
- `worker_console_desktop/src/settings.ts` and `settings.example.json` support `localWorkerApi`, `minimizeToTray`, and `refreshIntervalMs`.
- UI shows connected, reconnecting, disconnected, online, offline, error, last successful sync, and last error.
- Logs Panel supports auto refresh, manual refresh, error highlight, clear display, and last updated time.
- `worker_console_desktop/autostart/` is an AutoStart Placeholder only.

Boundary: no formal installer, no exe / dmg, no real autostart registration, no auto-update, no remote shell, no arbitrary command execution, and no real platform automation.

## Phase 33: Conversation Runtime Foundation

Status: completed.

Completed: `conversation_threads`, `conversation_events`, extended `conversation_messages.thread_id`, `ConversationService`, `run_conversation_turn`, Conversation APIs, Worker Console Chat Panel Foundation, Event Timeline, and polling event feed.

Events include `message_received`, `planning_started`, `plan_created`, `agent_started`, `tool_called`, `worker_action_started`, `worker_action_completed`, `assistant_response`, and `error`.

Boundary: this is Conversation Runtime Foundation only. It is not real WebSocket/SSE streaming, not real OpenClaw, not ComfyUI, and not TikTok / YouTube / X automation, login automation, cookie injection, proxy pool, fingerprint bypass, captcha automation, or real platform automation.

## Phase 34: Remote Browser Runtime Foundation

Status: completed.

Phase 34 adds the real remote browser runtime foundation. The AI Server can now select a registered remote worker through `app/browser/providers/remote_provider.py`, dispatch Browser Actions to the customer-machine worker, and let the Playwright runtime in `worker_client/browser_runtime` execute basic browser actions.

Completed:

- Added the `browser_runtime_sessions` model and migration.
- Added `BrowserRuntimeSessionService` for remote session create, get, navigate, screenshot, page-content fetch, close, and activity updates.
- Added API Server routes under `/api/v1/browser-runtime/sessions`.
- Added Worker Runtime API: `/browser/session/create`, `/browser/session/{session_id}/navigate`, `/browser/session/{session_id}/screenshot`, `/browser/session/{session_id}/page`, and `/browser/session/{session_id}/close`.
- Added screenshot storage under `storage/browser_screenshots`, configured by `BROWSER_RUNTIME_SCREENSHOT_DIR`.
- Added Browser Sessions Panel to both Worker Console Web and Worker Console Desktop.
- Updated customer worker setup with `playwright install chromium`.

Boundary: no stealth browser, proxy pool, cookie injection, captcha bypass, TikTok / YouTube / X automation, remote desktop streaming, DevTools remote control, real OpenClaw device, or ComfyUI.

## Phase 35B: Real Client Worker E2E Validation Plan

Status: completed validation plan and script.

This phase adds `scripts/validate_real_client_worker_e2e.py` to validate the full chain after a real customer-machine worker is online: AI Server -> RemoteBrowserProvider -> BrowserWorkerSelector -> real customer-machine `worker_client` -> local `browser_runtime` -> local Playwright Chromium -> screenshot / page content / status returned.

Completed:

- E2E validation script with `server_url`, `workspace_id`, `user_id`, and `expected_worker_name`.
- JSON output and exit codes: `0=PASS`, `1=FAIL`, `2=SKIPPED`.
- When `expected_worker_name` is missing, the script returns `SKIPPED` with reason `real client worker not online` and does not execute browser actions.
- Added `docs/zh/REAL_CLIENT_WORKER_E2E.md` and `docs/en/REAL_CLIENT_WORKER_E2E.md`.
- Documented the Swagger validation flow and Worker Console validation checklist.

Boundary: this does not fabricate real-client E2E success and does not implement TikTok / YouTube / X automation, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, real platform automation, OpenClaw real device, or ComfyUI.

## Phase 35A: Browser Runtime Observability & Replay

Status: completed.

Phase 35A strengthens Phase 34 Remote Browser Runtime observability and debugging. It adds `browser_runtime_events`, `browser_runtime_snapshots`, `browser_runtime_replays`, and `BrowserRuntimeObservabilityService`.

Completed:

- Timeline Event Flow: `session_created`, `navigate_started`, `navigate_completed`, `screenshot_started`, `screenshot_completed`, `page_snapshot_captured`, `action_failed`, `session_closed`, and `replay_requested`.
- Snapshot Storage: page HTML/TXT, error JSON, and replay JSON are written under `BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots`; screenshots continue to use `storage/browser_screenshots`.
- Replay Metadata Flow: replay is metadata-only and does not re-run browser actions.
- Failure Debug: failed actions record worker_id, action_type, target/url, error, duration_ms, last known URL, and last page title.
- New APIs: events, snapshots, replay, and replay export.
- Worker Console Web/Desktop Browser Sessions Panel now includes Timeline, Screenshot history, Page snapshots, Replay metadata, Refresh events, and Refresh snapshots.

Boundary: this is not live stream, not VNC/noVNC, not DevTools remote control, and does not re-execute replay. It does not implement TikTok / YouTube / X, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, or real platform automation.

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

## Phase 38: Conversation Runtime Tool Execution Bridge (Completed)

Completed:
- Added `ConversationToolRouter` (`app/conversation/tool_router.py`) for deterministic rule-based routing. It is not an autonomous agent.
- Conversation run records `route_selected`, `tool_execution_started`, `tool_execution_completed`, `tool_execution_failed`, `agent_execution_started`, `agent_execution_completed`, `planning_execution_started`, `planning_execution_completed`, `bridge_fallback`, and `bridge_error`.
- `POST /api/v1/conversations/{thread_id}/run` returns `route_name`, `selected_tool`, `events_created`, `success`, `summary`, and `result_metadata`.
- Browser Bridge composes “open a page and screenshot” through `browser_tool`: create session -> navigate -> screenshot -> get page -> close session.
- OpenClaw mock bridge calls `openclaw_tool` mock only. It never calls real OpenClaw or real devices.
- RAG bridge calls `rag_search_tool` and returns a clear message when `collection_name` is missing.
- Content bridge calls `ContentAgent`.
- Planning bridge calls `PlanningService` to create a plan and steps. It does not execute real platform publishing.
- Admin Dashboard, Worker Console, and Worker Console Desktop show route selected, selected tool, tool status, result summary, and metadata panel.

Boundaries: this is not autonomous agent, not WebSocket, not SSE, and not real platform automation. It does not implement TikTok / YouTube / X automation, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, real platform publishing, real OpenClaw, or ComfyUI.

## Phase 39: Conversation Execution Review & Approval Flow (Completed)

Status: completed.

Phase 39 adds an execution review and approval gate to Conversation Runtime so one sentence cannot directly trigger medium/high risk Tool, Browser, OpenClaw mock, or future platform actions.

Completed:

- Added the `conversation_approvals` table with `route_name`, `selected_tool`, `risk_level`, `approval_status`, `proposed_action`, `proposed_payload`, reviewer fields, and status timestamps.
- Added `ConversationApprovalService` for create approval, approve, reject, cancel, expire pending, and mark executed.
- Added `ConversationRiskPolicy` for low / medium / high risk classification.
- `POST /api/v1/conversations/{thread_id}/run` supports `auto_safe`, `review_first`, and `execute_after_approval`.
- Tool Execution Gate: medium/high risk actions cannot execute without approval; approved actions execute through the execute API; executed approvals cannot run again.
- Added approval events: `approval_required`, `approval_created`, `approval_approved`, `approval_rejected`, `approval_cancelled`, `approval_expired`, `approval_executed`, `execution_blocked_pending_approval`, `execution_after_approval_started`, `execution_after_approval_completed`, and `execution_after_approval_failed`.
- Added Approval APIs: `GET /api/v1/conversations/{thread_id}/approvals`, `GET /api/v1/conversation-approvals/{approval_id}`, approve, reject, cancel, and execute.
- Admin Dashboard, Worker Console, and Worker Console Desktop now include a pending approvals panel with proposed action preview, proposed payload JSON, risk badge, approve / reject / cancel, and execute approved action.

Boundaries: this is not a full permission system, not WebSocket/SSE, and not real platform publishing. It does not implement TikTok / YouTube / X automation, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, real OpenClaw, or ComfyUI.
## Phase 40: Conversation Execution Templates & Playbooks

Status: completed.

This phase adds `conversation_playbooks` and `conversation_playbook_runs` so common Conversation execution flows can be reused as templates. The implementation includes `ConversationPlaybookService`, `ConversationPlaybookExecutor`, built-in Playbooks, Playbook Runs, Step Timeline, and Approval integration.

Completed built-ins:
- `browser_search_summary`
- `browser_screenshot_report`
- `rag_answer`
- `content_generation`
- `trend_research_draft`
- `openclaw_mock_device_check`

Safety boundary:
- Medium/high risk steps still go through the Phase 39 approval gate.
- `review_first`, `auto_safe`, and `execute_after_approval` remain active.
- This is not a full workflow builder.
- This is not an autonomous agent.
- There is no real social publishing, login, captcha, proxy, fingerprint handling, or real OpenClaw execution.

## Phase 41: Playbook Run Artifacts & Output Library

Status: completed.

Phase 41 adds `output_artifacts` and an Output Library for reusable results from Conversation, Playbook, Tool, Browser Runtime, RAG, ContentAgent, Planning, and OpenClaw mock flows.

Completed:
- `OutputArtifactService` supports create, list, get, update, soft delete, export, create from Playbook Run, create from Conversation message, and create from Browser Runtime snapshot.
- Completed Playbook Runs automatically generate artifacts: `content_generation` creates `content_draft`; `browser_screenshot_report` creates `screenshot` and `report`; `rag_answer` creates `rag_answer`; planning creates `plan`; OpenClaw mock creates `json`.
- Assistant messages can be saved with Save as Artifact.
- Export supports markdown / json / txt.
- Export files are stored under `storage/output_artifacts/{workspace_id}/{artifact_id}/`.
- Events include `artifact_created`, `artifact_exported`, `artifact_deleted`, and `artifact_linked_to_playbook_run`.
- Admin Dashboard, Worker Console, and Worker Console Desktop include Output Library / generated artifacts panels.

Boundaries:
- This is not a full DAM.
- No S3 / MinIO integration.
- No production publishing asset management.
- No TikTok / YouTube / X, login, captcha, proxy, fingerprint handling, real OpenClaw, or ComfyUI.
## Phase 42: Task Orchestration & Background Execution (Completed)

Completed: `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, `TaskRetryPolicy`, and the `/api/v1/task-runs` API. `POST /api/v1/conversations/{thread_id}/run` now supports `execution_mode=immediate|background|scheduled` plus `scheduled_at`; background mode returns `task_run_id` and clients poll task status and timeline. Background Conversation / Playbook execution records queued / running / waiting_approval / retrying / completed / failed / cancelled / expired states, supports retry, cancel, approval resume, and links Output Library artifacts with `task_run_id`.

Boundary: this is an in-process queue foundation, not Celery, RabbitMQ, Kubernetes scheduler, or production HA distributed queue. It does not implement TikTok / YouTube / X automation, real publishing, login, CAPTCHA, proxy/fingerprint bypass, real OpenClaw, or ComfyUI.

Phase 42 verifier markers: not Celery, not Kubernetes, Task Orchestration & Background Execution, `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, `TaskRetryPolicy`, `execution_mode`.
## Phase 43: Task Scheduler Persistence & Worker Recovery (Completed)

Completed: Task Scheduler Persistence, `task_scheduler_state`, Task Lease fields on `task_runs`, `TaskRecoveryService`, Scheduler Health API, manual recovery API, Failed Diagnostics, and frontend scheduler health panels.

Task Lease: running task runs receive `lease_owner`, `lease_token`, `lease_expires_at`, and `heartbeat_at`. Expired lease and stale heartbeat are recoverable through scan or manual recover.

Recovery rules: running + expired lease or stale heartbeat -> retrying if retry budget remains, otherwise failed; pending scheduled due -> queued; retrying delay elapsed -> queued; waiting_approval is not auto-executed; completed/cancelled/expired are not recovered.

Admin Dashboard now shows Scheduler Health, lease status, recoverable badge, diagnostics panel, scheduled due indicator, and manual recover. Worker Console and Worker Console Desktop show simplified Task recovery state.

Boundary: this remains an in-process scheduler foundation, not Celery, not Kubernetes, and not production HA distributed queue.

<!-- PHASE44_STATUS:START -->
## Phase 44 - Output Artifact Pipeline & Export System

Status: completed.

Implemented Artifact lineage, `artifact_relationships`, `ArtifactExportService`, `ArtifactPackagingService`, `ArtifactRetentionService`, export/package APIs, Artifact Explorer UI, lineage graph lookup, relationship graph lookup, retention preview, and bundle metadata. Current storage roots are `storage/output_artifacts`, `storage/output_packages`, and `storage/output_exports`.

Boundary: this is not a full DAM, not a production object storage platform, and not a production S3 / MinIO / CDN system.
<!-- PHASE44_STATUS:END -->

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

Phase 46 adds a graph-capable workflow runtime on top of the Phase 45 Workflow State foundation. It introduces `workflow_graphs`, `workflow_graph_nodes`, `workflow_graph_edges`, and `workflow_replays`, plus `WorkflowExecutionPlanner` for graph validation, dependency resolution, conditional routing, retry/fallback planning, and replay metadata.

Completed:

- Workflow Graph Runtime stores graph definitions, nodes, edges, entry node, version, retry policy, timeout metadata, and execution mode.
- Conditional Execution uses `SafeConditionEvaluator` for `workflow.variables`, `workflow.status`, `step.output`, `artifact.metadata`, and `approval.status` conditions. Supported operators are `==`, `!=`, `and`, `or`, `in`, and `exists`.
- Workflow runs now track `workflow_graph_id`, `graph_execution`, `current_node_key`, `planned_next_nodes`, `skipped_nodes`, `retry_state`, and `fallback_state`.
- Workflow steps now track `node_key`, `parent_node_key`, and `dependency_state`.
- Replay Foundation creates `workflow_replays` metadata from checkpoints; it does not re-execute actions.
- Output Artifact graph lineage adds `producing_node_key`, `replay_source`, and `graph_lineage`; Agent Memory Snapshots can store `node_key`.
- Admin Dashboard adds Workflow Graphs with node list, edge list, planner result, conditional routing result, Retry/Fallback Path, and replay panel.
- Worker Console and Desktop show simplified graph execution state.

Boundaries: not a visual DAG builder, not a drag/drop workflow editor, not distributed orchestration engine, not ComfyUI, not WebSocket/SSE streaming, not real platform publishing, and not TikTok / YouTube / X automation.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47: Workflow Template Registry & Versioning

Status: completed.

Phase 47 adds Workflow Template Registry & Versioning on top of the Phase 46 Workflow Graph Runtime. It adds `workflow_templates`, `workflow_template_versions`, and `workflow_template_runs`. `WorkflowTemplateRegistryService` manages template registration, immutable version creation, active version activation, import/export, template runs, and built-in template seeding. `WorkflowTemplateCompatibilityService` checks required node types, input_schema, output_schema, graph validation, risk_level, runtime capabilities, warnings, errors, and missing_capabilities.

Built-in templates include `browser_screenshot_report_graph`, `content_generation_graph`, `rag_answer_graph`, `approval_then_browser_graph`, `openclaw_mock_inspect_graph`, and `task_retry_demo_graph`.

Version and status fields include `template_key`, `current_version`, `latest_version`, `validation_status`, and `compatibility`. Conversation, Task, Output Artifact, and Agent Memory records can store `workflow_template_id`, `workflow_template_version_id`, and `workflow_template_run_id`.

Frontends add Template Library support: Admin Dashboard shows template detail, Version list, Validation result, Compatibility result, Import / Export JSON, Run template, and Template runs. Worker Console and Worker Console Desktop provide simplified Template Library, select template, run template, and template run status views.

Boundaries: this is not a visual DAG builder, not a drag/drop workflow editor, not ComfyUI, not WebSocket/SSE streaming, not TikTok / YouTube / X automation, not real platform publishing, and not automatic login, captcha automation, proxy pools, fingerprint bypass, or real OpenClaw.
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

?????Phase 51 ?????????????????????????????????? release readiness???????????????????????????????? code signing?auto updater?MSI/EXE?DMG/notarization ? Kubernetes/Helm?

Keywords: Phase 51; Release Packaging & Deployment Bundle Foundation; release/manifest.json; release/version.json; server deployment bundle; frontend production build bundle; desktop release readiness; aiops.release.env.template; validate_release_packaging.py; Windows / Mac startup scripts; not a formal production release; no code signing; no auto updater; no MSI/EXE; no DMG/notarization; no Kubernetes/Helm.
<!-- PHASE51_SYNC:END -->
