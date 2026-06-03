# Phase 72N Client Runbook Readiness Refresh Gate

Phase 72N continues the runbook evidence path after Phase 72M. Phase 72M lets an operator submit real runbook evidence; Phase 72N makes the readiness refresh button reflect the same strict backend gate instead of letting the operator click into an avoidable API error.

## Implementation

- `worker_console` and `worker_console_desktop` now derive `clientDeliveryAuditBlockerRunbookPackageCount`, `clientDeliveryAuditBlockerRunbookResolvedCount`, `clientDeliveryAuditBlockerRunbookMissingEvidenceCount`, `clientDeliveryAuditBlockerRunbookBlockedCount`, `clientDeliveryAuditBlockerRunbookNeedsFollowUpCount`, `clientDeliveryAuditBlockerRunbookDismissedCount`, and `clientDeliveryAuditBlockerRunbookSubmittedCount` from evidence coverage.
- The clients derive `clientDeliveryAuditBlockerRunbookRefreshReady`, `clientDeliveryAuditBlockerRunbookRefreshRequired`, `clientDeliveryAuditBlockerRunbookRefreshGateReason`, `clientDeliveryAuditBlockerRunbookRefreshDisabled`, and `clientDeliveryAuditBlockerRunbookRefreshLabel`.
- `refreshClientDeliveryAuditBlockerRunbookEvidenceReadiness` now exits locally with `runbook_evidence_readiness_refresh_blocked:{reason}` until coverage is resolved or no runbook evidence is required.
- The runbook section shows `client-production-delivery-audit-runbook-refresh-gate` so the operator can see why refresh is disabled.
- The only backend write path remains `production_closed_loop_delivery_audit_blocker_runbook_evidence_readiness_refresh`, and it is still reached only after explicit operator click.

## Boundary

Phase 72N is a client-side readiness-refresh gate and operator explanation layer. It does not mark evidence resolved, submit evidence, call readiness-refresh automatically, execute target endpoints, configure providers, deploy a real OpenClaw provider, mark mock providers ready, change env vars, store secrets, restart services, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.
