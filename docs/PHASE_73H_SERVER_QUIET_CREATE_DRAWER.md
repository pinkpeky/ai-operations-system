# Phase 73H Server Quiet Create Drawer

Phase 73H continues the Codex-like server backend simplification after Phase 73G. The server Commercial Ops page should not put the full create-operation form directly under the main status cockpit by default. Operators should first see the closed-loop status, maintenance entry, operation list, and selected-operation context, then open creation controls only when they need to start a new operation.

## Implementation

- `admin_dashboard/src/main.tsx` wraps the existing create-operation `Panel` in `commercial-server-create-drawer` with aria label `Phase 73H Server Quiet Create Operation Drawer`.
- The existing create form, `createOperation()` button, and action result drawer remain unchanged inside `commercial-server-create-body`.
- `admin_dashboard/src/styles.css` styles `commercial-server-create-drawer`, hides `commercial-server-create-body` while the drawer is closed, and keeps the drawer responsive with the same quiet summary treatment as server maintenance details.
- Phase 73G remains intact: `commercial-server-quiet-cockpit` still appears first, and `commercial-server-maintenance-drawer` still holds acceptance, delivery, intervention, and blocker diagnostics.

## Boundaries

This is frontend information architecture only. It does not remove create-operation capability, change commercial operation APIs, create operations automatically, approve records, reject records, acknowledge intervention records without an operator click, call target endpoints, run OpenClaw, run Playwright, publish, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, configure secrets, restart services, or bypass approval.

## Verification

- `admin_dashboard` typecheck should pass.
- Commercial operations docs/tests should assert that Phase 73H is documented and that the create form is folded behind `commercial-server-create-drawer` by default.
- Browser verification on `http://127.0.0.1:5173/` should confirm that the Commercial Ops page shows the quiet cockpit first, keeps server maintenance folded, keeps create-operation controls folded in `commercial-server-create-drawer`, and has no horizontal overflow.
