"""Workflow API route tests."""

from __future__ import annotations

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from app.api.router import create_api_router
from app.core.workspace_context import get_workspace_context
from app.db.postgres import get_session
from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_workflow_api_lists_steps_checkpoints_and_memory(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowStateService(session)
    workflow = await service.create_workflow_run(workspace_id="workspace-api", source_type="conversation")
    step = await service.start_step(
        workspace_id="workspace-api",
        workflow_run_id=workflow.id,
        step_index=0,
        step_name="API step",
        step_type="message",
    )
    await service.complete_step(workspace_id="workspace-api", workflow_step_id=step.id)
    await service.create_checkpoint(workspace_id="workspace-api", workflow_run_id=workflow.id, checkpoint_name="api")
    await service.create_memory_snapshot(workspace_id="workspace-api", workflow_run_id=workflow.id, memory_type="task_context")

    app = FastAPI()
    app.include_router(create_api_router())

    async def override_session():  # type: ignore[no-untyped-def]
        yield session

    class Context:
        workspace_id = "workspace-api"
        user_id = "user"

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_workspace_context] = lambda: Context()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        runs = await client.get("/api/v1/workflow-runs")
        steps = await client.get(f"/api/v1/workflow-runs/{workflow.id}/steps")
        checkpoints = await client.get(f"/api/v1/workflow-runs/{workflow.id}/checkpoints")
        memories = await client.get(f"/api/v1/workflow-runs/{workflow.id}/memory-snapshots")

    assert runs.status_code == 200
    assert runs.json()["items"][0]["id"] == str(workflow.id)
    assert steps.json()["items"][0]["step_name"] == "API step"
    assert checkpoints.json()["items"][0]["checkpoint_name"] == "api"
    assert memories.json()["items"][0]["memory_type"] == "task_context"
