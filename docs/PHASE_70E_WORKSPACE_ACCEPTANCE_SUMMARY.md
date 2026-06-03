# Phase 70E Workspace Acceptance Summary

Phase 70E adds an authoritative workspace-level production closed-loop acceptance summary. Phase 70D made the Admin Dashboard easier to scan, but it was still a client-derived view. Phase 70E moves the acceptance aggregate into the server contract so maintainers can see whether the current workspace is accepted, partially ready, blocked, or waiting for intervention from one API response.

## Scope

- `CommercialOperationService.get_production_closed_loop_acceptance_summary` aggregates operation readiness, intervention queue state, stage blockers, and primary-step staleness.
- `GET /api/v1/commercial-operations/production-closed-loop/acceptance-summary` returns `CommercialOperationProductionClosedLoopAcceptanceSummaryResponse`.
- The response contract is `production_closed_loop_acceptance_summary`.
- The endpoint includes `accepted_count`, `ready_for_customer_machine_execution_count`, `ready_for_metric_feedback_count`, `ready_for_next_cycle_count`, `blocked_count`, `intervention_queue_count`, readiness/stage/staleness counts, `operations`, and `top_blockers`.
- `admin_dashboard` calls `commercialOperationsApi.productionClosedLoopAcceptanceSummary`.
- The Commercial Ops page stores the response in `productionAcceptanceSummaryState`.
- The page derives `productionClosedLoopAcceptanceSummary`, `productionClosedLoopAcceptanceOperations`, `productionClosedLoopAcceptanceTopBlockers`, `productionClosedLoopAcceptanceStatus`, and `productionClosedLoopAcceptanceCards`.
- The page renders `Phase 70E Workspace Acceptance Summary`.
- The overview shell uses `commercial-acceptance-summary-panel`.
- Acceptance cards use `commercial-acceptance-summary-grid`.
- Blocker shortcuts use `commercial-acceptance-blocker-list`.

## Boundary

This phase is acceptance aggregation and operator navigation only. It does not execute target endpoints, send reminders, send messages, call OpenClaw, call Playwright, publish from the server, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, download models, install workflows, upload files, or rebuild client packages.

## Verification

- `tests/test_operation_project_governance.py::test_operation_project_governance_closed_loop_api`
- `tests/test_admin_dashboard_commercial_operations.py::test_admin_dashboard_exposes_commercial_operations_page`
- `tests/test_commercial_operations_docs.py::test_commercial_operations_foundation_covers_phase_70e_workspace_acceptance_summary`
- `tests/test_commercial_operations_docs.py::test_phase_70e_workspace_acceptance_summary_is_documented`
