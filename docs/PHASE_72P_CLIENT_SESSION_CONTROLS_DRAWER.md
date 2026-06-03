# Phase 72P Client Session Controls Drawer

## Scope

Phase 72P continues the Codex-style customer-machine simplification by removing low-frequency session maintenance actions from the default first screen. Operators still have access to session creation and refresh, but those controls now live in the folded maintenance area instead of the main title bar.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` mark the title-bar session buttons with `client-session-title-actions`.
- Both clients add `simple-session-drawer` with aria label `Phase 72P Client Session Controls Drawer`.
- The drawer keeps the existing `createThread` and `refreshConversation` actions through `simple-session-actions`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` hide `.codex-simple-client .client-session-title-actions` and style `.simple-session-drawer` / `.simple-session-actions` as a compact maintenance control group.

## Boundaries

This is frontend information architecture only. It does not change conversation API contracts, create threads automatically, refresh conversations automatically, deploy a real OpenClaw provider, store platform credentials, configure secrets from the UI, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the title-bar `新建会话` / `刷新任务` buttons are no longer visible in the first viewport, while `.simple-session-drawer` remains present inside the maintenance drawer.
