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

## Phase 32: System Tray Development Rules

Phase 32 allows System Tray, Minimize To Tray, and local runtime controls in Tauri, but still forbids:

- formal installer
- exe / dmg release
- real autostart registration
- auto-update
- arbitrary shell
- remote shell
- remote command execution

Tray menu actions must emit `tray-control` events to the frontend. The frontend then calls local HTTP APIs through `localWorkerClient.ts`. Do not add `std::process`, shell plugins, process plugins, or arbitrary command execution logic in Rust or TypeScript.

## Phase 33: Conversation Runtime Foundation

Status: completed.

Completed: `conversation_threads`, `conversation_events`, extended `conversation_messages.thread_id`, `ConversationService`, `run_conversation_turn`, Conversation APIs, Worker Console Chat Panel Foundation, Event Timeline, and polling event feed.

Events include `message_received`, `planning_started`, `plan_created`, `agent_started`, `tool_called`, `worker_action_started`, `worker_action_completed`, `assistant_response`, and `error`.

Boundary: this is Conversation Runtime Foundation only. It is not real WebSocket/SSE streaming, not real OpenClaw, not ComfyUI, and not TikTok / YouTube / X automation, login automation, cookie injection, proxy pool, fingerprint bypass, captcha automation, or real platform automation.

## Phase 34 Remote Browser Runtime Development Notes

Remote browser runtime development must keep the dispatch boundary clear:

- API orchestration belongs in `BrowserRuntimeSessionService`.
- Remote worker calls belong in `app/browser/providers/remote_provider.py` and `BrowserWorkerClient`.
- Customer-machine execution belongs in `worker_client/browser_runtime`.
- Do not add platform automation, stealth behavior, proxy logic, cookie injection, or captcha bypass.
- Do not bypass workspace isolation when querying `browser_runtime_sessions`.
- Do not store screenshot base64 in database metadata; store files under `storage/browser_screenshots` and keep metadata paths.

Required verification after changes:

```bash
python -m pytest
python scripts/verify_docs_runtime.py
```

For real customer-machine runtime checks, install Chromium with:

```bash
playwright install chromium
```

## Phase 35B Real Client Worker E2E Development Rule

When changing `scripts/validate_real_client_worker_e2e.py`, preserve these rules:

- Missing `expected_worker_name` returns `SKIPPED`, not PASS.
- Browser actions are executed only after the expected worker is online and available.
- JSON output must include checks, warnings, summary, and exit code.
- `BROWSER_PROVIDER=remote` mismatch is a WARNING only.
- Never fabricate a real customer-machine E2E result.

Required tests:

```bash
python -m pytest tests/test_real_client_worker_e2e_script.py tests/test_real_client_worker_e2e_docs.py
```

## Phase 35A Development Rule: Browser Runtime Observability

When adding or changing Browser Runtime actions, keep these artifacts synchronized:

- `BrowserRuntimeObservabilityService`
- `browser_runtime_events`
- `browser_runtime_snapshots`
- `browser_runtime_replays`
- `docs/zh/API_REFERENCE.md`
- `docs/en/API_REFERENCE.md`
- Worker Console Timeline / Snapshots / Replay metadata panels

Required verification flow:

```powershell
python -m pytest
cd worker_console
npm install
npm run build
cd ..\worker_console_desktop
npm install
npm run build
cd ..
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

Boundary: replay must remain metadata-only replay. Do not re-run browser actions, and do not add live stream, VNC/noVNC, DevTools remote control, or real platform automation.

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
## Phase 38 Development Rule

When adding a Conversation bridge route, extend `ConversationToolRouter` Routing Rules first, then implement the bounded bridge in `ConversationService`. Every execution must record `route_selected`, `tool_execution_started` / `tool_execution_completed` / `tool_execution_failed`, or the matching agent / planning event, and store full structured output in `result_metadata`. Do not describe this foundation as autonomous agent, WebSocket, SSE, or real platform publishing.

## Phase 39 Development Rules

When adding a Conversation route that can trigger Tool / Browser / OpenClaw / Task execution, update `ConversationRiskPolicy`. Medium/high risk routes must not bypass `ConversationApprovalService` or the Tool Execution Gate.

Fixed checks:

- Confirm whether the route creates `conversation_approvals` or is clearly low risk and auto-safe.
- Record approval events.
- Ensure rejected / cancelled / expired / executed approvals cannot execute.
- Update Admin Dashboard, Worker Console, and Worker Console Desktop pending approvals panel.
- Update docs and `scripts/verify_docs_runtime.py`.

Do not describe Phase 39 as a full permission system, real platform publishing, or autonomous agent.
## Phase 40 Development Rule: Playbooks

When adding a Playbook, update:

- `app/conversation/playbook_definitions.py`
- `ConversationPlaybookService`
- API_REFERENCE
- Admin Dashboard / Worker Console Playbook UI
- pytest
- `python scripts/verify_docs_runtime.py`

Playbook steps must not bypass `ConversationRiskPolicy` or `ConversationApprovalService`. New high-risk steps may create approvals only; they must not execute directly.

## Phase 41 Development Rule

When adding Conversation / Playbook / Tool outputs, prefer `OutputArtifactService` and `output_artifacts`. Do not store oversized raw payloads in `content`. File artifacts should keep paths and metadata; text artifacts may store bounded content. Every phase must keep Output Library API docs, frontend pages, pytest, frontend builds, Docker smoke, and docs verifier synchronized.
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
## Phase 46 Development Notes

Workflow Graph Runtime development centers on `WorkflowExecutionPlanner`, `SafeConditionEvaluator`, `WorkflowGraphService`, and `WorkflowStateService`. Tests should cover graph validation, Conditional Execution, Retry/Fallback Path planning, Replay Foundation metadata, `current_node_key`, `planned_next_nodes`, `skipped_nodes`, `producing_node_key`, and `graph_lineage`. Do not use Python eval for conditions; do not build a visual DAG builder or distributed orchestration engine.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47: Development Notes

New development entrypoints: `app/workflow/template_definitions.py` defines built-in templates, `app/workflow/template_registry.py` implements `WorkflowTemplateRegistryService` and `WorkflowTemplateCompatibilityService`, `app/schemas/workflow_template.py` defines API schemas, and `app/api/routes/workflow_templates.py` exposes `/api/v1/workflow-templates` and `/api/v1/workflow-template-runs`. All three frontends include `workflowTemplateClient.ts`.

Development boundaries: versions are immutable, `template_key` is workspace-unique, validate_template must reuse planner validation, and template runs must not bypass approval or risk gates. This is not a visual DAG builder and does not connect ComfyUI.
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
