# Phase 72V Client Unified Current Work Panel

## Scope

Phase 72V continues the Codex-like customer-machine UI simplification by collapsing the first-screen work area into one current-work panel. The operator should see one primary thing to handle, with supporting counts and a folded secondary-action drawer, instead of separate current-inbox and delivery-audit main cards.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` add `SimpleCurrentWorkItem`, `simpleCurrentWorkItems`, `simpleCurrentWorkItem`, `simpleSecondaryWorkItems`, `simpleCurrentWorkTitle`, `simpleCurrentWorkMoreLabel`, `simpleCurrentWorkOpenPanelId`, and `simpleCurrentWorkIsDelivery`.
- The unified work model merges the current inbox item, delivery readiness, and current creation review into one priority-ranked queue using the existing `simpleReviewStatePriority`.
- The first-screen UI renders `simple-current-work-panel` under `Phase 72V Client Unified Current Work Panel`.
- The panel keeps the primary delivery operator-queue action when delivery is the current work item, otherwise the primary action opens the guarded destination through `openClientDetailPanel(simpleCurrentWorkOpenPanelId)`.
- `simple-current-work-more` and `simple-current-work-more-actions` preserve secondary current-work navigation plus runbook-evidence and readiness-refresh actions.
- The legacy `simple-action-inbox` and `simple-delivery-audit-card` remain in the DOM for continuity and contracts, but `.codex-simple-client .simple-action-inbox` and `.codex-simple-client .simple-delivery-audit-card` are hidden from the default first screen.
- `simple-current-work-panel` is included in the mobile responsive grid list so it collapses to one column on narrow screens.

## Boundaries

This is frontend information architecture only. It does not change delivery-audit APIs, change readiness scoring, create or clear blockers automatically, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the first screen shows one `simple-current-work-panel`, hides the legacy `simple-action-inbox` and `simple-delivery-audit-card`, keeps secondary actions folded, has no horizontal overflow, and preserves the guarded open/detail behavior.
