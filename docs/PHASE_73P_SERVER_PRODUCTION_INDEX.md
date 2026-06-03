# Phase 73P Server Production Index

## Scope

Phase 73P continues the Codex-like server UI simplification after Phase 73O. It keeps the Commercial Ops server page compact, but adds a small `commercial-server-production-index` below the quiet cockpit so maintainers can jump to production maintenance, operation queue, selected context, action audit, upstream production, and closed-loop delivery without scanning the full drawer stack.

## Implementation

- `admin_dashboard/src/main.tsx` adds `commercialServerProductionIndexCards` from existing server state: intervention pressure, `operationsForTable`, selected operation context, `productionClosedLoopActionAudits`, content/assets/ComfyUI handoffs, deliverables, execution runs, and results.
- `admin_dashboard/src/main.tsx` adds `openCommercialServerDrawer(drawerSelector)`, which opens the target details drawer and scrolls it into view after an explicit operator click.
- `commercial-server-production-index` renders six compact cards and routes them to the existing `.commercial-server-maintenance-drawer`, `.commercial-server-operation-list-drawer`, `.commercial-server-operation-context-drawer`, `.commercial-server-action-audit-drawer`, `.commercial-server-production-upstream-drawer`, and `.commercial-server-production-closed-loop-drawer`.
- `admin_dashboard/src/styles.css` adds `commercial-server-production-index-head`, `commercial-server-production-index-grid`, and `commercial-server-production-index-card` rules with compact status borders so the server first screen stays simple instead of becoming another dense dashboard.

## Boundary

This is frontend information architecture only. It does not add a new backend state source, remove maintenance details, remove operation selection, remove operation context, remove action audit visibility, remove content drafts, remove asset requests, remove ComfyUI handoffs, remove deliverables, remove execution runs, remove results, change commercial operation APIs, create operations automatically, resolve gates directly without evidence, change env vars, store secrets, configure providers, mark mock providers ready, restart services, call target endpoints, approve records, reject records, acknowledge intervention records without an operator click, send reminders, retry failed work, recover failed work, select output candidates without an operator click, submit ComfyUI prompts, mutate workflow JSON, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, auto-refresh readiness, ingest analytics, or bypass approval.

## Verification

- `tests/test_admin_dashboard_commercial_operations.py::test_phase_73p_server_production_index_contract`
- `tests/test_commercial_operations_docs.py::test_phase_73p_server_production_index_is_documented`
