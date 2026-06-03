# Phase 68E Workflow Library Candidate Selection

Date: 2026-05-30

## Goal

Phase 68E turns the imported ComfyUI_cu130 workflow RAG library into a project-level candidate selection layer.

The operator workflow is:

1. A production task is created under an operation project.
2. The customer-machine frontend asks the server for workflow candidates.
3. The server ranks ComfyUI workflows by task goal, output type, required capability, model/runtime evidence, and risk.
4. The operator binds one candidate into a `WorkflowSelection`.
5. The normal `WorkflowSelection` approval flow continues before any runtime execution.

This phase is deliberately not an auto-generation step. It does not submit ComfyUI prompts, mutate original workflow JSON files, publish to social platforms, control accounts, or bypass operator approval.

## Implemented Scope

- `GET /api/v1/commercial-operations/{operation_id}/production-tasks/{production_task_id}/workflow-candidates`
- `CommercialOperationWorkflowCandidate`
- `CommercialOperationWorkflowCandidateListResponse`
- `CommercialOperationService.list_workflow_candidates()`
- `worker_console/src/api/commercialOperationClient.ts`
- `worker_console_desktop/src/api/commercialOperationClient.ts`
- `worker_console/src/main.tsx`
- `worker_console_desktop/src/main.tsx`
- `worker_console/src/styles.css`
- `worker_console_desktop/src/styles.css`
- `tests/test_operation_project_governance.py`
- `tests/test_worker_console_client_ux.py`

## Candidate Evidence

The server reuses the existing CU130 RAG document:

- `deployment/comfyui/commercial_ktv_workflow/cu130_runtime_workflow_rag_documents.jsonl`

Each candidate includes:

- workflow name, source, path, category, rank, and score;
- capability tags such as `image_generation`, `image_to_video`, `digital_human`, `motion_transfer`, `tts`, `music`, `video_analysis`, and `post_processing`;
- input requirements that the operator must satisfy before generation;
- expected outputs and final-selection expectations;
- runtime readiness and prompt-validation state;
- missing model references and missing executable node types;
- estimated VRAM and rough duration guidance;
- recommendation reasons and risk notes.

## Selection Boundary

The endpoint only returns candidates. It does not create a `WorkflowSelection` by itself.

The customer-machine frontend lets the operator bind a candidate. Binding creates a normal `WorkflowSelection` record and moves it to `ready_for_review`. Final operator approval still uses the existing workflow approval action.

This matters because workflow choice is a production decision, not just an Agent guess. The Agent can rank and explain, but staff still own the final choice until the system has enough verified runtime history to automate more safely.

## Project Fit

Phase 68E is project-wide, not KTV-only.

The same endpoint can support:

- image/poster/first-frame workflows;
- video and audio-video workflows;
- digital-human workflows;
- audio, TTS, and music workflows;
- reference-video analysis workflows;
- post-processing workflows.

KTV digital-human video is one media case inside the broader commercial operation closed loop.

## Frontend Behavior

The customer-machine frontend now shows a `Phase 68E Workflow Library Candidate Selection` panel inside the project workbench.

Operators can:

- refresh workflow candidates for the next task requiring workflow selection;
- inspect capabilities, runtime readiness, risk notes, VRAM estimate, and recommendation reasons;
- bind a candidate into `WorkflowSelection`;
- still record a placeholder workflow when the RAG library is unavailable or the real workflow must be chosen manually.

## Boundaries

- No automatic ComfyUI prompt submission is added.
- No original workflow JSON is overwritten.
- No workflow graph materialization is added in this phase.
- No output candidate is generated in this phase.
- No OpenClaw, Playwright, or social-platform publishing execution is added.
- No approval bypass is added.

## Verification

- Backend syntax compile must pass for the service, schemas, and route.
- `tests/test_operation_project_governance.py` must verify the `workflow-candidates` endpoint and candidate evidence.
- `tests/test_worker_console_client_ux.py` must verify web/desktop client methods, frontend state, candidate panel classes, and documentation.
- Web and Desktop typecheck/build must pass.

## Next Step

Phase 68F should connect approved workflow selections to output candidate registration and preview management. It should still keep runtime submission guarded: selected workflows and produced assets must be inspectable before publish packaging or customer-machine execution.
