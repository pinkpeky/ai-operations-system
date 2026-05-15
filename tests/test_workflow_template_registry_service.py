"""Workflow template registry service tests."""

from __future__ import annotations

import pytest

from app.workflow.template_registry import WorkflowTemplateRegistryService


@pytest.mark.asyncio
async def test_run_low_risk_template_creates_workflow_and_artifact(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowTemplateRegistryService(session)
    templates = await service.list_templates(workspace_id="workspace-template-run")
    template = next(item for item in templates if item.template_key == "content_generation_graph")

    result = await service.run_template(
        workspace_id="workspace-template-run",
        user_id="user",
        template_id=template.id,
        input_payload={"topic": "AI automation"},
    )

    assert result.success is True
    assert result.run.status == "completed"
    assert result.workflow_run_id is not None
    assert result.run.output_payload["workflow_run_id"] == str(result.workflow_run_id)
    assert result.run.output_payload.get("artifact_id")


@pytest.mark.asyncio
async def test_medium_risk_template_waits_for_approval_by_default(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowTemplateRegistryService(session)
    templates = await service.list_templates(workspace_id="workspace-template-approval")
    template = next(item for item in templates if item.template_key == "browser_screenshot_report_graph")

    result = await service.run_template(
        workspace_id="workspace-template-approval",
        user_id="user",
        template_id=template.id,
        input_payload={"url": "https://example.com"},
        mode="auto_safe",
    )

    assert result.run.status == "running"
    assert result.run.output_payload["approval_required"] is True
    assert "waiting for approval" in result.summary
