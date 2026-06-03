# Phase 68Z7 Production Closed-Loop Optimization Decision Lifecycle

Phase 68Z7 fixes the lifecycle gap after Phase 68Z6 verified a real optimization decision record.

## Purpose

Phase 68Z6 proved that a real bound `OptimizationDecision` can pass the result-record validation gate. The next production problem was more subtle: a draft optimization decision cannot be approved directly because the existing API correctly requires `ready_for_review` first.

Phase 68Z7 aligns the controlled next-action contract with that lifecycle:

1. `draft` or `rejected` optimization decisions produce `mark_optimization_decision_ready`.
2. `ready_for_review` optimization decisions produce `approve_optimization_decision`.
3. An approved optimization decision completes `analysis_improvement` and moves readiness to `ready_for_next_cycle`.

## Backend

- `GET /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action`
- `POST /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/ready`
- `POST /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/approve`
- `CommercialOperationService.get_production_closed_loop_next_action`
- `CommercialOperationService.refresh_production_closed_loop_action_result_readiness`

For draft/rejected decisions, the selected action is:

```text
action_key=mark_optimization_decision_ready
expected_result.record_type=OptimizationDecision
expected_result.decision_status=ready_for_review
```

For ready decisions, the selected action is:

```text
action_key=approve_optimization_decision
expected_result.record_type=OptimizationDecision
expected_result.decision_status=approved
```

After the approved result is bound, validated, and refreshed:

- `record_validation_gate_status=record_validation_passed`
- `record_validation_required=false`
- `record_validation_passed=true`
- `refresh_status=stage_completed`
- `underlying_refresh_status=stage_completed`
- `stage_completed_after_binding=true`
- `readiness.ready_for_next_cycle=true`
- `readiness.readiness_status=ready_for_next_cycle`
- `next_action_key=prepare_next_approved_operation_cycle`

## Customer Console

No new panel is introduced. The existing `worker_console` and `worker_console_desktop` action-audit controls remain the operator surface:

- confirm selected next action
- execute the reviewed target endpoint outside the audit endpoint
- bind the returned result record
- validate the bound record
- refresh readiness after validation

The important change is that the selected action no longer suggests an invalid direct approval for a draft decision.

## Boundaries

- Does not execute target endpoints from the audit endpoint.
- Does not execute the next action automatically.
- Does not create or mutate the bound business record during result binding, validation, or readiness refresh.
- Does not publish from the server.
- Does not run OpenClaw or Playwright on the server.
- Does not submit ComfyUI prompts.
- Does not mutate workflow JSON.
- Does not store credentials, session tokens, cookies, verification codes, or account passwords.
- Does not bypass operator approval.
- Does not force a project stage complete without an approved optimization decision.

## Test Coverage

- `tests/test_operation_project_governance.py` verifies the full lifecycle:
  - a verified draft decision selects `mark_optimization_decision_ready`
  - the ready action is audited, executed through the real API, bound, validated, and refreshed
  - the next action becomes `approve_optimization_decision`
  - the approve action is audited, executed through the real API, bound, validated, and refreshed
  - readiness becomes `ready_for_next_cycle`
- `tests/test_worker_console_client_ux.py` verifies this phase is documented across recovery docs.
- `tests/test_commercial_operations_docs.py` verifies the foundation documentation covers the lifecycle contract.
