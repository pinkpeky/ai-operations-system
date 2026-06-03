# Phase 68X Customer Frontend Production Alignment

Phase 68X connects the formally registered production browser worker from Phase 68W to the customer-machine frontends.

## Objective

Operators should not have to infer production readiness from scripts or logs. `worker_console` and `worker_console_desktop` now show whether the visible customer machine is aligned with the same server workspace that the commercial project loop uses.

## Implemented

- `worker_console` and `worker_console_desktop` default to `VITE_AI_SERVER_API=http://127.0.0.1:8000`, `VITE_WORKSPACE_ID=production-workspace`, and `VITE_USER_ID=production-operator`.
- `admin_dashboard` uses the same production workspace fallback and `.env.example` values.
- Browser Runtime clients normalize `VITE_AI_SERVER_API` so both `http://127.0.0.1:8000` and `http://127.0.0.1:8000/api/v1` resolve to the real API prefix.
- The customer-machine home screen includes a `Phase 68X Production Runtime Alignment` strip showing production workspace, registered worker, heartbeat, and local metric poll state.
- The operation project workbench includes a `client-production-runtime-panel` before server pressure and project process, so operators see workspace alignment beside production work.
- The panel compares the server workspace from conversation settings with the local worker workspace from `/local/status`.
- The local worker CORS allowlist includes the production and development customer-console origins on ports `5173`, `5174`, `5180`, and `5181`, so the browser UI can read `/local/status` directly during server-host and customer-machine operation.

## Operator Contract

Expected production values:

```env
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
VITE_AI_SERVER_API=http://127.0.0.1:8000
VITE_WORKSPACE_ID=production-workspace
VITE_USER_ID=production-operator
```

For the current server-host production worker, `/local/status` should report:

```text
workspace_id=production-workspace
registered=true
runtime_running=true
heartbeat_running=true
worker_base_url=http://host.docker.internal:9100
```

If the UI shows a mismatch, the worker must be re-registered or the frontend workspace setting must be corrected before operators use workflow selection, output selection, publish handoff, or metric pullback.

## Boundaries

Phase 68X is visibility and configuration alignment only. It does not log in to social platforms, publish content, collect account credentials, bypass verification, scrape analytics, mutate ComfyUI workflows, submit ComfyUI prompts, run OpenClaw/Playwright account actions from the server, install services, or rebuild release packages.

## Verification

- Static UX test: `tests/test_worker_console_client_ux.py::test_worker_consoles_expose_phase_68x_production_runtime_alignment`
- Local worker CORS test: `tests/test_worker_console_client_ux.py::test_phase_68x_local_worker_cors_allows_production_frontend_ports`
- Admin config test: `tests/test_admin_dashboard_config.py`
- Frontend typecheck/build for `worker_console` and `worker_console_desktop`
- Runtime smoke: local worker `/local/status` plus API remote browser session selection under `production-workspace`
