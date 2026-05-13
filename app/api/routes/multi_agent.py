"""Multi-Agent API 路由。"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session as get_db_session
from app.multi_agent.services import MultiAgentService
from app.schemas.multi_agent import (
    AgentHandoffListResponse,
    AgentHandoffResponse,
    AgentMessageListResponse,
    AgentMessageResponse,
    AgentRunListResponse,
    AgentRunResponse,
    ExecuteAgentChainRequest,
    ExecuteAgentChainResponse,
    MultiAgentRunCreateRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/multi-agent", tags=["multi-agent"])


@router.post("/runs", response_model=AgentRunResponse, status_code=201)
async def create_run(
    request: MultiAgentRunCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgentRunResponse:
    """创建 Multi-Agent run。"""

    try:
        service = MultiAgentService(session, settings=get_settings())
        run = await service.create_run(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            session_id=request.session_id,
            root_agent=request.root_agent,
            run_input=request.input,
        )
        return AgentRunResponse.from_model(run)
    except KeyError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except PermissionError as exc:
        raise AppError(str(exc), status_code=403) from exc
    except Exception as exc:
        logger.exception("Multi-Agent create run API failed")
        raise AppError("Multi-Agent create run failed", status_code=500) from exc


@router.get("/runs", response_model=AgentRunListResponse)
async def list_runs(
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgentRunListResponse:
    """列出当前 workspace 的 Multi-Agent runs。"""

    service = MultiAgentService(session, settings=get_settings())
    runs = await service.list_runs(workspace_id=context.workspace_id, limit=limit)
    return AgentRunListResponse(items=[AgentRunResponse.from_model(run) for run in runs])


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
async def get_run(
    run_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgentRunResponse:
    """查询单个 Multi-Agent run。"""

    service = MultiAgentService(session, settings=get_settings())
    run = await service.get_run(run_id=run_id, workspace_id=context.workspace_id)
    if run is None:
        raise AppError("Multi-Agent run not found", status_code=404)
    return AgentRunResponse.from_model(run)


@router.post("/runs/{run_id}/execute-chain", response_model=ExecuteAgentChainResponse)
async def execute_chain(
    run_id: UUID,
    request: ExecuteAgentChainRequest,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ExecuteAgentChainResponse:
    """执行固定 Content Planning Chain。"""

    try:
        service = MultiAgentService(session, settings=get_settings())
        run = await service.get_run(run_id=run_id, workspace_id=context.workspace_id)
        if run is None:
            raise AppError("Multi-Agent run not found", status_code=404)
        run, agents_involved = await service.execute_agent_chain(
            run=run,
            chain_name=request.chain_name,
            chain_input=request.input,
        )
        messages = await service.list_messages(run_id=run.id, workspace_id=context.workspace_id)
        handoffs = await service.list_handoffs(run_id=run.id, workspace_id=context.workspace_id)
        return ExecuteAgentChainResponse(
            run=AgentRunResponse.from_model(run),
            agents_involved=agents_involved,
            success=run.status == "completed",
            error=run.error,
            duration_ms=run.duration_ms or 0,
            messages=[AgentMessageResponse.from_model(message) for message in messages],
            handoffs=[AgentHandoffResponse.from_model(handoff) for handoff in handoffs],
        )
    except AppError:
        raise
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Multi-Agent execute chain API failed", extra={"run_id": str(run_id)})
        raise AppError(str(exc) or "Multi-Agent execute chain failed", status_code=500) from exc


@router.get("/runs/{run_id}/messages", response_model=AgentMessageListResponse)
async def list_messages(
    run_id: UUID,
    limit: int = Query(default=200, ge=1, le=1000),
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgentMessageListResponse:
    """查询 run messages。"""

    service = MultiAgentService(session, settings=get_settings())
    run = await service.get_run(run_id=run_id, workspace_id=context.workspace_id)
    if run is None:
        raise AppError("Multi-Agent run not found", status_code=404)
    messages = await service.list_messages(run_id=run_id, workspace_id=context.workspace_id, limit=limit)
    return AgentMessageListResponse(run_id=run_id, items=[AgentMessageResponse.from_model(item) for item in messages])


@router.get("/runs/{run_id}/handoffs", response_model=AgentHandoffListResponse)
async def list_handoffs(
    run_id: UUID,
    limit: int = Query(default=200, ge=1, le=1000),
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgentHandoffListResponse:
    """查询 run handoffs。"""

    service = MultiAgentService(session, settings=get_settings())
    run = await service.get_run(run_id=run_id, workspace_id=context.workspace_id)
    if run is None:
        raise AppError("Multi-Agent run not found", status_code=404)
    handoffs = await service.list_handoffs(run_id=run_id, workspace_id=context.workspace_id, limit=limit)
    return AgentHandoffListResponse(run_id=run_id, items=[AgentHandoffResponse.from_model(item) for item in handoffs])
