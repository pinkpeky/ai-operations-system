"""Workflow graph fallback path tests."""

from __future__ import annotations

from app.models.workflow import WorkflowGraph, WorkflowGraphEdge, WorkflowGraphNode, WorkflowRun
from app.workflow.planner import WorkflowExecutionPlanner


def test_planner_routes_failure_to_fallback_edge() -> None:
    graph = WorkflowGraph(workspace_id="workspace-fallback", name="fallback", entry_node="start")
    graph.nodes = [
        WorkflowGraphNode(workspace_id="workspace-fallback", node_key="start"),
        WorkflowGraphNode(workspace_id="workspace-fallback", node_key="fallback-node", node_type="no_op"),
    ]
    graph.edges = [
        WorkflowGraphEdge(
            workspace_id="workspace-fallback",
            source_node_key="start",
            target_node_key="fallback-node",
            edge_type="fallback",
        )
    ]
    workflow = WorkflowRun(workspace_id="workspace-fallback", source_type="test", status="running")

    result = WorkflowExecutionPlanner().plan_next(graph=graph, workflow=workflow, current_node="start", status="failure")

    assert result.next_nodes == ["fallback-node"]
    assert result.fallback_paths == [{"from": "start", "to": "fallback-node", "matched": True}]
