# Phase 72X Client Command Run Options Drawer

## Scope

Phase 72X keeps the customer-machine command area closer to a Codex-style single primary action. After Phase 73V, the default command bar uses the plan-first operation submit action, while background execution stays available inside a folded run-options drawer.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` wrap `sendBackgroundConversation` in `simple-run-options-drawer`.
- The drawer is labelled `Phase 72X Client Command Run Options Drawer`.
- The default visible command action is now the Phase 73V `submitSimpleOperationGoal` plan-first path, not the generic `sendConversationMessage` playbook route.
- `sendBackgroundConversation` and `workbenchCopy.backgroundRun` are preserved inside `simple-run-options-actions`.
- CSS adds `simple-run-options-drawer`, `simple-run-options-drawer > summary`, `simple-run-options-actions`, and `.simple-run-options-drawer:not([open]) .simple-run-options-actions` so background execution is reachable but folded by default.

## Boundaries

This is frontend information architecture only. It does not change conversation APIs, remove background execution, start background execution automatically, change delivery-audit APIs, change readiness scoring, create or clear blockers automatically, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the command area shows one primary send button by default, keeps the run-options drawer closed, reveals the background-run button after opening the drawer, and has no horizontal overflow.
