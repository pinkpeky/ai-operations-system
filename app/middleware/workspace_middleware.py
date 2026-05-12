"""Workspace Context Middleware 模块。"""

import logging
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class WorkspaceContextMiddleware(BaseHTTPMiddleware):
    """从请求头读取工作区和用户上下文并写入 request.state。"""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """注入 X-Workspace-Id / X-User-Id 到 request.state。"""

        workspace_id = request.headers.get("X-Workspace-Id")
        user_id = request.headers.get("X-User-Id")
        request.state.workspace_id = workspace_id.strip() if workspace_id else None
        request.state.user_id = user_id.strip() if user_id else None
        logger.debug(
            "Workspace context parsed",
            extra={
                "workspace_id": request.state.workspace_id,
                "has_user_id": bool(request.state.user_id),
            },
        )
        return await call_next(request)
