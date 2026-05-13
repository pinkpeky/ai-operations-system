"""Tool API 执行测试。"""

from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import tools as tools_routes
from app.core.errors import AppError, app_error_handler
from app.db.postgres import get_session
from app.middleware.workspace_middleware import WorkspaceContextMiddleware
from app.tools.base import ToolExecutionRecord


class FakeTool:
    """API 测试用工具描述。"""

    name = "fake_tool"
    description = "Fake tool"
    permission_scopes = ["fake:read"]

    def input_json_schema(self) -> dict[str, Any]:
        return {"type": "object"}

    def output_json_schema(self) -> dict[str, Any]:
        return {"type": "object"}


class FakeRegistration:
    """API 测试用注册信息。"""

    def __init__(self) -> None:
        self.tool = FakeTool()
        self.enabled = True
        self.permission_scopes = ["fake:read"]


class FakeRegistry:
    """API 测试用 Registry。"""

    def list_tools(self, *, workspace_id: str | None = None, include_disabled: bool = False) -> list[FakeRegistration]:
        return [FakeRegistration()]

    def get_tool(self, tool_name: str, workspace_id: str | None = None) -> FakeTool:
        if tool_name != "fake_tool":
            raise KeyError(tool_name)
        return FakeTool()

    async def execute_tool(self, *, tool_name: str, tool_input: dict[str, Any], context, agent_name=None) -> ToolExecutionRecord:  # type: ignore[no-untyped-def]
        return ToolExecutionRecord(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output={"ok": True, "workspace_id": context.workspace_id},
            success=True,
            error=None,
            latency_ms=1,
        )


def create_client(monkeypatch) -> TestClient:  # type: ignore[no-untyped-def]
    """创建只挂载 tools 路由的测试应用。"""

    app = FastAPI()
    app.add_middleware(WorkspaceContextMiddleware)
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(tools_routes.router, prefix="/api/v1")

    async def fake_get_session():  # type: ignore[no-untyped-def]
        yield object()

    app.dependency_overrides[get_session] = fake_get_session
    monkeypatch.setattr(tools_routes, "build_default_tool_registry", lambda: FakeRegistry())
    return TestClient(app)


def test_tools_list_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """GET /tools 应返回工具清单。"""

    client = create_client(monkeypatch)

    response = client.get("/api/v1/tools", headers={"X-Workspace-Id": "workspace-a"})

    assert response.status_code == 200
    assert response.json()["items"][0]["name"] == "fake_tool"


def test_tool_execute_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """POST /tools/{tool_name}/execute 应返回执行结果。"""

    client = create_client(monkeypatch)

    response = client.post(
        "/api/v1/tools/fake_tool/execute",
        headers={"X-Workspace-Id": "workspace-a"},
        json={"input": {"hello": "world"}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["output"]["workspace_id"] == "workspace-a"


def test_tools_api_requires_workspace(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """工具 API 缺少 workspace header 时应返回清晰错误。"""

    client = create_client(monkeypatch)

    response = client.get("/api/v1/tools")

    assert response.status_code == 400
    assert response.json()["detail"] == "X-Workspace-Id header is required"
