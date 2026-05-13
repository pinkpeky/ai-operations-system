"""Browser screenshot tests."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import browser as browser_routes
from app.browser.providers.playwright_provider import PlaywrightLocalProvider
from app.browser.services import BrowserService
from app.core.config import Settings
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_browser_service_saves_screenshot(fake_playwright, tmp_path, session: AsyncSession) -> None:  # type: ignore[no-untyped-def]
    """screenshot action 应保存 png 并写入 output_payload。"""

    provider = PlaywrightLocalProvider(screenshot_dir=tmp_path)
    service = BrowserService(session, provider=provider)
    browser_session = await service.create_browser_session(workspace_id="workspace-shot", user_id="user-a")
    action = await service.execute_action(
        workspace_id="workspace-shot",
        session_id=browser_session.id,
        action_type="screenshot",
        input_payload={"screenshot_name": "example-home"},
    )

    assert action.status == "completed"
    assert action.screenshot_path is not None
    assert action.output_payload is not None
    assert action.output_payload["data"]["screenshot_filename"] == "example-home.png"


@pytest.mark.asyncio
async def test_browser_screenshot_api_returns_png(fake_playwright, tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """GET /browser/screenshot/{session_id}/{filename} 应返回 PNG。"""

    engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    settings = Settings(BROWSER_SCREENSHOT_DIR=str(tmp_path))
    monkeypatch.setattr(browser_routes, "get_settings", lambda: settings)
    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(browser_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with session_factory() as db_session:
            service = BrowserService(db_session, settings=settings, provider=PlaywrightLocalProvider(screenshot_dir=tmp_path))
            browser_session = await service.create_browser_session(workspace_id="workspace-shot-api", user_id="user-a")
            action = await service.execute_action(
                workspace_id="workspace-shot-api",
                session_id=browser_session.id,
                action_type="screenshot",
                input_payload={"screenshot_name": "api-shot"},
            )
            assert action.status == "completed"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/browser/screenshot/{browser_session.id}/api-shot.png",
                headers={"X-Workspace-Id": "workspace-shot-api"},
            )

        assert response.status_code == 200
        assert response.content.startswith(b"\x89PNG")
    finally:
        await engine.dispose()
