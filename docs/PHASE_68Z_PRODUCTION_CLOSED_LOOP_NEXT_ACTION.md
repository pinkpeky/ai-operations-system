# Phase 68Z Production Closed-Loop Controlled Next Action

Phase 68Z turns the Phase 68Y readiness result into a controlled next-action contract.

## Objective

Operators need a deterministic next step after checking production readiness. The system should not guess, auto-publish, or bypass approval. It should return the exact target endpoint, payload template, approval gates, evidence requirements, and execution boundary for the current blocked or reviewable stage.

## Implemented

- Backend endpoint: `GET /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action`.
- Service method: `CommercialOperationService.get_production_closed_loop_next_action`.
- API response: `CommercialOperationProductionClosedLoopNextActionResponse`.
- Action item schema: `CommercialOperationProductionClosedLoopActionResponse`.
- The response is derived from `production_closed_loop_e2e_readiness`.
- `worker_console` and `worker_console_desktop` expose `Phase 68Z Production Closed-Loop Controlled Next Action`.
- The customer-machine panel uses `client-production-next-action-panel`.

## Contract

The next-action endpoint is a contract surface. It does not execute the returned action automatically.

Each selected action includes:

```text
action_key
stage_key
action_type
method
endpoint
payload_template
evidence_requirements
review_gates
expected_result
boundary
```

Metadata contract:

```text
phase=68Z
contract=production_closed_loop_next_action
source_readiness_contract=production_closed_loop_e2e_readiness
server_side_external_execution=false
```

## Boundaries

- Does not submit ComfyUI prompts.
- Does not mutate workflow JSON.
- Does not publish from the server.
- Does not run OpenClaw or Playwright on the server.
- Does not control social accounts.
- Does not collect credentials or verification codes.
- Does not bypass operator approval.

## Operator Use

1. Refresh Phase 68Y readiness.
2. Refresh Phase 68Z next action.
3. Review the selected action endpoint, payload template, and evidence requirements.
4. Perform the action only after the relevant operator approval.
5. Return the required evidence through the listed endpoint before treating the stage as complete.

## Verification

- API E2E test: `tests/test_operation_project_governance.py::test_operation_project_governance_closed_loop_api`
- Frontend static UX test: `tests/test_worker_console_client_ux.py::test_worker_consoles_expose_phase_68z_production_closed_loop_next_action`
