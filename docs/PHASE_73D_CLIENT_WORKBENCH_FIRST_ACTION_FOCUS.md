# Phase 73D Client Workbench First Action Focus

## Scope

Phase 73D continues the Codex-like customer-machine simplification by making the main workbench open directly on actionable content. The default screen no longer spends vertical space on a duplicate panel title or explanatory operator-mode header; it shows the compact status strip, goal input, and current-work action first. Full operation details remain available, but they are visually lower priority.

## Implemented

- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` hide the duplicated `panel-title` inside `.chat-panel.codex-simple-client`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` hide `.simple-operator-header` inside `.codex-simple-client`, while keeping the DOM and accessible workbench labels intact.
- The existing `simple-command-status-strip` remains the first visible workbench context surface.
- The existing `simple-goal-box` remains the primary input and run action surface.
- The existing `client-operation-desk-drawer` is retained but moved to `order: 6`, after the first-action surfaces, so full delivery/execution/publish details do not compete with the default operating path.

## Boundaries

This is frontend information architecture only. It does not remove the workbench, remove the operation detail drawer, remove operation details, remove status cards, remove the goal input, remove current-work actions, change conversation APIs, change local worker APIs, change upload APIs, change current-work priority, change delivery-audit APIs, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, collect credentials, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the default workbench surface starts with the compact status strip and goal input instead of duplicated title/header copy, the operation detail drawer remains reachable lower in the workbench, and the page has no horizontal overflow.
