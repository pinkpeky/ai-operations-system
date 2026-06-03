# Phase 71N Production Closed-Loop Audit Next Action Plan

Phase 71N turns the read-only production closed-loop delivery audit blockers into a deduplicated operator action plan.

## Added Contract

- `scripts/check_production_closed_loop.py`
- Audit contract name: `production_closed_loop_delivery_audit`
- Report fields: `next_actions` and `next_action_count`
- Action fields: `action_key`, `title`, `owner`, `priority`, `source_blockers`, `target`, `required_endpoint`, `verification_commands`, and `external_dependency_required`
- Text output marker: `next_action`

The action plan maps production config, OpenClaw smoke, worker health, API health, acceptance gates, operation blockers, runbook evidence coverage, and runbook readiness refresh blockers into owner-routed actions. Examples include `configure_real_openclaw_provider`, `resolve_runbook_evidence_coverage`, `refresh_runbook_evidence_readiness`, `clear_operation_project_blockers`, and `clear_acceptance_gate`.

## Operational Meaning

The audit still fails when a blocker exists. Phase 71N does not weaken the gate. It adds an actionable closure plan so an operator can move from `blocking_reasons` to the exact owner, target, endpoint, and verification command needed to clear each blocker.

## Boundaries

Phase 71N is read-only audit planning. It does not configure OpenClaw, change environment variables, store or print secrets, execute target endpoints, run OpenClaw, run Playwright, publish, click final submit, submit ComfyUI prompts, approve records, mark mock providers ready, call the Phase 71L POST endpoint, or bypass approval.

## Verification

- `tests/test_production_closed_loop_audit.py` verifies the pass path has no next actions, blocked audits produce owner-routed next actions, and resolved runbook evidence with unrefreshed readiness produces `refresh_runbook_evidence_readiness`.
- `tests/test_commercial_operations_docs.py` verifies this document plus `docs/COMMERCIAL_OPERATIONS_FOUNDATION.md`, `docs/CURRENT_RUNTIME.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/PROJECT_STATUS.md`, and `docs/PHASE_INDEX.md`.
