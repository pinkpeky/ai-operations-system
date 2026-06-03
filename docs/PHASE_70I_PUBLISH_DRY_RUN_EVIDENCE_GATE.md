# Phase 70I Publish Dry-Run Evidence Gate

Phase 70I hardens the customer-machine publish lane after Phase 70H. A successful `capture_publish_execution_result` call is now blocked unless the publish package already contains customer-machine OpenClaw/Playwright dry-run evidence recorded in `publish_execution_status_history`.

## Contract

- The dry-run gate contract is `client_publish_execution_dry_run_result_gate`.
- Missing evidence blocks successful result capture with `client_publish_openclaw_dry_run_required_before_result_capture`.
- Verified evidence adds the review marker `client_publish_openclaw_dry_run_verified_before_result_capture`.
- The accepted dry-run marker is the Phase 70H status metadata contract `client_publish_execution_dry_run_bridge`.
- The recognized execution-log marker is `Phase 70H Client Publish OpenClaw Dry-Run Bridge`.
- The controlled next action can return `record_client_publish_openclaw_dry_run_bridge_status` when a package was marked succeeded without the required dry-run trail.

## Runtime Behavior

`CommercialOperationService._publish_execution_client_dry_run_gate` scans the latest status and `publish_execution_status_history`. It treats a `running` or `succeeded` status with `client_publish_execution_dry_run_bridge` metadata, Phase 70H metadata, or the visible Phase 70H execution-log marker as verified dry-run evidence.

`CommercialOperationService.capture_publish_execution_result` allows failure capture without the dry-run gate, so operators can still record failed customer-machine attempts. It requires the gate only when `publish_succeeded=true`, because only that path marks the package published and can move the project toward metric analysis.

## Boundaries

This phase does not run OpenClaw or Playwright on the server, click the real publish button, log in automatically, collect credentials, bypass verification, publish from the server, submit ComfyUI prompts, mutate workflow JSON, restart services, or rebuild client packages. It only validates customer-machine evidence before accepting a successful publish result.

## Verification

- `tests/test_operation_project_governance.py` blocks `/execution-result` before Phase 70H dry-run evidence exists, records `client_publish_execution_dry_run_bridge`, then verifies the successful result path.
- `tests/test_commercial_operations_docs.py` checks this document plus `docs/COMMERCIAL_OPERATIONS_FOUNDATION.md`, `docs/CURRENT_RUNTIME.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/PROJECT_STATUS.md`, and `docs/PHASE_INDEX.md`.
