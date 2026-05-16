"""Workflow checkpoint tests."""

from __future__ import annotations

import pytest

from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_workflow_checkpoints_are_append_only(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowStateService(session)
    workflow = await service.create_workflow_run(workspace_id="workspace-checkpoint", source_type="task")
    first = await service.create_checkpoint(
        workspace_id="workspace-checkpoint",
        workflow_run_id=workflow.id,
        checkpoint_name="first",
        checkpoint_type="auto",
    )
    second = await service.create_checkpoint(
        workspace_id="workspace-checkpoint",
        workflow_run_id=workflow.id,
        checkpoint_name="second",
        checkpoint_type="manual",
    )

    checkpoints = await service.list_checkpoints(workspace_id="workspace-checkpoint", workflow_run_id=workflow.id)

    assert [item.id for item in checkpoints] == [first.id, second.id]
