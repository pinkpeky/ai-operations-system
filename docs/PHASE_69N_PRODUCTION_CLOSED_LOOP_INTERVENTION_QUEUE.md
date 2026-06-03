# Phase 69N Production Closed-Loop Intervention Queue

Date: 2026-06-01

## Goal

Phase 69N exposes a workspace-level intervention queue for production closed-loop operations whose current primary action is `stale` or `watch`.

Phase 69M made stale/watch state visible in the operation list. Phase 69N adds a focused queue contract so server maintainers and Agents can fetch only the projects that need human attention.

## Implemented Scope

- `CommercialOperationService.get_production_closed_loop_intervention_queue`.
- `GET /api/v1/commercial-operations/production-closed-loop/intervention-queue`.
- `CommercialOperationProductionClosedLoopInterventionQueueResponse`.
- `CommercialOperationProductionClosedLoopInterventionQueueItemResponse`.
- Queue items include `operation`, `action_audit_summary`, `primary_step_key`, `staleness_status`, `waiting_seconds`, `escalation_recommended`, `priority_score`, and `recommended_action_key`.
- `admin_dashboard` calls `commercialOperationsApi.productionClosedLoopInterventionQueue`.
- Server UI state uses `productionInterventionQueueState`, `loadProductionClosedLoopInterventionQueue`, `productionClosedLoopInterventionQueueItems`, `productionClosedLoopInterventionQueueRows`, and `productionClosedLoopInterventionQueueCount`.
- The maintenance cockpit exposes `Phase 69N Production Closed-Loop Intervention Queue`.

## Boundary

Phase 69N is read-only queue prioritization.

It does not execute target endpoints, run OpenClaw, run Playwright, publish, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, create publish evidence, or force readiness complete.

## Verification

- Governance closed-loop API test verifies the queue after a stale primary step.
- Admin dashboard tests verify queue API wiring and UI markers.
- Documentation tests cover Phase 69N recovery markers.

## Next Step

The next production slice should add a queue item acknowledgement or assignment record so stale intervention ownership can be tracked without executing the target action.
