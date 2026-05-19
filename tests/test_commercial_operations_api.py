"""Commercial operations API tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.router import create_api_router
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session
from app.models import CommercialOperation, CommercialOperationLink


@pytest.mark.asyncio
async def test_commercial_operations_api_flow() -> None:
    _ = (CommercialOperation, CommercialOperationLink)
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
    app.include_router(create_api_router())

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session
    headers = {"X-Workspace-Id": "workspace-commercial-api", "X-User-Id": "user-commercial-api"}

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            missing_header = await client.post(
                "/api/v1/commercial-operations",
                json={"title": "Missing", "objective": "missing workspace"},
            )
            assert missing_header.status_code == 400

            created = await client.post(
                "/api/v1/commercial-operations",
                headers=headers,
                json={
                    "title": "Lead generation operation",
                    "objective": "Increase qualified leads in 30 days.",
                    "target_audience": "B2B buyers",
                    "channels": ["website", "newsletter"],
                    "success_metrics": ["qualified_leads", "review_pass_rate"],
                    "constraints": ["human approval required"],
                    "knowledge_collection": "ai_knowledge_base",
                    "priority": "high",
                    "risk_level": "medium",
                    "budget_amount": "1200.50",
                },
            )
            assert created.status_code == 201
            body = created.json()
            operation_id = body["id"]
            assert body["workspace_id"] == "workspace-commercial-api"
            assert body["status"] == "draft"
            assert [step["step_key"] for step in body["plan_outline"]] == [
                "intake",
                "knowledge_research",
                "content_production",
                "human_review",
                "execution_dry_run",
                "monitor_recover",
            ]

            plan = await client.post(f"/api/v1/commercial-operations/{operation_id}/plan-draft", headers=headers)
            assert plan.status_code == 200
            assert plan.json()["operation_id"] == operation_id
            assert len(plan.json()["plan_outline"]) == 6

            fetched = await client.get(f"/api/v1/commercial-operations/{operation_id}", headers=headers)
            assert fetched.status_code == 200
            assert fetched.json()["status"] == "planning"

            hidden = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden.status_code == 404

            updated = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
                json={"status": "ready", "risk_level": "high", "constraints": ["review", "dry-run"]},
            )
            assert updated.status_code == 200
            assert updated.json()["status"] == "ready"
            assert updated.json()["risk_level"] == "high"
            assert updated.json()["constraints"] == ["review", "dry-run"]

            listed = await client.get("/api/v1/commercial-operations?status=ready", headers=headers)
            assert listed.status_code == 200
            assert [item["id"] for item in listed.json()["items"]] == [operation_id]

            link = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/links",
                headers=headers,
                json={
                    "link_type": "conversation",
                    "target_type": "conversation_thread",
                    "target_id": "thread-123",
                    "title": "Intake conversation",
                    "summary": "Initial operator goal intake.",
                    "source_name": "admin_dashboard",
                    "metadata": {"handoff": "operator"},
                },
            )
            assert link.status_code == 201
            link_body = link.json()
            assert link_body["workspace_id"] == "workspace-commercial-api"
            assert link_body["operation_id"] == operation_id
            assert link_body["link_type"] == "conversation"
            assert link_body["target_id"] == "thread-123"

            links = await client.get(f"/api/v1/commercial-operations/{operation_id}/links", headers=headers)
            assert links.status_code == 200
            assert [item["id"] for item in links.json()["items"]] == [link_body["id"]]

            hidden_links = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/links",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_links.status_code == 404

            deleted = await client.delete(
                f"/api/v1/commercial-operations/{operation_id}/links/{link_body['id']}",
                headers=headers,
            )
            assert deleted.status_code == 200
            assert deleted.json()["id"] == link_body["id"]

            links_after_delete = await client.get(f"/api/v1/commercial-operations/{operation_id}/links", headers=headers)
            assert links_after_delete.status_code == 200
            assert links_after_delete.json()["items"] == []

            invalid = await client.post(
                "/api/v1/commercial-operations",
                headers=headers,
                json={
                    "title": "Bad dates",
                    "objective": "Invalid date range",
                    "start_at": "2026-06-02T00:00:00Z",
                    "end_at": "2026-06-01T00:00:00Z",
                },
            )
            assert invalid.status_code == 422
    finally:
        await engine.dispose()
