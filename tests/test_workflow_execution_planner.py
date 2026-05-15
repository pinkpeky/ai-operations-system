"""Workflow graph planner tests."""

from __future__ import annotations

from app.models.workflow import WorkflowGraph, WorkflowGraphEdge, WorkflowGraphNode, WorkflowRun, WorkflowStep
from app.workflow.planner import WorkflowExecutionPlanner


def _graph() -> WorkflowGraph:
    graph = WorkflowGraph(workspace_id="workspace-planner", name="planner", entry_node="start")
    graph.nodes = [
        WorkflowGraphNode(workspace_id="workspace-planner", node_key="start", node_type="no_op"),
        WorkflowGraphNode(workspace_id="workspace-planner", node_key="review", node_type="approval_gate"),
        WorkflowGraphNode(workspace_id="workspace-planner", node_key="publish", node_type="tool_call"),
        WorkflowGraphNode(workspace_id="workspace-planner", node_key="fallback", node_type="no_op"),
    ]
    graph.edges = [
        WorkflowGraphEdge(
            workspace_id="workspace-planner",
            source_node_key="start",
            target_node_key="review",
            edge_type="conditional",
            condition_expression="workflow.variables.requires_review == true",
        ),
        WorkflowGraphEdge(workspace_id="workspace-planner", source_node_key="review", target_node_key="publish", edge_type="success"),
        WorkflowGraphEdge(workspace_id="workspace-planner", source_node_key="review", target_node_key="fallback", edge_type="fallback"),
    ]
    return graph


def test_planner_validates_and_routes_conditionally() -> None:
    graph = _graph()
    workflow = WorkflowRun(
        workspace_id="workspace-planner",
        source_type="test",
        variables={"requires_review": True},
        status="running",
    )

    planner = WorkflowExecutionPlanner()
    validation = planner.validate_graph(graph=graph)
    result = planner.plan_next(graph=graph, workflow=workflow, current_node="start", status="success")

    assert validation.valid is True
    assert validation.entry_node == "start"
    assert result.next_nodes == ["review"]
    assert result.condition_results[0]["matched"] is True


def test_planner_exposes_latest_step_output_conditions() -> None:
    graph = _graph()
    graph.edges[0].condition_expression = "step.output.score == 7"
    workflow = WorkflowRun(workspace_id="workspace-planner", source_type="test", status="running")
    step = WorkflowStep(
        workspace_id="workspace-planner",
        step_index=0,
        step_name="start",
        step_type="no_op",
        node_key="start",
        status="completed",
        output_payload={"score": 7},
    )

    result = WorkflowExecutionPlanner().plan_next(
        graph=graph,
        workflow=workflow,
        completed_steps=[step],
        current_node="start",
        status="success",
    )

    assert result.next_nodes == ["review"]
