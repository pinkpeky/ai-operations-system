# Phase 69Q Production Closed-Loop Intervention Reminder Dispatch

Phase 69Q turns the Phase 69P reminder signal into an auditable operator record. It is intentionally record-only: the server stores reminder routing intent and manual-dispatch evidence, but it does not send messages, call OpenClaw, call Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, restart services, or rebuild client packages.

## Backend Contract

- `CommercialOperationService.record_production_closed_loop_intervention_reminder_dispatch` records an operator-confirmed reminder dispatch for stale/watch intervention queue items when `acknowledgement_sla.reminder_recommended=true`.
- `CommercialOperationService.list_production_closed_loop_intervention_reminder_dispatches` returns the reminder dispatch history for one operation.
- `CommercialOperationProductionClosedLoopInterventionReminderDispatchRequest` accepts `reminder_status`, `reminder_channel`, `reminder_recipient`, `reminder_message`, `operator_confirmed`, `evidence_links`, `dispatch_notes`, and `metadata`.
- `CommercialOperationProductionClosedLoopInterventionReminderDispatchResponse` returns the stored record, including the current acknowledgement status, acknowledgement assignee, acknowledgement SLA, queue-item snapshot, record boundaries, and metadata.
- `CommercialOperationProductionClosedLoopInterventionReminderDispatchListResponse` returns `reminder_dispatch_count`, `latest_record`, `records`, `generated_at`, boundaries, and metadata.
- Queue items expose `latest_intervention_reminder_dispatch`, `reminder_dispatch_status`, and `reminder_dispatch_channel`.

## API Surface

- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/reminder-dispatches`
- `GET /api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/reminder-dispatches`

The create endpoint requires `operator_confirmed=true`. `routed_to_operator` and `sent_manually` records require a recipient; `sent_manually` records require evidence links or dispatch notes. Records are stored under `commercial_operations.operation_metadata.production_closed_loop_intervention_reminder_dispatches`, capped at the latest 100 records, with `production_closed_loop_intervention_reminder_dispatch_latest` cached for queue display.

## Admin Dashboard

- `commercialOperationsApi.createProductionClosedLoopInterventionReminderDispatch` records a reminder dispatch.
- `commercialOperationsApi.productionClosedLoopInterventionReminderDispatches` reads reminder dispatch history.
- `recordProductionClosedLoopInterventionReminderDispatch` is the Admin Dashboard action.
- `interventionReminderChannel`, `interventionReminderRecipient`, and `interventionReminderMessage` are the operator-editable routing fields.
- The intervention queue table shows `reminder_dispatch_status` and `reminder_dispatch_channel` beside `ack_sla_status`, `ack_waiting_seconds`, and `reminder_recommended`.

## Verification

- `tests/test_operation_project_governance.py::test_operation_project_governance_closed_loop_api` covers overdue SLA, reminder dispatch creation, reminder dispatch list retrieval, and queue backfill through `latest_intervention_reminder_dispatch`.
- `tests/test_admin_dashboard_commercial_operations.py` checks the Admin Dashboard function names, table fields, inputs, and API client endpoints.
- `tests/test_commercial_operations_docs.py` checks this document plus `docs/COMMERCIAL_OPERATIONS_FOUNDATION.md`, `docs/CURRENT_RUNTIME.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/PROJECT_STATUS.md`, and `docs/PHASE_INDEX.md`.
