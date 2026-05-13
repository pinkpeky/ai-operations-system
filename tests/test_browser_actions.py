"""Browser action persistence tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserService


@pytest.mark.asyncio
async def test_browser_action_writes_output_duration_and_logs(session: AsyncSession) -> None:
    """Completed browser actions should include output, duration, and logs."""

    service = BrowserService(session)
    browser_session = await service.create_browser_session(workspace_id="workspace-browser-actions", user_id="user-a")

    action = await service.execute_action(
        workspace_id="workspace-browser-actions",
        session_id=browser_session.id,
        action_type="navigate",
        target="https://example.com",
        input_payload={"wait_until": "domcontentloaded"},
    )
    actions = await service.list_actions(workspace_id="workspace-browser-actions", session_id=browser_session.id)
    logs = await service.list_logs(workspace_id="workspace-browser-actions", session_id=browser_session.id)

    assert action.status == "completed"
    assert action.output_payload is not None
    assert action.output_payload["message"] == "mock browser navigate success"
    assert action.duration_ms is not None
    assert actions[0].id == action.id
    assert any(log.log_metadata.get("action_type") == "navigate" for log in logs)


@pytest.mark.asyncio
async def test_browser_action_records_failure_for_unknown_action(session: AsyncSession) -> None:
    """Unsupported actions should be recorded as failed rather than crashing."""

    service = BrowserService(session)
    browser_session = await service.create_browser_session(workspace_id="workspace-browser-fail", user_id=None)

    action = await service.execute_action(
        workspace_id="workspace-browser-fail",
        session_id=browser_session.id,
        action_type="unknown_action",
        target=None,
        input_payload={},
    )

    assert action.status == "failed"
    assert "Unsupported browser action_type" in str(action.error)
