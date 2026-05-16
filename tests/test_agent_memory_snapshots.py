"""Agent memory snapshot tests."""

from __future__ import annotations

import pytest

from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_agent_memory_snapshots_filter_by_type(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowStateService(session)
    workflow = await service.create_workflow_run(workspace_id="workspace-memory", source_type="conversation")
    await service.create_memory_snapshot(
        workspace_id="workspace-memory",
        workflow_run_id=workflow.id,
        memory_type="conversation_summary",
        summary="Conversation summary",
    )
    await service.create_memory_snapshot(
        workspace_id="workspace-memory",
        workflow_run_id=workflow.id,
        memory_type="tool_result",
        summary="Tool result",
    )

    snapshots = await service.list_memory_snapshots(
        workspace_id="workspace-memory",
        workflow_run_id=workflow.id,
        memory_type="tool_result",
    )

    assert len(snapshots) == 1
    assert snapshots[0].memory_type == "tool_result"
