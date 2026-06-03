# Phase 69V Customer Console Production Intervention Visibility

Phase 69V makes the Phase 69U main Agent intervention routing visible to customer-machine operators. `worker_console` and `worker_console_desktop` now consume the `agent-skill-orchestration` fields `production_intervention_queue`, `production_intervention_required`, and `production_intervention_recommended_action`, then render them in a read-only `client-production-intervention-panel`.

This phase is visibility-only. It does not acknowledge intervention queue items, record reminder dispatches, send messages, execute target endpoints, call OpenClaw, call Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, restart services, or rebuild client packages.

## Customer Console Contract

- `CommercialOperationRoutingDecision` is now typed in both customer-machine clients.
- `CommercialOperationAgentSkillOrchestration` includes `routing_decision`.
- `CommercialOperationAgentSkillOrchestration` includes `specialist_tracks`.
- `CommercialOperationAgentSkillOrchestration` includes `production_intervention_queue`.
- `worker_console/src/main.tsx` derives `clientProductionInterventionQueue`.
- `worker_console/src/main.tsx` derives `clientProductionInterventionRecommendedAction`.
- `worker_console/src/main.tsx` derives `clientProductionInterventionRequired`.
- `worker_console_desktop/src/main.tsx` mirrors the same derived state.

## Operator Surface

The new `client-production-intervention-panel` appears inside the project workbench beside the production runtime/readiness panels. It shows:

- recommended action key and reason from `production_intervention_recommended_action`;
- queue status and count from `production_intervention_queue`;
- whether operator confirmation is required;
- the target operation and contract boundary.

The panel keeps the operator inside the existing approval and queue flow. Real acknowledgements, reminders, OpenClaw execution, Playwright execution, and publishing still require their dedicated endpoints and customer-machine actions.

## Verification

- `tests/test_worker_console_client_ux.py` checks both customer-machine frontends and TypeScript clients for the 69V panel, fields, and styles.
- `tests/test_commercial_operations_docs.py` checks this document plus `docs/COMMERCIAL_OPERATIONS_FOUNDATION.md`, `docs/CURRENT_RUNTIME.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/PROJECT_STATUS.md`, and `docs/PHASE_INDEX.md`.
