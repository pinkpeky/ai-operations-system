# Phase 68Z1 Production Closed-Loop Action Audit

Phase 68Z1 adds an audit layer for the Phase 68Z controlled next-action contract.

## Purpose

The server can now record what a worker/operator did with the current controlled next action: reviewed it, confirmed it, submitted it through the proper guarded endpoint, returned evidence, or blocked/failed it. This creates a traceable production closed-loop history without turning the next-action contract into an automatic executor.

## Backend

- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records`
- `GET /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records`
- `CommercialOperationService.record_production_closed_loop_action_audit`
- `CommercialOperationService.list_production_closed_loop_action_audits`
- Request schema: `CommercialOperationProductionClosedLoopActionAuditCreateRequest`
- Record schema: `CommercialOperationProductionClosedLoopActionAuditRecordResponse`
- List schema: `CommercialOperationProductionClosedLoopActionAuditListResponse`

Audit records are persisted in `commercial_operations.operation_metadata.production_closed_loop_action_audits` and keep a bounded history with `production_closed_loop_action_audit_latest`.

## Validation

The create endpoint checks the submitted `action_key` against the current Phase 68Z next-action contract. It also validates `stage_key`, target method, and target endpoint when supplied.

`confirmed`, `submitted`, and `evidence_returned` require `operator_confirmed=true`. `submitted` and `evidence_returned` must match the selected next action, and `evidence_returned` must include either `evidence_links` or `evidence_summary`.

The audit endpoint rejects sensitive keys or values such as password, token, secret, cookie, authorization, credential, session id, API key, access key, and verification-code markers. It is meant for operational evidence and record ids, not credentials.

## Customer Console

- `worker_console` exposes `Phase 68Z1 Controlled Action Audit`.
- `worker_console_desktop` exposes `Phase 68Z1 Controlled Action Audit`.
- The customer-machine panel uses `client-production-action-audit-panel`.
- Operators can record confirmation for the selected next-action contract and refresh audit history.

The UI does not call the selected target endpoint. It records confirmation only, then the operator or a later guarded workflow can submit through the proper endpoint and return evidence.

## Boundaries

- Does not execute target endpoints.
- Does not publish from the server.
- Does not run OpenClaw or Playwright on the server.
- Does not submit ComfyUI prompts.
- Does not mutate workflow JSON.
- Does not store credentials, session tokens, cookies, verification codes, or account passwords.
- Does not bypass operator approval.

## Runtime Contract

```text
phase=68Z1
contract=production_closed_loop_next_action_audit
storage=commercial_operations.operation_metadata.production_closed_loop_action_audits
server_side_external_execution=false
```

## Test Coverage

- `tests/test_operation_project_governance.py` verifies the audit create/list API, contract snapshot, no-execution metadata, and rejection of unconfirmed submitted/sensitive audit payloads.
- `tests/test_worker_console_client_ux.py` verifies the web and desktop clients expose the Phase 68Z1 panel, API methods, and CSS classes.
- `tests/test_commercial_operations_docs.py` verifies the foundation documentation covers the Phase 68Z1 action audit contract.
