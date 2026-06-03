# Phase 70O Server Acceptance OpenClaw Provider Readiness Gate

Phase 70O moves real OpenClaw provider readiness from a customer-machine UI hint into the server acceptance score. The system can no longer present the production closed loop as 100% complete when the registered OpenClaw worker is missing, mock, unreachable, or lacks guarded real-submit capability.

## What Changed

- Added `CommercialOperationService._get_server_acceptance_openclaw_provider_readiness`.
- `GET /api/v1/commercial-operations/production-closed-loop/acceptance-summary` now returns `openclaw_provider_readiness`.
- `CommercialOperationProductionClosedLoopAcceptanceSummaryResponse` exposes `openclaw_provider_readiness`.
- `score_breakdown` now includes `real_publish_provider_ready`.
- `remaining_gates` includes `configure_real_openclaw_publish_provider` when the workspace has operations but the provider is not production-ready.
- The acceptance gates include `real_openclaw_publish_provider_ready_for_customer_machine_submit`.
- `admin_dashboard` shows the server-side OpenClaw provider status in the acceptance cards and score strip.
- `worker_console` and `worker_console_desktop` show the server acceptance provider status alongside the client objective score.

## Readiness Contract

The server readiness gate selects the registered Browser Worker with `openclaw=true` and calls its `GET /openclaw/capabilities` endpoint. It does not execute OpenClaw actions, run Playwright, log in, publish, collect credentials, or control real accounts.

The provider is marked ready only when all of these are true:

- the worker is available and reachable;
- the worker response succeeds;
- `mock=false`;
- `capabilities.real_publish_submit=true`;
- `capabilities.publish_submit_guarded=true` or the action list includes `publish_submit_guarded`.

Otherwise the readiness status stays blocked with `real_publish_provider_not_configured`.

## Scoring Impact

The production closed-loop score now reserves 10 points for `real_publish_provider_ready`. The score can still show progress through planning, workflow selection, output approval, publish handoff, metric feedback, and next-cycle review, but it cannot honestly reach 100% while the live provider remains mock or unavailable.

## Boundaries

Phase 70O is server acceptance validation only. It does not deploy a third-party OpenClaw adapter, store platform credentials, run server-side OpenClaw or Playwright, publish from the server, click final submit, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

## Verification

- `tests/test_operation_project_governance.py` asserts `server_acceptance_openclaw_provider_readiness_gate`, `openclaw_provider_readiness`, `real_publish_provider_ready`, and `configure_real_openclaw_publish_provider`.
- `tests/test_admin_dashboard_commercial_operations.py` asserts the Admin Dashboard provider readiness display.
- `tests/test_worker_console_client_ux.py` asserts the customer consoles consume the readiness field and display the server-side provider status.
