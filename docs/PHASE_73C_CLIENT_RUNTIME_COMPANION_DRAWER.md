# Phase 73C Client Runtime Companion Drawer

## Scope

Phase 73C continues the Codex-like customer-machine simplification by folding the local runtime companion block into one compact status drawer. The default screen keeps the current task workspace visually dominant; operators can still expand the drawer when they need runtime controls, language switching, or deeper client maintenance details.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` add `client-runtime-companion-drawer` with aria label `Phase 73C Client Runtime Companion Drawer`.
- The drawer summary exposes the existing local connection label and the current readiness headline, such as `客户机已就绪` / `Client ready`.
- The existing `client-runtime-summary` remains available inside `client-runtime-companion-body`.
- The existing `client-runtime-controls-drawer` remains available inside `client-runtime-companion-body`, preserving runtime start, heartbeat start, refresh, and language switching controls.
- The existing `client-home-detail-drawer` remains available inside `client-runtime-companion-body`, preserving advanced maintenance and diagnostic details.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` add `client-runtime-companion-drawer`, `client-runtime-companion-body`, folded-body rules, and compact summary styling.

## Boundaries

This is frontend information architecture only. It does not remove local runtime controls, remove language switching, remove advanced maintenance details, remove runtime status, remove heartbeat status, change local worker APIs, start runtime automatically, start heartbeat automatically, refresh status automatically, change conversation APIs, change upload APIs, change current-work priority, change delivery-audit APIs, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, collect credentials, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that only the compact runtime companion summary is visible by default, the runtime summary and advanced detail drawer are hidden while it is closed, both become reachable after opening it, and the page has no horizontal overflow.
