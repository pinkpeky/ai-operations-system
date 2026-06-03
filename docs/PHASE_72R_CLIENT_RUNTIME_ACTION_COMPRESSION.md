# Phase 72R Client Runtime Action Compression

## Scope

Phase 72R continues the customer-machine UI simplification by reducing default first-screen maintenance actions. The customer operator should see the current runtime state, the active operating mode, the command input, and the most important work decision first. Low-frequency runtime maintenance and secondary delivery-audit actions remain reachable, but they no longer compete with the main command workspace.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` wrap language switching, runtime start, heartbeat start, and status refresh controls in `client-runtime-controls-drawer` under aria label `Phase 72R Client Runtime Controls Drawer`.
- The runtime drawer summary keeps the connection state visible through `copy.connectionCard`, `copy.connected`, and `nextStep`; the actual buttons remain inside `client-runtime-summary-actions`.
- The delivery audit card keeps the primary operator action visible in `simple-delivery-audit-primary-row`.
- Secondary delivery-audit actions for runbook evidence, readiness refresh, and detail navigation move into `simple-delivery-audit-more` / `simple-delivery-audit-more-actions` under aria label `Phase 72R Client Delivery Audit Secondary Actions`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` add compact drawer styling for `client-runtime-controls-drawer`, `simple-delivery-audit-primary-row`, and `simple-delivery-audit-more` so the first viewport reads closer to a Codex-style command workspace.
- Closed drawer CSS explicitly hides `client-runtime-summary-actions`, `operator-page-tab-actions`, and `simple-delivery-audit-more-actions` while preserving them after expansion.

## Boundaries

This is frontend information architecture only. It does not remove language switching, remove runtime controls, start the runtime automatically, start heartbeat automatically, refresh status automatically, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that runtime controls are folded by default, delivery-audit secondary actions are folded by default, both drawers reveal their original controls when opened, and the page has no horizontal overflow.
