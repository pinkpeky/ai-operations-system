"""文件上传知识导入 API。"""

import logging
from dataclasses import asdict

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.rag import create_document_lifecycle_service
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.file_pipeline.services.upload_service import DuplicateStrategy, FileUploadService
from app.repositories.document_repository import DocumentRepository
from app.schemas.file import FileUploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])


def create_file_upload_service(
    *,
    settings: Settings,
    session: AsyncSession,
    collection_name: str | None,
) -> FileUploadService:
    """创建文件上传服务。"""

    return FileUploadService(
        settings=settings,
        lifecycle_service=create_document_lifecycle_service(
            settings=settings,
            session=session,
            collection_name=collection_name,
        ),
        document_repository=DocumentRepository(session),
    )


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(..., description="待导入知识库的文件，支持 PDF/DOCX/TXT/MD/CSV"),
    collection_name: str | None = Form(default=None, description="可选 Qdrant collection 名称"),
    duplicate_strategy: DuplicateStrategy = Form(default="skip", description="重复文件策略：skip 或 force_reingest"),
    chunk_size: int = Form(default=500, ge=1, le=10000, description="字符切分长度"),
    chunk_overlap: int = Form(default=50, ge=0, le=9999, description="相邻 chunk 重叠字符数"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> FileUploadResponse:
    """上传文件并导入 RAG 知识库。"""

    try:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        settings = get_settings()
        service = create_file_upload_service(
            settings=settings,
            session=session,
            collection_name=collection_name,
        )
        result = await service.upload_file(
            upload_file=file,
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            collection_name=collection_name,
            duplicate_strategy=duplicate_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        logger.info(
            "File upload API completed",
            extra={
                "upload_filename": result.filename,
                "file_type": result.file_type,
                "skipped_duplicate": result.skipped_duplicate,
                "chunk_count": result.chunk_count,
            },
        )
        return FileUploadResponse(**asdict(result))
    except ValueError as exc:
        logger.warning("File upload API received invalid request", extra={"error": str(exc)})
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("File upload API failed")
        raise AppError(str(exc) or "File upload failed", status_code=500) from exc
