"""Workflow template ORM/service smoke tests."""

from __future__ import annotations

import pytest

from app.workflow.template_registry import WorkflowTemplateRegistryService


@pytest.mark.asyncio
async def test_builtin_workflow_templates_seeded(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowTemplateRegistryService(session)

    templates = await service.list_templates(workspace_id="workspace-template-seed")

    keys = {item.template_key for item in templates}
    assert "browser_screenshot_report_graph" in keys
    assert "content_generation_graph" in keys
    assert "rag_answer_graph" in keys
    assert "approval_then_browser_graph" in keys
    assert "openclaw_mock_inspect_graph" in keys
    assert "task_retry_demo_graph" in keys
