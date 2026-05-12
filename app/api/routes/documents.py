"""文档生命周期管理 API 路由模块。"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.rag import create_document_lifecycle_service
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.models.enums import DocumentStatus
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import (
    DocumentDeleteResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentReingestRequest,
    DocumentReingestResponse,
    DocumentResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    status: DocumentStatus | None = Query(default=None, description="文档状态过滤"),
    source_id: str | None = Query(default=None, description="来源 ID 过滤"),
    collection_name: str | None = Query(default=None, description="collection 过滤"),
    limit: int = Query(default=100, ge=1, le=500, description="返回数量"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> DocumentListResponse:
    """查询文档列表。"""

    try:
        repository = DocumentRepository(session)
        documents = await repository.list_documents(
            status=status.value if status is not None else None,
            source_id=source_id,
            collection_name=collection_name,
            workspace_id=context.workspace_id,
            limit=limit,
        )
        return DocumentListResponse(items=[DocumentResponse.from_model(document) for document in documents])
    except Exception as exc:
        logger.exception("Document list API failed")
        raise AppError("Document list failed", status_code=500) from exc


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> DocumentDetailResponse:
    """查询文档详情和 chunk 列表。"""

    try:
        repository = DocumentRepository(session)
        document = await repository.get_document(document_id)
        if document is None:
            raise AppError("Document not found", status_code=404)
        if document.workspace_id != context.workspace_id:
            raise AppError("Document not found in workspace", status_code=404)
        chunks = await repository.list_chunks(document_id)
        return DocumentDetailResponse.from_model(document, chunks)
    except AppError:
        raise
    except Exception as exc:
        logger.exception("Document detail API failed", extra={"document_id": str(document_id)})
        raise AppError("Document detail failed", status_code=500) from exc


@router.delete("/by-source/{source_id}", response_model=DocumentDeleteResponse)
async def delete_documents_by_source(
    source_id: str,
    collection_name: str | None = Query(default=None, description="可选 collection 过滤"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> DocumentDeleteResponse:
    """按 source_id 软删除文档和 chunks。"""

    try:
        settings = get_settings()
        service = create_document_lifecycle_service(
            settings=settings,
            session=session,
            collection_name=collection_name,
        )
        result = await service.delete_by_source(
            source_id=source_id,
            collection_name=collection_name,
            workspace_id=context.workspace_id,
        )
        return DocumentDeleteResponse(
            source_id=result.source_id,
            collection_name=result.collection_name,
            deleted_documents=result.deleted_documents,
            deleted_chunks=result.deleted_chunks,
            qdrant_deleted_points=result.qdrant_deleted_points,
        )
    except Exception as exc:
        logger.exception("Document delete API failed", extra={"source_id": source_id})
        raise AppError("Document delete failed", status_code=500) from exc


@router.post("/reingest", response_model=DocumentReingestResponse)
async def reingest_document(
    request: DocumentReingestRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> DocumentReingestResponse:
    """重新写入同一 source_id，旧版本会标记为 outdated。"""

    try:
        settings = get_settings()
        service = create_document_lifecycle_service(
            settings=settings,
            session=session,
            collection_name=request.collection_name,
        )
        result = await service.ingest_text(
            text=request.text,
            metadata=request.metadata,
            source_id=request.source_id,
            source_name=request.source_name,
            source_type=request.source_type,
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
        return DocumentReingestResponse(
            collection_name=result.collection_name,
            source_id=result.source_id,
            document_id=result.document_id,
            version=result.version,
            chunk_count=result.chunk_count,
            chunk_ids=result.chunk_ids,
        )
    except ValueError as exc:
        logger.warning("Document reingest API received invalid request", extra={"error": str(exc)})
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Document reingest API failed", extra={"source_id": request.source_id})
        raise AppError("Document reingest failed", status_code=500) from exc
