# Phase 72U Client Delivery Blocker Deep Link

## Scope

Phase 72U keeps the Codex-like customer-machine surface simple while making the visible delivery status more actionable. The first-screen delivery status no longer opens only the broad project workbench; it now routes to the most relevant existing delivery-audit subsection for the current blocker shape.

## Implemented

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` add `simpleDeliveryFocusPanelId`.
- `simpleDeliveryFocusPanelId` routes waiting or ready delivery states to `client-project-workbench`, external dependency pressure to `client-production-delivery-audit-blocker-clearance`, runbook evidence gaps to `client-production-delivery-audit-runbooks`, operator-owned actions to `client-production-delivery-audit-operator-queue`, and remaining action pressure to `client-production-delivery-audit-next-action-plan`.
- `clientProjectDeliveryAuditPanelIds` identifies the delivery-audit subsection targets.
- `clientProjectDetailPanelIds` lets `openClientDetailPanel` expand the existing project drawer before scrolling to a delivery-audit subsection.
- `projectSupportDrawer` is opened for delivery-audit subsection targets so the deep-link destination is visible.
- `window.requestAnimationFrame` delays the final `scrollIntoView` until the details layers have opened.
- The delivery-readiness item in `simpleMinimalStatusCards` now uses `panelId: simpleDeliveryFocusPanelId`.
- The folded delivery detail action now calls `openClientDetailPanel(simpleDeliveryFocusPanelId)`.
- Existing delivery-audit sections now have stable ids: `client-production-delivery-audit-blocker-clearance`, `client-production-delivery-audit-runbooks`, `client-production-delivery-audit-next-action-plan`, `client-production-delivery-audit-operator-queue`, and `client-production-delivery-audit-openclaw-provider-handoff`.
- CSS adds `scroll-margin-top: 18px` for the delivery-audit deep-link targets.

## Boundaries

This is frontend information architecture only. It does not change delivery-audit APIs, change readiness scoring, create or clear blockers automatically, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, deploy a real OpenClaw provider, store platform credentials, configure secrets from the UI, approve records without an operator click, reject records without an operator click, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, restart services by itself, mark mock providers as ready, auto-refresh readiness, or bypass approval.

## Verification

- `npm.cmd run typecheck` in `worker_console`
- `npm.cmd run typecheck` in `worker_console_desktop`
- `pytest tests/test_worker_console_client_ux.py tests/test_commercial_operations_docs.py`
- Browser verification on `http://127.0.0.1:5181/` should confirm that the delivery-readiness status pill opens the existing project drawer and lands on the current blocker subsection without adding another visible first-screen control.
