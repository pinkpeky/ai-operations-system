# Phase 68F Output Candidate Delivery

Date: 2026-05-30

## Goal

Phase 68F connects approved project work to reviewable production output without turning the customer-machine frontend into an unsafe runtime executor.

The intended operator workflow is:

1. A `ProductionTask` is approved or started.
2. If the task requires ComfyUI or another production workflow, a `WorkflowSelection` is approved first.
3. The customer-machine frontend asks for an `output-prep-package`.
4. The operator registers a real generated file path, browser-preview URL, or reviewed text output.
5. The server creates an `OutputCandidate`, marks it ready for review, and keeps the existing `FinalSelection` approval gate before publish packaging.

This phase is a delivery-contract step. It does not submit ComfyUI prompts, overwrite workflow JSON, upload files to ComfyUI, publish to social platforms, control accounts, run OpenClaw/Playwright, restart services, mutate runtime configuration, or bypass operator approval.

## Implemented Scope

- `GET /api/v1/commercial-operations/{operation_id}/production-tasks/{production_task_id}/output-prep-package`
- `CommercialOperationOutputPrepPackage`
- `CommercialOperationService.get_output_prep_package()`
- Output readiness checks for approved/started production tasks and approved workflow selections
- Output candidate blueprint, required inputs, expected outputs, review gates, storage policy, existing `OutputCandidate` records, and existing `FinalSelection` records
- `worker_console/src/api/commercialOperationClient.ts`
- `worker_console_desktop/src/api/commercialOperationClient.ts`
- `worker_console/src/main.tsx`
- `worker_console_desktop/src/main.tsx`
- `worker_console/src/styles.css`
- `worker_console_desktop/src/styles.css`
- `tests/test_operation_project_governance.py`
- `tests/test_worker_console_client_ux.py`

## Output Prep Package

The `output-prep-package` endpoint is read-only. It gives the customer-machine frontend enough context to register a produced asset safely:

- operation id and production task id;
- `readiness_status` and `blocking_reasons`;
- task summary and workflow requirement state;
- approved `WorkflowSelection` id when present;
- candidate blueprint for `OutputCandidate` creation;
- required inputs and expected outputs;
- review gates that must remain human-approved;
- currently registered output candidates;
- existing final selections;
- storage and preview policy.

This is deliberately separate from ComfyUI execution. The server can describe what is needed for the output, but the operator still decides when a generated asset is good enough to register.

## Customer-Machine Behavior

The customer-machine project workbench now includes a `Phase 68F Output Candidate Delivery` panel.

Operators can:

- refresh the output prep package for the next eligible production task;
- see whether the task is blocked by missing approval or missing workflow selection;
- register a produced image, video, audio, or copy/text output;
- preserve local Windows paths as source references;
- use HTTP, data, blob, or app-relative URLs as previewable browser resources;
- create a ready `OutputCandidate` for human preview and selection.

The UI also keeps the prior project workbench capabilities for `OperationPlan`, `ProjectMaterial`, `ProductionTask`, `WorkflowSelection`, `OutputCandidate`, `FinalSelection`, `PublishPackage`, and `PlatformMetricSnapshot`.

## Review Boundary

`OutputCandidate` registration is not final approval.

After a candidate is registered:

- staff still preview and select/reject/archive candidates;
- a `FinalSelection` must still be created and approved;
- publish package creation remains downstream of approved final selections;
- social publishing and account control remain outside this phase.

This keeps the closed loop honest: generation, candidate registration, final selection, copy packaging, publishing, and metric analysis stay observable as separate steps.

## Project Fit

Phase 68F is project-wide, not KTV-only.

It supports:

- image/poster/first-frame output registration;
- video and audio-video output registration;
- audio/TTS/music output registration;
- copy/script/text output registration;
- digital-human output as part of the wider video/audio-video flow;
- later automation where a runtime adapter can register outputs through the same `OutputCandidate` contract.

## Verification

- Backend syntax compile must pass for service, schemas, and routes.
- `tests/test_operation_project_governance.py` must verify the `output-prep-package` contract and output readiness behavior.
- `tests/test_worker_console_client_ux.py` must verify web/desktop client methods, frontend state, panel classes, and documentation.
- Web and Desktop typecheck/build must pass.

## Next Step

The next project slice should connect selected final outputs to publish-package preparation and platform copy review. That step should still be approval-gated and should not run OpenClaw/Playwright or real social publishing until the client execution contract is explicit.
