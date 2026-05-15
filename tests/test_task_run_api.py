"""Phase 42 task run API tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import task_runs as task_run_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_task_run_api_create_list_retry_cancel() -> None:
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

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"X-Workspace-Id": "workspace-task-api", "X-User-Id": "user-task-api"}
            created = await client.post(
                "/api/v1/task-runs",
                headers=headers,
                json={
                    "task_type": "conversation",
                    "source_type": "conversation",
                    "source_id": "11111111-1111-1111-1111-111111111111",
                    "input_payload": {"thread_id": "11111111-1111-1111-1111-111111111111", "input": {"message": "hello"}},
                },
            )
            assert created.status_code == 201
            task_id = created.json()["id"]

            listed = await client.get("/api/v1/task-runs?status=queued", headers=headers)
            assert listed.status_code == 200
            assert listed.json()["items"][0]["id"] == task_id

            cancelled = await client.post(f"/api/v1/task-runs/{task_id}/cancel", headers=headers, json={"reason": "test"})
            assert cancelled.status_code == 200
            assert cancelled.json()["status"] == "cancelled"

            events = await client.get(f"/api/v1/task-runs/{task_id}/events", headers=headers)
            assert events.status_code == 200
            assert "task_cancelled" in {event["event_type"] for event in events.json()["items"]}

            retry = await client.post(f"/api/v1/task-runs/{task_id}/retry", headers=headers, json={"reason": "retry cancelled"})
            assert retry.status_code == 400
    finally:
        await engine.dispose()
