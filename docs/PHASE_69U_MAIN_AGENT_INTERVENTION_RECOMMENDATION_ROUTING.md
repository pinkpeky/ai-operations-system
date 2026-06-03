# Phase 69U Main Agent Intervention Recommendation Routing

Phase 69U connects the production closed-loop intervention queue to the main Agent. The queue already exposes a `recommended_action`; this phase makes that recommendation part of `agent-skill-orchestration` so the main Agent can prioritize stale/watch production issues before continuing ordinary content or execution planning.

This phase is routing-only. It does not send messages, acknowledge queue items automatically, call reminder endpoints automatically, execute target endpoints, call OpenClaw, call Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, restart services, or rebuild client packages.

## Backend Contract

- `CommercialOperationService.get_agent_skill_orchestration` builds `production_intervention_queue`.
- `production_intervention_queue.contract` is `production_closed_loop_intervention_main_agent_input`.
- `production_intervention_queue.recommended_action` is the operation-specific `production_closed_loop_intervention_queue_recommended_action`.
- `CommercialOperationMainAgent` adds the `production_intervention` track.
- Routing decisions expose `production_intervention_required`.
- Routing decisions expose `production_intervention_recommended_action`.
- Routing decisions expose `production_intervention_queue_summary`.

## Main Agent Advance

Main Agent advance treats the `production_intervention` track as recommendation-only. It returns operator next actions that point to the dedicated intervention queue endpoint when appropriate, but it creates no acknowledgement, reminder, publish, OpenClaw, Playwright, or ComfyUI execution record automatically.

## Verification

- `tests/test_commercial_operation_main_agent.py` verifies that `CommercialOperationMainAgent` prioritizes the `production_intervention` track when the queue marks the operation as stale/watch.
- `tests/test_operation_project_governance.py::test_operation_project_governance_closed_loop_api` verifies API-level `agent-skill-orchestration` consumption of `production_intervention_queue`.
- `tests/test_commercial_operations_docs.py` checks this document plus `docs/COMMERCIAL_OPERATIONS_FOUNDATION.md`, `docs/CURRENT_RUNTIME.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/PROJECT_STATUS.md`, and `docs/PHASE_INDEX.md`.
