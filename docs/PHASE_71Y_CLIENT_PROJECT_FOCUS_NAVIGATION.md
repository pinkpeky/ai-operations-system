# Phase 71Y Client Project Focus Navigation

Phase 71Y continues the customer-machine UI simplification after Phase 71X. The first screen is now simpler, but the expanded project workbench still contains many production-loop sections. This phase adds a focused navigation strip so operators can jump directly to the project area they need.

## Scope

- `worker_console` and `worker_console_desktop` now derive `clientProjectFocusCards`.
- The project workbench renders `client-project-focus-strip`, `client-project-focus-grid`, and `client-project-focus-card`.
- Focus cards summarize approvals, materials, ComfyUI workflow selection, output preview, publish packages, and data feedback.
- Each card scrolls to an existing guarded section through `scrollClientProjectFocus`.
- Existing project sections now have stable anchors such as `client-project-section-plans`, `client-project-section-materials`, `client-project-section-workflows`, `client-project-section-outputs`, and `client-project-section-publish`.

## Operator Experience

The intended expanded-workbench flow is:

1. Open the project workbench from the simple task surface.
2. Read the compact project focus strip.
3. Click the card for the current human decision: approval, material, workflow, output, publishing, or data.
4. Complete the real decision in the existing guarded section.

The strip is navigation and summarization only. It does not replace review controls, publish controls, ComfyUI submission controls, or metric pullback controls.

## Boundaries

Phase 71Y is frontend information architecture only. It does not approve plans, reject plans, approve workflow selections, reject workflow selections, select output candidates, reject output candidates, create output candidates, submit ComfyUI prompts, mutate workflow JSON, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, configure providers, store secrets, restart services, mark mock providers ready, call readiness-refresh POST endpoints, ingest analytics, or bypass approval.

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

- `client-project-focus-strip` appears near the top of the expanded project workbench.
- Six `client-project-focus-card` buttons are rendered.
- Clicking a focus card scrolls to the existing guarded project section.
- No card automatically approves, selects, publishes, runs OpenClaw/Playwright, or submits ComfyUI prompts.
