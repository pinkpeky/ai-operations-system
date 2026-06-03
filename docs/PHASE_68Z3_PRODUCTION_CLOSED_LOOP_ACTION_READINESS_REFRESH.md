# Phase 68Z3 Production Closed-Loop Action Readiness Refresh

Phase 68Z3 connects the Phase 68Z2 result binding back to the production readiness and controlled next-action contracts.

## Purpose

Phase 68Z2 records which business result came back from a controlled action. Phase 68Z3 answers the next production question: did that bound result actually move the project forward?

The refresh endpoint re-runs the Phase 68Y readiness view and the Phase 68Z next-action contract after a result binding. If the underlying business record is complete, the response shows the advanced stage and next action. If only a result id was bound but the actual project object is still missing or unapproved, the response stays on the same stage and tells the operator what remains.

## Backend

- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{audit_id}/result-binding/readiness-refresh`
- `CommercialOperationService.refresh_production_closed_loop_action_result_readiness`
- Request schema: `CommercialOperationProductionClosedLoopActionReadinessRefreshRequest`
- Response schema: `CommercialOperationProductionClosedLoopActionReadinessRefreshResponse`
- The existing audit list response now carries `readiness_refresh_status`, `readiness_refresh`, and `readiness_refreshes` on each audit record.

Readiness refresh snapshots are persisted in `commercial_operations.operation_metadata.production_closed_loop_action_audits[*].readiness_refresh` and also in the bounded `commercial_operations.operation_metadata.production_closed_loop_action_readiness_refreshes` history.

## Validation

The refresh endpoint requires `operator_confirmed=true` and a previous `result_recorded` or `evidence_verified` result binding. It rejects sensitive keys or values such as password, token, secret, cookie, authorization, credential, session id, API key, access key, and verification-code markers.

The endpoint returns both the refreshed `CommercialOperationProductionClosedLoopReadinessResponse` and the refreshed `CommercialOperationProductionClosedLoopNextActionResponse`.

## Customer Console

- `worker_console` exposes readiness refresh status inside `Phase 68Z1 Controlled Action Audit`.
- `worker_console_desktop` exposes the same refresh status.
- Both clients call `refreshProductionClosedLoopActionReadinessAfterResultBinding`.
- The customer-machine panel keeps using `client-production-action-audit-panel` so audit, result binding, and readiness refresh stay in one operator surface.

The refresh control is available only after a result binding exists.

## Boundaries

- Does not execute target endpoints.
- Does not execute the next action.
- Does not publish from the server.
- Does not run OpenClaw or Playwright on the server.
- Does not submit ComfyUI prompts.
- Does not mutate workflow JSON.
- Does not store credentials, session tokens, cookies, verification codes, or account passwords.
- Does not bypass operator approval.
- Does not force a project stage complete; real project records and approval statuses remain the source of truth.

## Runtime Contract

```text
phase=68Z3
contract=production_closed_loop_action_result_readiness_refresh
source_result_binding_contract=production_closed_loop_action_result_binding
source_readiness_contract=production_closed_loop_e2e_readiness
storage=commercial_operations.operation_metadata.production_closed_loop_action_readiness_refreshes
server_side_external_execution=false
```

## Test Coverage

- `tests/test_operation_project_governance.py` verifies readiness refresh creation, refreshed readiness/next-action payloads, list visibility, operator confirmation enforcement, and no-execution metadata.
- `tests/test_worker_console_client_ux.py` verifies the web and desktop clients expose the Phase 68Z3 refresh API and UI controls.
- `tests/test_commercial_operations_docs.py` verifies the foundation documentation covers the Phase 68Z3 readiness refresh contract.
