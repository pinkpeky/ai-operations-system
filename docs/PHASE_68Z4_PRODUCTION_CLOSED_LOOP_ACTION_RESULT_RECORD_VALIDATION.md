# Phase 68Z4 Production Closed-Loop Action Result Record Validation

Phase 68Z4 adds a verification step between result binding and readiness refresh.

## Purpose

Phase 68Z2 records the result record type and id returned by a controlled action. Phase 68Z4 checks whether that declared record actually exists in the commercial operation project tables, belongs to the same workspace and operation, and has a status compatible with the expected result contract.

This keeps the production loop honest: a bound id is not treated as progress until the referenced business record can be verified.

## Backend

- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{audit_id}/result-binding/record-validation`
- `CommercialOperationService.validate_production_closed_loop_action_result_record`
- Request schema: `CommercialOperationProductionClosedLoopActionResultRecordValidationRequest`
- Response schema: `CommercialOperationProductionClosedLoopActionResultRecordValidationResponse`
- The audit list response carries `result_record_validation_status`, `result_record_validation`, and `result_record_validations` on each audit record.

Validation snapshots are persisted in `commercial_operations.operation_metadata.production_closed_loop_action_audits[*].result_record_validation` and in the bounded `commercial_operations.operation_metadata.production_closed_loop_action_result_record_validations` history.

## Validation Scope

The endpoint supports the project records used by the production closed loop, including operation plans, project materials, production tasks, workflow selections, output candidates, final selections, publish packages, platform metric snapshots, commercial operation results, monitoring observations, and optimization decisions.

The validation result can be:

- `record_verified`
- `record_missing`
- `record_type_unsupported`
- `record_scope_mismatch`
- `record_status_mismatch`
- `record_status_terminal`

The response includes `record_exists`, `workspace_matches`, `operation_matches`, `status_matches`, `status_field`, `record_status`, `expected_statuses`, `record_summary`, and `supported_record_types`.

## Customer Console

- `worker_console` exposes the record check state inside `Phase 68Z1 Controlled Action Audit`.
- `worker_console_desktop` exposes the same record check state.
- Both clients call `validateProductionClosedLoopActionResultRecord`.
- The check button is available only after a result binding exists.

## Boundaries

- Does not execute target endpoints.
- Does not execute the next action.
- Does not create, update, approve, reject, or archive the bound business record.
- Does not publish from the server.
- Does not run OpenClaw or Playwright on the server.
- Does not submit ComfyUI prompts.
- Does not mutate workflow JSON.
- Does not store credentials, session tokens, cookies, verification codes, or account passwords.
- Does not bypass operator approval.
- Does not force a project stage complete.

## Runtime Contract

```text
phase=68Z4
contract=production_closed_loop_action_result_record_validation
source_result_binding_contract=production_closed_loop_action_result_binding
storage=commercial_operations.operation_metadata.production_closed_loop_action_result_record_validations
server_side_external_execution=false
```

## Test Coverage

- `tests/test_operation_project_governance.py` verifies record validation creation, missing-record detection, list visibility, operator confirmation enforcement, supported record types, and no-execution metadata.
- `tests/test_worker_console_client_ux.py` verifies the web and desktop clients expose the Phase 68Z4 validation API and UI controls.
- `tests/test_commercial_operations_docs.py` verifies the foundation documentation covers the Phase 68Z4 record validation contract.
