# Phase 73O Client Production Index

## Scope

Phase 73O continues the customer-machine Codex-like UI work after Phase 73N. It keeps the first screen folded, but adds a compact `simple-production-index` inside the expanded production detail drawer so operators can jump directly to reviews, materials, workflow selections, output candidates, publish packages, and metric/data records.

## Implementation

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` add `simple-production-index` with aria label `Phase 73O Client Production Index` inside `simple-production-details-body`.
- The index reuses the existing `clientProjectFocusCards` array instead of creating another source of truth for production state.
- Each index card calls `openClientDetailPanel(card.targetId)`, preserving the Phase 73N parent-drawer opening behavior and deep-linking to `client-project-section-materials`, `client-project-section-workflows`, `client-project-section-outputs`, `client-project-section-publish`, and the other project record sections.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` add compact `simple-production-index-head`, `simple-production-index-grid`, and `simple-production-index-card` rules so the expanded detail drawer stays scannable instead of becoming another full dashboard.

## Boundary

This is frontend information architecture only. It does not add a new project state source, remove operation details, remove project context, remove approvals, remove output preview, remove material import, remove workflow selection, change local worker APIs, change conversation APIs, change upload APIs, start runtime automatically, start heartbeat automatically, refresh status automatically, approve records, reject records, acknowledge intervention records without an operator click, send reminders, retry failed work, recover failed work, select output candidates without an operator click, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, auto-refresh readiness, or bypass approval.

## Verification

- `tests/test_worker_console_client_ux.py::test_phase_73o_client_production_index_contract`
- `tests/test_commercial_operations_docs.py::test_phase_73o_client_production_index_is_documented`
