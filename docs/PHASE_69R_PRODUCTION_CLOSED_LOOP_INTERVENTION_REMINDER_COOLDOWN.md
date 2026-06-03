# Phase 69R Production Closed-Loop Intervention Reminder Cooldown

Phase 69R adds reminder cooldown and follow-up state to the Phase 69Q reminder-dispatch record. The goal is operational discipline: an overdue queue item can be routed to an operator, but the server should not allow repeated same-level reminders to pile up during the cooldown window.

This phase is throttle metadata only. It does not send messages, call OpenClaw, call Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, restart services, or rebuild client packages.

## Backend Contract

- `CommercialOperationService._production_closed_loop_intervention_reminder_dispatch_cooldown` derives cooldown state from the latest reminder dispatch and current acknowledgement SLA.
- Queue items expose `reminder_dispatch_cooldown`, `reminder_follow_up_recommended`, and `reminder_next_allowed_at`.
- Cooldown states include `not_due`, `not_dispatched`, `cooling_down`, `cooldown_elapsed`, `dismissed`, and `unknown`.
- `next_reminder_allowed=false` blocks duplicate non-dismissed same-level reminder dispatch records during the cooldown window.
- Lifecycle progression remains allowed inside cooldown, for example recording `routed_to_operator` after `ready_for_review`.

## Admin Dashboard

- `productionClosedLoopInterventionFollowUpCount` counts queue items where a follow-up reminder is currently recommended.
- Intervention queue rows expose `reminder_cooldown_status`.
- Intervention queue rows expose `next_reminder_allowed`.
- Existing fields `reminder_dispatch_status` and `reminder_dispatch_channel` remain visible alongside the cooldown state.

## Verification

- `tests/test_operation_project_governance.py::test_operation_project_governance_closed_loop_api` verifies first reminder dispatch, cooldown state, duplicate-reminder rejection, and lifecycle progression.
- `tests/test_admin_dashboard_commercial_operations.py` checks the Admin Dashboard field names and follow-up count.
- `tests/test_commercial_operations_docs.py` checks this document plus `docs/COMMERCIAL_OPERATIONS_FOUNDATION.md`, `docs/CURRENT_RUNTIME.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/PROJECT_STATUS.md`, and `docs/PHASE_INDEX.md`.
