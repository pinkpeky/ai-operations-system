"""UI access API tests."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import browser as browser_routes
from app.api.routes import browser_workers as browser_worker_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_ui_access_api_flow() -> None:
    """API 应支持 create/get/validate/revoke/expire。"""

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
    app.include_router(browser_worker_routes.runtime_router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"X-Workspace-Id": "workspace-ui-api", "X-User-Id": "user-ui-api"}
            created_session = await client.post("/api/v1/browser/sessions", headers=headers, json={"metadata": {"phase": "25"}})
            session_id = created_session.json()["id"]
            requested = await client.post(
                "/api/v1/browser/human-control/request",
                headers=headers,
                json={"browser_session_id": session_id, "reason": "manual check"},
            )
            control_id = requested.json()["id"]
            await client.post(f"/api/v1/browser/human-control/{control_id}/start", headers=headers, json={})

            created = await client.post(
                "/api/v1/browser/ui-access",
                headers=headers,
                json={
                    "browser_session_id": session_id,
                    "human_control_session_id": control_id,
                    "metadata": {"phase": "25"},
                },
            )
            body = created.json()
            token = body["access_token"]
            access_id = body["id"]
            fetched = await client.get(f"/api/v1/browser/ui-access/{access_id}", headers=headers)
            validated = await client.get(f"/api/v1/browser/ui-access/{access_id}/validate", headers=headers, params={"token": token})
            capabilities = await client.get("/api/v1/browser-worker-runtime/ui-access/capabilities")
            revoked = await client.post(f"/api/v1/browser/ui-access/{access_id}/revoke", headers=headers)
            expired = await client.post("/api/v1/browser/ui-access/expire", headers=headers)

            assert created.status_code == 201
            assert body["remote_control_url"].endswith(access_id)
            assert body["live_view_url"].endswith(access_id)
            assert body["devtools_url"] is None
            assert token
            assert fetched.json()["access_token"] is None
            assert validated.json()["valid"] is True
            assert capabilities.json()["placeholder"] is True
            assert revoked.json()["status"] == "revoked"
            assert expired.json()["expired_count"] == 0
    finally:
        await engine.dispose()
