# Phase 68H Customer-Machine Publish Execution Handoff

Date: 2026-05-30

## Goal

Phase 68H connects an operator-approved `PublishPackage` to a guarded customer-machine execution handoff.

The operator workflow is:

1. Staff approve the `FinalSelection`.
2. Staff prepare a `PublishPackage` draft from the Phase 68G publish-prep package.
3. Staff approve the `PublishPackage`.
4. The customer-machine frontend requests `client-execution-handoff`.
5. The server returns `CommercialOperationPublishExecutionHandoff` with package payload, account confirmation, dry-run plan, expected evidence, metric pullback plan, and review gates.
6. The customer-machine operator prepares the package for controlled OpenClaw/Playwright execution.
7. Real publishing and metric capture still require operator approval and customer-machine evidence.

This phase does not run OpenClaw, run Playwright, publish to social platforms, control real accounts, bypass operator approval, mutate ComfyUI workflows, submit prompts, restart services, or change runtime configuration.

## Implemented Scope

- `GET /api/v1/commercial-operations/{operation_id}/publish-packages/{publish_package_id}/client-execution-handoff`
- `CommercialOperationPublishExecutionHandoff`
- `CommercialOperationService.get_publish_execution_handoff()`
- Readiness checks for approved or prepared `PublishPackage` records
- Linked `FinalSelection`, selected `OutputCandidate`, and existing `PlatformMetricSnapshot` visibility
- Customer-machine `getPublishExecutionHandoff` client method
- `Phase 68H Customer-Machine Publish Execution Handoff` panel in `worker_console/src/main.tsx`
- Matching desktop panel in `worker_console_desktop/src/main.tsx`
- Tests in `tests/test_operation_project_governance.py`
- Frontend contract/documentation tests in `tests/test_worker_console_client_ux.py`

## Handoff Contract

`client-execution-handoff` is read-only.

It returns:

- publish package id, platform, package status, and execution target;
- blocking reasons if the package is not approved or prepared;
- linked `PublishPackage`, `FinalSelection`, and selected `OutputCandidate` records;
- `client_execution_payload` for the customer-machine runner;
- `execution_runbook` steps for account confirmation, dry-run, publish action, and result recording;
- `account_confirmation` requiring operator verification of the real account;
- `dry_run_plan` requiring a non-submit OpenClaw/Playwright dry-run;
- `expected_evidence` for screenshots, logs, account confirmation, and publish result URL/content id;
- `metric_pullback_plan` for daily platform data snapshots;
- `review_gates` that keep publishing and closed-loop analysis approval-gated.

## Customer-Machine Behavior

The customer-machine workbench now exposes a publish execution handoff action when a `PublishPackage` is `approved` or `prepared`.

Operators can:

- refresh handoff readiness;
- inspect account and evidence requirements;
- move an approved package to `prepared`;
- keep real OpenClaw/Playwright publishing outside the server process;
- keep platform metric collection tied to `PlatformMetricSnapshot` review.

The server produces a controlled handoff package. It does not log in, click submit, or control a real social account.

## Review Boundary

The required gates are:

- `PublishPackage` must be approved or prepared;
- linked `FinalSelection` must remain approved;
- the customer-machine operator must confirm the real account;
- OpenClaw/Playwright dry-run evidence must be captured before real publish;
- publish result must be recorded with URL/content id and screenshot evidence;
- platform metrics must be captured as `PlatformMetricSnapshot`;
- closed-loop analysis waits for metric approval.

## Project Fit

Phase 68H is project-wide. It supports KTV video publishing, image posts, audio-led posts, text posts, and future platform-specific publishing adapters.

It keeps the architecture objective intact: the server plans, reviews, packages, and analyzes; the customer machine handles account-bound execution under human control.

## Verification

- Backend syntax compile must pass for service, schemas, and routes.
- `tests/test_operation_project_governance.py` must verify the handoff after publish package approval.
- `tests/test_worker_console_client_ux.py` must verify web/desktop client methods, frontend state, panel classes, and documentation.
- Web and Desktop typecheck/build must pass.

## Next Step

The next project slice should record customer-machine publish execution evidence and result capture against the prepared `PublishPackage`, then connect the scheduled platform metric pullback to the existing closed-loop improvement records.
