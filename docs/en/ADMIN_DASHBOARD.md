# Admin Dashboard Foundation

Phase 36 is completed. `admin_dashboard` is the Server Admin Dashboard Foundation for inspecting AI Server, Browser Workers, Browser Runtime, Timeline, Snapshots, Replay metadata, Tasks, Conversation Runtime, OpenClaw mock, Audit Logs, and RAG / Documents state from a browser.

## Current Scope

- Completed: read-only monitoring foundation.
- Completed: standalone Vite + React + TypeScript + Tailwind frontend project.
- Completed: calls existing AI Server APIs with `X-Workspace-Id` and `X-User-Id` headers.
- Completed: Settings page stores `aiServerUrl`, `workspaceId`, and `userId` in localStorage.
- Experimental: Browser Runtime page can create metadata-only replay for debugging. It does not re-execute browser actions.
- Planned: production-grade operations backend, login UI, permission UI, publishing business flow, and complex editing workflows.

Current explicit boundaries: no login UI, no permission UI, no publishing business flow, no real social platform control, no production-grade operations backend.

## Project Structure

```text
admin_dashboard/
├── package.json
├── .env.example
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── src/main.tsx
├── src/styles.css
└── src/api/client.ts
```

## Runtime Configuration

```env
VITE_AI_SERVER_API=http://localhost:8000
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

Default AI Server:

```text
http://localhost:8000
```

Development:

```powershell
cd admin_dashboard
npm install
npm run dev
```

Static build:

```powershell
cd admin_dashboard
npm run build
```

## Pages

| Page | Status | Description |
| --- | --- | --- |
| Overview | Completed | API health, worker online/offline, Browser Runtime session count, Task summary, Conversation count, OpenClaw mock status, recent errors |
| Workers | Completed | Browser worker inventory, available workers, health summary; read-only, no rotate secret / revoke actions |
| Browser Runtime | Completed | Sessions, events timeline, snapshots, metadata-only replay |
| Conversations | Completed | Threads, messages, events; explicitly marked as foundation |
| Tasks | Completed | Task list, events, logs, payload summary; read-only, no retry/cancel actions |
| OpenClaw | Completed | Health, capabilities, mock status; no real OpenClaw |
| Audit Logs | Completed | Browser security audit logs with basic event_type / success / target_type filters |
| RAG / Documents | Completed | Embedding health, documents, collections, simple hybrid search form |
| Settings | Completed | AI Server URL, Workspace ID, User ID, refresh interval |

## API Client

`admin_dashboard/src/api/client.ts` exports:

- `workersApi`
- `browserRuntimeApi`
- `conversationsApi`
- `tasksApi`
- `openclawApi`
- `auditApi`
- `ragApi`

Every request includes:

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

## Auto Refresh

- Overview: every 10 seconds.
- Workers: every 10 seconds.
- Browser Runtime: every 10 seconds.
- Logs / Events / Snapshots: manual refresh or detail selection.
- API failures are rendered as unavailable/error states and should not crash the entire page.

## Boundaries

Admin Dashboard Foundation does not implement:

- no login UI
- no permission UI
- no publishing business flow
- no real social platform control
- no production-grade operations backend
- no TikTok / YouTube / X automation
- no auto login
- no cookie injection
- no proxy pool
- no fingerprint bypass
- no captcha automation

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
## Phase 38: Conversation Tool Bridge Frontend Integration

The Admin Dashboard Conversation page now displays route selected, selected tool, tool status, result summary, event timeline, and full metadata panel. Events include `route_selected`, `tool_execution_started`, `tool_execution_completed`, `agent_execution_started`, `planning_execution_started`, `bridge_fallback`, and `bridge_error`. It remains polling only, not WebSocket, not SSE, not a full ChatGPT UI, and not autonomous agent.

## Phase 39: Conversation Approval Panel

The Admin Dashboard Conversations page now includes the Approval Flow Foundation:

- pending approvals panel
- proposed action preview
- proposed payload JSON
- risk badge
- approve / reject / cancel buttons
- execute approved action button
- approval events timeline

Related APIs: `GET /api/v1/conversations/{thread_id}/approvals`, `POST /api/v1/conversation-approvals/{approval_id}/approve`, `/reject`, `/cancel`, and `/execute`. This is an execution review gate, not a full permission system. It does not implement real platform publishing, real OpenClaw, login, captcha, proxy, fingerprint bypass, or social automation.
## Phase 40: Playbooks Page and Conversation Playbook UI

Admin Dashboard adds a `Playbooks` page and extends the `Conversations` page with:

- Playbook selector
- Playbook list / description
- Run playbook button
- Playbook Runs
- Step Timeline
- Approval-aware execution controls

## Phase 41: Output Library

Admin Dashboard now includes an Output Library page:
- artifact list
- artifact detail
- artifact type badge
- source type
- related thread
- related Playbook Run
- preview content
- Export markdown / json / txt
- filter by `artifact_type` / `source_type`

Conversation pages show generated artifacts, and assistant messages expose Save as Artifact. Artifacts generated after Playbook Run completion appear in Output Library.

Boundary: Output Library is not a full DAM, has no S3 / MinIO integration, and is not production publishing asset management.

Built-ins visible in the UI: `browser_search_summary`, `browser_screenshot_report`, `rag_answer`, `content_generation`, `trend_research_draft`, and `openclaw_mock_device_check`.

This is a basic run/monitoring entrypoint. It is not a visual workflow editor, does not publish to real social platforms, and does not bypass the Phase 39 approval gate.
## Phase 42: Task Orchestration & Background Execution

This phase adds the Task Orchestration foundation: `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, and `TaskRetryPolicy`. Conversation / Playbook runs can use `execution_mode=background`, then `/api/v1/task-runs` exposes queued, running, waiting_approval, retrying, completed, failed, cancelled, expired state plus timeline events. `scheduled_at` supports scheduled runs; retry uses exponential backoff; approval resume continues to enforce the Phase 39 Approval Gate; Output Library artifacts are linked by `task_run_id`.

Boundary: this is an in-process queue, not Celery / RabbitMQ / Kubernetes scheduler / production HA distributed queue. It does not implement real publishing, real OpenClaw, ComfyUI, CAPTCHA handling, proxies, or fingerprint bypass.
