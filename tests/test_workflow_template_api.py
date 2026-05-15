"""Workflow template API tests."""

from __future__ import annotations

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from app.api.router import create_api_router
from app.core.workspace_context import get_workspace_context
from app.db.postgres import get_session


@pytest.mark.asyncio
async def test_workflow_template_api_list_validate_export_import_and_run(session) -> None:  # type: ignore[no-untyped-def]
    app = FastAPI()
    app.include_router(create_api_router())

    async def override_session():  # type: ignore[no-untyped-def]
        yield session

    class Context:
        workspace_id = "workspace-template-api"
        user_id = "user"

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_workspace_context] = lambda: Context()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        templates = await client.get("/api/v1/workflow-templates")
        assert templates.status_code == 200
        item = next(row for row in templates.json()["items"] if row["template_key"] == "content_generation_graph")
        template_id = item["id"]
        version_id = item["versions"][0]["id"]

        validate = await client.post(f"/api/v1/workflow-templates/{template_id}/validate")
        export = await client.get(f"/api/v1/workflow-templates/{template_id}/export")
        import_dry_run = await client.post(
            "/api/v1/workflow-templates/import",
            json={"template": {**export.json(), "template_key": "api_imported_template"}, "dry_run": True},
        )
        version = await client.get(f"/api/v1/workflow-templates/{template_id}/versions/{version_id}")
        run = await client.post(
            f"/api/v1/workflow-templates/{template_id}/run",
            json={"input": {"topic": "AI automation"}, "mode": "auto_safe"},
        )
        runs = await client.get("/api/v1/workflow-template-runs")

    assert validate.json()["compatible"] is True
    assert export.json()["template_key"] == "content_generation_graph"
    assert import_dry_run.json()["valid"] is True
    assert version.status_code == 200
    assert run.status_code == 201
    assert run.json()["workflow_run_id"]
    assert runs.status_code == 200
    assert len(runs.json()["items"]) == 1
