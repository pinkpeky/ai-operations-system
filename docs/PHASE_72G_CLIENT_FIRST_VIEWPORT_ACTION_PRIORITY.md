# Phase 72G Client First Viewport Action Priority

Phase 72G continues the customer-machine UI simplification after Phase 72F. The first screen now has current attention, creation review, and progress focus cards, but the focus stats and quick-start templates still consumed the top of the first viewport. This phase folds those startup helpers into a context drawer so the current task appears earlier without removing the operator's shortcuts.

## Scope

- `worker_console` and `worker_console_desktop` add copy fields `simpleContextTitle` and `simpleContextSummary`.
- The former always-visible `simple-focus-strip` and `simple-template-row` now live inside `simple-start-drawer`.
- `simple-start-drawer-body` contains the existing stats and quick-start templates, preserving the same controls and selected-template behavior.
- The drawer summary shows the selected template and a compact context label while keeping the full stats/templates one click away.
- CSS hides `simple-start-drawer-body` while the drawer is closed and keeps the summary responsive on narrow screens.

## Operator Experience

The intended first-screen reading order is:

1. See the client task title and selected startup context.
2. Enter or adjust the operating goal.
3. Handle the current attention item.
4. Handle the current creation review item.
5. Read the current project stage.
6. Open startup context only when stats or a different quick-start template is needed.

This keeps useful shortcuts available, but makes the current operator action the dominant first-viewport object.

## Boundaries

Phase 72G is frontend interaction architecture only. It does not create tasks, approve approvals, reject approvals, retry failed work, select output candidates, create output candidates, submit ComfyUI prompts, mutate workflow JSON, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, ingest analytics, or bypass approval.

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

- `simple-start-drawer` appears before `simple-goal-box`.
- `simple-focus-strip` and `simple-template-row` are inside `simple-start-drawer-body`.
- `simple-start-drawer-body` is hidden while the drawer is closed.
- The current attention card appears higher in the first viewport than before.
- Opening startup context reveals the same stats and quick-start templates without triggering execution.
