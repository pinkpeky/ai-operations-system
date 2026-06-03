# Phase 72T Client Delivery Next Action Focus

## Scope

Phase 72T continues the customer-machine UI simplification by making the first-screen delivery card speak in operator terms. Instead of leading with audit wording, the card now leads with the current blocker state and the recommended next action while preserving the underlying delivery-audit data and controls.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` add `simpleDeliveryFocusTitle`, `simpleDeliveryFocusHeadline`, `simpleDeliveryFocusDetail`, and `simpleDeliveryFocusNextLabel`.
- The focus fields reuse existing delivery evidence: `simpleDeliveryAuditBlockerCount`, `simpleDeliveryAuditActionCount`, `simpleDeliveryAuditExternalCount`, `simpleDeliveryAuditOperatorCount`, `simpleDeliveryAuditRunbookEvidenceCount`, `clientObjectiveCompletionNextFocus`, `productionClosedLoopDeliveryAuditNextActionPlan`, and `productionClosedLoopDeliveryAuditOperatorQueue`.
- The first-screen delivery card keeps `simple-delivery-audit-card`, but its aria label now includes `Phase 72T Client Delivery Next Action Focus`.
- The card uses `simple-delivery-next-action-focus` and `simple-delivery-focus-detail` so the default view reads as current blockers plus recommended action.
- The existing primary operator-queue action, runbook evidence action, readiness refresh, and detail navigation remain in place.

## Boundaries

This is frontend information architecture only. It does not change delivery-audit APIs, change readiness scoring, create or clear blockers automatically, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the first-screen delivery card shows a current blocker or ready/waiting title, a blocker/action headline, a human-readable detail line, and the recommended action while secondary actions remain folded.
