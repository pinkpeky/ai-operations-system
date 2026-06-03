# Phase 73Q Client Production Action Summary

## Scope

Phase 73Q continues the Codex-like customer-machine UI work after Phase 73P. It keeps the default first screen quiet, but makes the expanded production detail drawer immediately useful by showing the current production action before the navigation index.

## Implementation

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` add `simple-production-action-summary` with aria label `Phase 73Q Client Production Action Summary` inside `simple-production-details-body`.
- The summary reuses existing `clientProjectDecisionCards`, `clientProjectCurrentDecision`, `clientProjectSecondaryDecisionCards`, and `clientProjectDecisionTotalCount`; it does not create another project-state source.
- The current action shows the review label, detail, status badge, primary operator action, optional secondary operator action, and a detail-open button that calls `openClientDetailPanel(clientProjectCurrentDecision.targetId)`.
- Secondary production actions render as compact `simple-production-action-chip` buttons that open their existing project sections for review.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` add compact `simple-production-action-head`, `simple-production-action-current`, `simple-production-action-buttons`, `simple-production-action-secondary`, and `simple-production-action-chip` rules so the drawer reads like an action summary rather than a dashboard.

## Boundary

This is frontend information architecture and explicit operator action surfacing only. It does not add a new project state source, remove production records, remove approvals, remove output preview, remove material import, remove workflow selection, change local worker APIs, change conversation APIs, change upload APIs, start runtime automatically, start heartbeat automatically, refresh status automatically, approve records without an operator click, reject records without an operator click, acknowledge intervention records without an operator click, send reminders, retry failed work, recover failed work, select output candidates without an operator click, create output candidates without the existing operator action, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, auto-refresh readiness, or bypass approval.

## Verification

- `tests/test_worker_console_client_ux.py::test_phase_73q_client_production_action_summary_contract`
- `tests/test_commercial_operations_docs.py::test_phase_73q_client_production_action_summary_is_documented`
