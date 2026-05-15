"""Workflow failure hotspot diagnostics tests."""

from __future__ import annotations

import pytest

from app.workflow.observability import WorkflowDiagnosticsService, WorkflowExecutionTraceService
from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_failure_hotspots_are_grouped_by_node_key(session) -> None:  # type: ignore[no-untyped-def]
    workflow = await WorkflowStateService(session).create_workflow_run(workspace_id="hotspot-ws", source_type="test")
    traces = WorkflowExecutionTraceService(session)
    for _ in range(2):
        await traces.create_trace(
            workspace_id="hotspot-ws",
            workflow_run_id=workflow.id,
            node_key="fragile-node",
            event_type="node_failed",
        )
    await traces.create_trace(
        workspace_id="hotspot-ws",
        workflow_run_id=workflow.id,
        node_key="other-node",
        event_type="node_failed",
    )

    summary = await traces.summarize_trace(workspace_id="hotspot-ws", workflow_run_id=workflow.id)
    analytics = await WorkflowDiagnosticsService(session).analytics(workspace_id="hotspot-ws", workflow_run_id=workflow.id)

    assert summary["failure_hotspots"]["fragile-node"] == 2
    assert analytics["node_failure_hotspots"]["other-node"] == 1
