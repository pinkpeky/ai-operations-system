"""Browser security audit log tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserWorkerService
from app.browser.services import BrowserSecurityAuditService, BrowserService, BrowserUIAccessService


@pytest.mark.asyncio
async def test_browser_security_audit_logs_capture_worker_and_ui_access_events(session: AsyncSession) -> None:
    """安全审计日志应记录 worker 注册和 UI token 生命周期事件。"""

    worker_service = BrowserWorkerService(session)
    worker = await worker_service.register_worker(
        workspace_id="workspace-audit",
        worker_name="audit-worker",
        worker_type="playwright",
        base_url="http://browser-worker:9100",
        capabilities={"browser": "chromium"},
        metadata={},
    )
    browser_session = await BrowserService(session).create_browser_session(workspace_id="workspace-audit", user_id="user-a")
    ui_service = BrowserUIAccessService(session)
    created = await ui_service.create_access_session(
        workspace_id="workspace-audit",
        browser_session_id=browser_session.id,
        scopes=["view"],
    )
    await ui_service.validate_access_token(
        workspace_id="workspace-audit",
        access_session_id=created.access_session.id,
        token=created.access_token,
        scope="view",
    )
    await ui_service.revoke_access_session(
        workspace_id="workspace-audit",
        access_session_id=created.access_session.id,
        reason="audit test done",
    )

    logs = await BrowserSecurityAuditService(session).list_logs(workspace_id="workspace-audit", limit=20)
    event_types = {log.event_type for log in logs}

    assert worker.worker_secret_hash
    assert "worker_registered" in event_types
    assert "ui_token_created" in event_types
    assert "ui_token_validated" in event_types
    assert "ui_token_revoked" in event_types
