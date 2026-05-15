"""Workflow template marketplace tests."""

from __future__ import annotations

import pytest

from app.workflow.template_governance import WorkflowTemplateGovernanceService
from app.workflow.template_registry import WorkflowTemplateRegistryService


@pytest.mark.asyncio
async def test_marketplace_exposes_badges_and_run_metrics(session) -> None:  # type: ignore[no-untyped-def]
    registry = WorkflowTemplateRegistryService(session)
    governance = WorkflowTemplateGovernanceService(session)
    templates = await registry.list_templates(workspace_id="workspace-template-marketplace")
    template = next(item for item in templates if item.template_key == "content_generation_graph")

    await registry.run_template(
        workspace_id="workspace-template-marketplace",
        user_id="user",
        template_id=template.id,
        input_payload={"topic": "AI automation"},
    )
    marketplace = await governance.list_marketplace(workspace_id="workspace-template-marketplace")
    item = next(row for row in marketplace if row["template"].id == template.id)

    assert "verified" in item["badges"]
    assert "recommended" in item["badges"]
    assert item["metrics"]["total_runs"] >= 1
    assert item["metrics"]["success_rate"] >= 0
