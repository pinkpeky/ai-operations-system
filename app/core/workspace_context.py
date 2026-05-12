"""Workspace Context 工具模块。

该模块只负责从 request.state 读取工作区上下文，不实现完整认证或权限系统。
"""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Header, Request

from app.core.errors import AppError


@dataclass(frozen=True, slots=True)
class WorkspaceContext:
    """当前请求的工作区上下文。"""

    workspace_id: str
    user_id: str | None = None


def get_workspace_context(
    request: Request,
    x_workspace_id: Annotated[str | None, Header(alias="X-Workspace-Id")] = None,
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
) -> WorkspaceContext:
    """读取必需工作区上下文，缺失时阻止查全库。"""

    workspace_id = getattr(request.state, "workspace_id", None) or x_workspace_id
    user_id = getattr(request.state, "user_id", None) or x_user_id
    if not workspace_id:
        raise AppError("X-Workspace-Id header is required", status_code=400)
    return WorkspaceContext(workspace_id=str(workspace_id), user_id=str(user_id) if user_id else None)


def get_optional_workspace_context(
    request: Request,
    x_workspace_id: Annotated[str | None, Header(alias="X-Workspace-Id")] = None,
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
) -> WorkspaceContext | None:
    """读取可选工作区上下文。"""

    workspace_id = getattr(request.state, "workspace_id", None) or x_workspace_id
    user_id = getattr(request.state, "user_id", None) or x_user_id
    if not workspace_id:
        return None
    return WorkspaceContext(workspace_id=str(workspace_id), user_id=str(user_id) if user_id else None)
