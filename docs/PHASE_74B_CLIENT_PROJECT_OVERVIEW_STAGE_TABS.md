# Phase 74B Client Project Overview Stage Tabs

Phase 74B follows Phase 74A by changing the customer-machine workbench from a stacked production page into a project-first workspace with a clean side navigation and one main work area.

## Scope

- `worker_console` and `worker_console_desktop` now start on `simple-project-overview-page` when no project is selected.
- The overview page shows project count, server pressure, pending review count, current progress, and a selectable project list.
- The workbench has six large stage tabs through `simple-workspace-page-tabs`: overview, planning, text tasks, media flow, outputs, and publish.
- The old `implementation` page state is replaced by explicit `text`, `media`, `outputs`, and `publish` stages.
- `openClientProjectRecordsAndScroll` maps detail targets through `simpleWorkspacePageForTarget`, opens parent `details` drawers, and then scrolls to the correct guarded record section.
- `simple-production-guide` uses `data-guide-step={step.key}` so each stage only shows the relevant production guidance.
- `KnowledgeBasePanel` accepts `onBackToWorkspace`, giving operators a visible back path after project knowledge upload or review.
- CSS changes the customer-machine console into a reference-style two-column shell: left-side project/stage navigation and a right-side main workspace.

## Operator Contract

Operators should first choose or create a project from the overview. Inside a project, they should move through planning, text tasks, media flow, outputs, and publish as separate work surfaces instead of scanning one long page. Project knowledge upload remains available, but returning to the workbench is an explicit button rather than an implicit browser-back action.

## Non-Goals

Phase 74B does not approve plans, approve tasks, create outputs, select outputs, upload files, submit ComfyUI prompts, mutate workflow JSON, run OpenClaw, run Playwright, publish to social media, collect analytics, restart services, or bypass approval.

## Verification

- Static UI contract coverage lives in `tests/test_worker_console_client_ux.py`.
- Documentation coverage lives in `tests/test_commercial_operations_docs.py`.
- Visible frontend changes must be validated in a real browser at `http://127.0.0.1:5181/` before they are treated as complete.
