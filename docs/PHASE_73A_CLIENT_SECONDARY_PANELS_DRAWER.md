# Phase 73A Client Secondary Panels Drawer

## Scope

Phase 73A reduces the customer-machine first-screen drawer stack by grouping the lower-frequency project context and plan/status panels behind one secondary-panels drawer. The default screen keeps server pressure, project progress, the goal input, and the current-work panel visible; operators can still expand the grouped drawer for project context or detailed plan status.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` add `simple-secondary-panels-drawer` with aria label `Phase 73A Client Secondary Panels Drawer`.
- The grouped drawer summary exposes one default entry labelled `更多面板` / `More panels`.
- The existing `simple-project-context-drawer` remains inside `simple-secondary-panels-body`.
- The existing `operator-detail-drawer` remains inside `simple-secondary-panels-body`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` add `simple-secondary-panels-drawer`, `simple-secondary-panels-body`, and folded-body rules so the two nested panels do not occupy first-screen space until the operator expands the grouped drawer.

## Boundaries

This is frontend information architecture only. It does not remove project context, remove plan/status details, remove approval panels, remove output panels, change current-work priority, change delivery-audit APIs, change readiness scoring, change conversation APIs, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that one secondary-panels drawer is visible by default, the project-context and plan/status nested panels are not visible while it is closed, both nested panels become visible after opening it, and the page has no horizontal overflow.
