"""Phase 43 task scheduler API tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import task_runs as task_run_routes
from app.api.routes import task_scheduler as task_scheduler_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_task_scheduler_health_scan_diagnostics_and_recover_api() -> None:
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
    app.include_router(task_run_routes.router, prefix="/api/v1")
    app.include_router(task_scheduler_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"X-Workspace-Id": "workspace-scheduler-api", "X-User-Id": "user-scheduler-api"}
            created = await client.post(
                "/api/v1/task-runs",
                headers=headers,
                json={
                    "task_type": "conversation",
                    "source_type": "conversation",
                    "source_id": "22222222-2222-4222-8222-222222222222",
                    "input_payload": {"thread_id": "22222222-2222-4222-8222-222222222222"},
                },
            )
            assert created.status_code == 201
            task_id = created.json()["id"]

            health = await client.get("/api/v1/task-scheduler/health", headers=headers)
            assert health.status_code == 200
            assert health.json()["status"] == "active"

            scan = await client.post("/api/v1/task-scheduler/scan", headers=headers)
            assert scan.status_code == 200
            assert set(scan.json()["details"]) >= {"scheduled_recovered", "retrying_recovered", "expired_leases_recovered"}

            diagnostics = await client.get(f"/api/v1/task-runs/{task_id}/diagnostics", headers=headers)
            assert diagnostics.status_code == 200
            assert diagnostics.json()["task_run_id"] == task_id

            recovered = await client.post(f"/api/v1/task-runs/{task_id}/recover", headers=headers, json={"reason": "api test"})
            assert recovered.status_code == 200
            assert recovered.json()["status"] == "queued"
            assert recovered.json()["recovery_count"] == 1

            listed = await client.get("/api/v1/task-runs?recoverable=false", headers=headers)
            assert listed.status_code == 200
            assert any(item["id"] == task_id for item in listed.json()["items"])
    finally:
        await engine.dispose()
