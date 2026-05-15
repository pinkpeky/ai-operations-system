"""OpenClaw API tests."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import browser_workers as browser_worker_routes
from app.api.routes import openclaw as openclaw_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session
from app.openclaw.client import OpenClawWorkerClientResult


class FakeOpenClawWorkerClient:
    """测试用 OpenClaw client。"""

    def __init__(self, **_: object) -> None:
        pass

    async def health_check(self) -> OpenClawWorkerClientResult:
        return OpenClawWorkerClientResult(success=True, message="ok", data={"success": True, "provider": "mock", "enabled": True, "reachable": True, "mock": True, "version": "mock-openclaw-0.1"})

    async def capabilities(self) -> OpenClawWorkerClientResult:
        return OpenClawWorkerClientResult(success=True, message="ok", data={"success": True, "provider": "mock", "mock": True, "capabilities": {"openclaw": True}, "actions": ["execute_action"]})

    async def execute_action(self, *, payload: dict[str, object]) -> OpenClawWorkerClientResult:
        return OpenClawWorkerClientResult(
            success=True,
            message="ok",
            data={
                "success": True,
                "action_type": payload["action_type"],
                "output_payload": {"real_openclaw_called": False},
                "duration_ms": 1,
                "provider": "mock",
                "mock": True,
            },
        )


@pytest.mark.asyncio
async def test_openclaw_api_health_capabilities_and_action(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """OpenClaw API 应使用已注册 worker 并返回 mock 结果。"""

    from app.openclaw import service as service_module

    monkeypatch.setattr(service_module, "OpenClawWorkerClient", FakeOpenClawWorkerClient)
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(browser_worker_routes.router, prefix="/api/v1")
    app.include_router(openclaw_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        headers = {"X-Workspace-Id": "workspace-openclaw-api", "X-User-Id": "user-openclaw"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            registered = await client.post(
                "/api/v1/browser-workers/register",
                headers=headers,
                json={
                    "worker_name": "openclaw-worker",
                    "worker_type": "playwright",
                    "base_url": "http://worker",
                    "capabilities": {"browser": "chromium", "openclaw": True},
                    "metadata": {},
                },
            )
            health = await client.get("/api/v1/openclaw/health", headers=headers)
            capabilities = await client.get("/api/v1/openclaw/capabilities", headers=headers)
            action = await client.post(
                "/api/v1/openclaw/actions",
                headers=headers,
                json={"action_type": "mock_inspect", "target": "https://example.com"},
            )

        assert registered.status_code == 201
        assert health.status_code == 200
        assert health.json()["reachable"] is True
        assert capabilities.json()["capabilities"]["openclaw"] is True
        assert action.status_code == 200
        assert action.json()["success"] is True
        assert action.json()["log_id"] is not None
    finally:
        await engine.dispose()
