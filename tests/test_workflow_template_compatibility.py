"""Workflow template compatibility checks."""

from __future__ import annotations

from app.workflow.template_registry import WorkflowTemplateCompatibilityService


def test_template_compatibility_accepts_supported_graph() -> None:
    result = WorkflowTemplateCompatibilityService().check(
        graph_definition={
            "nodes": [{"node_key": "start", "node_type": "no_op"}, {"node_key": "finish", "node_type": "workflow_checkpoint"}],
            "edges": [{"source_node_key": "start", "target_node_key": "finish", "edge_type": "success"}],
        },
        entry_node="start",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        risk_level="low",
    )

    assert result["compatible"] is True
    assert result["validation_status"] == "valid"


def test_template_compatibility_rejects_unsupported_node_type() -> None:
    result = WorkflowTemplateCompatibilityService().check(
        graph_definition={"nodes": [{"node_key": "start", "node_type": "comfyui_node"}], "edges": []},
        entry_node="start",
        input_schema={},
        output_schema={},
        risk_level="low",
    )

    assert result["compatible"] is False
    assert "node_type:comfyui_node" in result["missing_capabilities"]
