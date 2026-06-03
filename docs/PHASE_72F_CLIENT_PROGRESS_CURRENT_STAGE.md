# Phase 72F Client Progress Current Stage

Phase 72F continues the customer-machine UI simplification after Phase 72E. The first screen now has a current attention item and a current creation review item, but the project progress block still read like a small stage board on narrow screens. This phase makes project progress follow the same single-focus rule: one current stage first, with a compact stage trail below it.

## Scope

- `worker_console` and `worker_console_desktop` keep `goalStatusStages` and `simpleCurrentStage` as the source of truth for project progress.
- Both consoles add `simpleProgressDoneCount` and `simpleProgressCurrentSummary` so the progress header can show a compact completed/total count.
- New copy fields `simpleProgressCurrent` and `simpleProgressTrail` label the current stage focus and the compact stage trail.
- `simple-progress-current` renders the current stage, stage detail, status label, and suggested action.
- `simple-progress-stages` remains visible, but now behaves as a compact horizontal trail instead of expanding into a tall stage list on narrow screens.

## Operator Experience

The intended first-screen reading order is:

1. Enter the operating goal.
2. Clear the current attention item.
3. Handle the current creation review item.
4. Read the current project stage in `simple-progress-current`.
5. Use `simpleProgressTrail` only as quick context for where the project is in the broader loop.

This makes the first screen consistently task-focused without hiding progress state.

## Boundaries

Phase 72F is frontend interaction architecture only. It does not create tasks, approve approvals, reject approvals, retry failed work, select output candidates, create output candidates, submit ComfyUI prompts, mutate workflow JSON, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, ingest analytics, or bypass approval.

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

- `simple-progress-current` appears inside `simple-progress-card`.
- The header shows `simpleProgressCurrentSummary` as completed/total.
- The current stage shows the selected `simpleCurrentStage` label, detail, status, and suggested action.
- `simple-progress-stages` stays available as a compact horizontal trail.
- No project action, approval, publish, ComfyUI submission, OpenClaw action, or Playwright action is executed from the progress card itself.
