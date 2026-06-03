# Phase 72J Client Delivery Audit Focus

Phase 72J continues the Codex-like customer-machine UI simplification after the production audit summary work. The production audit and project workbench already expose detailed evidence, but an operator still needs a first-screen answer to one question: whether the current project can be delivered, and what single blocker path comes next.

## Implementation

- `worker_console` and `worker_console_desktop` now derive a compact `simpleDeliveryAuditLoaded`, `simpleDeliveryAuditBlockerCount`, `simpleDeliveryAuditExternalCount`, `simpleDeliveryAuditOperatorCount`, `simpleDeliveryAuditReady`, and `simpleDeliveryAuditPrimaryAction` from the existing production closed-loop acceptance summary, delivery audit next-action plan, and delivery audit operator queue.
- The first-screen surface adds `simple-delivery-audit-card` between `simple-action-inbox` and `simple-project-context-drawer`.
- The card uses `simpleDeliveryAuditTitle`, `simpleDeliveryAuditReady`, `simpleDeliveryAuditBlocked`, `simpleDeliveryAuditWaiting`, `simpleDeliveryAuditExternal`, `simpleDeliveryAuditOperator`, `simpleDeliveryAuditBlockers`, `simpleDeliveryAuditActions`, `simpleDeliveryAuditNext`, and `simpleDeliveryAuditRefresh`.
- The compact view reuses `productionClosedLoopDeliveryAuditNextActionPlan`, `productionClosedLoopDeliveryAuditOperatorQueue`, `productionClosedLoopAcceptanceSummary`, and `refreshProductionClosedLoopReadiness`; it does not create a second delivery-audit data path.
- The detail jump still opens the guarded `client-project-workbench`, where the full audit, runbook evidence, operator queue, and provider handoff remain available.

## Boundary

Phase 72J is frontend visibility and navigation only. It does not configure providers, deploy a real OpenClaw provider, mark mock providers ready, change env vars, store secrets, restart services, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, call readiness-refresh POST endpoints, or bypass approval.
