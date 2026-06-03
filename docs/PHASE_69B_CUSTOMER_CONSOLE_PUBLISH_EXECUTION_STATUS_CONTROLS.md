# Phase 69B Customer Console Publish Execution Status Controls

Date: 2026-06-01

## Goal

Phase 69B exposes the Phase 69A publish execution status contract in the customer-machine consoles.

The operator workflow is:

1. Open the approved or prepared `PublishPackage` handoff.
2. Confirm the package can be handled on the customer machine.
3. Record `queued`, `running`, `needs_operator`, `succeeded`, or `failed` status from the publish execution panel.
4. Attach optional screenshot or log evidence.
5. Continue to the existing publish result capture only after the real platform submission has completed.

This phase does not automate OpenClaw, automate Playwright, click platform submit buttons, publish from the server, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

## Implemented Scope

- `CommercialOperationPublishExecutionHandoff.execution_status` in both customer-console API clients
- `CommercialOperationPublishExecutionStatus`
- `CommercialOperationPublishExecutionStatusValue`
- `commercialOperationClient.updatePublishExecutionStatus`
- `updatePublishExecutionStatusFromClient`
- `publishExecutionStatusRecord`
- `publishExecutionStatusLoading`
- customer-machine status buttons for `queued`, `running`, `needs_operator`, `succeeded`, and `failed`
- latest attempt, progress, and attempt id visibility in `client-publish-execution-panel`
- matching web and desktop TypeScript coverage

## UI Contract

The existing `client-publish-execution-panel` now carries Phase 68H handoff and Phase 69B progress controls together.

It shows:

- handoff readiness;
- account confirmation target;
- expected evidence count;
- latest customer-machine execution status;
- current progress;
- current attempt id;
- action buttons for the status transitions.

Each status update prompts the operator for:

- customer machine id;
- progress;
- failure or manual-intervention reason when required;
- optional evidence path or URL.

The client sends `operator_confirmed=true` and includes `phase=69B`, `source=worker_console_publish_execution_status` or `source=worker_console_desktop_publish_execution_status`, and `server_side_external_execution=false`.

## Review Boundary

The customer-machine console records progress only.

The server still does not:

- log in to social platforms;
- run OpenClaw or Playwright for account-bound publishing;
- operate real browser sessions;
- submit platform forms;
- verify credentials;
- fetch analytics without evidence;
- mark publish results complete without `execution-result`.

## Project Fit

Phase 69B makes long customer-machine publishing runs visible to staff without weakening the security boundary. It is suitable for KTV video jobs and for future image, audio, text, or multi-platform publishing because the UI sits on the shared `PublishPackage` lane.

## Verification

- `worker_console` typecheck passes.
- `worker_console_desktop` typecheck passes.
- `tests/test_worker_console_client_ux.py` verifies web and desktop API clients, state, UI text, action handlers, and panel markers.

## Next Step

The next project slice should connect the latest publish execution status to production closed-loop readiness and next-action summaries, so operators can see whether a project is waiting on publish execution, final result capture, or metric pullback.
