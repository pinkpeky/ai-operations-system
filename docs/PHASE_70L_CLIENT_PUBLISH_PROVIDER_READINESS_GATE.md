# Phase 70L Client Publish Provider Readiness Gate

Phase 70L makes the remaining real-publish blocker explicit on the customer machine. Phase 70K made `/openclaw/*` available on the standalone worker, and Phase 70J prevents mock submit evidence from counting as success. Phase 70L now checks whether the local OpenClaw provider is actually capable of final publishing before the operator can enter the guarded submit path.

## What Changed

- `worker_console` and `worker_console_desktop` import `LocalWorkerOpenClawHealth` and `LocalWorkerOpenClawCapabilities`.
- Both customer-machine consoles expose `refreshPublishProviderReadiness`.
- Both consoles call `localWorkerClient.openClawHealth` and `localWorkerClient.openClawCapabilities`.
- The publish execution panel now shows `Phase 70L Client Publish Provider Readiness Gate`.
- The action marker is `phase_70l_client_publish_provider_readiness_gate`.
- The panel renders `client-publish-provider-readiness-status` and `client-publish-provider-readiness`.
- The readiness check requires `real_publish_submit=true`.
- The readiness check requires `publish_submit_guarded` to be available.
- The readiness check requires `mock=false` on the local provider.
- If the provider is not ready, the console records a customer-machine `needs_operator` publish execution status with `client_publish_provider_readiness_gate`.
- The controlled blocker remains `real_publish_provider_not_configured`.

## Why It Matters

The system can now distinguish three states that previously looked similar to an operator:

- the local worker route contract is missing;
- the OpenClaw route contract exists but only a mock provider is configured;
- a real non-mock provider is available for guarded final submit.

That distinction matters for the production closed loop. A project can be fully prepared, dry-run evidence can exist, and the final submit bridge can be visible, but the loop still cannot be considered 100% production-complete until the customer machine has a non-mock provider that can perform `publish_submit_guarded`.

## Boundaries

Phase 70L does not implement a real OpenClaw provider, does not publish from the server, does not log in automatically, does not collect credentials, does not bypass verification, does not click the real publish button from the server, does not submit ComfyUI prompts, does not mutate workflow JSON, does not restart services, and does not rebuild client packages.

## Verification

- `tests/test_worker_console_client_ux.py` checks the Phase 70L customer-console markers, states, readiness button, and CSS.
- `tests/test_commercial_operations_docs.py` checks this document plus the phase index, runtime, status, and foundation docs.
- TypeScript checks for `worker_console` and `worker_console_desktop` verify the new local OpenClaw readiness types.
