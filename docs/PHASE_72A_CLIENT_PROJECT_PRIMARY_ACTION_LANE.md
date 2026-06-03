# Phase 72A Client Project Primary Action Lane

Phase 72A continues the customer-machine UI simplification after Phase 71Z. The support diagnostics are now folded, but the project workbench still exposed every production button at once. This phase turns the action area into a Codex-like priority lane while keeping the complete guarded action list available in a drawer.

## Scope

- `worker_console` and `worker_console_desktop` now derive `ClientProjectPrimaryAction`, `clientProjectPrimaryActions`, and `clientProjectPrimaryReadyCount`.
- The expanded project workbench renders `client-project-primary-actions` after `client-project-support-drawer`.
- `client-project-primary-action-grid` shows the current high-signal actions for main Agent advance, material handling, workflow, output, publish, and data.
- `client-project-action-drawer` contains the previous full `client-project-actions` button list so advanced controls remain accessible without dominating the default view.
- Primary actions reuse existing guarded handlers and can also use `scrollClientProjectFocus` to open the relevant review section instead of approving records directly.
- The CSS now explicitly hides closed drawer bodies such as `client-operation-desk-drawer`, `client-home-detail-drawer`, `maintenance-drawer`, `client-project-support-drawer`, and `client-project-action-drawer` so custom display rules cannot leak folded content into the layout.

## Operator Experience

The intended expanded-workbench order is:

1. Read project counts and focus cards.
2. Open support diagnostics only when the summary says it needs review.
3. Use the priority action lane for the next likely production move.
4. Expand the full action drawer only for less common controls.
5. Continue to the guarded project sections for final approvals, output selection, publish review, and data feedback.

This keeps production capability intact while making the default screen feel closer to a focused task console than a control-room dashboard.

## Boundaries

Phase 72A is frontend information architecture only. It does not approve plans, reject plans, approve workflow selections, reject workflow selections, select output candidates, reject output candidates, create output candidates without an operator click, submit ComfyUI prompts, mutate workflow JSON, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, ingest analytics, or bypass approval.

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

- `client-project-primary-actions` appears after `client-project-support-drawer`.
- `client-project-primary-action-grid` renders six compact priority actions.
- `client-project-action-drawer` is collapsed by default and contains the full `client-project-actions` list.
- Closed drawer bodies remain hidden even when their child panels define custom `display` rules.
- The guarded project sections remain outside the action drawer.
- No primary action or drawer summary automatically approves, selects, publishes, runs OpenClaw/Playwright, or submits ComfyUI prompts without an operator click.
