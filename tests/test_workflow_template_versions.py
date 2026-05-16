"""Workflow template versioning tests."""

from __future__ import annotations

import pytest

from app.workflow.template_registry import WorkflowTemplateRegistryService


@pytest.mark.asyncio
async def test_template_versions_are_immutable(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowTemplateRegistryService(session)
    template = await service.create_template(
        workspace_id="workspace-template-versions",
        template_key="custom_graph",
        name="Custom Graph",
        description=None,
        category="custom",
        status="draft",
        risk_level="low",
        tags=[],
        metadata={},
        version="1",
        entry_node="start",
        graph_definition={"nodes": [{"node_key": "start"}], "edges": []},
    )

    with pytest.raises(ValueError):
        await service.create_version(
            workspace_id="workspace-template-versions",
            template_id=template.id,
            version="1",
            entry_node="start",
            graph_definition={"nodes": [{"node_key": "start"}], "edges": []},
        )

    version_two = await service.create_version(
        workspace_id="workspace-template-versions",
        template_id=template.id,
        version="2",
        entry_node="start",
        graph_definition={"nodes": [{"node_key": "start"}], "edges": []},
    )
    assert version_two.version == "2"
    assert version_two.validation_status == "valid"
