"""Workflow graph model/service tests."""

from __future__ import annotations

import pytest

from app.workflow.services import WorkflowGraphService, WorkflowStateService


@pytest.mark.asyncio
async def test_workflow_graph_service_creates_valid_graph(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowGraphService(session)

    graph = await service.create_graph(
        workspace_id="workspace-graph",
        name="simple graph",
        entry_node="start",
        nodes=[
            {"node_key": "start", "node_type": "no_op"},
            {"node_key": "finish", "node_type": "workflow_checkpoint"},
        ],
        edges=[{"source_node_key": "start", "target_node_key": "finish", "edge_type": "success"}],
    )

    loaded = await service.get_graph(workspace_id="workspace-graph", graph_id=graph.id)
    validation = await service.validate_graph(workspace_id="workspace-graph", graph_id=graph.id)

    assert loaded is not None
    assert loaded.entry_node == "start"
    assert len(loaded.nodes) == 2
    assert validation.valid is True


@pytest.mark.asyncio
async def test_workflow_state_records_graph_node_metadata(session) -> None:  # type: ignore[no-untyped-def]
    graph = await WorkflowGraphService(session).create_graph(
        workspace_id="workspace-graph-state",
        name="state graph",
        entry_node="start",
        nodes=[{"node_key": "start"}, {"node_key": "finish"}],
        edges=[{"source_node_key": "start", "target_node_key": "finish", "edge_type": "success"}],
    )
    service = WorkflowStateService(session)
    workflow = await service.create_workflow_run(
        workspace_id="workspace-graph-state",
        source_type="test",
        workflow_graph_id=graph.id,
        graph_execution=True,
        current_node_key="start",
    )
    step = await service.start_step(
        workspace_id="workspace-graph-state",
        workflow_run_id=workflow.id,
        step_index=0,
        step_name="Start",
        step_type="no_op",
        node_key="start",
    )
    await service.complete_step(workspace_id="workspace-graph-state", workflow_step_id=step.id)
    refreshed = await service.require_workflow_run(workspace_id="workspace-graph-state", workflow_run_id=workflow.id)

    assert refreshed.current_node_key == "start"
    assert refreshed.planned_next_nodes == ["finish"]
