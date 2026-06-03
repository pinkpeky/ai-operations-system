# Phase 73G Server Codex Quiet Cockpit

## Scope

Phase 73G applies the same Codex-like simplification to the server web backend that Phase 73F applied to the customer-machine console. Server maintainers should first see a concise production closed-loop summary, then open detailed maintenance only when they need acceptance, delivery, blocker, or intervention diagnostics.

## Implemented

- `admin_dashboard/src/main.tsx` adds `commercial-server-quiet-cockpit` with aria label `Phase 73G Server Codex Quiet Cockpit`.
- The quiet cockpit summarizes objective completion, production pressure, intervention queue pressure, and the selected operation's current primary step.
- `admin_dashboard/src/main.tsx` wraps the existing `commercial-maintenance-cockpit`, `commercial-intervention-pressure-overview`, `commercial-acceptance-summary-panel`, `commercial-delivery-plan-panel`, `commercial-project-stage-overview`, and production closed-loop intervention queue panel inside `commercial-server-maintenance-drawer`.
- `admin_dashboard/src/styles.css` styles `commercial-server-quiet-cockpit`, `commercial-server-quiet-pill`, `commercial-server-maintenance-drawer`, and `commercial-server-maintenance-body`.
- The drawer keeps the existing server maintenance, acceptance, delivery, project-stage, and queue diagnostics available while closed by default.
- Responsive CSS puts the quiet cockpit and maintenance drawer summary into one-column layouts on narrower screens.

## Boundaries

This is frontend information architecture only. It does not remove `commercial-maintenance-cockpit`, remove `commercial-acceptance-summary-panel`, remove `commercial-delivery-plan-panel`, remove intervention queue controls, remove delivery audit controls, change commercial operation APIs, change server readiness scoring, create operations automatically, approve records without an operator click, reject records without an operator click, acknowledge intervention items without an operator click, send reminders, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, collect credentials, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `admin_dashboard`
- `pytest tests/test_admin_dashboard_commercial_operations.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5173/` should confirm that the Commercial Ops page shows `commercial-server-quiet-cockpit`, the detailed server maintenance area is folded in `commercial-server-maintenance-drawer` by default, existing diagnostics appear after expansion, and the page has no horizontal overflow.
