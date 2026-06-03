# Phase 72C Client Project Current Decision Focus

Phase 72C continues the customer-machine UI simplification after Phase 72B. The project workbench already hides full records and secondary actions behind drawers, but the decision queue still asked the operator to scan several cards at once. This phase makes the customer UI closer to a Codex-style operating surface: one current decision is prominent, the allowed action is direct, and deeper records stay one click away.

## Scope

- `worker_console` and `worker_console_desktop` keep `ClientProjectDecisionCard`, but each card now carries `primaryLabel`, `primaryDisabled`, `onPrimary`, optional `secondaryLabel`, optional `secondaryDisabled`, and optional `onSecondary`.
- Both consoles derive `clientProjectCurrentDecision` from the first pending decision and `clientProjectSecondaryDecisionCards` from the remaining compact cards.
- The expanded project workbench renders `client-project-decision-focus` with `projectDecisionCurrent`, the current record detail, status, and direct approve/select/ready action.
- `client-project-decision-focus-actions` exposes the primary action, the guarded reject action when available, and `projectDecisionDetail` for opening the exact record section through `openClientProjectRecordsAndScroll`.
- Secondary decisions remain visible in `client-project-decision-grid`, but only after the current focus item.
- The previous full project records still live inside `client-project-records-drawer`; the full action set still lives inside `client-project-action-drawer`.

## Operator Experience

The intended expanded-workbench reading order is:

1. Confirm the project focus summary.
2. Use the primary action lane for production progress.
3. Handle the single current decision in `client-project-decision-focus`.
4. Open details only when evidence needs review.
5. Use secondary cards as a short backlog, not as the main screen.
6. Open the records drawer only for full evidence, exceptions, or audit history.

This keeps the first screen direct and low-noise while preserving the human review boundary.

## Boundaries

Phase 72C is frontend interaction architecture only. It does not create plans, approve plans without a click, reject plans without a click, approve materials without a click, reject materials without a click, approve tasks without a click, reject tasks without a click, approve workflow selections without a click, reject workflow selections without a click, select output candidates without a click, reject output candidates without a click, approve final selections without a click, reject final selections without a click, approve publish packages without a click, reject publish packages without a click, approve metric snapshots without a click, reject metric snapshots without a click, create output candidates, submit ComfyUI prompts, mutate workflow JSON, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, ingest analytics, or bypass approval.

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

- `client-project-decision-focus` appears only when there is at least one project-level decision.
- The focus item shows `projectDecisionCurrent`, one primary action, optional reject action, and `projectDecisionDetail`.
- Clicking the detail action opens `client-project-records-drawer` and scrolls to the existing guarded section.
- Secondary decision cards remain compact and do not replace the current focus item.
- No default view exposes the full project grid or full action row until the operator opens the relevant drawer.
