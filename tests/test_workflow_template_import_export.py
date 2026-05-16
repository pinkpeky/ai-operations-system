"""Workflow template import/export tests."""

from __future__ import annotations

import pytest

from app.workflow.template_registry import WorkflowTemplateRegistryService


@pytest.mark.asyncio
async def test_template_export_and_import_dry_run(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowTemplateRegistryService(session)
    templates = await service.list_templates(workspace_id="workspace-template-import")
    template = next(item for item in templates if item.template_key == "content_generation_graph")

    exported = await service.export_template(workspace_id="workspace-template-import", template_id=template.id)
    dry_run = await service.import_template(
        workspace_id="workspace-template-import",
        payload={**exported, "template_key": "content_generation_graph_copy", "version": "1"},
        dry_run=True,
    )

    assert exported["template_key"] == "content_generation_graph"
    assert dry_run["dry_run"] is True
    assert dry_run["valid"] is True
    assert dry_run["action"] == "create_template"


@pytest.mark.asyncio
async def test_template_import_creates_new_template(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowTemplateRegistryService(session)
    payload = {
        "template_key": "imported_graph",
        "name": "Imported Graph",
        "category": "import",
        "version": "1",
        "entry_node": "start",
        "graph_definition": {"nodes": [{"node_key": "start"}], "edges": []},
        "input_schema": {},
        "output_schema": {},
        "metadata": {"risk_level": "low"},
    }

    result = await service.import_template(workspace_id="workspace-template-import-create", payload=payload, dry_run=False)

    assert result["valid"] is True
    assert result["template"].template_key == "imported_graph"
