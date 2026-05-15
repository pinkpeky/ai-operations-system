"""Workflow execution trace service tests."""

from __future__ import annotations

import pytest

from app.workflow.observability import WorkflowExecutionTraceService
from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_workflow_step_lifecycle_writes_execution_traces(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowStateService(session)
    workflow = await service.create_workflow_run(workspace_id="trace-ws", source_type="test")
    step = await service.start_step(
        workspace_id="trace-ws",
        workflow_run_id=workflow.id,
        step_index=0,
        step_name="Trace node",
        step_type="tool_call",
        node_key="trace-node",
        input_payload={"target": "example"},
    )

    await service.complete_step(
        workspace_id="trace-ws",
        workflow_step_id=step.id,
        output_payload={"ok": True},
    )

    traces = await WorkflowExecutionTraceService(session).list_traces(workspace_id="trace-ws", workflow_run_id=workflow.id)

    assert [trace.event_type for trace in traces] == ["node_started", "node_completed", "planner_decision"]
    assert traces[0].input_snapshot["target"] == "example"
    assert traces[1].output_snapshot["ok"] is True
