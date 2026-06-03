# Phase 72Q Client Mode Switch Drawer

## Scope

Phase 72Q continues the customer-machine UI simplification by turning the top-level operation/knowledge page switch into a compact current-mode drawer. The knowledge base and material upload page remains reachable, but it no longer appears as a competing first-screen action beside the main operating workspace.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` replace the always-visible two-button `operator-page-tabs` section with `operator-page-mode-drawer`.
- The drawer summary shows the current mode (`pageOperations` or `pageKnowledge`) under aria label `Phase 72Q Client Mode Switch Drawer`.
- The existing `setOperatorPage("operations")` and `setOperatorPage("knowledge")` actions remain inside `operator-page-tab-actions`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` style `.operator-page-tabs > summary`, `.operator-page-tabs[open] > summary`, and `.operator-page-tab-actions` so the default first screen reads as one compact mode label instead of two primary buttons.

## Boundaries

This is frontend information architecture only. It does not remove the knowledge base page, remove material import, change upload APIs, change RAG ingestion, create documents automatically, create threads automatically, refresh conversations automatically, deploy a real OpenClaw provider, store platform credentials, configure secrets from the UI, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that `operator-page-mode-drawer` is visible as one compact summary, the default first viewport has fewer visible buttons, and opening the drawer reveals the operations and knowledge buttons.
