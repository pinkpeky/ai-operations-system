"""Phase 44 output artifact package API tests."""

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
async def test_output_artifact_package_api_and_lineage() -> None:
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
    headers = {"X-Workspace-Id": "workspace-package-api", "X-User-Id": "user"}
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            created = await client.post(
                "/api/v1/output-artifacts",
                headers=headers,
                json={"source_type": "playbook", "artifact_type": "report", "title": "Package API Artifact", "content": "hello"},
            )
            artifact_id = created.json()["id"]
            packaged = await client.post(
                f"/api/v1/output-artifacts/{artifact_id}/package",
                headers=headers,
                json={"package_type": "bundle_zip", "include_related": True},
            )
            lineage = await client.get(f"/api/v1/output-artifacts/{artifact_id}/lineage", headers=headers)

            assert packaged.status_code == 200
            assert packaged.json()["generated_artifact"]["artifact_type"] == "bundle"
            assert lineage.status_code == 200
            assert len(lineage.json()["relationships"]) == 1
    finally:
        await engine.dispose()
