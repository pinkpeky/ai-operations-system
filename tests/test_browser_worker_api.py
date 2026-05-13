"""Browser worker API tests."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import browser_workers as browser_worker_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_browser_worker_api_register_heartbeat_list_and_runtime() -> None:
    """Worker API 应支持注册、心跳、列表和 mock runtime health。"""

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
    app.include_router(browser_worker_routes.runtime_router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"X-Workspace-Id": "workspace-worker-api", "X-User-Id": "user-worker"}
            registered = await client.post(
                "/api/v1/browser-workers/register",
                headers=headers,
                json={
                    "worker_name": "local-worker-1",
                    "worker_type": "playwright",
                    "base_url": "http://localhost:8000/api/v1/browser-worker-runtime",
                    "capabilities": {"browser": "chromium", "screenshot": True},
                    "metadata": {},
                },
            )
            worker_id = registered.json()["id"]
            heartbeat = await client.post(
                f"/api/v1/browser-workers/{worker_id}/heartbeat",
                headers=headers,
                json={"status": "online", "capabilities": {"browser": "chromium"}, "metadata": {"load": 0}},
            )
            listing = await client.get("/api/v1/browser-workers?status=online", headers=headers)
            summary = await client.get("/api/v1/browser-workers/health/summary", headers=headers)
            available = await client.get("/api/v1/browser-workers/available", headers=headers)
            cleanup = await client.post(
                "/api/v1/browser-workers/cleanup-sessions",
                headers=headers,
                json={"session_timeout_seconds": 1800, "close_stale_sessions": True},
            )
            offline = await client.post(
                f"/api/v1/browser-workers/{worker_id}/mark-offline",
                headers=headers,
                json={"error_message": "api test offline"},
            )
            sessions = await client.get(f"/api/v1/browser-workers/{worker_id}/sessions", headers=headers)
            health = await client.get("/api/v1/browser-worker-runtime/health")

            assert registered.status_code == 201
            assert heartbeat.status_code == 200
            assert listing.status_code == 200
            assert summary.status_code == 200
            assert available.status_code == 200
            assert cleanup.status_code == 200
            assert offline.status_code == 200
            assert sessions.status_code == 200
            assert len(listing.json()["items"]) == 1
            assert summary.json()["online_workers"] == 1
            assert cleanup.json()["stale_sessions"] == 0
            assert cleanup.json()["offline_worker_sessions"] == 0
            assert offline.json()["status"] == "offline"
            assert health.status_code == 200
            assert health.json()["success"] is True
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_browser_worker_api_requires_workspace() -> None:
    """Worker management API 必须要求 workspace header。"""

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(browser_worker_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        yield object()

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/browser-workers")

    assert response.status_code == 400
    assert response.json()["detail"] == "X-Workspace-Id header is required"
