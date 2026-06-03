# Phase 71T Client Codex Minimal UI

Phase 71T continues the customer-machine usability work after Phase 71S. The product requirement is no longer just "fold the advanced panels"; the first screen must feel like a Codex-style operator surface: one clear task input, short quick-start chips, visible project progress, and a small pending-work summary.

## Scope

- `worker_console` and `worker_console_desktop` now mark the task surface with `codex-simple-client`.
- The main input starts empty so the operator sees the actual goal placeholder instead of a demo task.
- `simple-template-row` is a horizontal quick-start strip instead of a stacked grid on narrow screens.
- `simple-focus-strip` shows only four essential counters: approvals, active work, recovery, and artifacts.
- `maintenance-drawer` no longer opens automatically when approvals or failures exist; it exposes a count through `data-has-work` and stays collapsed until the operator chooses to inspect it.
- The page shell width, topbar spacing, and task card styling are reduced so the first viewport prioritizes the task composer and project progress.

## Operator Experience

The intended default path is:

1. Confirm the runtime badges are green.
2. Pick a quick-start chip only if useful.
3. Type the operating goal in the main textarea.
4. Send the task or run it in the background.
5. Use the progress card and pending-work summary to decide whether to open approvals, outputs, or recovery details.

The low-frequency engineering surfaces remain present behind drawers. They are no longer the first thing a normal operator has to parse.

## Boundaries

Phase 71T is frontend information architecture and visual hierarchy only. It does not change backend contracts, deploy a real OpenClaw provider, store platform credentials, configure secrets, approve records, execute target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, restart services, mark mock providers ready, or bypass approval.

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

Expected first viewport:

- compact Worker title and runtime badges
- task/knowledge tabs
- `客户机任务工作台`
- empty textarea with the operating-goal placeholder
- four compact focus counters
- horizontal quick-start chips
- project progress visible without opening engineering drawers
