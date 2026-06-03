# Phase 72H Client Single Focus Context Drawer

Phase 72H continues the customer-machine UI simplification after Phase 72G. The first screen now keeps the operating goal and current attention item as the only always-visible work objects. Creation review and project progress remain available, but they move into a compact project-context drawer so the default surface reads like a Codex-style command console instead of a small dashboard.

## Scope

- `worker_console` and `worker_console_desktop` add copy fields `simpleProjectContextTitle`, `simpleProjectContextSummary`, `simpleProjectContextReview`, and `simpleProjectContextProgress`.
- The existing `simple-review-strip` and `simple-progress-card` move into `simple-project-context-drawer`.
- `simple-project-context-body` preserves the current creation-review and progress controls without changing their guarded actions.
- The drawer summary shows a compact review count plus current stage summary.
- CSS hides `simple-project-context-body` while the drawer is closed and removes duplicated margins/borders from the nested review/progress blocks.

## Operator Experience

The intended default reading order is:

1. See the selected startup context.
2. Enter or adjust the operating goal.
3. Handle the current attention item.
4. Open project context only when flow selection, output preview, or stage progress is needed.
5. Open maintenance details only for deeper approval/output/recovery work.

This keeps flow selection, output preview, and project progress discoverable without making them compete with the main command input and current task.

## Boundaries

Phase 72H is frontend interaction architecture only. It does not create tasks, approve approvals, reject approvals, retry failed work, select output candidates, create output candidates, submit ComfyUI prompts, mutate workflow JSON, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, ingest analytics, or bypass approval.

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

- `simple-project-context-drawer` appears after `simple-action-inbox`.
- `simple-review-strip` and `simple-progress-card` are inside `simple-project-context-body`.
- `simple-project-context-body` is hidden while the drawer is closed.
- The default first screen keeps the goal input and current attention item as the primary visible work path.
