# Phase 72L Client Runbook Evidence Quick Path

Phase 72L continues the Codex-like customer-machine first screen after Phase 72K. The previous card could show delivery blockers and record operator ownership; Phase 72L adds the missing runbook evidence pressure to the same card without expanding it into a full audit dashboard.

## Implementation

- `worker_console` and `worker_console_desktop` now add `simpleDeliveryAuditEvidence`, `simpleDeliveryAuditRecordEvidence`, and `simpleDeliveryAuditRecordingEvidence`.
- The compact `simple-delivery-audit-card` derives `simpleDeliveryAuditRunbookPackage`, `simpleDeliveryAuditRunbookMissingCount`, `simpleDeliveryAuditRunbookBlockedCount`, `simpleDeliveryAuditRunbookEvidenceCount`, `simpleDeliveryAuditRunbookCoverageStatus`, `simpleDeliveryAuditEvidenceDisabled`, and `simpleDeliveryAuditEvidenceLabel`.
- The card shows a third compact stat for runbook evidence pressure beside external and internal action counts.
- The card adds a small evidence button before refresh/detail. It calls `recordClientDeliveryAuditBlockerRunbookEvidence(simpleDeliveryAuditRunbookPackage)` only after an operator click.
- The write path remains the existing `production_closed_loop_delivery_audit_blocker_runbook_evidence` contract and then refreshes evidence records, coverage, and runbook packages.

## Boundary

Phase 72L is an operator-click evidence-status shortcut only. The current implementation records the existing runbook evidence status path; it does not claim the runbook is solved without operator evidence. It does not execute target endpoints, configure providers, deploy a real OpenClaw provider, mark mock providers ready, change env vars, store secrets, restart services, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, call readiness-refresh POST endpoints, or bypass approval.
