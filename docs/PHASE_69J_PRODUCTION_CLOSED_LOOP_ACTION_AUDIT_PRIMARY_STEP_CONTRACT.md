# Phase 69J Production Closed-Loop Action Audit Primary Step Contract

Date: 2026-06-01

## Goal

Phase 69J exposes the current action-audit primary step from the server.

Phase 69H returned the full operator checklist. Phase 69J adds `primary_step` to the same list response so clients and admin views can show the single next confirm, bind, validate, or refresh step without scanning the checklist themselves.

## Implemented Scope

- `CommercialOperationProductionClosedLoopActionAuditListResponse.primary_step`.
- `primary_step_contract=production_closed_loop_action_audit_primary_step`.
- `CommercialOperationService.list_production_closed_loop_action_audits` selects the first checklist item whose `status` is `next`.
- `worker_console` and `worker_console_desktop` read `productionClosedLoopServerActionAuditPrimaryStep`.
- `productionClosedLoopActionAuditPrimaryStep` still drives the visible primary button.
- The customer consoles fall back to local checklist scanning if `primary_step` is absent.

## Contract

`primary_step` is either the first checklist item with `status=next`, or `null` when no operator action is currently available from the checklist.

For example:

- after confirmation, `primary_step.step_key=bind`;
- after result binding, `primary_step.step_key=validate`;
- after `record_verified`, `primary_step.step_key=refresh`;
- after readiness refresh, `primary_step=null`.

## Boundary

Phase 69J is state exposure only.

It does not execute target endpoints, run OpenClaw, run Playwright, publish, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, create publish evidence, or force readiness complete.

## Verification

- Governance closed-loop API test verifies `primary_step` progression.
- `worker_console` typecheck passes.
- `worker_console_desktop` typecheck passes.
- Customer-console tests verify API client and UI markers.
- Documentation tests cover the Phase 69J recovery markers.

## Next Step

The next production slice should surface this `primary_step` in server-side dashboards and project summaries so maintainers can spot customer-machine stalls without opening the full client console.
