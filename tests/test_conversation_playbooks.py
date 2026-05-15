"""Phase 40 conversation playbook foundation tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationPlaybookService


@pytest.mark.asyncio
async def test_builtin_playbooks_seed_and_list(session) -> None:  # type: ignore[no-untyped-def]
    service = ConversationPlaybookService(session)

    playbooks = await service.list_playbooks(workspace_id="workspace-playbooks")
    names = {item.name for item in playbooks}

    assert {
        "browser_search_summary",
        "browser_screenshot_report",
        "rag_answer",
        "content_generation",
        "trend_research_draft",
        "openclaw_mock_device_check",
    } <= names


@pytest.mark.asyncio
async def test_create_custom_playbook(session) -> None:  # type: ignore[no-untyped-def]
    service = ConversationPlaybookService(session)

    playbook = await service.create_playbook(
        workspace_id="workspace-custom-playbook",
        name="custom_note",
        description="Custom note playbook",
        category="custom",
        risk_level="low",
        steps=[{"step_type": "message", "title": "Record note", "message": "hello"}],
    )

    assert playbook.name == "custom_note"
    assert playbook.status == "active"
