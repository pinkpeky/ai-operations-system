"""Workspace middleware 测试模块。"""

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.middleware.workspace_middleware import WorkspaceContextMiddleware


def test_workspace_middleware_sets_request_state() -> None:
    """Middleware 应从 header 写入 request.state。"""

    app = FastAPI()
    app.add_middleware(WorkspaceContextMiddleware)

    @app.get("/echo")
    async def echo_context(request: Request) -> dict[str, str | None]:
        return {
            "workspace_id": request.state.workspace_id,
            "user_id": request.state.user_id,
        }

    client = TestClient(app)
    response = client.get("/echo", headers={"X-Workspace-Id": "workspace-a", "X-User-Id": "user-a"})

    assert response.status_code == 200
    assert response.json() == {"workspace_id": "workspace-a", "user_id": "user-a"}


def test_workspace_middleware_allows_missing_headers_for_public_routes() -> None:
    """Middleware 本身不拦截无 header 请求，具体路由依赖负责强制校验。"""

    app = FastAPI()
    app.add_middleware(WorkspaceContextMiddleware)

    @app.get("/public")
    async def public_route(request: Request) -> dict[str, str | None]:
        return {"workspace_id": request.state.workspace_id}

    client = TestClient(app)
    response = client.get("/public")

    assert response.status_code == 200
    assert response.json() == {"workspace_id": None}
