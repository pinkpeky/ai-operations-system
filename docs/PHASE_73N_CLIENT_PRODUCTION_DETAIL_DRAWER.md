# Phase 73N Client Production Detail Drawer

## Scope

Phase 73N continues the customer-machine Codex-like UI simplification after Phase 73M. It keeps the first screen focused on the current operating goal and current work, then folds lower-frequency production context into one `simple-production-details-drawer` in both `worker_console` and `worker_console_desktop`.

## Implementation

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` add `simpleProductionDetailCount` and `simpleProductionDetailOutputCount` so the folded entry can summarize approvals, materials, workflow selections, and output candidates without expanding every panel by default.
- Both customer-machine frontends add `simple-production-details-drawer` with aria label `Phase 73N Client Production Detail Drawer`.
- The existing `simple-secondary-panels-drawer` and `maintenance-drawer` remain available inside `simple-production-details-body`, preserving project context, delivery details, approvals, output preview, and selection controls.
- `openClientDetailPanel` now walks `detailsAncestor` through `target.closest("details")` so any deep-link target opens its parent detail drawers before scrolling.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` fold `simple-production-details-body` while the drawer is closed, restyle nested detail drawers for the compact body, and hide the closed `client-operation-desk-drawer` from the default first screen while keeping it available when a deep-link action opens it.

## Boundary

This is frontend information architecture only. It does not remove operation details, remove project context, remove approvals, remove output preview, remove material import, remove workflow selection, change local worker APIs, change conversation APIs, change upload APIs, start runtime automatically, start heartbeat automatically, refresh status automatically, approve records, reject records, acknowledge intervention records without an operator click, send reminders, retry failed work, recover failed work, select output candidates without an operator click, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, auto-refresh readiness, or bypass approval.

## Verification

- `tests/test_worker_console_client_ux.py::test_phase_73n_client_production_detail_drawer_contract`
- `tests/test_commercial_operations_docs.py::test_phase_73n_client_production_detail_drawer_is_documented`
