"""Workflow observability analytics tests."""

from __future__ import annotations

import pytest

from app.workflow.observability import WorkflowDiagnosticsService, WorkflowExecutionTraceService
from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_analytics_counts_fallback_approval_replay_and_hotspots(session) -> None:  # type: ignore[no-untyped-def]
    workflow = await WorkflowStateService(session).create_workflow_run(
        workspace_id="analytics-ws",
        source_type="test",
        current_node_key="router",
    )
    traces = WorkflowExecutionTraceService(session)
    await traces.create_trace(
        workspace_id="analytics-ws",
        workflow_run_id=workflow.id,
        node_key="router",
        event_type="fallback_triggered",
        fallback_triggered=True,
    )
    await traces.create_trace(
        workspace_id="analytics-ws",
        workflow_run_id=workflow.id,
        node_key="approval",
        event_type="approval_wait",
    )
    await traces.create_trace(
        workspace_id="analytics-ws",
        workflow_run_id=workflow.id,
        node_key="browser",
        event_type="node_failed",
    )
    await WorkflowDiagnosticsService(session).create_replay_session(workspace_id="analytics-ws", workflow_run_id=workflow.id)

    analytics = await WorkflowDiagnosticsService(session).analytics(workspace_id="analytics-ws", workflow_run_id=workflow.id)

    assert analytics["fallback_frequency"] == 1
    assert analytics["approval_wait_frequency"] == 1
    assert analytics["replay_frequency"] == 1
    assert analytics["node_failure_hotspots"]["browser"] == 1
