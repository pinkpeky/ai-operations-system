# Phase 72K Client Delivery Audit Quick Action

Phase 72K continues the customer-machine first-screen simplification after Phase 72J. Phase 72J made the delivery audit readable at a glance; Phase 72K makes that same card actionable without turning it into a full audit console.

## Implementation

- `worker_console` and `worker_console_desktop` now derive `simpleDeliveryAuditQueueItem` from `productionClosedLoopDeliveryAuditOperatorQueue.first_item` with owner-group fallback.
- The card derives `simpleDeliveryAuditRecordStatus`, `simpleDeliveryAuditRecordInProgress`, `simpleDeliveryAuditRecordDisabled`, and `simpleDeliveryAuditRecordLabel`.
- New copy keys are `simpleDeliveryAuditRecordAction`, `simpleDeliveryAuditRecordingAction`, and `simpleDeliveryAuditInProgress`.
- The `simple-delivery-audit-card` now includes a primary action button before refresh/detail.
- The button calls the existing `recordClientDeliveryAuditOperatorQueueInProgress(simpleDeliveryAuditQueueItem)` function, which records a `production_closed_loop_delivery_audit_operator_queue_record` status update only after an operator click.
- The existing refresh button and project-workbench detail jump remain available beside the quick action.

## Boundary

Phase 72K is operator-click queue record evidence only. It does not execute target endpoints, configure providers, deploy a real OpenClaw provider, mark mock providers ready, change env vars, store secrets, restart services, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, call readiness-refresh POST endpoints, or bypass approval.
