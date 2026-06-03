# Phase 70J Publish Submit Evidence Gate

Phase 70J adds the customer-machine publish submit evidence gate after Phase 70I. Dry-run evidence is necessary but not enough for a production publish result: a successful result now also needs a customer-machine submit trail that proves the final publish action happened outside the server boundary.

## Contract

- The submit bridge marker is `client_publish_execution_submit_bridge`.
- The backend submit gate contract is `client_publish_execution_submit_result_gate`.
- Missing submit evidence blocks successful result capture with `client_publish_submit_evidence_required_before_result_capture`.
- Verified capture returns `client_publish_submit_evidence_verified_before_result_capture`.
- The controlled next action can return `record_client_publish_submit_bridge_status`.
- The customer consoles call the local worker with `publish_submit_guarded`.
- Submit evidence must include `actual_publish_performed=true` and `operator_final_submit_confirmed=true`.
- Mock OpenClaw providers return `real_publish_provider_not_configured` and are not counted as verified submit evidence.

## Runtime Behavior

`CommercialOperationService._publish_execution_client_submit_gate` scans `publish_execution_status_history` for `client_publish_execution_submit_bridge` or `Phase 70J Client Publish Submit Bridge`. The gate only verifies a succeeded customer-machine status when the evidence says the publish action was actually performed, the operator confirmed final submit, and the provider was not mock.

`worker_console` and `worker_console_desktop` expose `runPublishExecutionSubmitFromClient`, `publishExecutionSubmitStatus`, `publishExecutionSubmitLoading`, and `publishExecutionSubmitResult`. The UI button uses `phase_70j_client_publish_submit_bridge` and calls `localWorkerClient.executeOpenClawAction` with `publish_submit_guarded`.

The local mock OpenClaw provider still supports the protocol, but it returns `success=false`, `actual_publish_performed=false`, and `real_publish_provider_not_configured` for submit actions. That keeps the production boundary honest until a real customer-machine OpenClaw provider is configured.

## Boundaries

This phase does not run OpenClaw or Playwright on the server, click through accounts from the server, collect credentials, bypass login/verification, publish from the server, submit ComfyUI prompts, mutate workflow JSON, restart services, or rebuild client packages. It only defines and verifies the customer-machine submit evidence needed before accepting a successful publish result.

## Verification

- `tests/test_operation_project_governance.py` blocks `/execution-result` until both dry-run and submit gates are verified.
- `tests/test_openclaw_worker_runtime.py` proves the mock provider exposes `publish_submit_guarded` but returns `real_publish_provider_not_configured`.
- `tests/test_worker_console_client_ux.py` checks the customer-machine submit bridge UI.
- `tests/test_commercial_operations_docs.py` checks this document plus the phase index, runtime, status, and foundation docs.
