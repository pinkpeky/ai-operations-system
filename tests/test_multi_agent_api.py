"""Multi-Agent API 测试。"""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import agents as agent_routes
from app.api.routes import multi_agent as multi_agent_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_multi_agent_api_flow() -> None:
    """API 应支持 registry、run 创建、执行链路、查询 messages/handoffs。"""

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
    app.include_router(agent_routes.router, prefix="/api/v1")
    app.include_router(multi_agent_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"X-Workspace-Id": "workspace-ma-api", "X-User-Id": "user-ma-api"}
            registry = await client.get("/api/v1/agents/registry", headers=headers)
            assert registry.status_code == 200
            assert "tool_agent" in {item["name"] for item in registry.json()["items"]}

            created = await client.post(
                "/api/v1/multi-agent/runs",
                headers=headers,
                json={
                    "root_agent": "content_planner",
                    "input": {
                        "topic": "AI 自动化运营",
                        "platform": "tiktok",
                        "style": "专业简洁",
                        "query": "ping"
                    },
                },
            )
            assert created.status_code == 201
            run_id = created.json()["id"]

            executed = await client.post(
                f"/api/v1/multi-agent/runs/{run_id}/execute-chain",
                headers=headers,
                json={"chain_name": "content_planning"},
            )
            assert executed.status_code == 200
            body = executed.json()
            assert body["success"] is True
            assert body["run"]["status"] == "completed"
            assert len(body["handoffs"]) == 3

            messages = await client.get(f"/api/v1/multi-agent/runs/{run_id}/messages", headers=headers)
            handoffs = await client.get(f"/api/v1/multi-agent/runs/{run_id}/handoffs", headers=headers)
            assert messages.status_code == 200
            assert handoffs.status_code == 200
            assert len(messages.json()["items"]) >= 4
            assert len(handoffs.json()["items"]) == 3
    finally:
        await engine.dispose()

