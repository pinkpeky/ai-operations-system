"""文档生命周期 API 数据模型模块。"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.document import Document, DocumentChunk
from app.models.enums import DocumentStatus
from app.schemas.rag import IngestRequest, IngestResponse


class DocumentChunkResponse(BaseModel):
    """文档 chunk 响应。"""

    id: UUID
    document_id: UUID
    collection_name: str
    chunk_index: int
    text: str
    qdrant_point_id: str
    metadata: dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, chunk: DocumentChunk) -> "DocumentChunkResponse":
        """从 ORM 对象构建响应，兼容 metadata 保留字段映射。"""

        return cls(
            id=chunk.id,
            document_id=chunk.document_id,
            collection_name=chunk.collection_name,
            chunk_index=chunk.chunk_index,
            text=chunk.text,
            qdrant_point_id=chunk.qdrant_point_id,
            metadata=chunk.chunk_metadata,
            status=chunk.status,
            created_at=chunk.created_at,
            updated_at=chunk.updated_at,
        )


class DocumentResponse(BaseModel):
    """文档响应。"""

    id: UUID
    workspace_id: str | None
    user_id: str | None
    source_id: str
    source_name: str | None
    source_type: str
    file_hash: str | None
    version: int
    status: str
    collection_name: str
    metadata: dict[str, Any]
    chunk_count: int
    ingest_status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, document: Document) -> "DocumentResponse":
        """从 ORM 对象构建响应，兼容 metadata 保留字段映射。"""

        return cls(
            id=document.id,
            workspace_id=document.workspace_id,
            user_id=document.user_id,
            source_id=document.source_id,
            source_name=document.source_name,
            source_type=document.source_type,
            file_hash=document.file_hash,
            version=document.version,
            status=document.status,
            collection_name=document.collection_name,
            metadata=document.document_metadata,
            chunk_count=document.chunk_count,
            ingest_status=document.ingest_status,
            error_message=document.error_message,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


class DocumentDetailResponse(DocumentResponse):
    """文档详情响应，包含 chunk 列表。"""

    chunks: list[DocumentChunkResponse] = Field(default_factory=list)

    @classmethod
    def from_model(cls, document: Document, chunks: list[DocumentChunk]) -> "DocumentDetailResponse":
        """从 ORM 对象构建详情响应。"""

        base = DocumentResponse.from_model(document).model_dump()
        return cls(
            **base,
            chunks=[DocumentChunkResponse.from_model(chunk) for chunk in chunks],
        )


class DocumentListResponse(BaseModel):
    """文档列表响应。"""

    items: list[DocumentResponse]


class DocumentDeleteResponse(BaseModel):
    """文档删除响应。"""

    source_id: str
    collection_name: str | None
    deleted_documents: int
    deleted_chunks: int
    qdrant_deleted_points: int


class DocumentReingestRequest(IngestRequest):
    """文档重新写入请求。"""

    source_id: str = Field(min_length=1, max_length=255, description="必须指定需要重新写入的来源 ID")


class DocumentReingestResponse(IngestResponse):
    """文档重新写入响应。"""


class DocumentListFilter(BaseModel):
    """文档列表过滤条件。"""

    status: DocumentStatus | None = None
    source_id: str | None = None
    collection_name: str | None = None
    workspace_id: str | None = None
