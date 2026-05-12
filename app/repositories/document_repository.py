"""知识库文档 Repository 模块。"""

import logging
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk
from app.models.enums import DocumentIngestStatus, DocumentStatus

logger = logging.getLogger(__name__)


class DocumentRepository:
    """documents 和 document_chunks 数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_document(
        self,
        *,
        source_id: str,
        source_name: str | None,
        source_type: str,
        file_hash: str | None,
        version: int,
        collection_name: str,
        metadata: dict[str, Any],
        workspace_id: str | None = None,
        user_id: str | None = None,
    ) -> Document:
        """创建文档记录，事务由上层 Service 控制。"""

        document = Document(
            workspace_id=workspace_id,
            user_id=user_id,
            source_id=source_id,
            source_name=source_name,
            source_type=source_type,
            file_hash=file_hash,
            version=version,
            status=DocumentStatus.ACTIVE.value,
            collection_name=collection_name,
            document_metadata=metadata,
            chunk_count=0,
            ingest_status=DocumentIngestStatus.PENDING.value,
        )
        self.session.add(document)
        await self.session.flush()
        logger.info("Document record created", extra={"document_id": str(document.id), "source_id": source_id})
        return document

    async def create_chunks(self, chunks: Sequence[DocumentChunk]) -> list[DocumentChunk]:
        """批量创建 chunk 记录。"""

        self.session.add_all(list(chunks))
        await self.session.flush()
        logger.info("Document chunk records created", extra={"count": len(chunks)})
        return list(chunks)

    async def get_document(self, document_id: UUID) -> Document | None:
        """按 ID 查询文档。"""

        return await self.session.get(Document, document_id)

    async def list_chunks(self, document_id: UUID) -> list[DocumentChunk]:
        """查询文档 chunk 列表。"""

        statement = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_documents(
        self,
        *,
        status: str | None = None,
        source_id: str | None = None,
        collection_name: str | None = None,
        workspace_id: str | None = None,
        limit: int = 100,
    ) -> list[Document]:
        """按过滤条件查询文档列表。"""

        statement = select(Document)
        if status is not None:
            statement = statement.where(Document.status == status)
        if source_id is not None:
            statement = statement.where(Document.source_id == source_id)
        if collection_name is not None:
            statement = statement.where(Document.collection_name == collection_name)
        if workspace_id is not None:
            statement = statement.where(Document.workspace_id == workspace_id)
        statement = statement.order_by(Document.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_active_document_by_file_hash(
        self,
        *,
        file_hash: str,
        workspace_id: str,
        collection_name: str | None = None,
    ) -> Document | None:
        """按 file_hash 和 workspace 查询 active 文档，用于文件重复检测。"""

        statement = (
            select(Document)
            .where(
                Document.file_hash == file_hash,
                Document.workspace_id == workspace_id,
                Document.status == DocumentStatus.ACTIVE.value,
            )
            .order_by(Document.created_at.desc())
            .limit(1)
        )
        if collection_name is not None:
            statement = statement.where(Document.collection_name == collection_name)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update_document_metadata(
        self,
        *,
        document_id: str,
        metadata: dict[str, Any],
    ) -> None:
        """更新文档 metadata，用于写入文件导入结果摘要。"""

        statement = update(Document).where(Document.id == UUID(str(document_id))).values(document_metadata=metadata)
        await self.session.execute(statement)

    async def get_latest_version(
        self,
        *,
        source_id: str,
        collection_name: str,
        workspace_id: str | None = None,
    ) -> int:
        """获取同一来源在当前 collection/workspace 下的最新版本号。"""

        statement = select(func.max(Document.version)).where(
            Document.source_id == source_id,
            Document.collection_name == collection_name,
        )
        if workspace_id is None:
            statement = statement.where(Document.workspace_id.is_(None))
        else:
            statement = statement.where(Document.workspace_id == workspace_id)
        result = await self.session.execute(statement)
        return int(result.scalar_one_or_none() or 0)

    async def list_documents_for_source(
        self,
        *,
        source_id: str,
        collection_name: str | None = None,
        workspace_id: str | None = None,
        statuses: Sequence[str] | None = None,
        scope_to_workspace: bool = False,
    ) -> list[Document]:
        """查询同一 source_id 的文档，用于去重、删除和 re-ingest。"""

        statement = select(Document).where(Document.source_id == source_id)
        if collection_name is not None:
            statement = statement.where(Document.collection_name == collection_name)
        if workspace_id is not None:
            statement = statement.where(Document.workspace_id == workspace_id)
        elif scope_to_workspace:
            statement = statement.where(Document.workspace_id.is_(None))
        if statuses is not None:
            statement = statement.where(Document.status.in_(list(statuses)))
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_qdrant_point_ids(self, document_ids: Sequence[UUID]) -> list[str]:
        """查询一组文档对应的 Qdrant point IDs。"""

        if not document_ids:
            return []
        statement = select(DocumentChunk.qdrant_point_id).where(DocumentChunk.document_id.in_(list(document_ids)))
        result = await self.session.execute(statement)
        return [str(point_id) for point_id in result.scalars().all()]

    async def list_qdrant_point_ids_by_collection(self, document_ids: Sequence[UUID]) -> dict[str, list[str]]:
        """按 collection 查询一组文档对应的 Qdrant point IDs。"""

        if not document_ids:
            return {}
        statement = select(DocumentChunk.collection_name, DocumentChunk.qdrant_point_id).where(
            DocumentChunk.document_id.in_(list(document_ids))
        )
        result = await self.session.execute(statement)
        grouped: dict[str, list[str]] = {}
        for collection_name, point_id in result.all():
            grouped.setdefault(str(collection_name), []).append(str(point_id))
        return grouped

    async def mark_documents_status(self, document_ids: Sequence[UUID], status: DocumentStatus) -> int:
        """批量更新文档状态。"""

        if not document_ids:
            return 0
        statement = update(Document).where(Document.id.in_(list(document_ids))).values(status=status.value)
        result = await self.session.execute(statement)
        logger.info("Document records status updated", extra={"status": status.value, "count": result.rowcount or 0})
        return int(result.rowcount or 0)

    async def mark_chunks_status_by_documents(self, document_ids: Sequence[UUID], status: DocumentStatus) -> int:
        """批量更新文档下所有 chunk 状态。"""

        if not document_ids:
            return 0
        statement = update(DocumentChunk).where(DocumentChunk.document_id.in_(list(document_ids))).values(status=status.value)
        result = await self.session.execute(statement)
        logger.info("Document chunk records status updated", extra={"status": status.value, "count": result.rowcount or 0})
        return int(result.rowcount or 0)
