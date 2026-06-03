# Phase 71U Client Codex Focus Shell

Phase 71U continues the customer-machine UI simplification requested after Phase 71T. The operator console should feel like a focused Codex-style work surface: the task composer is the primary page, runtime status is a thin companion strip, and diagnostic material stays behind explicit drawers.

## Scope

- `worker_console` and `worker_console_desktop` now mark the local runtime summary with `client-runtime-companion`.
- The former large `operator-home` card is reduced to `client-runtime-summary`, a compact status row with language, runtime, heartbeat, and refresh actions.
- Worker connection cards, production workspace alignment, quick links, recovery steps, and boundary notes remain available inside the collapsed `client-home-detail-drawer`.
- `simple-focus-strip` is rendered as an inline status line instead of four visually heavy cards.
- `simple-progress-card` is reduced to a light progress section inside the task composer rather than a second prominent card.

## Operator Experience

The intended default first screen is:

1. Choose task or knowledge mode.
2. Type the operating goal in the main task box.
3. Use quick-start chips only when they help.
4. Read the inline project status and progress.
5. Open runtime diagnostics only when the compact status row is blocked or stale.

This keeps the customer-machine console useful for ordinary workers while preserving the production evidence and recovery controls required for delivery.

## Boundaries

Phase 71U is frontend information architecture and visual hierarchy only. It does not change backend contracts, deploy a real OpenClaw provider, store platform credentials, configure secrets, approve records, execute target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, restart services, mark mock providers ready, call readiness-refresh POST endpoints, or bypass approval.

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

- the main task composer remains above runtime diagnostics
- `client-runtime-companion` appears as a compact row
- `client-home-detail-drawer` is collapsed by default
- `simple-focus-strip` is an inline status line
- `simple-progress-card` is visually secondary to the textarea
