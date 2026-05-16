"""Workflow run model tests."""

from __future__ import annotations

import pytest

from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_workflow_run_workspace_isolation(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowStateService(session)
    workflow = await service.create_workflow_run(workspace_id="workspace-a", source_type="conversation", source_id="m1")

    assert await service.get_workflow_run(workspace_id="workspace-a", workflow_run_id=workflow.id) is not None
    assert await service.get_workflow_run(workspace_id="workspace-b", workflow_run_id=workflow.id) is None
