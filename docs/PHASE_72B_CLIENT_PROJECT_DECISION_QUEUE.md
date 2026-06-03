# Phase 72B Client Project Decision Queue

Phase 72B continues the customer-machine UI simplification after Phase 72A. The project workbench now has a compact priority action lane, but the detailed project records still made the default view feel like a long dashboard. This phase adds a decision queue so operators see the current human-review items first, while the full approval/output records stay available in a collapsed drawer.

## Scope

- `worker_console` and `worker_console_desktop` now derive `ClientProjectDecisionCard`, `clientProjectDecisionCandidates`, `clientProjectDecisionCards`, and `clientProjectDecisionTotalCount`.
- The expanded project workbench renders `client-project-decision-lane` after the priority actions and before the full action drawer.
- `client-project-decision-grid` shows up to six pending decision cards across plans, materials, production tasks, workflow selections, output candidates, final selections, publish packages, and metric snapshots.
- `openClientProjectRecordsAndScroll` opens `client-project-records-drawer` and scrolls to the existing guarded section such as `client-project-section-workflows` or `client-project-section-outputs`.
- The previous `client-project-grid` is now inside `client-project-records-drawer`, keeping approval buttons, output selection buttons, publish controls, and metric confirmation controls available without exposing the whole record table by default.

## Operator Experience

The intended expanded-workbench order is:

1. Read project focus and support summaries.
2. Use the priority action lane for the next production move.
3. Review the decision queue to see what needs human judgement.
4. Click a decision card to open the record drawer at the exact guarded section.
5. Use the original approval, selection, publish, or metric controls inside that section.

This keeps the human-in-the-loop boundary intact while reducing first-read complexity.

## Boundaries

Phase 72B is frontend information architecture only. It does not approve plans, reject plans, approve workflow selections, reject workflow selections, select output candidates, reject output candidates, approve final selections, approve publish packages, approve metrics, create output candidates, submit ComfyUI prompts, mutate workflow JSON, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, ingest analytics, or bypass approval.

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

- `client-project-decision-lane` appears after `client-project-primary-actions`.
- `client-project-records-drawer` is collapsed by default and contains `client-project-grid`.
- The project grid and boundary are hidden while the records drawer is closed.
- Clicking a decision card opens the records drawer and scrolls to the matching guarded section.
- No decision card automatically approves, selects, publishes, runs OpenClaw/Playwright, or submits ComfyUI prompts.
