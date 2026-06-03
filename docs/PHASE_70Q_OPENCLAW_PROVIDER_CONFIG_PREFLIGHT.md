# Phase 70Q OpenClaw Provider Configuration Preflight

Phase 70Q makes the remaining real-publish blocker diagnosable before any social-platform action is attempted. It adds a read-only OpenClaw provider configuration preflight so operators can see whether the customer-machine worker is still mock, missing its HTTP adapter base URL, missing an API key, or ready for the existing health/capability checks.

## What Changed

- `OpenClawRuntime.provider_diagnostics()` returns the `openclaw_provider_configuration_preflight` contract without calling the provider.
- `GET /openclaw/provider-diagnostics` is exposed from both `worker_client.runtime` and standalone `worker.main`.
- The response redacts secret fields and reports `WORKER_CLIENT_OPENCLAW_PROVIDER`, `WORKER_CLIENT_OPENCLAW_BASE_URL`, and `WORKER_CLIENT_OPENCLAW_API_KEY` as required setup inputs.
- The preflight distinguishes `openclaw_provider_is_mock`, `openclaw_http_base_url_required`, `openclaw_provider_disabled`, and `openclaw_provider_configured_pending_capability_check`.
- `worker_console` and `worker_console_desktop` call `openClawProviderDiagnostics()` and show a Phase 70Q `client-openclaw-provider-diagnostics` card beside the Phase 70L publish-provider readiness gate.

## Boundary

Phase 70Q does not store platform credentials, does not configure secrets from the UI, does not launch OpenClaw, does not run Playwright, does not publish, does not click final submit, does not mark mock providers as ready, and does not bypass approval.

## Verification

- `tests/test_openclaw_worker_runtime.py` verifies `/openclaw/provider-diagnostics` for mock and missing-URL HTTP providers.
- `tests/test_worker_console_client_ux.py` verifies the customer consoles expose the Phase 70Q preflight card and local worker client method.
