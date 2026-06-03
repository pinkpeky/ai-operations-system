# Phase 71S Client Operator UI Simplification

## Objective

Phase 71S responds to the production usability gap found on the customer-machine console at `http://127.0.0.1:5181/`: the backend and workflow surface had grown functionally rich, but the first screen exposed too many engineering panels, Phase labels, and low-frequency controls to an ordinary operator.

The goal is a Codex-like default surface: status, next step, goal input, and progress first; engineering details only when the operator intentionally expands them.

## Implemented Scope

- `worker_console` and `worker_console_desktop` keep the existing operational capabilities but fold them behind explicit details drawers.
- `production-runtime-strip` is now a collapsed readiness drawer by default, keeping workspace/worker/heartbeat/scheduler detail available without occupying the first screen.
- `client-home-detail-drawer` folds quick links, recovery guidance, and boundary notes under advanced help.
- `client-task-workbench` is converted to an ordered operator flow: `simple-operator-workbench`, `simple-goal-box`, `simple-progress-card`, `operator-detail-drawer`, then the detailed production loop.
- `client-operation-desk-drawer` wraps the large product-operation desk, digital-human progress, guided actions, Agent/Skill orchestration, execution queue, publish loop, and delivery details.
- The visible default action remains the goal input and approved start/background run buttons; no endpoint contract changed.

## Operator Experience

Default screen order:

1. Compact runtime badges in the top bar.
2. Page switcher.
3. A single operating goal input.
4. Common task chips and start/background actions.
5. Current progress.
6. Optional plan/status details.
7. Optional full production loop, workstation runtime details, and diagnostics.

This keeps approvals, outputs, workflow selection, OpenClaw/Playwright handoff, video/digital-human progress, logs, and maintenance panels available while preventing them from dominating the first view.

## Boundaries

Phase 71S is frontend information architecture only. It does not call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure secrets, submit ComfyUI prompts, approve records, mutate workflows, restart services, mark mock providers ready, or bypass approval.

Client-machine live validation can be deferred because this phase changes default visibility and layout ordering, not the customer-machine execution contract.

## Files

- `worker_console/src/main.tsx`
- `worker_console/src/styles.css`
- `worker_console_desktop/src/main.tsx`
- `worker_console_desktop/src/styles.css`
- `tests/test_worker_console_client_ux.py`

## Verification

Expected verification:

- Static UX contract: `pytest tests/test_worker_console_client_ux.py -q`
- Web typecheck: `cd worker_console && npm.cmd run typecheck`
- Desktop typecheck: `cd worker_console_desktop && npm.cmd run typecheck`
- Browser visual smoke on `http://127.0.0.1:5181/` after reload.
