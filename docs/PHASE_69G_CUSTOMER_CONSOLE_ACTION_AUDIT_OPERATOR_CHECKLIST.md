# Phase 69G Customer Console Action Audit Operator Checklist

Date: 2026-06-01

## Goal

Phase 69G makes the controlled action-audit sequence visible as an operator checklist in both customer-machine consoles.

After Phase 69F fixed the button gates, operators still had to infer the current step from separate cards and buttons. Phase 69G adds one compact checklist for confirm, bind, validate, and refresh so the next required action is visible without reading raw audit metadata.

## Implemented Scope

- `Phase 69G Action Audit Operator Checklist` marker in `worker_console/src/main.tsx`.
- Matching marker in `worker_console_desktop/src/main.tsx`.
- `productionClosedLoopActionAuditChecklist` derives four checklist items: confirm, bind, validate, refresh.
- `productionClosedLoopActionAuditChecklistNext` marks the next executable operator step.
- `client-production-action-audit-checklist` renders the sequence below the audit state cards.
- `.client-production-action-audit-checklist article.done` marks completed steps.
- `.client-production-action-audit-checklist article.next` marks the next step.
- `.client-production-action-audit-checklist article.blocked` marks waiting steps.

## UI Contract

The checklist state is derived only from existing audit data:

- confirm is done when a latest audit record exists;
- bind is done when `result_binding_status` exists;
- validate is done when `result_record_validation_status=record_verified`;
- refresh is done when `readiness_refresh_status` exists;
- the first incomplete but available step becomes `next`;
- unavailable steps remain `blocked`.

## Boundary

Phase 69G is visibility and guidance only.

It does not execute target endpoints, run OpenClaw, run Playwright, publish, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, create publish evidence, or force readiness complete.

## Verification

- `worker_console` typecheck passes.
- `worker_console_desktop` typecheck passes.
- Customer-console tests cover the Phase 69G marker, checklist state variables, rendered checklist class, and done/next/blocked CSS states.
- Documentation tests cover the Phase 69G recovery markers.

## Next Step

The next production slice should make the same checklist available from the server response so other clients can render the identical audit-step state without reimplementing the frontend derivation.
