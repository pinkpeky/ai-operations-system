# Phase 72D Client Attention Current Task

Phase 72D continues the customer-machine UI simplification after Phase 72C. The expanded project workbench now has a single current decision, but the first-screen attention area still behaved like a small dashboard when several approvals, recoveries, outputs, or active runs existed. This phase makes the first-screen attention area read like one current task with a short backlog behind it.

## Scope

- `worker_console` and `worker_console_desktop` now derive `simpleCurrentInboxItem`, `simpleSecondaryInboxItems`, and `simpleInboxTotalCount` from the existing `simpleInboxItems`.
- The task composer renders `simple-action-current` inside `simple-action-current-stack` before any secondary attention rows.
- `simple-action-secondary-list` keeps the remaining attention items compact and secondary.
- New copy fields `simpleInboxCurrent`, `simpleInboxMore`, and `maintenanceCurrent` describe the current task and secondary queue in both Chinese and English.
- The collapsed `maintenance-drawer` summary now includes the current attention detail through `maintenanceCurrent`, so `审批与产出` is no longer only a count.

## Operator Experience

The intended first-screen reading order is:

1. Enter or adjust the operating goal.
2. Handle the one `simple-action-current` item when attention exists.
3. Use `simple-action-secondary-list` only as a compact backlog.
4. Open `审批与产出` only when the full approval, task, output, or recovery detail is needed.
5. Continue to creation review and project progress after the immediate attention item is clear.

This keeps the customer-machine surface direct while preserving all guarded panels behind explicit operator navigation.

## Boundaries

Phase 72D is frontend interaction architecture only. It does not approve commercial approvals, approve tool approvals, reject approvals, retry failed tasks, recover failed tasks, select output candidates, create output candidates, execute target endpoints, submit ComfyUI prompts, mutate workflow JSON, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, ingest analytics, or bypass approval.

## Verification

Required checks:

```powershell
npm.cmd run typecheck # worker_console
npm.cmd run typecheck # worker_console_desktop
python -m pytest tests/test_worker_console_client_ux.py -q
python -m pytest tests/test_commercial_operations_docs.py -q
```

Browser verification target:

```text
http://127.0.0.1:5181/
```

Expected behavior:

- `simple-action-current` appears when `simpleInboxItems` has at least one item.
- The current task includes the current label, detail, category/count context, and an operator-click detail button.
- Secondary attention items render only in `simple-action-secondary-list`.
- The `maintenance-drawer` summary includes the current attention detail when attention exists.
- Full approval/output/recovery panels remain hidden until the operator opens the drawer or the current task detail.
