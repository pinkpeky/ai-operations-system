# Development Guide

## Phase 28 Development Rules

When changing OpenClaw Worker Adapter Foundation, keep code, tests, and docs aligned:

- `worker_client/openclaw/` must remain mock-only until a future real OpenClaw phase explicitly changes it.
- `OpenClawWorkerClient` must call registered Browser Worker `base_url` values and must not bypass Workspace Isolation.
- `openclaw_tool` must continue to write `tool_call_logs`; OpenClaw actions must continue to write `openclaw_action_logs` and `browser_security_audit_logs`.
- New OpenClaw runtime routes must be documented in both `docs/zh/API_REFERENCE.md` and `docs/en/API_REFERENCE.md`.
- Do not add TikTok / YouTube / X automation, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha automation, or real platform automation in this phase.

Required verification flow:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Phase 20 Development Rules

`worker/` is the standalone Browser Worker service. It shares the repository with the API Server but runs as a separate container. Remote browser work must check:

- `worker/main.py`
- `worker/browser_worker/playwright_runtime.py`
- `app/browser/remote/client/browser_worker_client.py`
- `app/browser/providers/remote_browser_provider.py`
- `docker-compose.yml`
- `docs/CURRENT_RUNTIME.md`

Required verification flow:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Phase 27 Development Rules

When changing Customer Machine Worker Bootstrap, keep code, tests, and docs aligned:

- `worker_client/worker_config.example.yaml` is the only committed customer-machine config template.
- Local `worker_client/worker_config.yaml` and `worker_client/worker_state.json` must remain ignored by Git.
- `worker_state.json` may store the plaintext `worker_secret`; never log, print, document, or commit it.
- The registration flow must continue to call `POST /api/v1/browser-workers/register`.
- The heartbeat flow must continue to call `POST /api/v1/browser-workers/{worker_id}/heartbeat` with `X-Worker-Secret` and Phase 26 signed headers.
- The local worker runtime must remain protocol-compatible with the Docker `browser-worker` service.
- Keep `python -m worker_client.cli register`, `heartbeat`, `serve`, and `start` documented whenever CLI behavior changes.
- Do not add OpenClaw real integration, TikTok / YouTube / X automation, login automation, cookie injection, proxy pools, fingerprint bypass, captcha handling, or real platform automation in Phase 27 scope.

Required verification flow:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Phase 26 Development Rules

When changing Browser Worker Security & Access Control, keep the security foundation aligned with the existing Browser, Worker, Profile, and UI Access boundaries:

- `BrowserWorkerAuthService` is the single entry point for worker secret generation, hashing, signing, and verification.
- Plaintext `worker_secret` may be returned only by register / rotate responses; the database may store only `worker_secret_hash`.
- Worker signed requests must use `X-Worker-Signature`, `X-Worker-Timestamp`, `X-Worker-Nonce`, and request body hash validation.
- `BROWSER_WORKER_AUTH_STRICT=false` is for local development and smoke tests only; production hardening should configure a shared secret and enable strict mode.
- `BrowserActionPolicyService` is the single entry point for action type, domain, profile access, worker capability, and UI Access Scope checks.
- Do not loosen `BROWSER_ALLOW_EXTERNAL_DOMAINS=false` by default; new domains must be explicitly added to `BROWSER_ALLOWED_DOMAINS`.
- `browser_security_audit_logs` must record worker auth, UI token, policy block, and profile access security events.
- Changes to `browser_ui_access_sessions.scopes`, `one_time`, `used_at`, `revoked_reason`, `client_ip`, or `user_agent` must update schemas, tests, and docs.
- Do not add real platform login, cookie injection, proxy pools, fingerprint bypass, captcha automation, TikTok / YouTube / X automation, or complete RBAC/JWT/OAuth in Phase 26 scope.

Required verification flow:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Phase 25 Development Rules

When changing Browser Worker UI Access Placeholder, keep the scope limited to backend placeholder access:

- `browser_ui_access_sessions` is the canonical UI access placeholder table.
- Store only `access_token_hash`; never persist plaintext access tokens.
- Return plaintext `access_token` only from `POST /api/v1/browser/ui-access`.
- Generated `remote_control_url` and `live_view_url` must be documented as placeholder URL values.
- `devtools_url` remains `null` until a real DevTools UI is explicitly implemented in a future phase.
- Worker `/ui-access/capabilities` must report `vnc=false`, `novnc=false`, `devtools=false`, and `placeholder=true`.
- `browser_tool` UI access actions must call `BrowserUIAccessService` and keep `tool_call_logs`.
- Do not add VNC, noVNC, Chrome DevTools remote UI, live browser video, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha automation, TikTok / YouTube / X automation, or real platform automation.

Required verification flow:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Phase 24 Development Rules

When changing Human-in-the-loop Browser Control, keep the implementation bounded to backend state management and metadata-level worker signaling:

- `browser_human_control_sessions` and `browser_human_control_events` are the canonical audit tables.
- State transitions must go through `BrowserHumanControlService`; do not scatter pause/resume writes across business code.
- Every transition must write an event: `requested`, `approved`, `started`, `completed`, `cancelled`, `expired`, `timeout`, or `note`.
- Requesting control must pause the browser session and preserve the profile lock and worker session.
- Completing or cancelling control must resume the browser session when the linked session still exists.
- Regular browser actions must stay blocked while the session is paused.
- `browser_tool` human-control actions must call the service and keep `tool_call_logs`.
- Worker `/human-control/*` endpoints are metadata-level only.
- Do not add VNC, noVNC, Chrome DevTools remote UI, automatic login, cookie injection, proxy pools, fingerprint bypass, captcha automation, TikTok / YouTube / X automation, or real platform automation.

Required verification flow:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Do not add social platform automation, login, cookie injection, proxy pools, fingerprint bypass, captcha automation, OCR, visual AI, OpenClaw, or autonomous browser agents to Phase 20 code or docs.

Last updated: 2026-05-12

This guide is for future Codex sessions and developers extending the project.

## Principles

- Do not modify Scheduler core logic unless a phase explicitly requires it.
- Do not modify TaskExecutor core logic unless a phase explicitly requires it.
- Keep RAG, LLM, Reranker, and File Upload logic in separate service layers.
- Never bypass Workspace Isolation.
- Do not document features that do not exist in code.
- Update docs after every phase.

## Layering

API:

- `app/api/routes/`
- Parse requests, inject dependencies, convert errors.

Services:

- `app/services/` or domain-specific service folders.
- Own business workflows.

Repositories:

- `app/repositories/`
- Own database access.

Providers:

- LLM: `app/agents/providers/`
- Embedding: `app/rag/providers/`
- Reranker: `app/reranker/providers/`

Schemas:

- `app/schemas/`
- Pydantic request/response models.

Tests:

- `tests/`
- Unit tests should not require real Ollama.

## File Upload Development Rules

Relevant paths:

```text
app/file_pipeline/
  parsers/
  services/
app/api/routes/files.py
app/schemas/file.py
```

Rules:

- Parsers only extract text.
- Text cleaner only normalizes text.
- Upload service handles temp files, hash, duplicate detection, parser dispatch, and lifecycle ingestion.
- DocumentLifecycle remains the canonical path for document/chunk/Qdrant writes.
- New file types require parser tests.
- Do not document unsupported formats as supported.

## Docs-as-Code Rules

Docs are the project Single Source of Truth.

Every completed phase must update:

- `docs/PROJECT_OVERVIEW.md`
- `docs/CURRENT_RUNTIME.md`
- `docs/zh/*`
- `docs/en/*`
- `docs/Aiops Project Documentation Update Request For Codex.docx`

New APIs must update:

- Method.
- Path.
- Request JSON or form fields.
- Response JSON.
- Required headers.
- Workspace requirements.
- Debug fields.
- Production / experimental / planned status.

New config must update:

- `app/core/config.py`
- `.env.example`
- `docker-compose.yml`
- `docs/CURRENT_RUNTIME.md`
- zh/en deployment docs.

## Docs Runtime Verification

Run:

```powershell
python scripts/verify_docs_runtime.py
```

The verifier checks:

- Settings defaults.
- docker-compose environment.
- FastAPI OpenAPI routes.
- `CURRENT_RUNTIME.md`.
- `PROJECT_OVERVIEW.md`.
- zh/en API_REFERENCE.
- Phase status.
- File Upload Pipeline fields.

Passing condition:

```text
SUMMARY: PASS
```

If it fails:

1. Read the `ERROR`.
2. Decide whether code or docs are stale.
3. Fix the source.
4. Re-run the verifier.

## Delivery Checklist

Every phase must finish with:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Recommended smoke tests:

- `GET /api/v1/health`
- `POST /api/v1/files/upload`
- `POST /api/v1/rag/search`
- `POST /api/v1/agentic-rag/query`

## Testing Strategy

- Unit tests should not depend on real Ollama.
- Local providers should use mock HTTP clients in tests.
- File parser tests should use small fixtures or fake readers.
- Workspace isolation must be tested across workspaces.
- Docs verifier must be part of the test suite.

## Do Not Implement Yet

- Real reranker.
- Elasticsearch / OpenSearch.
- OCR.
- PPTX / XLSX / image parsing.
- Browser Agent / OpenClaw / Playwright.
- Full RBAC / JWT / OAuth.
- Scheduler core changes.
- TaskExecutor core changes.

## Task Reliability Development Rules

After Phase 12, all task execution changes must preserve these constraints:

- New task statuses must update `TaskStatus`, API_REFERENCE, and the docs verifier.
- TaskExecutor start, success, failure, retry, cancelled skip, and timeout must write `task_events`.
- Key execution records must write `task_logs`.
- Terminal states should record `completed_at` and `duration_ms` when possible.
- `cancel`, `retry`, events, logs, and summary APIs must require `X-Workspace-Id`.
- Scheduler remains responsible for scanning, state transitions, and queueing; only minimal timeout/cancelled adaptation is allowed.
- Do not put Playwright, OpenClaw, video generation, or multi-agent business logic into TaskExecutor core.

New task handlers should return these fields in `TaskExecutionResult.data` when available:

```json
{
  "provider": "mock",
  "model": "mock-llm",
  "latency_ms": 10
}
```

TaskExecutor uses them for structured logs.

## Tool Calling Development Rules

After Phase 13, new internal tools must follow these rules:

- Every tool must inherit from `BaseTool`.
- Every tool must define `name`, `description`, `input_schema`, `output_schema`, and `execute()`.
- Tools that access business data must use `ToolExecutionContext.workspace_id` for isolation.
- Tool execution should go through `ToolRegistry.execute_tool()` so `tool_call_logs` are written.
- New tools must update `docs/zh/API_REFERENCE.md`, `docs/en/API_REFERENCE.md`, and `scripts/verify_docs_runtime.py`.
- Do not connect Browser Agent, OpenClaw, Playwright, Selenium, or external API tools in this phase.
- Do not document autonomous planner or ReAct as completed. Multi-Agent is available only as the Phase 15 fixed-chain foundation.

Recommended tests:

- Registry registration, disable behavior, and input validation.
- Successful and failed tool call logs.
- Workspace isolation.
- Manual Agent tool call trace.

## Memory Development Rules

After Phase 14, memory changes must preserve these constraints:

- Memory data must always be scoped by `workspace_id`.
- `conversation_sessions`, `conversation_messages`, `agent_memories`, and `memory_operation_logs` are the canonical tables.
- Message roles are limited to `system`, `user`, `assistant`, and `tool`.
- Memory types are limited to `short_term`, `long_term`, `task_memory`, and `retrieval_memory`.
- Current memory retrieval is PostgreSQL text search only. Do not document vector memory or graph memory as completed.
- `BaseAgent` memory usage should go through `MemoryExecutionContext`, `load_memory()`, and `save_memory()`.
- Agentic RAG debug output must keep `session_id`, `recent_messages_count`, `retrieved_memories_count`, and `memory_trace`.
- New memory APIs must update zh/en `API_REFERENCE.md`, `PROJECT_STATUS.md`, and `scripts/verify_docs_runtime.py`.
- Do not add autonomous memory planning, personality memory, Browser Agent, Playwright, or OpenClaw as part of this layer.

Recommended tests:

- Session workspace isolation.
- Message append and role validation.
- Memory retrieval by workspace, agent, and text query.
- BaseAgent memory context and save hooks.
- Agentic RAG memory trace.
- Memory API CRUD flow.

## Multi-Agent Development Rules

After Phase 15, Multi-Agent changes must preserve these constraints:

- `agent_runs`, `agent_messages`, and `agent_handoffs` are the canonical Multi-Agent tables.
- All Multi-Agent records must be scoped by `workspace_id`.
- `AgentRegistry` is the canonical in-code registry for available agents.
- Current registered agents are `content_planner`, `rag_agent`, `content_agent`, `review_agent`, `runtime_agent`, and `tool_agent`.
- The only current chain is `content_planning`: `content_planner -> rag_agent -> content_agent -> review_agent`.
- `ToolAgent` must use the existing `ToolRegistry`; do not bypass tool logging or workspace isolation.
- Memory integration should pass `session_id` and reuse the Phase 14 Memory Foundation.
- New Multi-Agent APIs must update zh/en `API_REFERENCE.md`, `PROJECT_STATUS.md`, and `scripts/verify_docs_runtime.py`.
- Do not add Browser Agent, OpenClaw, Playwright, Selenium, external platform APIs, autonomous planning, or ReAct as part of this foundation.

Recommended tests:

- AgentRegistry registration and disable behavior.
- Run create/list/get by workspace.
- Handoff creation and message trace.
- Fixed chain execution.
- Multi-Agent API flow with `X-Workspace-Id`.

## Planning Development Rules

After Phase 16, Planning changes must preserve these constraints:

- `plans`, `plan_steps`, and `plan_reviews` are the canonical Planning tables.
- All Planning records must be scoped by `workspace_id`.
- `SimplePlannerAgent` is rule-based and bounded. Do not document autonomous AGI planning, tree-of-thought, recursive planning, infinite Agent loops, or ReAct as completed.
- Plan steps may target either `agent_name` or `tool_name`, never both.
- Agent steps must go through `AgentRegistry` / `MultiAgentService`.
- Tool steps must go through `ToolRegistry` so tool isolation and logs remain intact.
- Each step must record status, duration, output, and error when applicable.
- Planning APIs must preserve `X-Workspace-Id` requirements.
- Planning memory integration is limited to `session_id` and `memory_trace`; do not document graph memory or advanced long-term planning as completed.
- New Planning APIs must update zh/en `API_REFERENCE.md`, `PROJECT_STATUS.md`, and `scripts/verify_docs_runtime.py`.
- Do not connect Browser Agent, OpenClaw, Playwright, Selenium, external platform APIs, autonomous planner, or ReAct inside this foundation.

Recommended tests:

- SimplePlannerAgent output stability.
- Plan create/list/get workspace isolation.
- Plan execution and review creation.
- Step retry and skip behavior.
- Planning API flow.

## Browser Adapter Development Rules

Phase 17 Browser Adapter rules:

- Keep `BROWSER_PROVIDER=mock` as the default.
- `MockBrowserProvider` must not start a browser.
- `PlaywrightBrowserProvider` must remain a placeholder until a future phase explicitly enables real browser execution.
- Browser data must stay workspace-scoped through `browser_sessions`, `browser_actions`, and `browser_action_logs`.
- Every browser action must record `duration_ms`, `success`/`error`, provider, action type, and logs.
- `browser_tool` must use `BrowserService` and `ToolRegistry` so tool call logs remain intact.
- Planning may target `tool_name=browser_tool`, but do not implement autonomous browser planning, ReAct, browser loops, OCR, visual AI, OpenClaw, Playwright execution, Selenium, or platform automation in this foundation.

Recommended tests:

- Provider placeholder behavior.
- BrowserService session/action/log persistence.
- Browser API workspace isolation.
- `browser_tool` execution and tool_call_logs.
- Planning step execution with `tool_name=browser_tool`.

## Playwright Local Provider Development Rules

After Phase 18, local Chromium execution is allowed only inside `PlaywrightLocalProvider` and must follow these rules:

- Keep `BROWSER_PROVIDER=mock` as the default.
- Enable real execution only through `BROWSER_PROVIDER=playwright_local`.
- Install Playwright Chromium only, not the full browser matrix.
- Allow only `example.com`, local test pages, and static `file://` pages.
- `screenshot` must write to `screenshots/{workspace_id}/{session_id}/{filename}.png` and store the path in `browser_actions.screenshot_path`.
- Every action must record `selector`, `target_url`, `page_title`, `duration_ms`, success/error, and `browser_action_logs`.
- Do not implement TikTok / YouTube / X, login automation, cookie injection, fingerprint bypass, proxy pools, captcha automation, OCR, visual AI, autonomous browser planning, Browser Worker, or real platform automation.

Phase 18 fixed verification:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Remote Browser Worker Development Rules

After Phase 19, Remote Browser Worker changes must follow these rules:

- Keep `BROWSER_PROVIDER=mock` as the default.
- `BROWSER_PROVIDER=remote` means protocol dispatch only; it does not mean a real external worker is deployed.
- Worker management APIs must remain scoped by `X-Workspace-Id`.
- `BrowserWorkerClient` must return structured success/error results and must not leak raw HTTP exceptions into business logic.
- `RemoteBrowserProvider` must be used through `BrowserService`; do not bypass `browser_actions` or `browser_action_logs`.
- Remote actions must record `worker_id`, `worker_name`, `remote_session_id`, `remote_action_id`, latency, success/error.
- Do not implement TikTok / YouTube / X, account login, auto-publishing, cookie injection, fingerprint bypass, proxy pools, captcha automation, or autonomous browser agents in this phase.

Phase 19 fixed verification:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```
## Phase 21 Development Rules

When changing Browser Worker Reliability, keep the scope bounded:

- Only change worker health, capacity, selection, session cleanup, action retry, and screenshot cleanup.
- Do not change Scheduler core logic.
- Do not change TaskExecutor core logic.
- Do not change Workspace Isolation core logic.
- Do not change Hybrid Search main logic.
- Do not add TikTok / YouTube / X automation, login, cookies, proxies, fingerprinting, captcha handling, OCR, visual AI, or autonomous browser planning.

Required verification flow:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

When adding or changing Browser Worker APIs, update:

- `docs/PROJECT_OVERVIEW.md`
- `docs/CURRENT_RUNTIME.md`
- `docs/zh/API_REFERENCE.md`
- `docs/en/API_REFERENCE.md`
- `scripts/verify_docs_runtime.py`

## Phase 22 Development Rules

When changing Persistent Browser Profile Foundation, keep the scope bounded:

- `browser_profiles` is the canonical table for profile lifecycle metadata.

## Phase 23 Development Rules

When changing Browser Profile Health & Recovery, keep code, migrations, tests, and docs in sync:

- Update profile health fields through `BrowserProfileHealthService`, `BrowserProfileBackupService`, or `BrowserProfileCleanupService`; avoid scattered lifecycle writes.
- `browser_profile_usage_logs` is the audit source for lock/release, session_start/session_close, backup/restore, recovery, and cleanup.
- Profile path validation must stay under `BROWSER_PROFILE_ROOT`; backup path validation must stay under `BROWSER_PROFILE_BACKUP_ROOT`.
- Cleanup APIs default to dry-run; new cleanup logic must support preview before deletion.
- Stale lock recovery can only release profiles in the current workspace.
- Every change must run `python -m pytest`, `docker compose up --build -d`, and `python scripts/verify_docs_runtime.py`.

Do not add account login, cookie injection, proxy pools, fingerprint bypass, captcha handling, real platform automation, or autonomous browser planning in Phase 23 scope.
- All profile operations must be scoped by `workspace_id`.
- A profile can be used by only one active session at a time through `locked_by_session_id`.
- `lock_profile` and `release_profile` must write browser logs when a session context is available.
- `POST /api/v1/browser/sessions` may use a profile only when `profile_id` and `use_persistent_profile=true` are explicitly provided.
- Worker runtime must use `launch_persistent_context` only for profile-backed sessions.
- Profile files must stay under `worker/profiles/{workspace_id}/{profile_id}`.
- Closing a profile-backed session must release the lock and update `last_used_at`.
- Do not add login automation, cookie injection, fingerprint bypass, proxy pools, captcha handling, social platform automation, or autonomous browser planning.

Required verification flow:

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

## Phase 29 Development Notes

When changing Worker Client runtime behavior, update these together: `worker_client/runtime_manager.py`, `worker_client/status.py`, `worker_client/logging.py`, `worker_client/runtime.py`, `worker_client/local_api_client.py`, packaging scripts, and docs. Run `python -m pytest`, `docker compose up --build -d`, and `python scripts/verify_docs_runtime.py`.

Do not log `worker_secret`. Do not commit `worker_client/runtime_state/status.json`, `worker_client/logs/worker.log`, `worker_client/worker_config.yaml`, or `worker_client/worker_state.json`.

Phase 29 remains Worker Console Foundation only: no GUI, no Electron/Tauri/PySide, no system tray, and no exe/dmg packaging.

## Phase 30 Worker Console Development Guide

When changing `worker_console`, run `npm install` when dependencies change, then `npm run build`. Keep `worker_console/src/api/localWorkerClient.ts`, docs, and `scripts/verify_docs_runtime.py` synchronized. Do not add Electron, Tauri, PySide, system tray, auto update, exe / dmg packaging, or platform automation in Phase 30.
## Phase 31: Worker Console Desktop Development Rules

The desktop shell lives in `worker_console_desktop` and uses Tauri + React + Vite + TypeScript + Tailwind. New desktop features must keep the Local API contract stable and should reuse `worker_console_desktop/src/api/localWorkerClient.ts`.

Required verification flow:

```bash
cd worker_console_desktop
npm install
npm run build
cd ..
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Do not add formal installers, exe / dmg packaging, system tray, autostart, auto update, or real platform automation in this phase. These capabilities may be documented only as planned roadmap items.
