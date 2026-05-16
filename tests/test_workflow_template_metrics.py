"""Workflow template metrics tests."""

from __future__ import annotations

import pytest

from app.workflow.template_registry import WorkflowTemplateRegistryService


@pytest.mark.asyncio
async def test_template_run_updates_marketplace_metrics(session) -> None:  # type: ignore[no-untyped-def]
    registry = WorkflowTemplateRegistryService(session)
    templates = await registry.list_templates(workspace_id="workspace-template-metrics")
    template = next(item for item in templates if item.template_key == "content_generation_graph")

    await registry.run_template(
        workspace_id="workspace-template-metrics",
        user_id="user",
        template_id=template.id,
        input_payload={"topic": "AI automation"},
    )
    refreshed = await registry.require_template(workspace_id="workspace-template-metrics", template_id=template.id)

    assert refreshed.usage_count == 1
    assert refreshed.success_rate == 1.0
    assert refreshed.average_step_count >= 1
