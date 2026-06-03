# Phase 69C Production Closed-Loop Publish Execution Status Readiness

Date: 2026-06-01

## Goal

Phase 69C connects customer-machine publish execution status back into the production closed-loop readiness and next-action contracts.

Before this phase, operators could record publish progress through Phase 69A/69B, but the production readiness view still treated the project mostly as waiting for final `execution-result`. Phase 69C makes the global loop aware of whether the project is waiting for status capture, waiting for operator intervention, ready for final result capture, or already through publish evidence.

## Implemented Scope

- `CommercialOperationService.get_production_closed_loop_readiness`
- `CommercialOperationService.get_production_closed_loop_next_action`
- `latest_records.publish_execution_status`
- `counts.publish_execution_statuses`
- `metadata.latest_publish_execution_status`
- acceptance gate `publish_execution_status_tracks_customer_machine_progress_before_result_capture`
- next action `record_customer_machine_publish_execution_status`
- next action `update_customer_machine_publish_execution_status`
- existing next action `submit_customer_machine_execution_result` now waits for `execution_status=succeeded`

## Readiness Rules

- `PublishPackage` approval remains a human gate.
- The publish package stage is complete once a package is `prepared` or `published`.
- The customer-machine execution stage is complete only after `publish_execution_result` exists.
- If no execution status exists, readiness blocks on `customer_machine_publish_execution_status_missing`.
- If latest status is `needs_operator`, readiness blocks on `customer_machine_publish_execution_needs_operator`.
- If latest status is `failed` or `cancelled`, readiness blocks on `customer_machine_publish_execution_failed_or_cancelled`.
- If latest status is `queued`, `running`, or `succeeded` but no result exists, readiness blocks on `customer_machine_publish_execution_result_missing`.
- When latest status is `succeeded`, next action becomes `submit_customer_machine_execution_result`.

## Next-Action Contract

When customer-machine execution has not yet succeeded, the next-action endpoint is:

```text
POST /api/v1/commercial-operations/{operation_id}/publish-packages/{publish_package_id}/execution-status
```

The expected result is:

```text
record_type=PublishExecutionStatus
```

When customer-machine execution has succeeded, the next-action endpoint returns to:

```text
POST /api/v1/commercial-operations/{operation_id}/publish-packages/{publish_package_id}/execution-result
```

This preserves the distinction between progress tracking and final evidence capture.

## Boundaries

Phase 69C is readiness aggregation only.

It does not run OpenClaw or Playwright on the server, publish from the server, control real accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, or mark final publish evidence complete without `execution-result`.

## Verification

- `tests/test_operation_project_governance.py::test_operation_project_governance_closed_loop_api` verifies:
  - `needs_operator` status is reflected in readiness;
  - current stage becomes `client_execution_result`;
  - latest status is visible in `latest_records.publish_execution_status`;
  - next action points to `execution-status`;
  - `succeeded` status switches next action to `execution-result`.
- Commercial operations docs and customer-console docs include Phase 69C recovery markers.

## Next Step

The next project slice should surface the production readiness publish-status reason in the customer-console closed-loop readiness panel so non-technical operators can see why a project is blocked.
