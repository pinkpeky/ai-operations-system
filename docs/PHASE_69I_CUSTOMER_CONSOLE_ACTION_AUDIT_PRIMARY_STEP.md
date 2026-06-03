# Phase 69I Customer Console Action Audit Primary Step

Date: 2026-06-01

## Goal

Phase 69I adds one primary operator button for the current action-audit checklist step in both customer-machine consoles.

Phase 69H made the checklist portable from the server. Phase 69I uses that checklist to choose the next available step and route the operator click to the existing confirm, bind, validate, or refresh handler. The individual buttons stay visible for audit clarity.

## Implemented Scope

- `Phase 69I Action Audit Primary Step` marker in `worker_console/src/main.tsx`.
- Matching marker in `worker_console_desktop/src/main.tsx`.
- `productionClosedLoopActionAuditPrimaryStep` selects the first checklist item with `state=next`.
- The primary button routes `confirm` to `recordProductionClosedLoopActionConfirmation`.
- The primary button routes `bind` to `bindProductionClosedLoopActionResultFromLatest`.
- The primary button routes `validate` to `validateProductionClosedLoopActionResultRecordFromLatest`.
- The primary button routes `refresh` to `refreshProductionClosedLoopActionReadinessAfterBinding`.

## Boundary

Phase 69I is operator interaction guidance only.

The primary button does not execute any step automatically. It requires a human click and calls the same guarded APIs as the existing individual buttons. It does not run OpenClaw, run Playwright, publish, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, create publish evidence, or force readiness complete.

## Verification

- `worker_console` typecheck passes.
- `worker_console_desktop` typecheck passes.
- Customer-console tests cover the Phase 69I marker, primary-step derivation, and handler routing tokens.
- Documentation tests cover the Phase 69I recovery markers.

## Next Step

The next production slice should expose the primary action state in server-side readiness and admin views so maintainers can see whether customer machines are waiting for confirmation, binding, validation, or readiness refresh.
