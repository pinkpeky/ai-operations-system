# Phase 71O Production Delivery Audit Next Action Plan API

Phase 71O promotes the Phase 71N audit next-action plan from a script-only report into a first-class server contract and frontend surface.

## Added Contract

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-audit/next-action-plan`
- `CommercialOperationService.get_production_closed_loop_delivery_audit_next_action_plan`
- `CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanResponse`
- `CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanActionResponse`
- Contract name: `production_closed_loop_delivery_audit_next_action_plan`

The endpoint composes the production closed-loop acceptance summary, Phase 71G blocker clearance plan, and Phase 71K runbook evidence coverage into a deduplicated action plan. It keeps `action_key`, `title`, `owner`, `priority`, `source_blockers`, `target`, `required_endpoint`, `verification_commands`, `external_dependency_required`, and `can_be_resolved_by_ui`, while also returning embedded source summaries for operator traceability.

## Frontend Surface

`admin_dashboard`, `worker_console`, and `worker_console_desktop` now load and display the same next-action plan.

- Admin Dashboard: `Phase 71O Production Delivery Audit Next Action Plan`, `productionDeliveryAuditNextActionPlanState`, `loadProductionClosedLoopDeliveryAuditNextActionPlan`, `commercial-delivery-audit-next-action-plan`, and `commercial-delivery-audit-next-action-list`.
- Customer consoles: `Phase 71O client production delivery audit next action plan`, `productionClosedLoopDeliveryAuditNextActionPlan`, `clientDeliveryAuditNextActionPlanStatus`, `client-production-delivery-audit-next-action-plan`, and `client-production-delivery-audit-next-action-list`.

## Operational Meaning

Phase 71O does not make the system production-ready by itself. It makes the remaining blockers visible in the same server and customer-machine consoles that operators already use, so the path from final audit failure to manual remediation is no longer hidden inside a command-line report.

The endpoint marks the plan blocked while required actions remain. Typical actions include `configure_real_openclaw_provider`, `resolve_runbook_evidence_coverage`, `refresh_runbook_evidence_readiness`, `clear_operation_project_blockers`, and `clear_acceptance_gate`.

## Boundaries

Phase 71O is read-only planning and UI visibility. It does not configure OpenClaw, change environment variables, store or print secrets, execute target endpoints, call readiness-refresh POST endpoints, run OpenClaw, run Playwright, publish, click final submit, submit ComfyUI prompts, approve records, mark mock providers ready, or bypass approval.

## Verification

- `tests/test_operation_project_governance.py` verifies blocked next-action plans and the resolved-evidence-but-unrefreshed readiness action.
- `tests/test_admin_dashboard_commercial_operations.py` verifies the admin API client and UI surface.
- `tests/test_worker_console_client_ux.py` verifies the customer-console API client, UI surface, and styles.
- `tests/test_commercial_operations_docs.py` verifies this document plus `docs/COMMERCIAL_OPERATIONS_FOUNDATION.md`, `docs/CURRENT_RUNTIME.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/PROJECT_STATUS.md`, and `docs/PHASE_INDEX.md`.
