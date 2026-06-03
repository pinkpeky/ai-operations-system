# Phase 72Z Client Current Work Metrics Drawer

## Scope

Phase 72Z reduces the customer-machine current-work panel one step further by moving its always-visible metrics into the existing more-actions drawer. The first screen keeps the current task and one primary action visible, while inbox count, review pressure, and delivery completion remain available after expansion.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` move the `simple-current-work-metrics` block inside `simple-current-work-more-actions`.
- The metrics block keeps the existing inbox, creation-review, and delivery-audit values.
- The metrics block now also has `simple-current-work-more-metrics` and the aria label `Phase 72Z Client Current Work Metrics Drawer`.
- `simple-current-work-panel` changes from three columns to two columns: `grid-template-columns: minmax(0, 1fr) minmax(220px, 0.7fr)`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` add `simple-current-work-more-metrics` styling so the folded metrics use the drawer width cleanly.

## Boundaries

This is frontend information architecture only. It does not remove inbox metrics, remove review metrics, remove delivery metrics, change delivery-audit APIs, change readiness scoring, change the current-work priority queue, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, change conversation APIs, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the current-work metrics are not visible while the more-actions drawer is closed, become visible after opening it, and the page has no horizontal overflow.
