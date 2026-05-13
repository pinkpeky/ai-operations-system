"""Tool Calling API 路由。"""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.repositories.tool_call_repository import ToolCallLogRepository
from app.schemas.tool import (
    ToolCallLogListResponse,
    ToolCallLogResponse,
    ToolExecuteRequest,
    ToolExecuteResponse,
    ToolInfoResponse,
    ToolListResponse,
)
from app.tools.base import ToolExecutionContext
from app.tools.registry import ToolRegistration, build_default_tool_registry

logger = logging.getLogger(__name__)

router = APIRouter(tags=["tools"])


def build_tool_info(registration: ToolRegistration) -> ToolInfoResponse:
    """将内部注册信息转换为 API 响应。"""

    tool = registration.tool
    return ToolInfoResponse(
        name=tool.name,
        description=tool.description,
        input_schema=tool.input_json_schema(),
        output_schema=tool.output_json_schema(),
        enabled=registration.enabled,
        permission_scopes=registration.permission_scopes,
    )


@router.get("/tools", response_model=ToolListResponse)
async def list_tools(context: WorkspaceContext = Depends(get_workspace_context)) -> ToolListResponse:
    """列出当前 workspace 可用工具。"""

    try:
        registry = build_default_tool_registry()
        registrations = registry.list_tools(workspace_id=context.workspace_id)
        return ToolListResponse(items=[build_tool_info(registration) for registration in registrations])
    except Exception as exc:
        logger.exception("Tool list API failed")
        raise AppError("Tool list failed", status_code=500) from exc


@router.get("/tools/{tool_name}", response_model=ToolInfoResponse)
async def get_tool(tool_name: str, context: WorkspaceContext = Depends(get_workspace_context)) -> ToolInfoResponse:
    """查询单个工具信息。"""

    try:
        registry = build_default_tool_registry()
        _ = registry.get_tool(tool_name, workspace_id=context.workspace_id)
        registration = next(item for item in registry.list_tools(workspace_id=context.workspace_id) if item.tool.name == tool_name)
        return build_tool_info(registration)
    except KeyError as exc:
        raise AppError("Tool not found", status_code=404) from exc
    except PermissionError as exc:
        raise AppError(str(exc), status_code=403) from exc
    except StopIteration as exc:
        raise AppError("Tool not found", status_code=404) from exc
    except Exception as exc:
        logger.exception("Tool detail API failed", extra={"tool_name": tool_name})
        raise AppError("Tool detail failed", status_code=500) from exc


@router.post("/tools/{tool_name}/execute", response_model=ToolExecuteResponse)
async def execute_tool(
    tool_name: str,
    request: ToolExecuteRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ToolExecuteResponse:
    """手动执行指定工具。"""

    try:
        registry = build_default_tool_registry()
        execution_context = ToolExecutionContext(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            session=session,
        )
        record = await registry.execute_tool(
            tool_name=tool_name,
            tool_input=request.input,
            context=execution_context,
        )
        return ToolExecuteResponse(
            tool_name=record.tool_name,
            success=record.success,
            output=record.tool_output,
            error=record.error,
            latency_ms=record.latency_ms,
        )
    except Exception as exc:
        logger.exception("Tool execution API failed", extra={"tool_name": tool_name})
        raise AppError("Tool execution failed", status_code=500) from exc


@router.get("/tool-calls", response_model=ToolCallLogListResponse)
async def list_tool_call_logs(
    tool_name: str | None = Query(default=None, description="工具名称过滤"),
    agent_name: str | None = Query(default=None, description="Agent 名称过滤"),
    success: bool | None = Query(default=None, description="是否成功过滤"),
    limit: int = Query(default=100, ge=1, le=500, description="返回数量"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ToolCallLogListResponse:
    """查询当前 workspace 的工具调用日志。"""

    try:
        repository = ToolCallLogRepository(session)
        logs = await repository.list_logs(
            workspace_id=context.workspace_id,
            tool_name=tool_name,
            agent_name=agent_name,
            success=success,
            limit=limit,
        )
        return ToolCallLogListResponse(items=[ToolCallLogResponse.from_model(log) for log in logs])
    except Exception as exc:
        logger.exception("Tool call log list API failed")
        raise AppError("Tool call log list failed", status_code=500) from exc
