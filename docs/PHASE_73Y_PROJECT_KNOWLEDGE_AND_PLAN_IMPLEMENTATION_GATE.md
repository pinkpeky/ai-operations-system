# Phase 73Y Project Knowledge and Plan Implementation Gate

## Scope

Phase 73Y tightens the plan-first customer-machine workflow after Phase 73X:

- Project knowledge is treated as the current operation project's context, not as a global-only RAG bucket in the worker UI.
- An approved `OperationPlan` is a locked version. It is not edited in place; future changes must create a new plan version and pass human approval again.
- `POST /api/v1/commercial-operations/{operation_id}/operation-plans/{plan_id}/approve` now advances the Main Agent one safe step after approval so the approved plan derives reviewable copy, image, media/video, and audio-capable `ProductionTask` records.

## Implementation

- `app/api/routes/commercial_operations.py` uses one `CommercialOperationService` instance for the plan decision route. When the action is `approve`, it calls `advance_main_agent_loop()` with `enter_implementation_after_plan_approval=true`.
- `worker_console` and `worker_console_desktop` replace the visible generic RAG wording in the plan-first workbench with project-scoped knowledge wording.
- The simple plan primary action no longer sends an approved plan back to "regenerate". Once a plan is approved, the primary action opens the production task section, or advances the Main Agent if the implementation tasks are unexpectedly missing.
- The UI shows a concise lock notice: an approved plan is a frozen version, and revisions require a new version plus approval.

## Boundaries

This phase does not auto-approve production tasks, submit ComfyUI prompts, mutate workflow JSON, run OpenClaw or Playwright, publish content, collect platform analytics, or bypass approval. It only moves the project from an approved plan into reviewable implementation tasks.

## Verification

- `tests/test_operation_project_governance.py` asserts that approving an operation plan through the API derives reviewable production tasks.
- `tests/test_worker_console_client_ux.py` asserts that both customer-machine frontends expose project-scoped knowledge, locked-plan copy, and the implementation task entry.
- Real browser verification should confirm that approving a generated plan changes the workbench from plan approval into production-task review without showing "regenerate" as the approved-plan primary action.
