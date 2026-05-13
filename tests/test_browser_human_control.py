"""Browser human control service tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserHumanControlService, BrowserService
from worker.browser_worker.config import WorkerSettings
from worker.browser_worker.playwright_runtime import PlaywrightBrowserWorkerRuntime


@pytest.mark.asyncio
async def test_human_control_service_full_flow(session: AsyncSession) -> None:
    """Human control 应记录事件，并在 complete 后恢复 browser session。"""

    browser_service = BrowserService(session)
    browser_session = await browser_service.create_browser_session(
        workspace_id="workspace-human-control",
        user_id="user-human",
    )
    service = BrowserHumanControlService(session)

    control = await service.request_control(
        workspace_id="workspace-human-control",
        browser_session_id=browser_session.id,
        reason="manual login required",
        requested_by="user-human",
        metadata={"phase": "24"},
    )
    requested_session = await browser_service.repository.get_session(
        session_id=browser_session.id,
        workspace_id="workspace-human-control",
    )
    assert control.status == "requested"
    assert requested_session is not None
    assert requested_session.status == "paused"
    assert requested_session.human_control_session_id == control.id

    approved = await service.approve_control(
        workspace_id="workspace-human-control",
        control_session_id=control.id,
        approved_by="operator",
    )
    started = await service.start_control(
        workspace_id="workspace-human-control",
        control_session_id=control.id,
    )
    started_status = started.status
    completed = await service.complete_control(
        workspace_id="workspace-human-control",
        control_session_id=control.id,
        note="manual step completed",
    )
    resumed_session = await browser_service.repository.get_session(
        session_id=browser_session.id,
        workspace_id="workspace-human-control",
    )
    events = await service.list_control_events(
        workspace_id="workspace-human-control",
        control_session_id=control.id,
    )

    assert approved.approved_by == "operator"
    assert started_status == "active"
    assert completed.status == "completed"
    assert resumed_session is not None
    assert resumed_session.status == "active"
    assert resumed_session.resumed_at is not None
    assert [event.event_type for event in events] == ["requested", "approved", "started", "completed"]


@pytest.mark.asyncio
async def test_worker_runtime_human_control_metadata(fake_playwright) -> None:  # type: ignore[no-untyped-def]
    """browser-worker runtime 应提供 metadata-level human control 接口。"""

    _ = fake_playwright
    runtime = PlaywrightBrowserWorkerRuntime(settings=WorkerSettings())
    created = await runtime.create_session(
        workspace_id="workspace-worker-human",
        local_browser_session_id="local-session",
        metadata={},
    )
    assert created.remote_session_id is not None

    started = await runtime.start_human_control(
        remote_session_id=created.remote_session_id,
        control_session_id="control-id",
        payload={"reason": "manual step"},
    )
    status = await runtime.get_human_control_status(remote_session_id=created.remote_session_id)
    completed = await runtime.complete_human_control(
        remote_session_id=created.remote_session_id,
        control_session_id="control-id",
        note="done",
        payload={},
    )
    await runtime.close_all()

    assert started.success is True
    assert started.status == "active"
    assert status.status == "active"
    assert completed.status == "completed"
