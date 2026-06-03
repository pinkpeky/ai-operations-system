# Phase 71X Client First Screen Priority

Phase 71X continues the customer-machine UI simplification after Phase 71W. The client console should behave like a simple operator command surface: the worker sees the current input, then the decisions that need attention, then the broader project progress.

## Scope

- `worker_console` and `worker_console_desktop` now place `simple-action-inbox` immediately after the main goal input.
- `simple-review-strip` follows the inbox so workflow selection and output preview are visible before broader status.
- `simple-progress-card` now follows the action and review surfaces instead of occupying the first slot under the input.
- The DOM order and CSS `order` values are aligned so keyboard, screen-reader, and visual priority all match.
- The top shell, goal textarea, template chips, and inbox rows use tighter first-screen heights so the action inbox and creation review can fit more reliably in the first viewport.

## Operator Experience

The intended first-screen order is:

1. Enter or review the operating goal.
2. Check approvals, recovery, output review, or active-run attention in `simple-action-inbox`.
3. Check creative decisions in `simple-review-strip`.
4. Read the broader project stage in `simple-progress-card` only after the actionable items.

This keeps the interface closer to a Codex-style work surface: fewer dashboard blocks at the top, clearer next action, and technical detail still available in the existing drawers.

## Boundaries

Phase 71X is frontend information architecture only. It does not approve plans, reject plans, approve workflow selections, reject workflow selections, select output candidates, reject output candidates, create output candidates, submit ComfyUI prompts, mutate workflow JSON, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, or bypass approval.

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

- The first screen shows the task input first.
- `simple-action-inbox` appears before `simple-review-strip`.
- `simple-review-strip` appears before `simple-progress-card`.
- Clicking review cards still opens `client-project-workbench`; it does not auto-approve or execute anything.
