# Phase 72E Client Creation Current Review

Phase 72E continues the customer-machine UI simplification after Phase 72D. The first-screen attention area now has one current task, but the creation review area still showed workflow selection and output preview as equal cards. This phase makes creation review follow the same Codex-like pattern: one current creative decision first, and any other creative item as a secondary row.

## Scope

- `worker_console` and `worker_console_desktop` keep `simpleReviewCards` as the workflow/output source list.
- Both consoles add `simpleReviewStatePriority`, `simpleCurrentReviewCard`, `simpleSecondaryReviewCards`, and `simpleReviewAttentionCount`.
- `simpleReviewStatePriority` orders creation review focus as `needs-action`, then `current`, then `waiting`, then `done`.
- `simple-review-current` renders the selected current creative review item inside `simple-review-current-stack`.
- `simple-review-secondary-list` keeps the remaining workflow/output item compact and secondary.
- New copy fields `simpleReviewCurrent` and `simpleReviewMore` describe the current review and secondary creative item in Chinese and English.

## Operator Experience

The intended first-screen reading order is:

1. Enter the operating goal.
2. Clear the current attention item.
3. Handle the current creation review item in `simple-review-current`.
4. Use `simple-review-secondary-list` only when the secondary workflow/output state needs context.
5. Open the project workbench for the real guarded workflow or output decision.

This means a worker no longer has to compare two creative cards when one of them is clearly more urgent.

## Boundaries

Phase 72E is frontend interaction architecture only. It does not approve workflow selections, reject workflow selections, select output candidates, reject output candidates, create output candidates, submit ComfyUI prompts, mutate workflow JSON, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, ingest analytics, or bypass approval.

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

- `simple-review-current` appears inside `simple-review-strip`.
- The current review item is chosen by `simpleReviewStatePriority`.
- The current review item opens `client-project-workbench` only after an operator click.
- Secondary workflow/output state appears in `simple-review-secondary-list`.
- No workflow is approved, no output is selected, and no ComfyUI prompt is submitted from the first-screen review card itself.
