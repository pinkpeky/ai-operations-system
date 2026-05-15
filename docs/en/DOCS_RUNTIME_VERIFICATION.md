# Docs Runtime Verification

## Phase 20 Verification Scope

`scripts/verify_docs_runtime.py` now checks Phase 20 runtime and docs alignment:

- `BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100` is documented in `CURRENT_RUNTIME.md` and exposed in `docker-compose.yml`.
- API Reference documents `Real Browser Worker Service`, `browser-worker`, `worker/main.py`, `worker/browser_worker/playwright_runtime.py`, `WORKER_TIMEOUT_SECONDS`, and `WORKER_SCREENSHOT_DIR`.
- `PROJECT_OVERVIEW.md` documents Phase 20, the API Server -> Worker call chain, Playwright Chromium, and `worker/screenshots`.
- `PROJECT_STATUS.md` marks Phase 20 as complete.

Run:

```powershell
python scripts/verify_docs_runtime.py
```

Expected result: `SUMMARY: PASS`.

Last updated: 2026-05-12

This document explains how to verify that docs match the current runtime.

## Goal

Docs Runtime Verification prevents:

- APIs being added without API_REFERENCE updates.
- Config defaults changing without CURRENT_RUNTIME updates.
- docker-compose drifting from config.
- Incorrect phase status.
- File Upload Pipeline being implemented without docs updates.
- Documentation claiming features that do not exist.

## Run

From the repository root:

```powershell
python scripts/verify_docs_runtime.py
```

Phase 17 verification additionally checks Browser Adapter runtime drift:

- `BROWSER_PROVIDER` in `app/core/config.py`, `docker-compose.yml`, and `docs/CURRENT_RUNTIME.md`.
- Browser API paths in OpenAPI and API Reference.
- `browser_sessions`, `browser_actions`, `browser_action_logs`.
- `BrowserProvider`, `MockBrowserProvider`, `PlaywrightBrowserProvider`, and `browser_tool`.

Docs must not describe real Playwright/Selenium/OpenClaw execution as completed while `BROWSER_PROVIDER=mock`.

After Phase 18, the docs verifier also checks Playwright Local Provider drift:

- `CURRENT_RUNTIME.md` and `docker-compose.yml` must document `BROWSER_TIMEOUT_SECONDS`, `BROWSER_HEADLESS`, `BROWSER_TYPE`, `BROWSER_VIEWPORT_WIDTH`, `BROWSER_VIEWPORT_HEIGHT`, and `BROWSER_SCREENSHOT_DIR`.
- OpenAPI and API Reference must document `GET /api/v1/browser/screenshot/{session_id}/{filename}`.
- API Reference must document `PlaywrightLocalProvider`, `playwright_local`, `browser_id`, `page_id`, `provider_session_metadata`, `selector`, `target_url`, `screenshot_path`, `page_title`, and `get_page_content`.
- `PROJECT_OVERVIEW.md` must document Phase 18, Playwright Local Provider Integration, Screenshot System, and safety boundaries.

Docs must still state clearly that Phase 18 is not a Browser Agent and does not implement TikTok / YouTube / X, login automation, cookie injection, fingerprint bypass, OCR, visual AI, or Browser Worker.

After Phase 19, the docs verifier also checks Remote Browser Worker drift:

- `CURRENT_RUNTIME.md` and `docker-compose.yml` must document `BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS` and `BROWSER_WORKER_RETRY_COUNT`.
- OpenAPI and API Reference must document `/api/v1/browser-workers/register`, `/api/v1/browser-workers/{worker_id}/heartbeat`, and `/api/v1/browser-workers`.
- OpenAPI and API Reference must document mock runtime: `/api/v1/browser-worker-runtime/health`, `/api/v1/browser-worker-runtime/sessions`, `/api/v1/browser-worker-runtime/actions`, and `/api/v1/browser-worker-runtime/sessions/{session_id}/close`.
- API Reference must document `RemoteBrowserProvider`, `BrowserWorkerClient`, `browser_workers`, `browser_worker_sessions`, `browser_worker_actions`, `remote_session_id`, and `remote_action_id`.
- `PROJECT_OVERVIEW.md` must document Phase 19, Remote Browser Worker Foundation, Worker Registration, Worker Heartbeat, and Worker Runtime Mock.

Docs must still state clearly that Phase 19 does not include real external worker deployment, TikTok / YouTube / X, account login, fingerprint bypass, proxy pools, or captcha automation.

Expected output:

```text
PASS: required docs files exist
PASS: CURRENT_RUNTIME contains config defaults
PASS: OpenAPI exposes required paths
PASS: API_REFERENCE includes required paths and fields
PASS: PROJECT_OVERVIEW includes current architecture markers
PASS: Phase 14 status is documented
SUMMARY: PASS
```

## Output Levels

`PASS`:

- Check succeeded.

`WARNING`:

- Potential drift. Review manually.

`ERROR`:

- Must be fixed. The script exits with a non-zero status.

## Current Checks

The script reads:

- `app/core/config.py`
- `docker-compose.yml`
- FastAPI OpenAPI schema
- `docs/CURRENT_RUNTIME.md`
- `docs/PROJECT_OVERVIEW.md`
- `docs/zh/API_REFERENCE.md`
- `docs/en/API_REFERENCE.md`
- `docs/zh/PROJECT_STATUS.md`
- `docs/en/PROJECT_STATUS.md`

It checks:

- Provider defaults.
- Search defaults.
- Embedding dimension.
- Upload settings.
- Required API paths.
- `search_mode`, `dense_top_k`, `keyword_top_k`, `final_top_k`, and `duplicate_strategy`.
- Phase 12 status.
- Task reliability APIs: cancel, retry, events, logs, observability summary.
- `task_events`, `task_logs`, and `duration_ms`.
- Tool Calling APIs: `/tools`, `/tools/{tool_name}`, `/tools/{tool_name}/execute`, and `/tool-calls`.
- `tool_call_logs`, `tool_name`, `tool_input`, and `tool_output`.
- Phase 13 status and Tool Calling overview markers.
- Memory APIs: `/memory/sessions`, `/memory/sessions/{session_id}`, `/memory/messages`, `/memory/messages/{session_id}`, `/memory/memories`, and `/memory/memories/{memory_id}`.
- `conversation_sessions`, `conversation_messages`, `agent_memories`, `memory_trace`, `recent_messages_count`, and `retrieved_memories_count`.
- Phase 14 status and Memory Foundation overview markers.
- Multi-Agent APIs: `/agents/registry`, `/multi-agent/runs`, `/multi-agent/runs/{run_id}`, `/multi-agent/runs/{run_id}/execute-chain`, `/multi-agent/runs/{run_id}/messages`, and `/multi-agent/runs/{run_id}/handoffs`.
- `agent_runs`, `agent_messages`, `agent_handoffs`, `AgentRegistry`, `agents_involved`, and `handoff_trace`.
- Phase 15 status and Multi-Agent Foundation overview markers.
- Planning APIs: `/plans`, `/plans/{plan_id}`, `/plans/{plan_id}/execute`, `/plans/{plan_id}/cancel`, `/plans/{plan_id}/steps`, and `/plans/{plan_id}/reviews`.
- `plans`, `plan_steps`, `plan_reviews`, `SimplePlannerAgent`, `PlanStep`, `PlanReview`, and planning `memory_trace`.
- Phase 16 status and Agent Planning Foundation overview markers.

## Docs Sync Rules

When adding an API:

1. Update the route.
2. Update the schema.
3. Update tests.
4. Update zh/en API_REFERENCE.
5. Run the verifier.

When adding config:

1. Update `app/core/config.py`.
2. Update `.env.example`.
3. Update `docker-compose.yml`.
4. Update `docs/CURRENT_RUNTIME.md`.
5. Update zh/en DEPLOYMENT.
6. Run the verifier.

When completing a phase:

1. Update `docs/PROJECT_OVERVIEW.md`.
2. Update zh/en PROJECT_STATUS.
3. Update zh/en ARCHITECTURE.
4. Update zh/en API_REFERENCE.
5. Update zh/en DEPLOYMENT.
6. Update zh/en DEVELOPMENT_GUIDE.
7. Update the Word snapshot.
8. Run pytest, Docker verification, and docs verifier.

## Test Integration

`tests/test_docs_runtime_verification.py` runs:

```powershell
python scripts/verify_docs_runtime.py
```

Docs drift therefore fails pytest.

## Scope

The verifier is a lightweight consistency check. It does not replace:

- Full API contract testing.
- Migration validation.
- Docker smoke testing.
- Security review.
- Performance testing.

Its job is to keep docs synchronized with runtime.
## Phase 21 Verification Scope

`scripts/verify_docs_runtime.py` now verifies Browser Worker Reliability:

- `CURRENT_RUNTIME.md` must document worker health, session cleanup, action retry, and screenshot retention settings.
- OpenAPI must include worker health summary, available workers, mark offline, cleanup sessions, worker sessions, and screenshot cleanup.
- `API_REFERENCE.md` must document `BrowserWorkerHealthService`, `BrowserWorkerSelector`, `BrowserSessionCleanupService`, `ScreenshotCleanupService`, capacity fields, and retry fields.
- `PROJECT_STATUS.md` must declare Phase 21 as complete.

If Phase 21 APIs or settings change, update docs first and then run:

```powershell
python scripts/verify_docs_runtime.py
```

## Phase 22 Verification Scope

`scripts/verify_docs_runtime.py` now verifies Persistent Browser Profile Foundation:

- `CURRENT_RUNTIME.md` must document `BROWSER_PROFILE_ROOT`.
- OpenAPI must include browser profile APIs and `POST /api/v1/browser/sessions/{session_id}/close`.
- `API_REFERENCE.md` must document `BrowserProfileService`, `browser_profiles`, `profile_id`, `profile_path`, `persistent_context_enabled`, `locked_by_session_id`, `locked_at`, `last_used_at`, `launch_persistent_context`, `BROWSER_PROFILE_ROOT`, and `WORKER_PROFILE_DIR`.
- `PROJECT_OVERVIEW.md` must document Phase 22, profile lock/release, worker-side persistent context, and `worker/profiles`.
- `PROJECT_STATUS.md` must declare Phase 22 as complete.

If Phase 22 APIs, schema fields, or profile runtime settings change, update docs first and then run:

## Phase 23 Verification Scope

`scripts/verify_docs_runtime.py` now verifies Browser Profile Health & Recovery:

- `config.py`, `.env.example`, and `docker-compose.yml` must document `BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS`, `BROWSER_PROFILE_BACKUP_ENABLED`, `BROWSER_PROFILE_MAX_BACKUPS`, `BROWSER_PROFILE_UNUSED_DAYS`, and `BROWSER_PROFILE_BACKUP_ROOT`.
- OpenAPI must expose `GET /api/v1/browser/profiles/health/summary`, `POST /api/v1/browser/profiles/{profile_id}/health-check`, `POST /api/v1/browser/profiles/recover-stale-locks`, `POST /api/v1/browser/profiles/{profile_id}/backup`, `GET /api/v1/browser/profiles/{profile_id}/backups`, `POST /api/v1/browser/profiles/{profile_id}/restore`, `POST /api/v1/browser/profiles/cleanup`, and `GET /api/v1/browser/profiles/{profile_id}/usage-logs`.
- `API_REFERENCE.md` must document `BrowserProfileHealthService`, `BrowserProfileBackupService`, `BrowserProfileCleanupService`, `browser_profile_usage_logs`, `health_status`, `last_health_check_at`, `last_error`, `usage_count`, `corrupted_at`, `backup_path`, `last_backup_at`, `recover-stale-locks`, and `health/summary`.
- `PROJECT_OVERVIEW.md` must document Phase 23, profile health, stale lock recovery, profile backup, and profile cleanup.
- `PROJECT_STATUS.md` must declare Phase 23 as complete.

If Phase 23 APIs, schema fields, migrations, or runtime settings change, update docs first and then run:

```powershell
python scripts/verify_docs_runtime.py
```

```powershell
python scripts/verify_docs_runtime.py
```

## Phase 24 Verification Scope

`scripts/verify_docs_runtime.py` now verifies Human-in-the-loop Browser Control:

- `config.py`, `.env.example`, and `docker-compose.yml` must document `BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS`.
- OpenAPI must expose `/api/v1/browser/human-control/request`, `/api/v1/browser/human-control`, `/api/v1/browser/human-control/{control_session_id}`, approve/start/complete/cancel/events routes, and metadata-level worker runtime `/human-control/*` routes.
- `API_REFERENCE.md` must document `BrowserHumanControlService`, `browser_human_control_sessions`, `browser_human_control_events`, `human_control_status`, `human_control_session_id`, `paused_at`, `resumed_at`, `request_human_control`, and `complete_human_control`.
- `PROJECT_OVERVIEW.md` must document Phase 24, Human-in-the-loop Browser Control, session paused/resumed behavior, and the metadata-level worker boundary.
- `PROJECT_STATUS.md` must declare Phase 24 as complete.

If Phase 24 APIs, schema fields, migrations, or runtime settings change, update docs first and then run:

```powershell
python scripts/verify_docs_runtime.py
```

## Phase 25 Verification Scope

`scripts/verify_docs_runtime.py` now verifies Browser Worker UI Access Placeholder:

- `config.py`, `.env.example`, and `docker-compose.yml` must document `BROWSER_UI_ACCESS_TIMEOUT_SECONDS`.
- OpenAPI must expose `/api/v1/browser/ui-access`, `/api/v1/browser/ui-access/expire`, `/api/v1/browser/ui-access/{access_session_id}`, revoke, validate, and `/api/v1/browser-worker-runtime/ui-access/capabilities`.
- `API_REFERENCE.md` must document `BrowserUIAccessService`, `browser_ui_access_sessions`, `access_token_hash`, `remote_control_url`, `live_view_url`, `devtools_url`, `create_ui_access`, and `revoke_ui_access`.
- `PROJECT_OVERVIEW.md` must document Phase 25, Browser Worker UI Access Placeholder, access token hash storage, placeholder URL generation, and explicit non-support for real VNC/noVNC/DevTools UI.
- `PROJECT_STATUS.md` must declare Phase 25 as complete.

If Phase 25 APIs, schema fields, migrations, or runtime settings change, update docs first and then run:

```powershell
python scripts/verify_docs_runtime.py
```

## Phase 26 Verification Scope

`scripts/verify_docs_runtime.py` now verifies Browser Worker Security & Access Control:

- `CURRENT_RUNTIME.md` must document `BROWSER_WORKER_AUTH_ENABLED`, `BROWSER_WORKER_AUTH_STRICT`, `BROWSER_ALLOWED_DOMAINS`, `BROWSER_BLOCKED_DOMAINS`, and `BROWSER_ALLOW_EXTERNAL_DOMAINS`.
- OpenAPI must contain `POST /api/v1/browser-workers/{worker_id}/rotate-secret`, `POST /api/v1/browser-workers/{worker_id}/revoke`, `GET /api/v1/browser/security/audit-logs`, and `POST /api/v1/browser/security/policy/check`.
- `API_REFERENCE.md` must document `BrowserWorkerAuthService`, `worker_secret_hash`, `X-Worker-Signature`, `UI Access Scope`, `BrowserActionPolicyService`, and `browser_security_audit_logs`.
- `PROJECT_OVERVIEW.md` must document Phase 26, Browser Worker Security & Access Control, signed worker request, UI Access Scope, and Browser Action Policy.
- `PROJECT_STATUS.md` must declare Phase 26 as complete.

If Phase 26 APIs, schema fields, migrations, or runtime settings change, update docs first and then run:

```powershell
python scripts/verify_docs_runtime.py
```

## Phase 27 Verification Scope

`scripts/verify_docs_runtime.py` now verifies Customer Machine Worker Bootstrap:

- Required files must exist: `worker_client/main.py`, `worker_client/config.py`, `worker_client/registration.py`, `worker_client/heartbeat.py`, `worker_client/runtime.py`, `worker_client/cli.py`, and `worker_client/worker_config.example.yaml`.
- `API_REFERENCE.md` must document `worker_client`, `worker_config.example.yaml`, `worker_config.yaml`, `worker_state.json`, `python -m worker_client.cli register`, `python -m worker_client.cli heartbeat`, `python -m worker_client.cli serve`, `python -m worker_client.cli start`, `registration flow`, `heartbeat flow`, and `local worker runtime`.
- `PROJECT_OVERVIEW.md` must document Phase 27, Customer Machine Worker Bootstrap, customer machine usage, registration flow, heartbeat flow, and local worker runtime.
- zh/en `PROJECT_STATUS.md` must declare Phase 27 as complete.

If Phase 27 CLI behavior, config shape, local runtime protocol, or Worker Client security behavior changes, update docs first and then run:

```powershell
python scripts/verify_docs_runtime.py
```

## Phase 29 Worker Client Runtime Verification

Docs verification now also checks Worker Console Foundation files: `worker_client/runtime_manager.py`, `worker_client/status.py`, `worker_client/logging.py`, `worker_client/local_api_client.py`, `packaging/windows_start_worker.ps1`, `packaging/mac_start_worker.sh`, and Worker Client install docs.

After any Worker Client runtime change, run:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

The local runtime API is documented as local-only: `GET /local/status`, `GET /local/health`, `POST /local/runtime/start`, `POST /local/runtime/stop`, `POST /local/runtime/restart`, `POST /local/heartbeat/start`, `POST /local/heartbeat/stop`, `GET /local/logs`.

## Phase 30 Worker Console Docs Verification

Docs verifier checks `worker_console`, `worker_console/src/api/localWorkerClient.ts`, `VITE_LOCAL_WORKER_API`, `http://127.0.0.1:9100`, Worker Console GUI Foundation docs, and the explicit no system tray / no exe / dmg boundary.
## Phase 31 Verification Addition

Docs Runtime Verification now covers the Worker Console Desktop App Foundation. Checked items include:

- `worker_console_desktop/package.json`
- `worker_console_desktop/src/api/localWorkerClient.ts`
- `worker_console_desktop/src-tauri/tauri.conf.json`
- `VITE_LOCAL_WORKER_API=http://127.0.0.1:9100`
- `npm run tauri dev`
- `Worker Console Desktop App Foundation`

After Phase 31, the required verification flow remains:

```bash
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

The desktop app is only a Tauri foundation shell: no formal installer, no exe / dmg, no system tray, and no auto update.

## Phase 32 Verification Addition

Docs Runtime Verification now covers the Worker Console System Tray & Desktop Runtime Foundation. Checked items include:

- `worker_console_desktop/src-tauri/src/main.rs`
- `worker_console_desktop/src-tauri/desktop-runtime.json`
- `worker_console_desktop/src/settings.ts`
- `worker_console_desktop/src/desktopBridge.ts`
- `worker_console_desktop/settings.example.json`
- `worker_console_desktop/autostart/README.md`
- `System Tray`
- `Minimize To Tray`
- `Tray Runtime Control`
- `Desktop Status Sync`
- `AutoStart Placeholder`

The docs must still distinguish completed and missing capabilities: there is no formal installer, no auto-update, and no real autostart registration.

## Phase 33: Conversation Runtime Foundation

Status: completed.

Completed: `conversation_threads`, `conversation_events`, extended `conversation_messages.thread_id`, `ConversationService`, `run_conversation_turn`, Conversation APIs, Worker Console Chat Panel Foundation, Event Timeline, and polling event feed.

Events include `message_received`, `planning_started`, `plan_created`, `agent_started`, `tool_called`, `worker_action_started`, `worker_action_completed`, `assistant_response`, and `error`.

Boundary: this is Conversation Runtime Foundation only. It is not real WebSocket/SSE streaming, not real OpenClaw, not ComfyUI, and not TikTok / YouTube / X automation, login automation, cookie injection, proxy pool, fingerprint bypass, captcha automation, or real platform automation.

## Phase 34 Docs Runtime Verification

The verifier now checks that Phase 34 Remote Browser Runtime Foundation is reflected in runtime docs:

- `browser_runtime_sessions`
- `BrowserRuntimeSessionService`
- `app/browser/providers/remote_provider.py`
- `worker_client/browser_runtime`
- `/browser/session/create`
- `/browser/session/{session_id}/navigate`
- `/browser/session/{session_id}/screenshot`
- `/browser/session/{session_id}/page`
- `/browser/session/{session_id}/close`
- `storage/browser_screenshots`
- `BROWSER_RUNTIME_SCREENSHOT_DIR`
- `Browser Sessions Panel`
- `playwright install chromium`

Run:

```bash
python scripts/verify_docs_runtime.py
```

The expected result is `SUMMARY: PASS`.

## Phase 35B Docs Runtime Verification

The verifier now requires:

- `scripts/validate_real_client_worker_e2e.py`
- `docs/zh/REAL_CLIENT_WORKER_E2E.md`
- `docs/en/REAL_CLIENT_WORKER_E2E.md`
- `Real Client Worker E2E Validation Plan`
- `expected_worker_name`
- `SKIPPED`
- `real client worker not online`
- `do not expose port 9100 to the public internet`
- `Tailscale`
- `VPN`

This keeps docs honest: Phase 35B prepares validation ability and does not claim a real customer-machine E2E pass until the customer machine is actually online.

## Phase 35A Verification Items

Docs Runtime Verification now checks that Browser Runtime Observability & Replay matches runtime code, including:

- `BrowserRuntimeObservabilityService`
- `browser_runtime_events`
- `browser_runtime_snapshots`
- `browser_runtime_replays`
- `BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots`
- events / snapshots / replay / replay export APIs
- API_REFERENCE coverage for metadata-only replay, Snapshot Storage, Timeline Event Flow, and Failure Debug

Run:

```powershell
python scripts/verify_docs_runtime.py
```

Expected result: `SUMMARY: PASS`. Replay is not live stream, not VNC/noVNC, not DevTools remote control, and it does not re-run browser actions.

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
## Phase 38 Docs Runtime Verification

`scripts/verify_docs_runtime.py` now checks `app/conversation/tool_router.py`, `Conversation Runtime Tool Execution Bridge`, `ConversationToolRouter`, `route_selected`, `tool_execution_started`, `route_name`, `selected_tool`, `events_created`, `success`, `summary`, `result_metadata`, and the boundaries: not autonomous agent, not WebSocket, and not SSE.

After Phase 39, the verifier also checks `app/conversation/risk_policy.py`, `app/conversation/services/approval_service.py`, `app/api/routes/conversation_approvals.py`, `conversation_approvals`, `ConversationApprovalService`, `ConversationRiskPolicy`, `review_first`, `auto_safe`, `execute_after_approval`, approval events, pending approvals panel, and the boundary: not a full permission system.
## Phase 40 Docs Runtime Verification

The verifier now checks:

- `app/conversation/services/playbook_service.py`
- `app/conversation/playbook_definitions.py`
- `app/api/routes/conversation_playbooks.py`
- OpenAPI Playbook routes
- `conversation_playbooks`
- `conversation_playbook_runs`
- `playbook_name`
- `playbook_run_id`
- `playbook_step_started`
- `playbook_waiting_approval`
- `playbook_completed`

If Playbook APIs are added or removed, update `scripts/verify_docs_runtime.py` in the same phase.

## Phase 41 Verification Addendum

The docs verifier now checks Output Library coverage: `output_artifacts`, `OutputArtifactService`, `/api/v1/output-artifacts`, artifact events, Save as Artifact, Export markdown, S3 / MinIO boundaries, and the not a full DAM statement. When Output Artifact APIs, fields, or frontend entry points change, update `scripts/verify_docs_runtime.py` in the same phase.
## Phase 42: Task Orchestration & Background Execution

This phase adds the Task Orchestration foundation: `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, and `TaskRetryPolicy`. Conversation / Playbook runs can use `execution_mode=background`, then `/api/v1/task-runs` exposes queued, running, waiting_approval, retrying, completed, failed, cancelled, expired state plus timeline events. `scheduled_at` supports scheduled runs; retry uses exponential backoff; approval resume continues to enforce the Phase 39 Approval Gate; Output Library artifacts are linked by `task_run_id`.

Boundary: this is an in-process queue, not Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue. It does not implement real publishing, real OpenClaw, ComfyUI, CAPTCHA handling, proxies, or fingerprint bypass.
