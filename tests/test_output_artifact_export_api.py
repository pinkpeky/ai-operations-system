"""Phase 44 output artifact export API tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import output_artifacts as artifact_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_output_artifact_export_api_creates_pipeline_export() -> None:
    engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(artifact_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session
    headers = {"X-Workspace-Id": "workspace-export-api", "X-User-Id": "user"}
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            created = await client.post(
                "/api/v1/output-artifacts",
                headers=headers,
                json={"source_type": "conversation", "artifact_type": "markdown", "title": "API Artifact", "content": "hello"},
            )
            assert created.status_code == 201
            exported = await client.post(
                f"/api/v1/output-artifacts/{created.json()['id']}/export",
                headers=headers,
                json={"format": "html", "metadata": {"phase": "44"}},
            )
            assert exported.status_code == 200
            assert exported.json()["generated_artifact"]["artifact_stage"] == "exported"
            assert exported.json()["output_path"].endswith("artifact.html")
    finally:
        await engine.dispose()
