# Phase 70G Client Objective Completion Score

Phase 70G mirrors the server-calculated production completion score into the customer-machine consoles. Phase 70F made `production_closed_loop_completion_score` authoritative on the server dashboard; Phase 70G puts the same objective progress, remaining gates, and next focus in front of the operators who run OpenClaw, Playwright, asset import, evidence capture, and metric pullback from the client machine.

## Scope

- `worker_console` and `worker_console_desktop` type `CommercialOperationProductionClosedLoopAcceptanceSummary`.
- Both clients call `productionClosedLoopAcceptanceSummary`.
- Both clients call `/commercial-operations/production-closed-loop/acceptance-summary`.
- Both clients pass `force_metric_due` and `scan_limit` so the client view matches the production closed-loop pressure view.
- Both consoles keep `productionClosedLoopAcceptanceSummary`.
- Both consoles keep `productionClosedLoopAcceptanceStatus`.
- Both consoles derive `clientObjectiveCompletionPercent`.
- Both consoles derive `clientObjectiveCompletionLevel`.
- Both consoles derive `clientObjectiveCompletionNextFocus`.
- Both consoles derive `clientObjectiveRemainingGates`.
- Both consoles derive `clientObjectiveScoreBreakdown`.
- Both consoles render `Phase 70G client objective completion score`.
- The completion shell uses `client-production-objective-completion`.
- The completion meter uses `client-production-objective-meter`.
- Remaining gates use `client-production-objective-gates`.
- The visible contract marker remains `production_closed_loop_completion_score`.

## Boundary

This phase is customer-machine visibility and operator guidance only. It does not execute target endpoints, send reminders, send messages, call OpenClaw automatically, call Playwright automatically, publish from the server, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, download models, install workflows, upload files, or rebuild client packages.

## Verification

- `tests/test_worker_console_client_ux.py::test_worker_consoles_expose_phase_70g_client_objective_completion_score`
- `tests/test_commercial_operations_docs.py::test_commercial_operations_foundation_covers_phase_70g_client_objective_completion_score`
- `tests/test_commercial_operations_docs.py::test_phase_70g_client_objective_completion_score_is_documented`
