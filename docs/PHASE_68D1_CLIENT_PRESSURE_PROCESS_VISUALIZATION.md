# Phase 68D1 Client Server Pressure and Project Process Visualization

Date: 2026-05-30

## Goal

Phase 68D1 adds the missing customer-machine visibility layer before the workflow-library work in Phase 68E. The client frontend should not only show approvals and output records; operators must also see whether the server is under pressure and where the operation project currently sits in the closed loop.

This phase is a frontend and client-API integration step. It does not change project governance rules, does not submit ComfyUI prompts, and does not publish to any social platform.

## Implemented Scope

- `worker_console/src/api/comfyuiRuntimeClient.ts`
- `worker_console_desktop/src/api/comfyuiRuntimeClient.ts`
- `worker_console/src/main.tsx`
- `worker_console_desktop/src/main.tsx`
- `worker_console/src/styles.css`
- `worker_console_desktop/src/styles.css`
- `tests/test_worker_console_client_ux.py`

## Server Pressure Sources

The customer-machine frontend now reads existing formal server endpoints:

- `GET /api/v1/task-scheduler/health`
- `GET /api/v1/comfyui-runtime/health`
- `GET /api/v1/comfyui-runtime/diagnostics`
- `GET /api/v1/comfyui-runtime/queue`
- `POST /api/v1/comfyui-runtime/video-resource-plans`

The pressure panel combines:

- scheduler status, active task count, and recovered task count;
- task-run backlog, failed/recoverable tasks, and completed tasks;
- commercial execution run load already loaded by the operation project workbench;
- ComfyUI queue running and pending counts;
- video GPU admission status, selected GPU, free VRAM, and blocking reasons when the guarded resource plan can read them;
- project review backlog for plans, materials, tasks, workflow selections, output candidates, final selections, publish packages, and metric snapshots.

## Project Process Visualization

The project process rail converts the Phase 68B/68C/68D project objects into a left-to-right operator view:

1. OperationPlan
2. ProjectMaterial
3. ProductionTask
4. WorkflowSelection
5. OutputCandidate
6. FinalSelection
7. PublishPackage
8. PlatformMetricSnapshot
9. OptimizationDecision

Each step is derived from real object states:

- `done` when the relevant approved, selected, completed, published, or approved metric record exists;
- `needs-action` when a ready-for-review or selectable object exists;
- `current` when the stage has started but has not reached review/completion;
- `waiting` when the stage has no usable record yet.

## Operator Behavior

The customer-machine workbench now gives staff three immediate answers:

- Can the server continue work now, or should we wait?
- Which part of the project needs human action?
- Is the project blocked by approval backlog, task queue pressure, ComfyUI queue pressure, or video GPU admission?

This keeps the operator workflow project-first rather than video-only. KTV/digital-human video remains one possible media flow inside the wider commercial operation project.

## Boundaries

- No automatic ComfyUI prompt submission is added.
- No ComfyUI workflow mutation is added.
- No real social publishing is added.
- No account control, OpenClaw execution, Playwright execution, captcha bypass, proxy pool, approval bypass, runtime mutation, service restart, or package rebuild is added.
- The video GPU admission read is an existing guarded planning endpoint, used for visibility only.

## Verification

- Web and Desktop typecheck must pass.
- Web and Desktop production build must pass.
- `tests/test_worker_console_client_ux.py` must confirm the server pressure panel, project process rail, ComfyUI runtime client, and documentation markers.

## Next Step

Phase 68E should still focus on the workflow library and workflow selection layer. It should turn the ComfyUI RAG workflow documents, workflow graph requirements, material inputs, expected outputs, estimated runtime, VRAM needs, and validation state into structured workflow candidates that staff can inspect and choose.
