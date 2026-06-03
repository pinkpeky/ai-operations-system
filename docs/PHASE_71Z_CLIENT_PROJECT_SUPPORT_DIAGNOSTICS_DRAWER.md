# Phase 71Z Client Project Support Diagnostics Drawer

Phase 71Z continues the customer-machine UI simplification after Phase 71Y. The project workbench now has focus navigation, but support diagnostics still took too much default space. This phase folds support diagnostics behind one drawer so operators can stay focused on the current production decision.

## Scope

- `worker_console` and `worker_console_desktop` now derive `clientProjectSupportAttention` and `clientProjectSupportStatus`.
- The expanded project workbench renders `client-project-support-drawer` after the focus strip.
- The drawer uses `data-has-attention` so blocked runtime, intervention, closed-loop readiness, or server pressure states remain visible from the summary row.
- The drawer contains `client-project-support-grid`, which holds the existing support panels:
  - `client-production-intervention-panel`
  - `client-production-runtime-panel`
  - `client-production-closed-loop-readiness`
  - `client-production-next-action-panel`
  - `client-production-action-audit-panel`
  - `client-server-pressure-panel`
  - `client-project-process-panel`
- The existing action buttons and guarded project sections remain outside the support drawer.

## Operator Experience

The intended expanded-workbench order is:

1. Read project counts and focus cards.
2. Use the support diagnostics drawer only when runtime, intervention, readiness, pressure, or process context is needed.
3. Continue to the actual guarded action buttons and project sections for approvals, workflow review, output selection, publishing, and data feedback.

This keeps diagnostic detail available without making it the default reading path.

## Boundaries

Phase 71Z is frontend information architecture only. It does not approve plans, reject plans, approve workflow selections, reject workflow selections, select output candidates, reject output candidates, create output candidates, submit ComfyUI prompts, mutate workflow JSON, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, ingest analytics, or bypass approval.

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

- `client-project-support-drawer` appears directly after `client-project-focus-strip`.
- `client-project-support-grid` contains the support panels only after the drawer is opened.
- The drawer summary remains visible and carries `data-has-attention`.
- The action buttons and guarded project sections remain visible outside the support drawer.
- No drawer action automatically approves, selects, publishes, runs OpenClaw/Playwright, or submits ComfyUI prompts.
