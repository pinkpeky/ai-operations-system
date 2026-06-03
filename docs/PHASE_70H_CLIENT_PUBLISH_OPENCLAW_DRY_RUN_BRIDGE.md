# Phase 70H Client Publish OpenClaw Dry-Run Bridge

Phase 70H turns the approved publish-package handoff into a client-machine dry-run bridge. The customer-machine consoles can now call the local worker OpenClaw endpoint for a non-submitting `publish_dry_run`, then write the dry-run result back into the server publish execution status trail.

## Scope

- `worker_console` and `worker_console_desktop` expose `runPublishExecutionDryRunFromClient`.
- Both consoles keep `publishExecutionDryRunStatus`.
- Both consoles keep `publishExecutionDryRunLoading`.
- Both consoles keep `publishExecutionDryRunResult`.
- Both consoles call `localWorkerClient.executeOpenClawAction`.
- The local worker clients type `LocalWorkerOpenClawActionResponse`.
- The local worker clients expose `openClawHealth`.
- The local worker clients expose `openClawCapabilities`.
- The local worker clients expose `executeOpenClawAction`.
- The local worker clients call `/openclaw/actions`, `/openclaw/health`, and `/openclaw/capabilities`.
- The dry-run action type is `publish_dry_run`.
- The server status metadata uses `client_publish_execution_dry_run_bridge`.
- The visible UI marker is `Phase 70H Client Publish OpenClaw Dry-Run Bridge`.
- The action button uses `phase_70h_client_publish_openclaw_dry_run_bridge`.
- The status text uses `client-publish-dry-run-status`.
- The result card uses `client-publish-dry-run-result`.

## Boundary

This phase executes only a customer-machine dry-run bridge and records the result. It does not click the real platform publish button, does not log in automatically, does not bypass verification, does not collect credentials, does not send messages, does not publish from the server, does not run server-side OpenClaw or Playwright, does not submit ComfyUI prompts, does not mutate workflow JSON, and does not restart services.

## Verification

- `tests/test_worker_console_client_ux.py::test_worker_consoles_expose_phase_70h_client_publish_openclaw_dry_run_bridge`
- `tests/test_openclaw_worker_runtime.py::test_worker_client_runtime_openclaw_routes`
- `tests/test_commercial_operations_docs.py::test_commercial_operations_foundation_covers_phase_70h_client_publish_openclaw_dry_run_bridge`
- `tests/test_commercial_operations_docs.py::test_phase_70h_client_publish_openclaw_dry_run_bridge_is_documented`
