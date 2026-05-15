"""Workflow graph retry path tests."""

from __future__ import annotations

from app.models.workflow import WorkflowGraph, WorkflowGraphEdge, WorkflowGraphNode, WorkflowRun
from app.workflow.planner import WorkflowExecutionPlanner


def test_planner_marks_retry_edges_without_executing_loop() -> None:
    graph = WorkflowGraph(workspace_id="workspace-retry", name="retry", entry_node="start")
    graph.nodes = [
        WorkflowGraphNode(workspace_id="workspace-retry", node_key="start"),
        WorkflowGraphNode(workspace_id="workspace-retry", node_key="retry-node", node_type="retry"),
    ]
    graph.edges = [
        WorkflowGraphEdge(workspace_id="workspace-retry", source_node_key="start", target_node_key="retry-node", edge_type="retry")
    ]
    workflow = WorkflowRun(workspace_id="workspace-retry", source_type="test", status="running")

    result = WorkflowExecutionPlanner().plan_next(graph=graph, workflow=workflow, current_node="start", status="retry")

    assert result.valid is True
    assert result.next_nodes == ["retry-node"]
    assert result.retry_paths == [{"from": "start", "to": "retry-node", "matched": True}]
