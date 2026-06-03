# Phase 74C Client Reference UI Browser Fixes

Date: 2026-06-02

Phase 74C follows Phase 74B by hardening the customer-machine workbench against the issues found during real browser operation at `http://127.0.0.1:5181/`.

## Scope

- `worker_console` and `worker_console_desktop` now keep the reference-style two-column customer workbench stable with a fixed left rail and a right main workspace that starts at the top of the card.
- Stage pages keep `simple-production-details-drawer` available instead of hiding it, so `查看详情` / detail actions open the current stage production flow instead of jumping into older maintenance sections.
- `openSimpleProductionDetailsAndScroll` routes stage-detail buttons to the compact production-flow drawer, while lower-level record drawers remain available for maintenance and audit.
- The operations page and knowledge page remain mounted behind `operator-page-host` containers with `hidden={operatorPage !== ...}`. This preserves the selected project and current page when the operator opens RAG upload/review and clicks `返回工作台`.
- Browser verification covered project overview, entering a project, stage tab switching, stage production-detail opening, and knowledge return context preservation.

## Boundaries

This phase is frontend information architecture and browser-tested interaction repair only. It does not approve plans or tasks, upload files to ComfyUI, submit ComfyUI prompts, mutate workflow JSON, select outputs without an operator click, run OpenClaw, run Playwright publishing, publish to social media, collect analytics, or bypass approval.

## Verification

- `python -m pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py -q`
- `npm run typecheck` in `worker_console`
- `npm run typecheck` in `worker_console_desktop`
- Real browser verification in the in-app browser at `http://127.0.0.1:5181/`
