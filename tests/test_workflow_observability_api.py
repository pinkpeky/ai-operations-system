"""Workflow observability API tests."""

from __future__ import annotations

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from app.api.router import create_api_router
from app.core.workspace_context import get_workspace_context
from app.db.postgres import get_session
from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_workflow_observability_api_endpoints(session) -> None:  # type: ignore[no-untyped-def]
    app = FastAPI()
    app.include_router(create_api_router())

    async def override_session():  # type: ignore[no-untyped-def]
        yield session

    class Context:
        workspace_id = "observability-api-ws"
        user_id = "api-user"

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_workspace_context] = lambda: Context()

    state = WorkflowStateService(session)
    workflow = await state.create_workflow_run(workspace_id="observability-api-ws", source_type="api")
    step = await state.start_step(
        workspace_id="observability-api-ws",
        workflow_run_id=workflow.id,
        step_index=0,
        step_name="API step",
        step_type="no_op",
    )
    await state.complete_step(workspace_id="observability-api-ws", workflow_step_id=step.id, output_payload={"ok": True})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        traces = await client.get(f"/api/v1/workflow-runs/{workflow.id}/traces")
        diagnostics = await client.get(f"/api/v1/workflow-runs/{workflow.id}/diagnostics")
        analytics = await client.get(f"/api/v1/workflow-runs/{workflow.id}/analytics")
        replay = await client.post(f"/api/v1/workflow-runs/{workflow.id}/replay-sessions", json={"replay_mode": "dry_run"})
        replays = await client.get(f"/api/v1/workflow-replay-sessions?workflow_run_id={workflow.id}")
        summary = await client.get(f"/api/v1/workflow-runs/{workflow.id}/runtime-summary")

    assert traces.status_code == 200
    assert traces.json()["items"][0]["event_type"] == "node_started"
    assert diagnostics.status_code == 200
    assert analytics.json()["analytics"]["avg_retries"] == 0
    assert replay.status_code == 201
    assert replay.json()["replay_mode"] == "dry_run"
    assert replays.json()["items"][0]["id"] == replay.json()["id"]
    assert summary.json()["summary"]["step_count"] == 1
