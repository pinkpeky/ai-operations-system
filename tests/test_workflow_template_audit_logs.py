"""Workflow template governance audit log tests."""

from __future__ import annotations

import pytest

from app.workflow.template_governance import WorkflowTemplateGovernanceService
from app.workflow.template_registry import WorkflowTemplateRegistryService


@pytest.mark.asyncio
async def test_governance_actions_write_audit_logs(session) -> None:  # type: ignore[no-untyped-def]
    registry = WorkflowTemplateRegistryService(session)
    governance = WorkflowTemplateGovernanceService(session)
    templates = await registry.list_templates(workspace_id="workspace-template-audit")
    template = next(item for item in templates if item.template_key == "content_generation_graph")
    version = template.versions[0]

    review = await governance.submit_for_review(
        workspace_id="workspace-template-audit",
        template_id=template.id,
        template_version_id=version.id,
        reviewer_id="reviewer",
        actor_id="author",
    )
    await governance.approve_review(workspace_id="workspace-template-audit", review_id=review.id, actor_id="reviewer")
    logs = await governance.list_governance_events(workspace_id="workspace-template-audit", template_id=template.id)
    actions = {log.action for log in logs}

    assert "review_submitted" in actions
    assert "review_approved" in actions
