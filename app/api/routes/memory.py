"""Memory API 路由。"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session as get_db_session
from app.memory.services import MemoryService
from app.models.enums import ConversationSessionStatus
from app.schemas.memory import (
    AgentMemoryCreateRequest,
    AgentMemoryDeleteResponse,
    AgentMemoryListResponse,
    AgentMemoryResponse,
    ConversationMessageCreateRequest,
    ConversationMessageListResponse,
    ConversationMessageResponse,
    ConversationSessionCreateRequest,
    ConversationSessionListResponse,
    ConversationSessionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/sessions", response_model=ConversationSessionResponse, status_code=201)
async def create_session(
    request: ConversationSessionCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationSessionResponse:
    """创建 conversation session。"""

    try:
        service = MemoryService(session)
        created = await service.create_session(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            title=request.title,
            metadata=request.metadata,
        )
        return ConversationSessionResponse.from_model(created)
    except Exception as exc:
        logger.exception("Memory session create API failed")
        raise AppError(str(exc) or "Memory session create failed", status_code=500) from exc


@router.get("/sessions", response_model=ConversationSessionListResponse)
async def list_sessions(
    status: ConversationSessionStatus | None = Query(default=None, description="会话状态过滤"),
    limit: int = Query(default=100, ge=1, le=500, description="返回数量"),
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationSessionListResponse:
    """列出当前 workspace 会话。"""

    try:
        service = MemoryService(session)
        sessions = await service.list_sessions(
            workspace_id=context.workspace_id,
            status=status.value if status else None,
            limit=limit,
        )
        return ConversationSessionListResponse(items=[ConversationSessionResponse.from_model(item) for item in sessions])
    except Exception as exc:
        logger.exception("Memory session list API failed")
        raise AppError("Memory session list failed", status_code=500) from exc


@router.get("/sessions/{session_id}", response_model=ConversationSessionResponse)
async def get_memory_session(
    session_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationSessionResponse:
    """查询会话详情。"""

    try:
        service = MemoryService(session)
        conversation = await service.get_session(session_id=session_id, workspace_id=context.workspace_id)
        if conversation is None:
            raise AppError("Conversation session not found", status_code=404)
        return ConversationSessionResponse.from_model(conversation)
    except AppError:
        raise
    except Exception as exc:
        logger.exception("Memory session detail API failed", extra={"session_id": str(session_id)})
        raise AppError("Memory session detail failed", status_code=500) from exc


@router.post("/messages", response_model=ConversationMessageResponse, status_code=201)
async def append_message(
    request: ConversationMessageCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationMessageResponse:
    """追加会话消息。"""

    try:
        service = MemoryService(session)
        message = await service.append_message(
            workspace_id=context.workspace_id,
            session_id=request.session_id,
            role=request.role,
            content=request.content,
            token_count=request.token_count,
            metadata=request.metadata,
        )
        return ConversationMessageResponse.from_model(message)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Memory message append API failed")
        raise AppError("Memory message append failed", status_code=500) from exc


@router.get("/messages/{session_id}", response_model=ConversationMessageListResponse)
async def list_messages(
    session_id: UUID,
    limit: int = Query(default=50, ge=1, le=500, description="返回数量"),
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationMessageListResponse:
    """查询会话消息。"""

    try:
        service = MemoryService(session)
        messages = await service.list_messages(
            session_id=session_id,
            workspace_id=context.workspace_id,
            limit=limit,
        )
        return ConversationMessageListResponse(
            session_id=session_id,
            items=[ConversationMessageResponse.from_model(item) for item in messages],
        )
    except Exception as exc:
        logger.exception("Memory message list API failed", extra={"session_id": str(session_id)})
        raise AppError("Memory message list failed", status_code=500) from exc


@router.post("/memories", response_model=AgentMemoryResponse, status_code=201)
async def save_memory(
    request: AgentMemoryCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgentMemoryResponse:
    """保存 Agent Memory。"""

    try:
        service = MemoryService(session)
        memory = await service.save_memory(
            workspace_id=context.workspace_id,
            agent_name=request.agent_name,
            memory_type=request.memory_type,
            content=request.content,
            metadata=request.metadata,
            importance_score=request.importance_score,
        )
        return AgentMemoryResponse.from_model(memory)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Memory save API failed")
        raise AppError("Memory save failed", status_code=500) from exc


@router.get("/memories", response_model=AgentMemoryListResponse)
async def list_memories(
    query: str | None = Query(default=None, description="文本检索 query"),
    agent_name: str | None = Query(default=None, description="Agent 名称过滤"),
    memory_type: str | None = Query(default=None, description="Memory 类型过滤"),
    limit: int = Query(default=50, ge=1, le=500, description="返回数量"),
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgentMemoryListResponse:
    """检索当前 workspace Agent Memory。"""

    try:
        service = MemoryService(session)
        memories = await service.search_memory(
            workspace_id=context.workspace_id,
            query=query,
            agent_name=agent_name,
            memory_type=memory_type,
            limit=limit,
        )
        return AgentMemoryListResponse(items=[AgentMemoryResponse.from_model(item) for item in memories])
    except Exception as exc:
        logger.exception("Memory list API failed")
        raise AppError("Memory list failed", status_code=500) from exc


@router.delete("/memories/{memory_id}", response_model=AgentMemoryDeleteResponse)
async def delete_memory(
    memory_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgentMemoryDeleteResponse:
    """删除当前 workspace 的 Agent Memory。"""

    try:
        service = MemoryService(session)
        deleted = await service.delete_memory(workspace_id=context.workspace_id, memory_id=memory_id)
        return AgentMemoryDeleteResponse(memory_id=memory_id, deleted=deleted)
    except Exception as exc:
        logger.exception("Memory delete API failed", extra={"memory_id": str(memory_id)})
        raise AppError("Memory delete failed", status_code=500) from exc
