# Phase 73F Client Codex Quiet Workbench

## Scope

Phase 73F continues the customer-machine UI simplification after Phase 73E. The operator screen should feel Codex-like: one quiet status line, one goal composer, one current-work card, and small entrances for lower-frequency panels. The full closed-loop capability remains available, but the default page no longer presents server pressure, project progress, operation details, and secondary panels as competing first-screen cards.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` now label the status row as `Phase 73F Client Quiet Status Rail`.
- The same frontends label `client-operation-desk-drawer` as `Phase 73F Client Quiet Operation Detail Entry`, `simple-secondary-panels-drawer` as `Phase 73F Client Quiet Secondary Panels`, and `maintenance-drawer` as `Phase 73F Client Approval Output Focus`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` convert `.simple-command-status-strip` under `.codex-simple-client` from two large status cards into a compact flex rail.
- The same styles make `.client-operation-desk-drawer` and `.simple-secondary-panels-drawer` quiet right-aligned entries while closed, then restore full-width content when opened.
- `.maintenance-drawer` remains visible as the approval/output entry, with slightly tighter spacing so active approvals stay close to the current-work panel.
- `.chat-panel.codex-simple-client` keeps the previous hidden title/header behavior and removes the remaining card shadow from the main workbench shell.

## Boundaries

This is frontend information architecture only. It does not remove server pressure visibility, remove project progress visibility, remove operation details, remove secondary panels, remove `maintenance-drawer`, remove approval or output review surfaces, change conversation APIs, change local worker APIs, change commercial operation APIs, deploy a real OpenClaw provider, store platform credentials, configure secrets from the UI, approve records without an operator click, reject records without an operator click, retry failed work automatically, recover failed work automatically, select output candidates without an operator click, create output candidates automatically, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the default workbench shows a compact status rail, the goal composer, the current-work card, quiet entries for more panels and operation details, the approval/output drawer, and no horizontal overflow.
