# Phase 72S Client Compact Shell

## Scope

Phase 72S continues the customer-machine UI simplification by reducing the outer console shell. The first screen should read as a customer task workspace, not as a developer Worker console. Runtime and heartbeat status remain visible, and diagnostics remain reachable, but low-frequency API and environment boundary details no longer sit above the operating workspace by default.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` mark the top shell with `client-shell-topbar` under aria label `Phase 72S Client Compact Shell`.
- The visible title is now a customer-facing workspace title through `client-shell-title` rather than the older Worker-console framing.
- Runtime and heartbeat badges remain visible inside `client-shell-diagnostics-drawer` under aria label `Phase 72S Client Shell Diagnostics Drawer`.
- The diagnostic body uses `client-shell-diagnostics-body` and is hidden until the drawer opens.
- `worker_console_desktop/src/main.tsx` moves the normal `connection-state`, `Desktop Runtime Foundation`, and server/client boundary panel into the diagnostics drawer while preserving the explicit API-unreachable alert when the local worker is not reachable.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` make the compact shell low-height on desktop and full-width on mobile.

## Boundaries

This is frontend information architecture only. It does not remove runtime status, remove heartbeat status, hide API-unreachable errors, change local worker APIs, start runtime automatically, start heartbeat automatically, refresh status automatically, change environment boundaries, configure providers, mark mock providers ready, change env vars, store secrets, restart services, approve records, call target endpoints, run OpenClaw actions, run Playwright, publish, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the first screen starts with the compact customer task workspace shell, runtime diagnostics are folded by default, opening the diagnostics drawer reveals folded details, and the page has no horizontal overflow.
