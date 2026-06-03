# Phase 74E Client Inner Panel Alignment

Date: 2026-06-02

Phase 74E follows Phase 74D after browser and operator feedback showed that the outer shell matched `docs/operation_project_ui_design_preview.html`, but the inner workbench still retained the old stacked information design.

## Scope

- `worker_console` and `worker_console_desktop` now mark the customer-machine workbench body with `data-simple-inner-layout="phase-74e-preview-panels"`.
- The visible inner workbench is now a strict reference-style `simple-reference-stage-workspace` rather than the previous stacked panels.
- The stage surface now has seven independent tabs: overview, planning, text, media, outputs, publish, and `feedback` data return.
- Planning uses `simple-reference-chat-surface` with a bounded chat message scroll area plus project knowledge and plan approval context cards.
- Text, media, outputs, publish, and feedback use bounded list panels: `simple-reference-copy-card`, `simple-reference-material-card`, `simple-reference-workflow-card`, `simple-reference-review-card`, `simple-reference-publish-card`, `simple-reference-feedback-card`, and `simple-reference-data-list`.
- The workbench now has fixed-height rules (`height: min(900px, calc(100vh - 96px))`) and page/list overflow handling so long content scrolls inside the relevant panel like an AI chat workspace instead of stretching the whole page.
- The old `simple-conversation-workspace`, `simple-plan-rag-row`, `simple-production-guide`, `simple-approval-workbench`, `simple-approval-output-preview`, `simple-production-details-drawer`, and `simple-production-details-body` remain in the code only as compatibility anchors and hidden fallback surfaces for existing deep-link handlers.

## Boundaries

This phase is customer-machine frontend inner-panel design alignment only. It does not create plans without operator input, approve plans or tasks, upload files to ComfyUI, submit ComfyUI prompts, mutate workflow JSON, select output candidates without an operator click, run OpenClaw, run Playwright, publish to social media, collect analytics, restart services, or bypass approval.

## Verification

- `npm run typecheck` in `worker_console`
- `npm run typecheck` in `worker_console_desktop`
- `python -m pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py -q`
- Real browser verification should cover `http://127.0.0.1:5181/` across planning, media, outputs, publish, and feedback, checking that each reference page has bounded internal scrolling and that the old stacked panels are not the primary visible UI.
