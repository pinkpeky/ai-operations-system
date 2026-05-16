"""WorkflowStateService behavior tests."""

from __future__ import annotations

import pytest

from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_workflow_state_service_records_steps_checkpoints_and_memory(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowStateService(session)

    workflow = await service.create_workflow_run(
        workspace_id="workspace-workflow-service",
        source_type="test",
        source_id="source-1",
        status="running",
        variables={"topic": "AI ops"},
        context={"phase": "45"},
    )
    step = await service.start_step(
        workspace_id="workspace-workflow-service",
        workflow_run_id=workflow.id,
        step_index=0,
        step_name="Collect context",
        step_type="message",
        input_payload={"message": "hello"},
    )
    completed_step = await service.complete_step(
        workspace_id="workspace-workflow-service",
        workflow_step_id=step.id,
        output_payload={"summary": "done"},
    )
    checkpoint = await service.create_checkpoint(
        workspace_id="workspace-workflow-service",
        workflow_run_id=workflow.id,
        checkpoint_name="after-step",
        checkpoint_type="manual",
    )
    snapshot = await service.create_memory_snapshot(
        workspace_id="workspace-workflow-service",
        workflow_run_id=workflow.id,
        memory_type="task_context",
        summary="Workflow memory",
        memory_payload={"step_id": str(step.id)},
    )

    assert completed_step.status == "completed"
    assert checkpoint.workflow_run_id == workflow.id
    assert snapshot.workflow_run_id == workflow.id
    assert (await service.list_steps(workspace_id="workspace-workflow-service", workflow_run_id=workflow.id))[0].id == step.id
    assert (await service.list_memory_snapshots(workspace_id="workspace-workflow-service", workflow_run_id=workflow.id))[0].id == snapshot.id


@pytest.mark.asyncio
async def test_workflow_pause_resume_and_restore_checkpoint(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowStateService(session)
    workflow = await service.create_workflow_run(
        workspace_id="workspace-workflow-restore",
        source_type="test",
        variables={"count": 1},
        context={"state": "original"},
    )
    checkpoint = await service.create_checkpoint(
        workspace_id="workspace-workflow-restore",
        workflow_run_id=workflow.id,
        checkpoint_name="manual",
        checkpoint_type="manual",
    )
    await service.update_variables(workspace_id="workspace-workflow-restore", workflow_run_id=workflow.id, variables={"count": 2})
    paused = await service.pause_workflow(workspace_id="workspace-workflow-restore", workflow_run_id=workflow.id)
    paused_status = paused.status
    resumed = await service.resume_workflow(workspace_id="workspace-workflow-restore", workflow_run_id=workflow.id)
    resumed_status = resumed.status
    restored = await service.restore_checkpoint(workspace_id="workspace-workflow-restore", checkpoint_id=checkpoint.id)

    assert paused_status == "paused"
    assert resumed_status == "running"
    assert restored.variables["count"] == 1
