# Phase 72Y Client Current Work Single Action

## Scope

Phase 72Y continues the customer-machine UI simplification by making the current-work panel expose one default primary action at a time. Delivery work shows the operator-queue record action first; non-delivery work shows the detail-open action first. Secondary detail navigation remains available inside the current-work drawer.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` keep `simple-current-work-panel` as the first-screen current-work surface.
- The delivery branch now renders `recordClientDeliveryAuditOperatorQueueInProgress(simpleDeliveryAuditQueueItem)` as the only default visible primary action.
- The non-delivery branch renders `openClientDetailPanel(simpleCurrentWorkOpenPanelId)` as the only default visible primary action.
- `simple-current-work-more` is labelled `Phase 72Y Client Current Work Single Action / Phase 72V Client Unified Current Work Secondary Actions`.
- The delivery detail-open button is preserved inside `simple-current-work-more-actions` so operators can still inspect the relevant blocker or delivery subsection after explicitly expanding more actions.
- `simpleSecondaryWorkItems`, runbook evidence recording, and production-readiness refresh remain folded inside the same drawer.

## Boundaries

This is frontend information architecture only. It does not change delivery-audit APIs, change readiness scoring, remove detail navigation, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, change conversation APIs, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the current-work panel shows one visible primary action by default, keeps secondary current-work actions folded, reveals detail navigation after opening the drawer, and has no horizontal overflow.
