"""Workflow Replay Center session tests."""

from __future__ import annotations

import pytest

from app.workflow.observability import WorkflowDiagnosticsService, WorkflowExecutionTraceService
from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_replay_session_is_metadata_only_and_traced(session) -> None:  # type: ignore[no-untyped-def]
    state = WorkflowStateService(session)
    workflow = await state.create_workflow_run(workspace_id="replay-session-ws", source_type="test", current_node_key="node-a")
    checkpoint = await state.create_checkpoint(
        workspace_id="replay-session-ws",
        workflow_run_id=workflow.id,
        checkpoint_name="before-node-a",
    )

    replay = await WorkflowDiagnosticsService(session).create_replay_session(
        workspace_id="replay-session-ws",
        workflow_run_id=workflow.id,
        replay_source_checkpoint_id=checkpoint.id,
        replay_mode="metadata_only",
        initiated_by="tester",
    )
    traces = await WorkflowExecutionTraceService(session).list_traces(workspace_id="replay-session-ws", workflow_run_id=workflow.id)

    assert replay.replay_status == "completed"
    assert replay.replay_metadata["no_runtime_reexecution"] is True
    assert [trace.event_type for trace in traces] == ["replay_started", "replay_completed"]


@pytest.mark.asyncio
async def test_replay_execution_mode_is_blocked(session) -> None:  # type: ignore[no-untyped-def]
    workflow = await WorkflowStateService(session).create_workflow_run(workspace_id="replay-block-ws", source_type="test")

    with pytest.raises(ValueError, match="not enabled"):
        await WorkflowDiagnosticsService(session).create_replay_session(
            workspace_id="replay-block-ws",
            workflow_run_id=workflow.id,
            replay_mode="replay_execution",
        )
