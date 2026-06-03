# Phase 72M Client Runbook Evidence Submission

Phase 72M continues the production closed-loop delivery audit path after Phase 72L. Phase 72L made runbook evidence pressure visible on the compact customer-machine card; Phase 72M adds the controlled evidence submission form in the project workbench so an operator can submit real review evidence instead of only recording a blocked status.

## Implementation

- `worker_console` and `worker_console_desktop` now define `ClientRunbookEvidenceStatus`, `ClientRunbookEvidenceDraft`, `initialClientRunbookEvidenceDraft`, `clientRunbookEvidenceDraft`, and `setClientRunbookEvidenceDraft`.
- The project workbench runbook section now includes `client-production-delivery-audit-runbook-evidence-form` with status, evidence summary, evidence link, operator notes, and operator confirmation fields.
- `submitClientDeliveryAuditBlockerRunbookEvidence` records the selected status through the existing `production_closed_loop_delivery_audit_blocker_runbook_evidence` contract.
- `submitted` and `resolved` require an explicit operator confirmation. They also require either an evidence summary or an evidence link; otherwise the UI returns `operator_confirmation_required_for_runbook_evidence` or `evidence_summary_or_link_required_for_runbook_evidence` before calling the API.
- After a successful submission, the client refreshes evidence records, evidence coverage, and runbook packages so the next action plan can reflect the new state.

## Boundary

Phase 72M is operator-supplied evidence submission only. It does not mark empty evidence as resolved, call readiness-refresh automatically, execute target endpoints, configure providers, deploy a real OpenClaw provider, mark mock providers ready, change env vars, store secrets, restart services, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.
