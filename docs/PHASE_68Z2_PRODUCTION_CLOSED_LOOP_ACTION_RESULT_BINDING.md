# Phase 68Z2 Production Closed-Loop Action Result Binding

Phase 68Z2 binds the Phase 68Z1 controlled-action audit record to the business result that came back after the approved workflow executed elsewhere.

## Purpose

Phase 68Z1 proves that an operator reviewed or confirmed the controlled next action. Phase 68Z2 adds the missing trace from that audit event to the returned result record, such as an optimization decision, publish package, output candidate, metric snapshot, or other project object.

This makes the production loop auditable end to end: selected action, operator confirmation, target endpoint, returned result id, evidence, and next readiness refresh can be inspected together.

## Backend

- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{audit_id}/result-binding`
- `CommercialOperationService.bind_production_closed_loop_action_result`
- Request schema: `CommercialOperationProductionClosedLoopActionResultBindingRequest`
- Response schema: `CommercialOperationProductionClosedLoopActionResultBindingResponse`
- The existing audit list response now carries `result_binding_status`, `result_record_type`, `result_record_id`, `result_status`, `result_endpoint`, `result_binding`, and `result_bindings` on each audit record.

Result bindings are persisted in `commercial_operations.operation_metadata.production_closed_loop_action_audits[*].result_binding` and also in the bounded `commercial_operations.operation_metadata.production_closed_loop_action_result_bindings` history.

## Validation

The binding endpoint requires `operator_confirmed=true`. `result_recorded` and `evidence_verified` require `result_record_id`. `result_failed` and `evidence_verified` require evidence summary or evidence links.

When the audit contract includes an expected result record type, the binding must match it. When `result_endpoint` is supplied, it must match or extend the audited target endpoint.

Sensitive keys or values such as password, token, secret, cookie, authorization, credential, session id, API key, access key, and verification-code markers are rejected.

## Customer Console

- `worker_console` exposes result binding status inside `Phase 68Z1 Controlled Action Audit`.
- `worker_console_desktop` exposes the same result binding status.
- Both clients call `bindProductionClosedLoopActionResult` only when an existing audited target record id is available.
- The customer-machine panel keeps using `client-production-action-audit-panel` so the audit and result binding remain one operator surface.

The UI does not invent missing result ids. If the current action creates a new record and no result id has been returned yet, the result binding control remains blocked until the real workflow returns a result id.

## Boundaries

- Does not execute target endpoints.
- Does not publish from the server.
- Does not run OpenClaw or Playwright on the server.
- Does not submit ComfyUI prompts.
- Does not mutate workflow JSON.
- Does not store credentials, session tokens, cookies, verification codes, or account passwords.
- Does not bypass operator approval.
- Does not prove record existence for every possible result type; the actual execution endpoint and operator evidence remain the source of truth.

## Runtime Contract

```text
phase=68Z2
contract=production_closed_loop_action_result_binding
source_audit_contract=production_closed_loop_next_action_audit
storage=commercial_operations.operation_metadata.production_closed_loop_action_result_bindings
server_side_external_execution=false
```

## Test Coverage

- `tests/test_operation_project_governance.py` verifies result binding creation, list visibility, operator confirmation enforcement, no-execution metadata, and result-binding coverage.
- `tests/test_worker_console_client_ux.py` verifies the web and desktop clients expose the Phase 68Z2 result binding API and UI controls.
- `tests/test_commercial_operations_docs.py` verifies the foundation documentation covers the Phase 68Z2 result binding contract.
