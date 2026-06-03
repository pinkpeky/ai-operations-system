# Phase 71F Production Delivery Remediation Work Order Readiness Refresh

Phase 71F adds the audited readiness-refresh step after Phase 71E completion. A completed remediation work order can now be explicitly refreshed against the current production closed-loop readiness and next-action contracts, then recorded as an auditable refresh event.

## Added Contract

- `POST /api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-completion/readiness-refresh`
- `CommercialOperationService.refresh_production_closed_loop_delivery_remediation_work_order_readiness`
- `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRequest`
- `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshResponse`
- Contract name: `production_closed_loop_delivery_remediation_work_order_readiness_refresh`

The request requires `operator_confirmed=true` and at least one completed remediation work order in `completed_pending_readiness_refresh`. It can be scoped by `operation_id`, `remediation_key`, or `gate_key`. The response returns `coverage_after`, `execution_prep_after`, `readiness`, `next_action`, `next_action_key`, `refresh_record`, and `readiness_refreshed_count`.

## Frontend Surface

- `admin_dashboard` exposes `Refresh readiness after completion` in the Phase 71D execution-prep panel.
- `worker_console` and `worker_console_desktop` expose the same `Refresh readiness after completion` action in the customer-machine execution-prep panel.
- After refresh, the consoles reload work orders, coverage, execution prep, and the remediation map. The customer-machine consoles also replace the visible readiness and next-action snapshot with the refreshed result.

## State Transition

Before Phase 71F, a Phase 71E completion leaves the item in `completed_pending_readiness_refresh`.

After a successful Phase 71F refresh:

- coverage item status becomes `completed_readiness_refreshed`;
- execution-prep item status becomes `completed_readiness_refreshed`;
- a refresh record is stored under `production_closed_loop_delivery_remediation_work_order_readiness_refreshes`;
- the next production action remains derived from `production_closed_loop_e2e_readiness` and `production_closed_loop_next_action`.

## Boundaries

Phase 71F is a readiness and audit contract only. It does not execute target endpoints, resolve gates directly, approve records, run OpenClaw, run Playwright, publish, click final submit, submit ComfyUI prompts, upload files, collect credentials, configure providers, mark mock providers ready, mutate runtime secrets, or bypass approval.

## Verification

- `tests/test_operation_project_governance.py` verifies Phase 71F after a completed remediation work order, refresh record creation, refreshed coverage/prep status, readiness/next-action snapshots, and no-execution boundaries.
- `tests/test_admin_dashboard_commercial_operations.py` verifies the server dashboard exposes Phase 71F controls.
- `tests/test_worker_console_client_ux.py` verifies both customer-machine consoles expose Phase 71F controls and typed client methods.
- `tests/test_commercial_operations_docs.py` verifies this document plus `docs/COMMERCIAL_OPERATIONS_FOUNDATION.md`, `docs/CURRENT_RUNTIME.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/PROJECT_STATUS.md`, and `docs/PHASE_INDEX.md`.
