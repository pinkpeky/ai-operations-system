# Phase 70V Main Agent Delivery Plan Routing

Phase 70V connects the Phase 70U delivery plan to the global commercial-operation Main Agent. It does not execute delivery gates, approve records, run OpenClaw, run Playwright, submit ComfyUI prompts, or publish.

## What Changed

- `CommercialOperationService.get_agent_skill_orchestration` now builds `production_delivery_plan` from `GET /api/v1/commercial-operations/production-closed-loop/delivery-plan`.
- The Main Agent receives `production_closed_loop_delivery_plan_main_agent_input`.
- `CommercialOperationMainAgent` now exposes a `production_delivery` specialist track.
- `routing_decision` now includes:
  - `production_delivery_plan_required`
  - `production_delivery_recommended_gate`
  - `production_delivery_plan_summary`
- `next_executable_contract.parameters` now carries the recommended delivery gate for downstream operator surfaces.
- `decisions` now includes `production_delivery_plan_recommended_gate`.
- `CommercialOperationRoutingDecisionResponse`, `CommercialOperationSpecialistTrackResponse`, and `CommercialOperationAgentSkillOrchestrationResponse` include the delivery-plan fields.

## Routing Behavior

The Main Agent still prioritizes `production_intervention` when an active intervention queue item requires operator acknowledgement or escalation. The delivery plan is carried as routing context for every orchestration response, but it does not automatically steal the normal closed-loop route. Normal stages such as approval, customer-machine execution, metric observation, analysis, and next-cycle content continue to route through their native tracks while exposing the recommended delivery gate in the routing decision and next executable contract.

`production_delivery` remains available as an explicit specialist track when the orchestration layer or an operator intentionally requests `production_delivery_skill`. This keeps real delivery blockers visible without preventing the main loop from drafting the next valid operator step.

## Boundary

Phase 70V is routing-only. It does not call target endpoints, create acknowledgement records, send reminders, approve operation plans, approve optimization decisions, submit ComfyUI prompts, install workflows, upload files, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, modify schedules, mark mock providers ready, bypass approval, or bypass operator approval.

## Verification

- `tests/test_commercial_operation_main_agent.py` verifies delivery-gate evidence is exposed without stealing normal routing, and verifies explicit `production_delivery_skill` routing.
- `tests/test_operation_project_governance.py` verifies the full commercial-operation API response includes `production_delivery_plan`, `production_delivery_recommended_gate`, and `production_delivery_plan_recommended_gate`.
