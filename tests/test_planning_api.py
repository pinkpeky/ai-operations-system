"""Planning API 测试。"""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import planning as planning_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_planning_api_flow() -> None:
    """API 应支持创建、执行、查询 steps/reviews。"""

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
    app.include_router(planning_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"X-Workspace-Id": "workspace-planning-api", "X-User-Id": "user-planning"}
            created = await client.post(
                "/api/v1/plans",
                headers=headers,
                json={
                    "root_goal": "生成 AI 自动化运营 TikTok 内容",
                    "metadata": {"query": "ping", "platform": "tiktok", "style": "专业简洁"},
                },
            )
            assert created.status_code == 201
            plan_id = created.json()["id"]

            steps = await client.get(f"/api/v1/plans/{plan_id}/steps", headers=headers)
            assert steps.status_code == 200
            assert len(steps.json()["items"]) == 3

            executed = await client.post(f"/api/v1/plans/{plan_id}/execute", headers=headers, json={})
            assert executed.status_code == 200
            body = executed.json()
            assert body["success"] is True
            assert body["status"] == "completed"
            assert body["review_result"] == "approved"

            reviews = await client.get(f"/api/v1/plans/{plan_id}/reviews", headers=headers)
            assert reviews.status_code == 200
            assert reviews.json()["items"][0]["review_result"] == "approved"
    finally:
        await engine.dispose()
