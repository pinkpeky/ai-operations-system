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
