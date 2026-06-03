# Phase 69L Production Closed-Loop Primary Step Staleness

Date: 2026-06-01

## Goal

Phase 69L adds a portable stale-action signal for the current production closed-loop primary step.

Phase 69K made the primary step visible in the server dashboard. Phase 69L adds `primary_step_staleness` to the same audit-list response so the server dashboard, customer-machine console, and future Agent logic can distinguish a fresh waiting step from one that should be escalated.

## Implemented Scope

- `CommercialOperationProductionClosedLoopActionAuditListResponse.primary_step_staleness`.
- `production_closed_loop_action_audit_primary_step_staleness` contract marker.
- `primary_step_staleness_contract` metadata.
- `CommercialOperationService._production_closed_loop_action_primary_step_staleness`.
- `admin_dashboard` displays `productionClosedLoopPrimaryStepStaleness`.
- Server dashboard fields include `staleness_status`, `waiting_seconds`, `escalation_recommended`, and `escalation_reason`.

## Contract

`primary_step_staleness` always exists.

- When there is no current primary step, `status=none`.
- When a step has a known waiting timestamp below one hour, `status=fresh`.
- After one hour, `status=watch`.
- After four hours, `status=stale` and `escalation_recommended=true`.

The timestamp source is step-aware:

- `confirm` waits from operation creation.
- `bind` waits from action-audit `created_at`.
- `validate` waits from result-binding `bound_at`.
- `refresh` waits from record-validation `validated_at`.

## Boundary

Phase 69L is read-only state analysis.

It does not execute target endpoints, run OpenClaw, run Playwright, publish, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, create publish evidence, or force readiness complete.

## Verification

- Governance closed-loop API test verifies fresh and stale primary-step staleness states.
- Admin dashboard tests verify the server-side staleness fields.
- Documentation tests cover Phase 69L recovery markers.

## Next Step

The next production slice should let maintainers filter and prioritize operations by stale primary-step state across the project list.
