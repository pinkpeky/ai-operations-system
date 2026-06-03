# Phase 74D Client Design Preview Alignment

Date: 2026-06-02

Phase 74D follows Phase 74C by applying `docs/operation_project_ui_design_preview.html` to the real customer-machine workbench instead of leaving it as a static preview.

## Scope

- `worker_console` and `worker_console_desktop` now expose a preview-inspired shell around the real project workbench:
  - `simple-design-sidebar-brand` for the `AI Ops Workbench` left rail identity.
  - `simple-design-topbar` for the operator greeting, search/command entry, and compact avatar.
  - `simple-design-project-switcher` for the current project context, current stage, platform, pending count, and project knowledge count.
  - `simple-design-action-hero` for the current primary operator action.
  - `simple-resource-page-links` for project-scoped material, RAG knowledge, workflow candidates, approvals, and local runtime entry points.
- The visual shell now uses the preview-width customer-machine workbench, a fixed left rail, a right-side main workspace, softer panels, colored overview metrics, and a three-column project overview grid.
- Existing project selection, project archive-delete, plan generation, plan approval, production task routing, ComfyUI workflow selection, output registration, publish package handling, knowledge page return, and production detail routing remain wired to the existing handlers.

## Boundaries

This phase is customer-machine frontend information architecture and design alignment only. It does not create operation plans automatically without operator input, approve plans or tasks, upload files to ComfyUI, submit ComfyUI prompts, mutate workflow JSON, select output candidates without an operator click, run OpenClaw, run Playwright, publish to social media, collect analytics, restart services, or bypass approval.

## Verification

- `npm run typecheck` in `worker_console`
- `npm run typecheck` in `worker_console_desktop`
- `python -m pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py -q`
- Real browser verification should cover `http://127.0.0.1:5181/` against the preview structure: left rail, project cards, stage navigation, project context card, primary action card, resource links, and stage-tab navigation.
