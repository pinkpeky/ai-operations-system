"""Memory API 测试模块。"""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import memory as memory_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_memory_api_crud_flow() -> None:
    """Memory API 应支持 session、message、memory 的基本读写，并强制 workspace header。"""

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
    app.include_router(memory_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            missing_header = await client.post("/api/v1/memory/sessions", json={"title": "Missing"})
            assert missing_header.status_code == 400

            headers = {"X-Workspace-Id": "workspace-memory-api", "X-User-Id": "user-memory-api"}
            session_response = await client.post(
                "/api/v1/memory/sessions",
                headers=headers,
                json={"title": "API Session", "metadata": {"phase": "14"}},
            )
            assert session_response.status_code == 201
            session_id = session_response.json()["id"]

            message_response = await client.post(
                "/api/v1/memory/messages",
                headers=headers,
                json={"session_id": session_id, "role": "user", "content": "Memory API message"},
            )
            assert message_response.status_code == 201
            assert message_response.json()["workspace_id"] == "workspace-memory-api"

            messages_response = await client.get(f"/api/v1/memory/messages/{session_id}", headers=headers)
            assert messages_response.status_code == 200
            assert len(messages_response.json()["items"]) == 1

            memory_response = await client.post(
                "/api/v1/memory/memories",
                headers=headers,
                json={
                    "agent_name": "AgenticRAGOrchestrator",
                    "memory_type": "long_term",
                    "content": "Memory API supports retrieval.",
                    "importance_score": 0.8,
                },
            )
            assert memory_response.status_code == 201
            memory_id = memory_response.json()["id"]

            list_response = await client.get(
                "/api/v1/memory/memories",
                headers=headers,
                params={"query": "retrieval", "agent_name": "AgenticRAGOrchestrator"},
            )
            assert list_response.status_code == 200
            assert [item["id"] for item in list_response.json()["items"]] == [memory_id]

            delete_response = await client.delete(f"/api/v1/memory/memories/{memory_id}", headers=headers)
            assert delete_response.status_code == 200
            assert delete_response.json()["deleted"] is True
    finally:
        await engine.dispose()

