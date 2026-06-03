# Phase 71W Client Creation Review Shortcuts

Phase 71W continues the customer-machine UI work after Phase 71V. The operator needs flow selection and output preview to be visible from the simple task surface, because these are frequent human decisions in the production content loop.

## Scope

- `worker_console` and `worker_console_desktop` now derive `simpleReviewCards`.
- `simple-review-strip` appears in the Codex-style task composer under the attention inbox.
- The strip contains two compact `simple-review-card` buttons: workflow selection and output preview.
- Each card summarizes existing state only: approved/pending workflow selections and selected/pending output candidates.
- Clicking either card opens the existing `client-project-workbench` detail area through `openClientDetailPanel`.

## Operator Experience

The intended flow is:

1. Type or review the operating goal in the simple task composer.
2. Check the creation review cards for workflow selection and output preview status.
3. Open the relevant card when a flow must be confirmed or an output must be previewed/selected.
4. Make the actual decision in the existing guarded project workbench.

The cards do not replace the project workbench. They make the common review path discoverable without returning to a dense dashboard.

## Boundaries

Phase 71W is frontend information architecture only. It does not approve workflow selections, reject workflow selections, select output candidates, reject output candidates, create output candidates, submit ComfyUI prompts, mutate workflow JSON, execute target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, or bypass approval.

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

Expected behavior:

- `simple-review-strip` is visible in the task composer.
- Workflow and output cards summarize the current workflow/output state.
- Clicking either card opens the existing project workbench.
- The main textarea and attention inbox remain the primary first-screen surface.
