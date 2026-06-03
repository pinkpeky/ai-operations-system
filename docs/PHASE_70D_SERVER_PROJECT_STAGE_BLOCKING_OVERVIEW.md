# Phase 70D Server Project Stage Blocking Overview

Phase 70D adds a server-side project stage and blocker overview to the Admin Dashboard Commercial Ops page. The intervention queue is useful, but maintainers also need a broader dispatch view across every operation: how many projects are in plan review, active delivery, watch, stale, intervention, or escalation states, and which blockers should be opened first.

## Scope

- `admin_dashboard` derives `productionClosedLoopProjectStageCounts`.
- `admin_dashboard` derives `productionClosedLoopProjectBlockerRows`.
- `admin_dashboard` derives `productionClosedLoopProjectBlockedCount`.
- `admin_dashboard` derives `productionClosedLoopProjectStageOverview`.
- The Commercial Ops page renders `Phase 70D Server Project Stage Blocking Overview`.
- The overview shell uses `commercial-project-stage-overview`.
- Stage cards use `commercial-project-stage-grid`.
- Blocker shortcuts use `commercial-project-blocker-list`.
- Blocker shortcuts select the corresponding operation in the existing detail panel.

## Boundary

This phase is server visibility and navigation only. It does not execute target endpoints, send reminders, send messages, call OpenClaw, call Playwright, publish from the server, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, download models, install workflows, upload files, or rebuild client packages.

## Verification

- `tests/test_admin_dashboard_commercial_operations.py::test_admin_dashboard_exposes_commercial_operations_page`
- `tests/test_commercial_operations_docs.py::test_commercial_operations_foundation_covers_phase_70d_server_project_stage_blocking_overview`
- `tests/test_commercial_operations_docs.py::test_phase_70d_server_project_stage_blocking_overview_is_documented`
