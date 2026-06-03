# Phase 70N OpenClaw HTTP Provider Contract

Phase 70N turns the OpenClaw provider boundary from a mock-only placeholder into a configurable real-provider contract. Before this phase, `OpenClawRuntime` silently downgraded every non-mock provider name to `MockOpenClawProvider`, which made production misconfiguration look like a working mock. Now non-mock provider names use an HTTP provider that either reaches a configured OpenClaw adapter or fails clearly.

## What Changed

- Added `worker_client.openclaw.http_provider.HttpOpenClawProvider`.
- `OpenClawRuntime` accepts `provider_config`.
- Non-mock provider names no longer silently downgrade to `MockOpenClawProvider`.
- Missing HTTP provider config returns `openclaw_http_base_url_required`.
- `worker_client.runtime.create_worker_client_app` passes `config.openclaw` into `OpenClawRuntime`.
- `worker.main:app` passes the compatibility worker OpenClaw config into `OpenClawRuntime`.
- `worker_client.config.load_worker_client_config` supports:
  - `WORKER_CLIENT_OPENCLAW_BASE_URL`
  - `WORKER_CLIENT_OPENCLAW_API_KEY`
  - `WORKER_CLIENT_OPENCLAW_TIMEOUT_SECONDS`
  - `WORKER_CLIENT_OPENCLAW_HEALTH_PATH`
  - `WORKER_CLIENT_OPENCLAW_CAPABILITIES_PATH`
  - `WORKER_CLIENT_OPENCLAW_ACTION_PATH`
- `WorkerClientConfig.redacted()` masks the OpenClaw `api_key`.
- `worker_client/worker_config.example.yaml` documents the HTTP provider fields.
- `docker-compose.yml`, `.env`, and `.env.example` expose the worker OpenClaw provider environment variables.

## Provider Contract

The real provider is expected to expose the same protocol shape as the local worker:

- `GET /openclaw/health`
- `GET /openclaw/capabilities`
- `POST /openclaw/actions`

Paths are configurable for adapters that use different route names.

For `publish_submit` and `publish_submit_guarded`, a successful response must include real evidence:

- `mock=false`
- `output_payload.actual_publish_performed=true` or `output_payload.real_openclaw_called=true`

If a provider returns success without that evidence, the worker response is downgraded to `success=false` with `real_publish_evidence_missing_from_provider`.

## Why It Matters

Phase 70L made the UI readiness gate visible, but a configured real provider still needed a stable runtime path. Phase 70N supplies that path without pretending a mock is real. Current deployments can remain on `provider=mock`; production deployments can switch to `WORKER_CLIENT_OPENCLAW_PROVIDER=openclaw_http` and provide `WORKER_CLIENT_OPENCLAW_BASE_URL`.

## Boundaries

Phase 70N does not ship a third-party OpenClaw server, does not store platform credentials, does not bypass verification, does not click publish from the server, does not run Playwright on the API server, does not submit ComfyUI prompts, does not mutate workflow JSON, and does not bypass approval.

## Verification

- `tests/test_openclaw_worker_runtime.py` covers mock behavior, missing HTTP provider config, successful real-submit evidence, and rejection of submit responses that lack real evidence.
- Existing Phase 70L customer-console readiness still blocks final submit when the local provider reports mock or lacks `real_publish_submit`.
