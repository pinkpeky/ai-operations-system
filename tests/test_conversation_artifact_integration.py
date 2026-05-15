"""Conversation message to artifact integration tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationService
from app.services.output_artifact_service import OutputArtifactService


@pytest.mark.asyncio
async def test_assistant_message_can_be_saved_as_artifact(session) -> None:  # type: ignore[no-untyped-def]
    workspace_id = "workspace-message-artifact"
    conversation = ConversationService(session)
    thread = await conversation.create_thread(workspace_id=workspace_id, user_id="user", title="Message artifact")
    message = await conversation.append_message(
        workspace_id=workspace_id,
        thread_id=thread.id,
        role="assistant",
        content="# Saved draft\n\nThis assistant response can become an artifact.",
        metadata={"route_name": "content_generation", "summary": "Saved draft"},
    )

    artifact = await OutputArtifactService(session).create_from_conversation_message(
        workspace_id=workspace_id,
        message_id=message.id,
        created_by="user",
    )

    assert artifact.thread_id == thread.id
    assert artifact.artifact_type == "content_draft"
    assert artifact.source_type == "conversation"
