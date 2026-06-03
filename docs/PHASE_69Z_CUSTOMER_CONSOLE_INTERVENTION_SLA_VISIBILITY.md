# Phase 69Z Customer Console Intervention SLA Visibility

Phase 69Z exposes the server-side intervention SLA and reminder pressure in the customer-machine project workbench. Phase 69Y lets the operator record status transitions; Phase 69Z shows why the intervention is urgent and whether a reminder/follow-up is due without requiring raw queue JSON.

## Scope

- `worker_console` and `worker_console_desktop` derive `clientProductionInterventionAcknowledgementSla`.
- Both frontends derive `clientProductionInterventionAcknowledgementSlaStatus`.
- Both frontends derive `clientProductionInterventionWaitingSeconds`.
- Both frontends derive `clientProductionInterventionReminderRecommended`.
- Both frontends derive `clientProductionInterventionReminderCooldownStatus`.
- Both frontends derive `clientProductionInterventionReminderDispatchStatus`.
- The customer-machine project workbench renders `Phase 69Z Client Intervention SLA Visibility`.
- `client-production-intervention-sla-grid` shows SLA status, waiting seconds, reminder recommendation, cooldown state, and latest dispatch state.

## Boundary

This phase is SLA/reminder visibility only. It does not send reminders, send messages, execute target endpoints, publish from the server, call OpenClaw, call Playwright, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, download models, install workflows, upload files, or rebuild client packages.

## Verification

- `tests/test_worker_console_client_ux.py::test_worker_consoles_expose_phase_69z_client_intervention_sla_visibility`
- `tests/test_commercial_operations_docs.py::test_commercial_operations_foundation_covers_phase_69z_client_intervention_sla_visibility`
- `tests/test_commercial_operations_docs.py::test_phase_69z_client_intervention_sla_visibility_is_documented`
