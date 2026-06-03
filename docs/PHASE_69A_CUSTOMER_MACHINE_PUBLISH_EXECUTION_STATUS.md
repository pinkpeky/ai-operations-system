# Phase 69A Customer-Machine Publish Execution Status

Date: 2026-06-01

## Goal

Phase 69A fills the gap between Phase 68H `client-execution-handoff` and Phase 68I `execution-result`.

The customer-machine workflow is:

1. Staff approve and prepare a `PublishPackage`.
2. The customer-machine frontend receives the guarded handoff package.
3. The customer-machine operator posts execution progress through `execution-status`.
4. The server records queued, running, needs-operator, succeeded, failed, or cancelled state on the `PublishPackage`.
5. The operator uses failure evidence and retry policy before continuing.
6. Final platform content id, URL, evidence, and optional initial metrics still enter through `execution-result`.

This phase does not run OpenClaw, run Playwright, publish to social platforms, control accounts, store credentials, collect tokens or cookies, bypass operator approval, mutate ComfyUI workflows, submit prompts, restart services, or change runtime configuration.

## Implemented Scope

- `POST /api/v1/commercial-operations/{operation_id}/publish-packages/{publish_package_id}/execution-status`
- `CommercialOperationPublishExecutionStatusUpdateRequest`
- `CommercialOperationPublishExecutionStatusResponse`
- `CommercialOperationService.update_publish_execution_status()`
- `CommercialOperationPublishExecutionHandoffResponse.execution_status`
- Status history stored in `PublishPackage.metadata.publish_execution_status_history`
- Current status stored in `PublishPackage.metadata.publish_execution_status`
- Server boundary marker `customer_machine_publish_execution_status`
- Operator-confirmed progress updates for `queued`, `running`, `needs_operator`, `succeeded`, `failed`, and `cancelled`
- Retry policy and next-action guidance for customer-machine operators
- Integration coverage in `tests/test_operation_project_governance.py`

## Status Contract

`execution-status` accepts:

- `execution_status`;
- `operator_confirmed`;
- `customer_machine_id`;
- optional `attempt_id` for continuing the same attempt;
- optional `progress`;
- optional `failure_reason`;
- optional `operator_notes`;
- optional `retry_after_seconds`;
- evidence links and execution log entries;
- metadata for client/runtime traceability.

The response returns:

- the selected `attempt_id`;
- current publish package status;
- latest execution attempt;
- bounded execution history;
- retry policy;
- review gates;
- next actions for the customer-machine operator.

## State Rules

- `operator_confirmed=true` is required.
- Only approved, prepared, published, or failed `PublishPackage` records can receive status updates.
- `queued`, `running`, `needs_operator`, and `succeeded` keep an approved package prepared for customer-machine execution.
- `failed` and `cancelled` mark the package failed with the reported reason.
- `succeeded` still requires `execution-result` before metric analysis can use publish evidence.
- Failed, cancelled, and needs-operator states require human review before retry.

## Customer-Machine Behavior

`worker_console` and `worker_console_desktop` should treat this API as the progress bridge for real browser/account work.

Operators can:

- claim or start a publish package;
- record dry-run and publishing progress;
- report login, verification, CAPTCHA, composer, upload, or platform errors;
- attach screenshots and browser logs;
- continue the same attempt after resolving an issue;
- capture the final publish result when platform submission succeeds.

The server only stores status and evidence. It does not operate a real social account.

## Review Boundary

The required gates are:

- `PublishPackage` must be approved or prepared before status updates;
- customer-machine account confirmation remains required;
- status updates require operator confirmation;
- OpenClaw/Playwright execution stays on the customer machine;
- final publish evidence still requires `execution-result`;
- closed-loop metric analysis waits for approved metric snapshots.

## Project Fit

Phase 69A is project-wide. It applies to KTV video projects, image posts, audio posts, text posts, and future multi-platform publishing because all of them pass through the same `PublishPackage` execution lane.

It improves the production closed loop by making long-running customer-machine publishing observable without moving account-bound execution onto the server.

## Verification

- Backend syntax compile passes for service, schemas, routes, and governance tests.
- `tests/test_operation_project_governance.py::test_operation_project_governance_closed_loop_api` verifies unconfirmed rejection, queued status, running status, needs-operator status, preserved attempt history, retry policy, and final result capture.
- Documentation tests verify that Phase 69A remains visible in foundation and recovery docs.

## Next Step

The next project slice should expose the execution-status controls in `worker_console` and `worker_console_desktop`, then connect the visible publish progress state to the production closed-loop readiness panel.
