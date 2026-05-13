"""Browser API tests."""

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
async def test_browser_api_flow() -> None:
    """Browser API should create sessions, execute actions, and list logs."""

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
            headers = {"X-Workspace-Id": "workspace-browser-api", "X-User-Id": "user-browser"}
            created = await client.post(
                "/api/v1/browser/sessions",
                headers=headers,
                json={"metadata": {"purpose": "api-test"}},
            )
            assert created.status_code == 201
            session_id = created.json()["id"]

            action = await client.post(
                "/api/v1/browser/actions",
                headers=headers,
                json={
                    "session_id": session_id,
                    "action_type": "navigate",
                    "target": "https://example.com",
                    "input_payload": {"wait": "none"},
                },
            )
            assert action.status_code == 201
            assert action.json()["status"] == "completed"

            actions = await client.get(f"/api/v1/browser/actions/{session_id}", headers=headers)
            logs = await client.get(f"/api/v1/browser/logs/{session_id}", headers=headers)
            cleanup = await client.post(
                "/api/v1/browser/screenshots/cleanup",
                headers=headers,
                json={"older_than_days": 7, "dry_run": True},
            )
            assert actions.status_code == 200
            assert len(actions.json()["items"]) == 1
            assert logs.status_code == 200
            assert len(logs.json()["items"]) >= 2
            assert cleanup.status_code == 200
            assert cleanup.json()["workspace_id"] == "workspace-browser-api"
            assert cleanup.json()["dry_run"] is True
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_browser_profile_api_flow() -> None:
    """Profile API should create, use, release, and list persistent profiles."""

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
            headers = {"X-Workspace-Id": "workspace-browser-profile-api", "X-User-Id": "user-browser"}
            profile = await client.post(
                "/api/v1/browser/profiles",
                headers=headers,
                json={"profile_name": "api-profile", "profile_type": "persistent", "provider": "mock"},
            )
            profile_id = profile.json()["id"]
            session_response = await client.post(
                "/api/v1/browser/sessions",
                headers=headers,
                json={"profile_id": profile_id, "use_persistent_profile": True, "metadata": {"source": "api-test"}},
            )
            session_id = session_response.json()["id"]
            locked = await client.get(f"/api/v1/browser/profiles/{profile_id}", headers=headers)
            closed = await client.post(f"/api/v1/browser/sessions/{session_id}/close", headers=headers)
            released = await client.get(f"/api/v1/browser/profiles/{profile_id}", headers=headers)
            listed = await client.get("/api/v1/browser/profiles", headers=headers)

            assert profile.status_code == 201
            assert profile.json()["status"] == "available"
            assert session_response.status_code == 201
            assert session_response.json()["profile_id"] == profile_id
            assert session_response.json()["persistent_context_enabled"] is True
            assert locked.json()["status"] == "locked"
            assert locked.json()["locked_by_session_id"] == session_id
            assert closed.status_code == 200
            assert released.json()["status"] == "available"
            assert len(listed.json()["items"]) == 1
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_browser_api_requires_workspace() -> None:
    """Browser API must reject requests without workspace context."""

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(browser_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        yield object()

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/browser/sessions")

    assert response.status_code == 400
    assert response.json()["detail"] == "X-Workspace-Id header is required"
