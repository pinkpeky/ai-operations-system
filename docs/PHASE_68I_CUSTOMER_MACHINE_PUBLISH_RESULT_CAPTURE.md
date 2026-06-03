# Phase 68I Customer-Machine Publish Result Capture

Date: 2026-05-30

## Goal

Phase 68I records the customer-machine publish result after a `PublishPackage` has been prepared for guarded execution.

The operator workflow is:

1. Staff approve and prepare a `PublishPackage`.
2. The customer-machine operator performs the approved account-bound publish action outside the server process.
3. The customer-machine frontend posts `execution-result` with platform content id or publish URL, screenshots/evidence, dry-run evidence, execution log, and optional initial metrics.
4. The server records the result into the `PublishPackage` metadata and marks the package `published` or `failed`.
5. If initial metrics are included, the server creates a `PlatformMetricSnapshot(collected)` for operator review.
6. Closed-loop analysis waits for metric approval before optimization.

This phase does not run OpenClaw, run Playwright, publish to social platforms, control accounts, bypass operator approval, mutate ComfyUI workflows, submit prompts, restart services, or change runtime configuration.

## Implemented Scope

- `POST /api/v1/commercial-operations/{operation_id}/publish-packages/{publish_package_id}/execution-result`
- `CommercialOperationPublishExecutionResult`
- `CommercialOperationService.capture_publish_execution_result()`
- Prepared/published `PublishPackage` readiness checks
- Customer-machine evidence, dry-run evidence, execution log, and result history stored on `PublishPackage.metadata`
- Successful result capture moves the package to `published`
- Failed result capture moves the package to `failed`
- Optional initial metrics create `PlatformMetricSnapshot(collected)`
- Customer-machine `capturePublishExecutionResult` client method
- `Phase 68I Customer-Machine Publish Result Capture` panel in `worker_console/src/main.tsx`
- Matching desktop panel in `worker_console_desktop/src/main.tsx`
- Tests in `tests/test_operation_project_governance.py`
- Frontend contract/documentation tests in `tests/test_worker_console_client_ux.py`

## Result Contract

`execution-result` accepts:

- `publish_succeeded`;
- platform content id or published URL for successful publishes;
- execution summary and operator notes;
- evidence links such as screenshots or exported browser logs;
- dry-run evidence collected before real submission;
- customer-machine execution log entries;
- optional initial metrics such as views, likes, comments, or reach;
- metadata for client/runtime traceability.

The response returns:

- updated `PublishPackage`;
- result status;
- captured execution result payload;
- optional created `PlatformMetricSnapshot`;
- review gates and next actions.

## Review Boundary

The required gates are:

- `PublishPackage` must be prepared before result capture;
- successful publish capture must include platform content id or URL;
- customer-machine evidence is operator-reported and not fetched or verified automatically;
- metric snapshots created from initial metrics remain `collected` until reviewed;
- closed-loop improvement waits for approved metrics.

## Project Fit

Phase 68I is project-wide. It supports KTV video publishing and any later image, audio, text, or multi-platform publish package that passes through the same approval and customer-machine execution path.

It keeps the division of responsibility clear: the server stores plans, packages, evidence, and analysis; the customer machine performs account-bound OpenClaw/Playwright work under human control.

## Verification

- Backend syntax compile must pass for service, schemas, and routes.
- `tests/test_operation_project_governance.py` must verify execution-result capture after publish package preparation.
- `tests/test_worker_console_client_ux.py` must verify web/desktop client methods, frontend state, panel classes, and documentation.
- Web and Desktop typecheck/build must pass.

## Next Step

The next project slice should connect approved `PlatformMetricSnapshot` records to a project-level metric analysis package so the main Agent can produce objective improvement recommendations for the next operation cycle.
