"""Conversation integration with workflow templates."""

from __future__ import annotations

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from app.api.router import create_api_router
from app.core.workspace_context import get_workspace_context
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_conversation_run_can_select_workflow_template(session) -> None:  # type: ignore[no-untyped-def]
    app = FastAPI()
    app.include_router(create_api_router())

    async def override_session():  # type: ignore[no-untyped-def]
        yield session

    class Context:
        workspace_id = "workspace-template-conversation"
        user_id = "user"

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_workspace_context] = lambda: Context()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        thread = await client.post("/api/v1/conversations", json={"title": "Template conversation"})
        thread_id = thread.json()["id"]
        run = await client.post(
            f"/api/v1/conversations/{thread_id}/run",
            json={
                "workflow_template_key": "content_generation_graph",
                "input": {"message": "Use template to draft AI automation copy", "topic": "AI automation"},
            },
        )
        events = await client.get(f"/api/v1/conversations/{thread_id}/events")

    assert run.status_code == 200
    payload = run.json()
    assert payload["workflow_template_key"] == "content_generation_graph"
    assert payload["workflow_template_run_id"]
    assert payload["workflow_run_id"]
    event_types = {item["event_type"] for item in events.json()["items"]}
    assert "workflow_template_selected" in event_types
