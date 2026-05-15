"""Workflow template rollback tests."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.workflow import WorkflowTemplateVersion
from app.workflow.template_governance import WorkflowTemplateGovernanceService
from app.workflow.template_registry import WorkflowTemplateRegistryService


@pytest.mark.asyncio
async def test_template_rollback_restores_previous_active_version(session) -> None:  # type: ignore[no-untyped-def]
    workspace_id = "workspace-template-rollback"
    registry = WorkflowTemplateRegistryService(session)
    governance = WorkflowTemplateGovernanceService(session)
    template = await registry.create_template(
        workspace_id=workspace_id,
        template_key="rollback_template",
        name="Rollback Template",
        description="Template rollback test",
        category="governance",
        status="draft",
        risk_level="low",
        tags=[],
        metadata={},
        version="1",
        graph_definition={"nodes": [{"node_key": "start", "node_type": "no_op"}], "edges": []},
        entry_node="start",
    )
    result = await session.execute(
        select(WorkflowTemplateVersion).where(WorkflowTemplateVersion.template_id == template.id, WorkflowTemplateVersion.version == "1")
    )
    version_one = result.scalar_one()
    review_one = await governance.submit_for_review(
        workspace_id=workspace_id,
        template_id=template.id,
        template_version_id=version_one.id,
        reviewer_id="reviewer",
    )
    await governance.approve_review(workspace_id=workspace_id, review_id=review_one.id, actor_id="reviewer")
    await governance.activate_template_version(workspace_id=workspace_id, template_id=template.id, version_id=version_one.id, actor_id="admin")

    version_two = await registry.create_version(
        workspace_id=workspace_id,
        template_id=template.id,
        version="2",
        graph_definition={"nodes": [{"node_key": "start", "node_type": "no_op"}], "edges": []},
        entry_node="start",
    )
    review_two = await governance.submit_for_review(
        workspace_id=workspace_id,
        template_id=template.id,
        template_version_id=version_two.id,
        reviewer_id="reviewer",
    )
    await governance.approve_review(workspace_id=workspace_id, review_id=review_two.id, actor_id="reviewer")
    await governance.activate_template_version(workspace_id=workspace_id, template_id=template.id, version_id=version_two.id, actor_id="admin")

    rolled_back = await governance.rollback_template_version(
        workspace_id=workspace_id,
        template_id=template.id,
        version_id=version_one.id,
        actor_id="admin",
        reason="regression",
    )

    assert rolled_back.status == "active"
    assert rolled_back.current_version == "1"
