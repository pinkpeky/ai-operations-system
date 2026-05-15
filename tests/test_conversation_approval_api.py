"""Phase 39 conversation approval API tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import conversation_approvals as approval_routes
from app.api.routes import conversations as conversation_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session
from app.tools.base import ToolExecutionRecord


class FakeBrowserRegistry:
    async def execute_tool(self, tool_name, tool_input, context, agent_name):  # type: ignore[no-untyped-def]
        output = {"action_type": tool_input["action_type"]}
        if tool_input["action_type"] == "create_session":
            output["session"] = {"id": "33333333-3333-3333-3333-333333333333"}
        if tool_input["action_type"] == "get_page":
            output["title"] = "Example Domain"
        return ToolExecutionRecord(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=output,
            success=True,
            error=None,
            latency_ms=1,
        )


@pytest.mark.asyncio
async def test_conversation_approval_api_review_approve_execute_and_reject(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.conversation.services.conversation_service.build_default_tool_registry",
        lambda: FakeBrowserRegistry(),
    )
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
    app.include_router(approval_routes.router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"X-Workspace-Id": "workspace-approval-api", "X-User-Id": "user-approval-api"}
            created = await client.post(
                "/api/v1/conversations",
                headers=headers,
                json={"title": "Approval API", "metadata": {"phase": "39"}},
            )
            assert created.status_code == 201
            thread_id = created.json()["id"]

            run = await client.post(
                f"/api/v1/conversations/{thread_id}/run",
                headers=headers,
                json={"input": {"message": "open https://example.com and screenshot"}, "mode": "review_first"},
            )
            assert run.status_code == 200
            body = run.json()
            assert body["approval_required"] is True
            approval_id = body["approval_id"]

            approvals = await client.get(f"/api/v1/conversations/{thread_id}/approvals", headers=headers)
            assert approvals.status_code == 200
            assert approvals.json()["items"][0]["approval_status"] == "pending"

            approved = await client.post(
                f"/api/v1/conversation-approvals/{approval_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Looks safe to execute."},
            )
            assert approved.status_code == 200
            assert approved.json()["approval_status"] == "approved"

            executed = await client.post(
                f"/api/v1/conversation-approvals/{approval_id}/execute",
                headers=headers,
                json={"input": {"approval_id": approval_id}},
            )
            assert executed.status_code == 200
            assert executed.json()["approval_status"] == "executed"

            repeat = await client.post(
                f"/api/v1/conversation-approvals/{approval_id}/execute",
                headers=headers,
                json={"input": {"approval_id": approval_id}},
            )
            assert repeat.status_code == 400

            second = await client.post(
                f"/api/v1/conversations/{thread_id}/run",
                headers=headers,
                json={"input": {"message": "open https://example.com and screenshot again"}, "mode": "review_first"},
            )
            rejected_id = second.json()["approval_id"]
            rejected = await client.post(
                f"/api/v1/conversation-approvals/{rejected_id}/reject",
                headers=headers,
                json={"reviewer_notes": "Do not execute this action."},
            )
            assert rejected.status_code == 200
            blocked = await client.post(
                f"/api/v1/conversation-approvals/{rejected_id}/execute",
                headers=headers,
                json={"input": {"approval_id": rejected_id}},
            )
            assert blocked.status_code == 400
    finally:
        await engine.dispose()
