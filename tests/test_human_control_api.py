"""Human control API tests."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import browser as browser_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_human_control_api_flow() -> None:
    """API 应支持 request/approve/start/complete/events 查询。"""

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
    app.include_router(browser_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"X-Workspace-Id": "workspace-human-api", "X-User-Id": "user-human-api"}
            created_session = await client.post("/api/v1/browser/sessions", headers=headers, json={"metadata": {"phase": "24"}})
            session_id = created_session.json()["id"]

            requested = await client.post(
                "/api/v1/browser/human-control/request",
                headers=headers,
                json={
                    "browser_session_id": session_id,
                    "reason": "manual login required",
                    "metadata": {"phase": "24"},
                },
            )
            control_id = requested.json()["id"]
            approved = await client.post(f"/api/v1/browser/human-control/{control_id}/approve", headers=headers, json={})
            started = await client.post(f"/api/v1/browser/human-control/{control_id}/start", headers=headers, json={})
            completed = await client.post(
                f"/api/v1/browser/human-control/{control_id}/complete",
                headers=headers,
                json={"note": "manual step completed"},
            )
            events = await client.get(f"/api/v1/browser/human-control/{control_id}/events", headers=headers)
            listed = await client.get("/api/v1/browser/human-control", headers=headers)

            assert requested.status_code == 201
            assert requested.json()["status"] == "requested"
            assert approved.json()["approved_by"] == "user-human-api"
            assert started.json()["status"] == "active"
            assert completed.json()["status"] == "completed"
            assert [event["event_type"] for event in events.json()["items"]] == ["requested", "approved", "started", "completed"]
            assert len(listed.json()["items"]) == 1
    finally:
        await engine.dispose()
