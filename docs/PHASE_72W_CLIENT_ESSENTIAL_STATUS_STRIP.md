# Phase 72W Client Essential Status Strip

## Scope

Phase 72W removes duplicated first-screen status controls after Phase 72V introduced the unified current-work panel. Server pressure and project progress stay visible because operators need immediate runtime and process context. Creation review and delivery readiness remain in the data model, but their first-screen action surface now lives inside the unified current-work panel instead of another status pill.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` add `simpleVisibleStatusCards`.
- `simpleVisibleStatusCards` filters `simpleMinimalStatusCards` to `server-pressure` and `project-progress`.
- `simple-command-status-strip` now renders `simpleVisibleStatusCards.map((card) => ...)` under `Phase 72W Client Essential Status Strip / Phase 72O Client Codex Minimal Workspace`.
- `simpleMinimalStatusCards` still keeps `creation-review` and `delivery-readiness` as structured status data for contracts and for the unified current-work panel.
- `simple-current-work-panel` remains the first-screen home for creation-review and delivery-readiness action context.
- CSS changes `.simple-command-status-strip` to `grid-template-columns: repeat(2, minmax(0, 1fr))`.

## Boundaries

This is frontend information architecture only. It does not remove server pressure visibility, remove project progress visibility, remove creation review data, remove delivery readiness data, change delivery-audit APIs, change readiness scoring, create or clear blockers automatically, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that `.simple-command-status-strip` shows two visible buttons, the unified current-work panel remains visible, legacy current-inbox and delivery cards remain hidden, and there is no horizontal overflow.
