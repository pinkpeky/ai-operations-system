"""Phase 40 playbook API tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import conversation_approvals as approval_routes
from app.api.routes import conversation_playbooks as playbook_routes
from app.api.routes import conversations as conversation_routes
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session
from app.tools.base import ToolExecutionRecord


class FakeBrowserRegistry:
    async def execute_tool(self, tool_name, tool_input, context, agent_name):  # type: ignore[no-untyped-def]
        output = {"action_type": tool_input["action_type"]}
        if tool_input["action_type"] == "create_session":
            output["session"] = {"id": "66666666-6666-6666-6666-666666666666"}
        return ToolExecutionRecord(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=output,
            success=True,
            error=None,
            latency_ms=1,
        )


@pytest.mark.asyncio
async def test_playbook_api_list_run_and_approval_execute(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.conversation.services.conversation_service.build_default_tool_registry",
        lambda: FakeBrowserRegistry(),
    )

    async def fake_content_run(self, agent_input):  # type: ignore[no-untyped-def]
        return {"title": "API title", "description": agent_input["topic"], "tags": [], "cta": "Review.", "raw_response": "mock"}

    monkeypatch.setattr("app.conversation.services.conversation_service.ContentAgent.run", fake_content_run)
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
    app.include_router(playbook_routes.router, prefix="/api/v1")
    app.include_router(playbook_routes.runs_router, prefix="/api/v1")

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"X-Workspace-Id": "workspace-playbook-api", "X-User-Id": "user"}
            playbooks = await client.get("/api/v1/conversation-playbooks", headers=headers)
            assert playbooks.status_code == 200
            items = playbooks.json()["items"]
            content_id = next(item["id"] for item in items if item["name"] == "content_generation")
            browser_name = "browser_screenshot_report"

            content_run = await client.post(
                f"/api/v1/conversation-playbooks/{content_id}/run",
                headers=headers,
                json={"input": {"topic": "AI operations", "platform": "short_video", "style": "concise"}},
            )
            assert content_run.status_code == 200
            assert content_run.json()["status"] == "completed"

            thread = await client.post(
                "/api/v1/conversations",
                headers=headers,
                json={"title": "Playbook conversation", "metadata": {"phase": "40"}},
            )
            thread_id = thread.json()["id"]
            conversation_run = await client.post(
                f"/api/v1/conversations/{thread_id}/run",
                headers=headers,
                json={
                    "input": {"message": "open https://example.com and screenshot"},
                    "playbook_name": browser_name,
                    "mode": "review_first",
                },
            )
            assert conversation_run.status_code == 200
            approval_id = conversation_run.json()["approval_id"]
            assert conversation_run.json()["playbook_status"] == "waiting_approval"

            approved = await client.post(
                f"/api/v1/conversation-approvals/{approval_id}/approve",
                headers=headers,
                json={"reviewer_notes": "safe"},
            )
            assert approved.status_code == 200
            executed = await client.post(
                f"/api/v1/conversation-approvals/{approval_id}/execute",
                headers=headers,
                json={"input": {"approval_id": approval_id}},
            )
            assert executed.status_code == 200
            assert executed.json()["playbook_status"] == "completed"
    finally:
        await engine.dispose()
