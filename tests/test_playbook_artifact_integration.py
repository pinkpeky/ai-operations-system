"""Playbook to Output Library integration tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationPlaybookService, ConversationService
from app.services.output_artifact_service import OutputArtifactService


@pytest.mark.asyncio
async def test_completed_content_playbook_creates_content_draft_artifact(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def fake_run(self, agent_input):  # type: ignore[no-untyped-def]
        return {
            "title": "Artifact draft",
            "description": agent_input["topic"],
            "tags": ["artifact"],
            "cta": "Save it.",
            "raw_response": "mock",
        }

    monkeypatch.setattr("app.conversation.services.conversation_service.ContentAgent.run", fake_run)
    workspace_id = "workspace-playbook-artifacts"
    thread = await ConversationService(session).create_thread(workspace_id=workspace_id, user_id="user", title="Artifacts")

    result = await ConversationPlaybookService(session).run_playbook_by_name(
        workspace_id=workspace_id,
        user_id="user",
        thread=thread,
        playbook_name="content_generation",
        input_payload={"topic": "AI ops", "platform": "short_video", "style": "brief"},
        mode="auto_safe",
        message_id=None,
        source_message="Generate content",
    )

    artifacts = await OutputArtifactService(session).list_artifacts(workspace_id=workspace_id, playbook_run_id=result.run.id)
    assert result.run.status == "completed"
    assert len(artifacts) == 1
    assert artifacts[0].artifact_type == "content_draft"
    assert "Artifact draft" in (artifacts[0].content or "")
