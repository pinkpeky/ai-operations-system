"""Workflow template governance service tests."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.workflow import WorkflowTemplateVersion
from app.workflow.template_governance import WorkflowTemplateGovernanceService
from app.workflow.template_registry import WorkflowTemplateRegistryService


@pytest.mark.asyncio
async def test_governance_activation_requires_approved_review(session) -> None:  # type: ignore[no-untyped-def]
    registry = WorkflowTemplateRegistryService(session)
    governance = WorkflowTemplateGovernanceService(session)
    template = await registry.create_template(
        workspace_id="workspace-template-governance",
        template_key="governed_template",
        name="Governed Template",
        description="A template that must pass review before activation.",
        category="governance",
        status="draft",
        risk_level="medium",
        tags=["governance"],
        metadata={},
        version="1",
        graph_definition={"nodes": [{"node_key": "start", "node_type": "no_op"}], "edges": []},
        entry_node="start",
    )
    result = await session.execute(
        select(WorkflowTemplateVersion).where(WorkflowTemplateVersion.template_id == template.id, WorkflowTemplateVersion.version == "1")
    )
    version = result.scalar_one()

    with pytest.raises(ValueError, match="approved"):
        await governance.activate_template_version(
            workspace_id="workspace-template-governance",
            template_id=template.id,
            version_id=version.id,
            actor_id="admin",
        )

    review = await governance.submit_for_review(
        workspace_id="workspace-template-governance",
        template_id=template.id,
        template_version_id=version.id,
        reviewer_id="reviewer",
    )
    await governance.approve_review(workspace_id="workspace-template-governance", review_id=review.id, actor_id="reviewer")
    activated = await governance.activate_template_version(
        workspace_id="workspace-template-governance",
        template_id=template.id,
        version_id=version.id,
        actor_id="admin",
    )

    assert activated.status == "active"
    assert activated.verified is True
