"""Workflow template lifecycle tests."""

from __future__ import annotations

import pytest

from app.workflow.template_governance import WorkflowTemplateGovernanceService
from app.workflow.template_registry import WorkflowTemplateRegistryService


@pytest.mark.asyncio
async def test_deprecated_and_archived_templates_are_not_runnable(session) -> None:  # type: ignore[no-untyped-def]
    registry = WorkflowTemplateRegistryService(session)
    governance = WorkflowTemplateGovernanceService(session)
    templates = await registry.list_templates(workspace_id="workspace-template-lifecycle")
    template = next(item for item in templates if item.template_key == "content_generation_graph")

    deprecated = await governance.deprecate_template(
        workspace_id="workspace-template-lifecycle",
        template_id=template.id,
        actor_id="admin",
        reason="superseded",
    )
    assert deprecated.status == "deprecated"
    with pytest.raises(ValueError, match="Only active"):
        await registry.run_template(
            workspace_id="workspace-template-lifecycle",
            user_id="user",
            template_id=template.id,
            input_payload={"topic": "AI automation"},
        )

    archived = await governance.archive_template(
        workspace_id="workspace-template-lifecycle",
        template_id=template.id,
        actor_id="admin",
        reason="retired",
    )
    assert archived.status == "archived"
