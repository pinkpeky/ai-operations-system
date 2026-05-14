"""Conversation Runtime API tests."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import conversations as conversation_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_conversation_api_flow(monkeypatch) -> None:
    """API 应支持 create/message/run/messages/events，并强制 workspace header。"""

    async def fake_run(self, agent_input):  # type: ignore[no-untyped-def]
        return {
            "title": "API 测试标题",
            "description": f"API 内容：{agent_input['topic']}",
            "tags": ["phase33"],
            "cta": "继续执行",
            "raw_response": "mock",
        }

    monkeypatch.setattr("app.conversation.services.conversation_service.ContentAgent.run", fake_run)

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
    app.include_router(conversation_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            missing_header = await client.post("/api/v1/conversations", json={"title": "Missing"})
            assert missing_header.status_code == 400

            headers = {"X-Workspace-Id": "workspace-conversation-api", "X-User-Id": "user-conversation-api"}
            created = await client.post(
                "/api/v1/conversations",
                headers=headers,
                json={"title": "API Conversation", "metadata": {"phase": "33"}},
            )
            assert created.status_code == 201
            thread_id = created.json()["id"]

            message = await client.post(
                f"/api/v1/conversations/{thread_id}/messages",
                headers=headers,
                json={"role": "user", "content": "请生成一条短视频文案。", "metadata": {"source": "test"}},
            )
            assert message.status_code == 201

            run = await client.post(
                f"/api/v1/conversations/{thread_id}/run",
                headers=headers,
                json={"input": {"message": "请生成一条短视频文案。"}},
            )
            assert run.status_code == 200
            assert run.json()["route"] == "content"
            assert run.json()["route_name"] == "content"
            assert run.json()["selected_tool"] is None
            assert run.json()["events_created"] >= 1
            assert run.json()["success"] is True
            assert "result_metadata" in run.json()

            messages = await client.get(f"/api/v1/conversations/{thread_id}/messages", headers=headers)
            assert messages.status_code == 200
            assert len(messages.json()["items"]) >= 2

            events = await client.get(f"/api/v1/conversations/{thread_id}/events", headers=headers)
            assert events.status_code == 200
            assert "assistant_response" in {item["event_type"] for item in events.json()["items"]}
    finally:
        await engine.dispose()
