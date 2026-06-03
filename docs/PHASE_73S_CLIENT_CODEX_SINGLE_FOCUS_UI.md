# Phase 73S Client Codex Single Focus UI

Phase 73S responds to the customer-machine UI requirement: the default worker screen should feel closer to Codex, with one obvious current task and one obvious input/action area, not a dense operations dashboard.

## Runtime Changes

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` add `simpleProductionDetailSummary` and `simpleProductionDetailFullSummary` so the closed production drawer shows only a compact pending-work summary while retaining the full counts in the summary title.
- The production drawer summary changes from a dense `reviews/materials/flows/outputs` line to a simple `Production flow` / pending-count summary.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` move `simple-current-work-panel` ahead of `simple-goal-box` visually, make `client-top-utility-drawer` a quiet top-right utility entry, and make `simple-production-details-drawer` a lightweight flow link until opened.
- The detailed production index, approvals, material import, workflow selection, output preview, publish handoff, data pullback, and diagnostics remain available after opening their drawers.

## Boundary

Phase 73S is frontend information architecture only. It does not remove approvals, remove output preview, remove material import, remove workflow selection, change local worker APIs, change conversation APIs, change upload APIs, configure providers, mark mock providers ready, restart services, call target endpoints, approve records without an operator click, reject records without an operator click, select output candidates without an operator click, run OpenClaw actions, run Playwright, publish, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, auto-refresh readiness, or bypass approval.
