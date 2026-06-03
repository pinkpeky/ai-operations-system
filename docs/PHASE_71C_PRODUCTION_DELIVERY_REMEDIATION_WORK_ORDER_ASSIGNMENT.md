# Phase 71C Production Delivery Remediation Work Order Assignment

Phase 71C adds a controlled way to assign work orders for remediation items that Phase 71B marks as unassigned. It is an operator-confirmed metadata operation: it creates `assigned` work-order records, then returns updated coverage, but it does not execute the remediation workflow.

## Added Contract

- `POST /api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-coverage/assign-missing`
- `CommercialOperationService.assign_missing_production_closed_loop_delivery_remediation_work_orders`
- `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentRequest`
- `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentResponse`
- Contract name: `production_closed_loop_delivery_remediation_work_order_assignment`

The request requires `assignee` and `operator_confirmed=true`. The response includes `assignment_status`, `requested_count`, `created_count`, `skipped_count`, generated work-order records, and `coverage_after` from `production_closed_loop_delivery_remediation_work_order_coverage`.

## Frontend Surface

- `admin_dashboard` exposes `Assign missing work orders` in `Phase 71B Production Delivery Remediation Work Order Coverage`.
- `worker_console` and `worker_console_desktop` expose the same `Assign missing work orders` control in `Phase 71B client delivery remediation work-order coverage`.
- The control refreshes work orders, coverage, and the remediation map after assignment.

## Boundaries

Phase 71C creates assignment records only. It does not resolve gates, execute target endpoints, approve records, run OpenClaw, run Playwright, publish, click final submit, submit ComfyUI prompts, upload files, collect credentials, configure providers, mark mock providers ready, or bypass approval. Remediation execution still requires a separate approved workflow and evidence trail.

## Verification

- `tests/test_operation_project_governance.py` verifies assignment creation, updated coverage, generated `assigned` work orders, and no-execution boundaries.
- `tests/test_admin_dashboard_commercial_operations.py` verifies the server dashboard exposes Phase 71C assignment controls.
- `tests/test_worker_console_client_ux.py` verifies both customer-machine consoles expose Phase 71C controls and typed client methods.
- `tests/test_commercial_operations_docs.py` verifies this document plus `docs/COMMERCIAL_OPERATIONS_FOUNDATION.md`, `docs/CURRENT_RUNTIME.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/PROJECT_STATUS.md`, and `docs/PHASE_INDEX.md`.
