# Phase 70S OpenClaw Provider Readiness Smoke

Phase 70S adds a read-only operator smoke check for the real OpenClaw provider. It verifies the worker runtime diagnostics, health, and capabilities contracts without executing `/openclaw/actions` and without performing any publish action.

## What Changed

- Added `scripts/check_openclaw_provider.py`.
- The script reads:
  - `GET /openclaw/provider-diagnostics`
  - `GET /openclaw/health`
  - `GET /openclaw/capabilities`
- The smoke passes only when diagnostics are configured, health is reachable/enabled/non-mock, capabilities are non-mock, `real_publish_submit=true`, and `publish_submit_guarded` is available.
- The report contract is `openclaw_provider_readiness_smoke`.
- The report explicitly includes `server_side_external_execution=false` and `actual_publish_performed=false`.

## Usage

```powershell
.\.venv\Scripts\python.exe scripts\check_openclaw_provider.py --base-url http://127.0.0.1:9100
.\.venv\Scripts\python.exe scripts\check_openclaw_provider.py --json --report-only
```

## Boundary

Phase 70S does not execute OpenClaw actions, does not run Playwright, does not publish, does not click final submit, does not collect credentials, does not print secrets, and does not bypass approval.

## Verification

- `tests/test_openclaw_provider_smoke.py` verifies the pass path for a real guarded provider and the block path for a mock provider.
