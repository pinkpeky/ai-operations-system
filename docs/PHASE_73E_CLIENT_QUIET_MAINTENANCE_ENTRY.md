# Phase 73E Client Quiet Maintenance Entry

## Scope

Phase 73E continues the Codex-like customer-machine simplification by turning the global advanced diagnostics drawer into a quiet maintenance entry. The default operating screen keeps attention on status, goal input, and current work; diagnostics, runtime details, browser sessions, and logs remain available when an operator intentionally opens maintenance.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` label the global diagnostics drawer as `Phase 73E Client Quiet Maintenance Entry`.
- The drawer summary now displays the compact `维护` / `Maintenance` label with `日志与诊断` / `Logs and diagnostics`, while preserving `copy.advancedSummary` as the accessible label and title.
- The existing `layout-grid`, dashboard, runtime control, browser sessions, and `logs-panel` content remain inside `advanced-diagnostics`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` make `.advanced-diagnostics` a small right-aligned entry by default with `order: 7`, `width: fit-content`, and compact summary text.
- The same styles restore full-width diagnostic layout when `.advanced-diagnostics[open]` and explicitly keep `.advanced-diagnostics:not([open]) .layout-grid` folded.
- `chat-settings-panel` keeps its normal summary styling and is not reduced by this phase.

## Boundaries

This is frontend information architecture only. It does not remove advanced diagnostics, remove logs, remove browser session visibility, remove dashboard fields, remove runtime controls, change local worker APIs, start runtime automatically, stop runtime automatically, start heartbeat automatically, stop heartbeat automatically, refresh status automatically, change conversation APIs, change upload APIs, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, collect credentials, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the default maintenance entry is compact and right-aligned, the diagnostics `layout-grid` is hidden while closed, the grid becomes visible after opening it, and the page has no horizontal overflow.
