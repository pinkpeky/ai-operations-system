"""RAG Eval API 路由模块。"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.rag_eval import (
    RAGEvalItemCreateRequest,
    RAGEvalItemListResponse,
    RAGEvalItemResponse,
    RAGEvalRunCreateRequest,
    RAGEvalRunListResponse,
    RAGEvalRunResponse,
    RAGEvalScoreUpdateRequest,
)
from app.services.rag_eval_service import RAGEvalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag/eval", tags=["rag-eval"])


def create_rag_eval_service(session: AsyncSession) -> RAGEvalService:
    """创建 RAG Eval Service。"""

    return RAGEvalService(session=session, settings=get_settings())


@router.post("/runs", response_model=RAGEvalRunResponse, status_code=201)
async def create_eval_run(
    request: RAGEvalRunCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> RAGEvalRunResponse:
    """创建 RAG Eval Run。"""

    try:
        service = create_rag_eval_service(session)
        run = await service.create_run(workspace_id=context.workspace_id, request=request)
        return RAGEvalRunResponse.from_model(run)
    except AppError:
        raise
    except Exception as exc:
        logger.exception("RAG eval run create API failed")
        raise AppError(f"RAG eval run create failed: {exc}", status_code=500) from exc


@router.get("/runs", response_model=RAGEvalRunListResponse)
async def list_eval_runs(
    limit: int = Query(default=100, ge=1, le=500, description="返回数量"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> RAGEvalRunListResponse:
    """查询当前 workspace 的 RAG Eval Runs。"""

    try:
        service = create_rag_eval_service(session)
        runs = await service.list_runs(workspace_id=context.workspace_id, limit=limit)
        return RAGEvalRunListResponse(items=[RAGEvalRunResponse.from_model(run) for run in runs])
    except Exception as exc:
        logger.exception("RAG eval run list API failed")
        raise AppError("RAG eval run list failed", status_code=500) from exc


@router.post("/runs/{run_id}/items", response_model=RAGEvalItemResponse, status_code=201)
async def create_eval_item(
    run_id: UUID,
    request: RAGEvalItemCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> RAGEvalItemResponse:
    """创建 RAG Eval Item。"""

    try:
        service = create_rag_eval_service(session)
        item = await service.create_item(workspace_id=context.workspace_id, run_id=run_id, request=request)
        return RAGEvalItemResponse.from_model(item)
    except AppError:
        raise
    except Exception as exc:
        logger.exception("RAG eval item create API failed", extra={"run_id": str(run_id)})
        raise AppError(f"RAG eval item create failed: {exc}", status_code=500) from exc


@router.get("/runs/{run_id}/items", response_model=RAGEvalItemListResponse)
async def list_eval_items(
    run_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> RAGEvalItemListResponse:
    """查询 RAG Eval Run 下的 Items。"""

    try:
        service = create_rag_eval_service(session)
        items = await service.list_items(workspace_id=context.workspace_id, run_id=run_id)
        return RAGEvalItemListResponse(items=[RAGEvalItemResponse.from_model(item) for item in items])
    except AppError:
        raise
    except Exception as exc:
        logger.exception("RAG eval item list API failed", extra={"run_id": str(run_id)})
        raise AppError("RAG eval item list failed", status_code=500) from exc


@router.patch("/items/{item_id}/score", response_model=RAGEvalItemResponse)
async def update_eval_item_score(
    item_id: UUID,
    request: RAGEvalScoreUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> RAGEvalItemResponse:
    """更新 RAG Eval Item 人工评分。"""

    try:
        service = create_rag_eval_service(session)
        item = await service.update_score(workspace_id=context.workspace_id, item_id=item_id, request=request)
        return RAGEvalItemResponse.from_model(item)
    except AppError:
        raise
    except Exception as exc:
        logger.exception("RAG eval item score API failed", extra={"item_id": str(item_id)})
        raise AppError(f"RAG eval item score failed: {exc}", status_code=500) from exc
