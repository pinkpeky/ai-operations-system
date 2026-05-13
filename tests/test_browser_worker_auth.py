"""Browser worker auth service tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserWorkerService
from app.core.config import Settings
from app.models.enums import BrowserWorkerAuthStatus, BrowserWorkerStatus


@pytest.mark.asyncio
async def test_worker_secret_returned_once_hashed_and_rotated(session: AsyncSession) -> None:
    """注册与轮换 worker secret 时，数据库只保存 hash。"""

    settings = Settings(BROWSER_WORKER_AUTH_ENABLED=True, BROWSER_WORKER_AUTH_STRICT=True)
    service = BrowserWorkerService(session, settings=settings)
    worker = await service.register_worker(
        workspace_id="workspace-worker-auth",
        worker_name="secure-worker",
        worker_type="playwright",
        base_url="http://browser-worker:9100",
        capabilities={"browser": "chromium", "screenshot": True},
        metadata={},
    )
    secret = service.last_worker_secret
    assert secret is not None
    assert worker.worker_secret_hash != secret
    assert len(worker.worker_secret_hash or "") == 64
    assert worker.auth_status == BrowserWorkerAuthStatus.UNVERIFIED.value

    verified = await service.heartbeat_worker(
        workspace_id="workspace-worker-auth",
        worker_id=worker.id,
        status=BrowserWorkerStatus.ONLINE.value,
        capabilities=worker.capabilities,
        metadata={},
        worker_secret=secret,
    )
    assert verified.auth_status == BrowserWorkerAuthStatus.VERIFIED.value
    assert verified.last_auth_at is not None

    rotated, rotated_secret = await service.rotate_worker_secret(
        workspace_id="workspace-worker-auth",
        worker_id=worker.id,
    )
    assert rotated_secret != secret
    assert rotated.worker_secret_hash != rotated_secret
    assert rotated.auth_status == BrowserWorkerAuthStatus.UNVERIFIED.value

    revoked = await service.revoke_worker(
        workspace_id="workspace-worker-auth",
        worker_id=worker.id,
        reason="unit test revoke",
    )
    assert revoked.auth_status == BrowserWorkerAuthStatus.REVOKED.value
    assert revoked.status == BrowserWorkerStatus.OFFLINE.value
