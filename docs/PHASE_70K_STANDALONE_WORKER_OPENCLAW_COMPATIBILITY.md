# Phase 70K Standalone Worker OpenClaw Compatibility

Phase 70K closes the runtime gap between the customer-machine consoles and the actual process currently serving port 9100. The production server was running `worker.main:app` in standalone browser-worker compatibility mode, which exposed `/local/status` but did not expose the `/openclaw/*` routes used by Phase 70H and Phase 70J.

## What Changed

- `worker.main:app` now exposes `GET /openclaw/health`.
- `worker.main:app` now exposes `GET /openclaw/capabilities`.
- `worker.main:app` now exposes `POST /openclaw/actions`.
- The standalone app reuses the customer-machine `OpenClawRuntime`.
- The default provider remains `MockOpenClawProvider`.
- The compatibility marker remains `standalone_browser_worker_compatibility`.
- `publish_submit_guarded` is available as a protocol action, but the mock provider returns `real_publish_provider_not_configured`.

## Why It Matters

`worker_console` and `worker_console_desktop` call the local worker API directly. Without these routes, the Phase 70H dry-run bridge and Phase 70J submit bridge could render correctly but fail at runtime with 404 from the real customer-machine process.

Phase 70K makes the current standalone process match the worker_client OpenClaw route contract while preserving the same safety boundary: mock submit actions do not count as true publishing, and real OpenClaw/Playwright publishing still requires a non-mock customer-machine provider.

## Boundaries

This phase does not implement a real OpenClaw provider, does not publish from the server, does not log in automatically, does not collect credentials, does not bypass verification, does not click the real publish button from the server, does not submit ComfyUI prompts, does not mutate workflow JSON, and does not restart services by itself.

## Verification

- `tests/test_worker_main_local_compatibility.py` checks `/openclaw/health`, `/openclaw/capabilities`, and `/openclaw/actions` on `worker.main:app`.
- `tests/test_openclaw_worker_runtime.py` checks the worker_client runtime path.
- `tests/test_worker_console_client_ux.py` checks the customer-machine UI bridge.
- `tests/test_commercial_operations_docs.py` checks this document plus the phase index, runtime, status, and foundation docs.
