# Phase 69F Customer Console Action Audit Guided Validation

Date: 2026-06-01

## Goal

Phase 69F fixes the customer-machine action-audit controls so operators can move from result binding to record validation without being blocked by the validation gate itself.

Before this phase, the record validation button was effectively enabled only after `result_record_validation_status=record_verified`, which is the state the button is supposed to produce. Phase 69F changes the customer-console gate to allow validation after a result binding exists, and keeps readiness refresh blocked until validation is actually verified.

## Implemented Scope

- `Phase 69F Action Audit Guided Validation` marker in `worker_console/src/main.tsx`.
- Matching marker in `worker_console_desktop/src/main.tsx`.
- `expectedActionResultStatusValue` helper reads expected result status fields including `execution_status`, `plan_status`, `task_status`, `selection_status`, `candidate_status`, `package_status`, `snapshot_status`, `decision_status`, `result_status`, `draft_status`, `request_status`, and `run_status`.
- `actionResultEndpointFor` avoids appending the result id twice when the selected endpoint already contains the target record id.
- `productionClosedLoopActionRecordValidationReady` enables record validation after result binding.
- `productionClosedLoopActionReadinessRefreshReady` keeps readiness refresh disabled until `record_verified`.

## UI Contract

The customer-machine action-audit panel now follows this operator sequence:

1. Confirm the current controlled next-action.
2. Bind the target result record.
3. Validate the bound record.
4. Refresh readiness only after the validation result is `record_verified`.

For publish execution status actions, `expected_result.execution_status` can now flow into the binding as `result_status`, so `PublishExecutionStatus` records from Phase 69E use the same guided path as table-backed records.

## Boundary

Phase 69F is customer-console guidance only.

It does not execute target endpoints, run OpenClaw, run Playwright, publish, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, create publish evidence, or mark readiness complete without `record_verified`.

## Verification

- `worker_console` typecheck passes.
- `worker_console_desktop` typecheck passes.
- Customer-console tests cover the Phase 69F UI marker, the new status/endpoint helpers, and the two explicit readiness booleans.
- Documentation tests cover the Phase 69F recovery markers.

## Next Step

The next production slice should package the guided audit path as a single operator-facing checklist state so the customer console can show exactly which of confirm, bind, validate, and refresh is next for each project.
