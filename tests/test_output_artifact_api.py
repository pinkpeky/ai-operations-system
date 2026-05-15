"""Output Artifact API tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import conversations as conversation_routes
from app.api.routes import output_artifacts as artifact_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_output_artifact_api_create_from_message_and_export() -> None:
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
    app.include_router(artifact_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session
    headers = {"X-Workspace-Id": "workspace-artifact-api", "X-User-Id": "user"}

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            thread = await client.post("/api/v1/conversations", headers=headers, json={"title": "Artifacts", "metadata": {}})
            message = await client.post(
                f"/api/v1/conversations/{thread.json()['id']}/messages",
                headers=headers,
                json={"role": "assistant", "content": "Artifact ready", "metadata": {"route_name": "rag_answer"}},
            )
            created = await client.post(f"/api/v1/output-artifacts/from-message/{message.json()['id']}", headers=headers)
            assert created.status_code == 201
            artifact_id = created.json()["id"]

            listed = await client.get("/api/v1/output-artifacts?artifact_type=rag_answer", headers=headers)
            assert listed.status_code == 200
            assert listed.json()["items"][0]["id"] == artifact_id

            exported = await client.get(f"/api/v1/output-artifacts/{artifact_id}/export?format=json", headers=headers)
            assert exported.status_code == 200
            assert exported.json()["format"] == "json"
            assert "Artifact ready" in exported.json()["content"]
    finally:
        await engine.dispose()
