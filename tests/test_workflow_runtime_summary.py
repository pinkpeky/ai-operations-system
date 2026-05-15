"""Workflow runtime summary tests."""

from __future__ import annotations

import pytest

from app.workflow.observability import WorkflowDiagnosticsService
from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_runtime_summary_includes_trace_checkpoint_and_replay_counts(session) -> None:  # type: ignore[no-untyped-def]
    state = WorkflowStateService(session)
    workflow = await state.create_workflow_run(workspace_id="summary-ws", source_type="test")
    step = await state.start_step(
        workspace_id="summary-ws",
        workflow_run_id=workflow.id,
        step_index=0,
        step_name="Summarize",
        step_type="no_op",
    )
    await state.complete_step(workspace_id="summary-ws", workflow_step_id=step.id, output_payload={"done": True})
    await state.create_checkpoint(workspace_id="summary-ws", workflow_run_id=workflow.id, checkpoint_name="summary")
    await WorkflowDiagnosticsService(session).create_replay_session(workspace_id="summary-ws", workflow_run_id=workflow.id)

    summary = await WorkflowDiagnosticsService(session).generate_runtime_summary(
        workspace_id="summary-ws",
        workflow_run_id=workflow.id,
    )

    assert summary["step_count"] == 1
    assert summary["checkpoint_count"] == 1
    assert summary["replay_session_count"] == 1
    assert summary["trace_summary"]["trace_count"] >= 5
