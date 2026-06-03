# Phase 72O Client Codex Minimal Workspace

## Scope

Phase 72O simplifies the customer-machine first screen without changing the production closed-loop backend. The goal is to make the operator UI behave more like a Codex workspace: one clear command area, one current attention item, and a compact status strip for project and server state.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` now derive `simpleServerPressureState`, `SimpleMinimalStatusCard`, and `simpleMinimalStatusCards`.
- The simplified first screen renders `Phase 72O Client Codex Minimal Workspace` through `simple-command-status-strip` and `simple-command-status-pill`.
- The strip exposes four high-signal signals: server pressure (`serverPressureScore` / `serverPressureLabel`), project progress (`simpleProgressCurrentSummary`), creation review (`simpleReviewAttentionCount`), and delivery readiness (`clientObjectiveCompletionPercent`).
- Each status pill opens the existing guarded project workbench through `openClientDetailPanel(card.panelId)`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` reduce first-screen density by hiding the startup drawer from the default Codex-style surface, compressing the goal input into a command bar, hiding secondary inbox rows by default, and keeping delivery audit actions horizontally compact.

## Boundaries

This is frontend information architecture only. It does not deploy a real OpenClaw provider, store platform credentials, configure secrets from the UI, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the first viewport keeps the command input, current attention, and compact status strip visible without horizontal overflow.
