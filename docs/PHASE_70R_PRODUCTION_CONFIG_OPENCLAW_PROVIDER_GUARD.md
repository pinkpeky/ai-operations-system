# Phase 70R Production Config OpenClaw Provider Guard

Phase 70R connects the OpenClaw provider preflight to the formal production configuration audit. The system should not pass a production deployment check when the server says OpenClaw is enabled but the customer-machine worker is still mock, missing its HTTP adapter URL, or missing an adapter API key.

## What Changed

- `Settings` now reads `WORKER_CLIENT_OPENCLAW_ENABLED`, `WORKER_CLIENT_OPENCLAW_PROVIDER`, `WORKER_CLIENT_OPENCLAW_BASE_URL`, and `WORKER_CLIENT_OPENCLAW_API_KEY`.
- `Settings.production_config_findings()` and `scripts/check_production_config.py` emit blocking findings for:
  - `WORKER_CLIENT_OPENCLAW_ENABLED=false` while `OPENCLAW_ENABLED=true`
  - `WORKER_CLIENT_OPENCLAW_PROVIDER=mock`
  - `WORKER_CLIENT_OPENCLAW_BASE_URL` missing for `openclaw_http`
  - `WORKER_CLIENT_OPENCLAW_API_KEY` missing or placeholder for `openclaw_http`
- `deployment/profiles/production-server/env.template` now includes the real worker OpenClaw provider variables.
- `deployment/profiles/production-server/profile.json` includes the worker OpenClaw provider variables in `required_env`.

## Boundary

Phase 70R does not create, install, or launch an OpenClaw adapter. It does not store credentials in code, print secrets, run Playwright, publish, click final submit, mark mock providers as production-ready, or bypass approval.

## Verification

- `tests/test_production_config.py` verifies formal production config passes with a real `openclaw_http` worker provider and fails when the provider is mock or missing base URL/API key.
