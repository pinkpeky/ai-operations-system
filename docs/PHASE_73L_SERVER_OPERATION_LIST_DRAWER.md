# Phase 73L Server Operation List Drawer

Phase 73L continues the Codex-like server backend simplification after Phase 73K. The Commercial Ops page should not open with a wide operation table by default; it should show a compact Operation queue entry and let maintainers expand the full list only when they need to switch or inspect operations.

## Implementation

- `admin_dashboard/src/main.tsx` adds `commercial-server-operation-list-drawer` with aria label `Phase 73L Server Operation List Drawer`.
- The drawer summary shows `Operation queue`, the `operationsForTable` count, and the currently selected operation title.
- The existing operation list `Panel`, refresh button, `operationsForTable` table, selected-row marker, and `setSelectedOperation(row)` selection behavior remain inside `commercial-server-operation-list-body`.
- `admin_dashboard/src/styles.css` hides `commercial-server-operation-list-body` while the drawer is closed and applies the same compact summary styling as the other server drawers.

## Boundaries

This is frontend information architecture only. It does not remove operations, remove operation selection, remove refresh, change `operationsForTable`, change commercial operation APIs, create operations automatically, approve records, reject records, acknowledge intervention records without an operator click, send reminders, retry failed work, recover failed work, select output candidates without an operator click, call target endpoints, run OpenClaw, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, configure secrets, restart services, or bypass approval.

## Verification

- `admin_dashboard` typecheck should pass.
- Commercial operations tests should assert that Phase 73L is documented and that the operation list is folded behind `commercial-server-operation-list-drawer`.
- Browser verification on `http://127.0.0.1:5173/` should confirm the Operation queue drawer is closed by default, expands to reveal the existing operation table, and does not create horizontal page overflow.
