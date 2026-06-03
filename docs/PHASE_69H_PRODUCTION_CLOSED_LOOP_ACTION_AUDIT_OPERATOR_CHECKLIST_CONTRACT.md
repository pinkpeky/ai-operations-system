# Phase 69H Production Closed-Loop Action Audit Operator Checklist Contract

Date: 2026-06-01

## Goal

Phase 69H moves the confirm, bind, validate, and refresh checklist into the server action-audit list contract.

Phase 69G made the checklist visible in the customer console. Phase 69H makes the same state portable by returning `operator_checklist` from `CommercialOperationProductionClosedLoopActionAuditListResponse`, so web, desktop, and future clients can render the same step order without reimplementing the status rules.

## Implemented Scope

- `CommercialOperationProductionClosedLoopActionAuditListResponse.operator_checklist`.
- `CommercialOperationService._production_closed_loop_action_operator_checklist`.
- `production_closed_loop_action_audit_operator_checklist` metadata contract marker.
- `operator_checklist_contract=production_closed_loop_action_audit_operator_checklist`.
- Checklist step keys: `confirm`, `bind`, `validate`, `refresh`.
- Checklist statuses: `done`, `next`, `blocked`.
- `worker_console` and `worker_console_desktop` now prefer `productionClosedLoopServerActionAuditChecklist`.
- Both clients keep `productionClosedLoopLocalActionAuditChecklist` as a fallback for older servers.

## Contract

The server checklist is derived from the latest action-audit record:

- `confirm` is `done` once a latest audit exists;
- `bind` is `next` after confirmation and `done` after result binding;
- `validate` is `next` after binding and `done` after `record_verified`;
- `validate` is `blocked` when validation found a missing or invalid bound record;
- `refresh` is `next` only after `record_verified`;
- `refresh` is `done` after readiness refresh status exists.

Each checklist item includes `step_key`, `label`, `status`, `detail`, `source_field`, `audit_id`, `action_key`, `blocking_reason`, `requires_operator_confirmation`, and `server_side_external_execution=false`.

## Boundary

Phase 69H is contract and UI consumption only.

It does not execute target endpoints, run OpenClaw, run Playwright, publish, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, create publish evidence, or force readiness complete.

## Verification

- Governance closed-loop API test verifies `operator_checklist` status progression.
- `worker_console` typecheck passes.
- `worker_console_desktop` typecheck passes.
- Customer-console tests verify API client and UI markers.
- Documentation tests cover the Phase 69H recovery markers.

## Next Step

The next production slice should use the server checklist to surface a single primary action button state, while still requiring explicit operator confirmation for each mutating API call.
