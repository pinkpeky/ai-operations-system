# Phase 69M Operation List Closed-Loop Staleness Priority

Date: 2026-06-01

## Goal

Phase 69M lifts the production closed-loop primary-step staleness signal into the operation list.

Phase 69L made one operation's current primary step measurable as `fresh`, `watch`, `stale`, or `none`. Phase 69M adds list-level fields so maintainers can prioritize stuck projects without opening each operation.

## Implemented Scope

- `CommercialOperationService.production_closed_loop_action_audit_summary_for_operation`.
- `CommercialOperationResponse.production_closed_loop_action_audit_summary`.
- `CommercialOperationResponse.production_closed_loop_primary_step`.
- `CommercialOperationResponse.production_closed_loop_primary_step_staleness`.
- Flat list fields: `production_closed_loop_primary_step_key`, `production_closed_loop_staleness_status`, `production_closed_loop_waiting_seconds`, and `production_closed_loop_escalation_recommended`.
- `admin_dashboard` sorts `operationsForTable` by `closedLoopStalenessPriority`.
- Operation list columns show `closed_loop_step`, `staleness`, and `waiting_s`.
- The attention metric includes `staleClosedLoopCount`.

## Boundary

Phase 69M is list-level visibility only.

It does not execute target endpoints, run OpenClaw, run Playwright, publish, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, create publish evidence, or force readiness complete.

## Verification

- Governance closed-loop API test verifies stale list-level fields.
- Admin dashboard tests verify table priority and list fields.
- Documentation tests cover Phase 69M recovery markers.

## Next Step

The next production slice should expose a workspace-level stale-operation queue endpoint so maintainers and Agents can fetch only operations that require intervention.
