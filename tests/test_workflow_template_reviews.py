"""Workflow template review queue tests."""

from __future__ import annotations

import pytest

from app.workflow.template_governance import WorkflowTemplateGovernanceService
from app.workflow.template_registry import WorkflowTemplateRegistryService


@pytest.mark.asyncio
async def test_template_review_can_be_submitted_and_approved(session) -> None:  # type: ignore[no-untyped-def]
    registry = WorkflowTemplateRegistryService(session)
    governance = WorkflowTemplateGovernanceService(session)
    templates = await registry.list_templates(workspace_id="workspace-template-review")
    template = next(item for item in templates if item.template_key == "content_generation_graph")
    version = template.versions[0]

    review = await governance.submit_for_review(
        workspace_id="workspace-template-review",
        template_id=template.id,
        template_version_id=version.id,
        reviewer_id="reviewer",
        actor_id="author",
    )
    approved = await governance.approve_review(
        workspace_id="workspace-template-review",
        review_id=review.id,
        actor_id="reviewer",
        review_notes="Looks safe.",
    )

    assert review.review_status == "approved"
    assert approved.review_status == "approved"
    assert approved.review_notes == "Looks safe."
