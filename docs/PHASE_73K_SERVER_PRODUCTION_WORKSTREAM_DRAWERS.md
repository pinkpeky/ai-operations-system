# Phase 73K Server Production Workstream Drawers

Phase 73K continues the Codex-like server backend simplification after Phase 73J. The Commercial Ops page should keep the first screen focused on status, current operation, and deliberate next actions, while the long production workstream remains available only after an operator expands it.

## Implementation

- `admin_dashboard/src/main.tsx` adds `commercial-server-production-upstream-drawer` with aria label `Phase 73K Server Production Upstream Drawer`.
- The upstream drawer keeps the ComfyUI entry panel, content drafts panel, and asset requests panel inside `commercial-server-production-upstream-body`.
- `admin_dashboard/src/main.tsx` also adds `commercial-server-production-closed-loop-drawer` with aria label `Phase 73K Server Production Closed Loop Drawer`.
- The closed-loop drawer keeps deliverables, evidence snapshots, execution requests, execution runs, results, monitoring observations, optimization decisions, approvals, dry-runs, and links inside `commercial-server-production-closed-loop-body`.
- `admin_dashboard/src/styles.css` gives both drawers the same compact summary shape as the Phase 73G-73J server drawers and hides each body while the drawer is closed.

## Boundaries

This is frontend information architecture only. It does not remove content drafts, remove asset requests, remove deliverables, remove approvals, remove dry-runs, remove links, change commercial operation APIs, create operations automatically, approve records, reject records, acknowledge intervention records without an operator click, send reminders, retry failed work, recover failed work, select output candidates without an operator click, call target endpoints, run OpenClaw, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, configure secrets, restart services, or bypass approval.

## Verification

- `admin_dashboard` typecheck should pass.
- Commercial operations tests should assert that Phase 73K is documented and that the production content/assets and delivery-loop panels are folded behind `commercial-server-production-upstream-drawer` and `commercial-server-production-closed-loop-drawer`.
- Browser verification on `http://127.0.0.1:5173/` should confirm both drawers are closed by default, expand to reveal the existing workstream panels, and do not create horizontal page overflow.
