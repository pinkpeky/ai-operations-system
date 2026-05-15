"""Workflow graph API tests."""

from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from app.api.router import create_api_router
from app.core.workspace_context import get_workspace_context
from app.db.postgres import get_session
from app.workflow.services import WorkflowGraphService, WorkflowStateService


@pytest.mark.asyncio
async def test_workflow_graph_api_create_validate_plan_and_replay(session) -> None:  # type: ignore[no-untyped-def]
    app = FastAPI()
    app.include_router(create_api_router())

    async def override_session():  # type: ignore[no-untyped-def]
        yield session

    class Context:
        workspace_id = "workspace-graph-api"
        user_id = "user"

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_workspace_context] = lambda: Context()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create = await client.post(
            "/api/v1/workflow-graphs",
            json={
                "name": "API graph",
                "entry_node": "start",
                "nodes": [{"node_key": "start"}, {"node_key": "finish"}],
                "edges": [{"source_node_key": "start", "target_node_key": "finish", "edge_type": "success"}],
            },
        )

    assert create.status_code == 201
    graph_id = UUID(create.json()["id"])

    workflow = await WorkflowStateService(session).create_workflow_run(
        workspace_id="workspace-graph-api",
        source_type="api",
        workflow_graph_id=graph_id,
        graph_execution=True,
        current_node_key="start",
    )
    checkpoint = await WorkflowStateService(session).create_checkpoint(
        workspace_id="workspace-graph-api",
        workflow_run_id=workflow.id,
        checkpoint_name="api-checkpoint",
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        graphs = await client.get("/api/v1/workflow-graphs")
        validate = await client.post(f"/api/v1/workflow-graphs/{graph_id}/validate")
        run_graph = await client.get(f"/api/v1/workflow-runs/{workflow.id}/graph")
        planner = await client.get(f"/api/v1/workflow-runs/{workflow.id}/planner")
        replay = await client.post(
            f"/api/v1/workflow-runs/{workflow.id}/replay",
            json={"replay_source_checkpoint_id": str(checkpoint.id), "replay_reason": "api replay"},
        )

    assert graphs.status_code == 200
    assert validate.json()["valid"] is True
    assert run_graph.json()["id"] == str(graph_id)
    assert planner.json()["next_nodes"] == ["finish"]
    assert replay.status_code == 201
    assert replay.json()["replay_status"] == "created"


@pytest.mark.asyncio
async def test_workflow_graph_api_rejects_invalid_graph(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowGraphService(session)

    with pytest.raises(ValueError):
        await service.create_graph(
            workspace_id="workspace-graph-api-invalid",
            name="invalid",
            entry_node="missing",
            nodes=[{"node_key": "start"}],
            edges=[],
        )
