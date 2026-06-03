# Phase 73B Client Top Utility Drawer

## Scope

Phase 73B continues the Codex-like customer-machine simplification by reducing the top-level workspace chrome to one compact utility drawer. The default screen keeps the customer workspace title, current-work panel, and primary operator action as the main visual path; runtime diagnostics and operation/knowledge mode switching remain reachable after opening the utility drawer.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` add `client-top-utility-drawer` with aria label `Phase 73B Client Top Utility Drawer`.
- The utility summary exposes `工作区工具` / `Workspace tools` plus the current mode and concise runtime readiness text.
- The existing `client-shell-diagnostics-drawer` stays available inside `client-top-utility-body`, preserving `Phase 72S Client Shell Diagnostics Drawer`, runtime status badges, and diagnostic details.
- The existing `operator-page-mode-drawer` stays available inside `client-top-utility-body`, preserving `Phase 72Q Client Mode Switch Drawer`, `operator-page-tab-actions`, `setOperatorPage("operations")`, and `setOperatorPage("knowledge")`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` add `client-top-utility-drawer`, `client-top-utility-body`, folded-body rules, and nested drawer sizing rules so the top tools do not compete with the first-screen work area.

## Boundaries

This is frontend information architecture only. It does not remove runtime diagnostics, remove runtime status, remove heartbeat status, remove the knowledge base page, remove mode switching, change local worker APIs, change conversation APIs, change upload APIs, change current-work priority, change delivery-audit APIs, change readiness scoring, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, collect credentials, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that only one top utility drawer is visible by default, runtime diagnostics and the mode switch are not visible while it is closed, both nested drawers become visible after opening it, and the page has no horizontal overflow.
