# Phase 70W Production Delivery Action Packages

Phase 70W turns the Phase 70U delivery plan gates into explicit manual action packages for the server dashboard and customer-machine console. It does not execute those actions.

## What Changed

- Added `GET /api/v1/commercial-operations/production-closed-loop/delivery-action-packages`.
- Added `CommercialOperationService.get_production_closed_loop_delivery_action_packages`.
- Added `CommercialOperationProductionClosedLoopDeliveryActionPackageListResponse`, `CommercialOperationProductionClosedLoopDeliveryActionPackageResponse`, and `CommercialOperationProductionClosedLoopDeliveryActionStepResponse`.
- Added the `production_closed_loop_delivery_action_packages` contract.
- Each open gate now exposes:
  - target console
  - action status
  - operation-specific endpoint when available
  - blocked reasons
  - evidence requirements
  - operator/server/client next actions
  - payload template
  - guardrails
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` now display the delivery action packages beside the Phase 70U delivery plan.

## Boundary

Phase 70W is action-packaging only. It does not approve records, call target endpoints, submit ComfyUI prompts, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure the real provider, mark mock providers ready, or bypass approval.

## Verification

- `tests/test_operation_project_governance.py` verifies the API response, provider configuration package, next-cycle approval package, guardrails, and no-execution metadata.
- `tests/test_admin_dashboard_commercial_operations.py` verifies the server dashboard exposes Phase 70W.
- `tests/test_worker_console_client_ux.py` verifies both customer-machine consoles expose Phase 70W.
