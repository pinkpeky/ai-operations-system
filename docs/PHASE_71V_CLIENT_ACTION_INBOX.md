# Phase 71V Client Action Inbox

Phase 71V continues the customer-machine UI simplification after Phase 71U. The first screen should not only be quiet; it must also tell an operator what needs attention without forcing them to open every production drawer.

## Scope

- `worker_console` and `worker_console_desktop` now derive `simpleInboxItems` from existing client state.
- `simple-action-inbox` appears inside the Codex-style task composer and shows a compact list of manual attention items.
- The inbox groups only existing evidence-backed states: pending commercial/tool approvals, failed or recoverable background tasks, generated or selected output candidates/artifacts, and active background tasks.
- `openClientDetailPanel` opens the existing drawer and target panel for each item instead of adding a new execution path.
- `client-project-workbench` now has a stable id so output-review items can jump to the existing project/output candidate area.

## Operator Experience

The intended flow is:

1. Enter a new operating goal when there is no pending work.
2. If the inbox shows approvals, recovery, outputs, or running tasks, click the relevant row.
3. The console opens the existing approval, task, output, or project detail area.
4. The operator still makes the real decision in the existing guarded panel.

This keeps the UI simple while making approvals and output selection discoverable from the main task surface.

## Boundaries

Phase 71V is frontend information architecture only. It does not approve records, reject records, retry tasks, recover tasks, select output candidates, execute target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, submit ComfyUI prompts, mutate workflow JSON, restart services, mark mock providers ready, call readiness-refresh POST endpoints, or bypass approval.

## Verification

Required checks:

```powershell
npm.cmd run typecheck # worker_console
npm.cmd run typecheck # worker_console_desktop
python -m pytest tests/test_worker_console_client_ux.py -q
```

Browser verification target:

```text
http://127.0.0.1:5181/
```

Expected behavior:

- `simple-action-inbox` is visible in the task composer.
- Pending approvals render as a compact row when present.
- Clicking an inbox item opens the existing maintenance/project detail panel.
- The main textarea remains empty and remains the primary action surface.
