"""知识库文档生命周期 Service 模块。

该 Service 负责 documents/document_chunks/collections_metadata 与 Qdrant 写入之间的编排。
"""

import hashlib
import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk as DocumentChunkModel
from app.models.enums import DocumentIngestStatus, DocumentStatus
from app.rag.ingestion import IngestionPipeline
from app.repositories.collection_repository import CollectionRepository
from app.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DocumentLifecycleIngestResult:
    """文档生命周期写入结果。"""

    collection_name: str
    source_id: str
    document_id: str
    version: int
    chunk_count: int
    chunk_ids: list[str]


@dataclass(frozen=True, slots=True)
class DocumentDeleteResult:
    """文档软删除结果。"""

    source_id: str
    collection_name: str | None
    deleted_documents: int
    deleted_chunks: int
    qdrant_deleted_points: int


class DocumentLifecycleService:
    """知识库文档生命周期编排服务。"""

    def __init__(
        self,
        *,
        session: AsyncSession,
        ingestion_pipeline: IngestionPipeline,
        document_repository: DocumentRepository | None = None,
        collection_repository: CollectionRepository | None = None,
    ) -> None:
        self.session = session
        self.ingestion_pipeline = ingestion_pipeline
        self.document_repository = document_repository or DocumentRepository(session)
        self.collection_repository = collection_repository or CollectionRepository(session)

    async def ingest_text(
        self,
        *,
        text: str,
        metadata: dict[str, Any] | None = None,
        source_id: str | None = None,
        source_name: str | None = None,
        source_type: str = "text",
        workspace_id: str | None = None,
        user_id: str | None = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        file_hash: str | None = None,
    ) -> DocumentLifecycleIngestResult:
        """写入文档，并处理同 source_id 的版本去重。"""

        normalized_source_id = source_id or str(uuid4())
        collection_name = self.ingestion_pipeline.vector_store.collection_name
        resolved_file_hash = file_hash or self._hash_text(text)
        try:
            embedding_dimension = await self.ingestion_pipeline.embedding_client.resolve_dimension()
            self.ingestion_pipeline.vector_store.embedding_dimension = embedding_dimension
            await self._ensure_collection_metadata(collection_name=collection_name, workspace_id=workspace_id)
            latest_version = await self.document_repository.get_latest_version(
                source_id=normalized_source_id,
                collection_name=collection_name,
                workspace_id=workspace_id,
            )
            version = latest_version + 1
            old_documents = await self.document_repository.list_documents_for_source(
                source_id=normalized_source_id,
                collection_name=collection_name,
                workspace_id=workspace_id,
                statuses=[DocumentStatus.ACTIVE.value],
                scope_to_workspace=True,
            )
            old_document_ids = [document.id for document in old_documents]
            old_point_ids = await self.document_repository.list_qdrant_point_ids(old_document_ids)

            document = await self.document_repository.create_document(
                source_id=normalized_source_id,
                source_name=source_name,
                source_type=source_type,
                file_hash=resolved_file_hash,
                version=version,
                collection_name=collection_name,
                metadata=metadata or {},
                workspace_id=workspace_id,
                user_id=user_id,
            )
            result = await self.ingestion_pipeline.ingest_text(
                text=text,
                metadata=metadata,
                source_id=normalized_source_id,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                document_id=str(document.id),
                version=version,
                workspace_id=workspace_id,
                user_id=user_id,
                status=DocumentStatus.ACTIVE.value,
            )
            chunk_models = [
                DocumentChunkModel(
                    document_id=document.id,
                    collection_name=collection_name,
                    chunk_index=chunk.chunk_index,
                    text=chunk.text,
                    qdrant_point_id=chunk.id,
                    chunk_metadata=chunk.metadata,
                    status=DocumentStatus.ACTIVE.value,
                )
                for chunk in result.chunks
            ]
            await self.document_repository.create_chunks(chunk_models)

            if old_document_ids:
                await self.document_repository.mark_documents_status(old_document_ids, DocumentStatus.OUTDATED)
                await self.document_repository.mark_chunks_status_by_documents(old_document_ids, DocumentStatus.OUTDATED)
                await self.ingestion_pipeline.vector_store.delete_points(old_point_ids)

            document.chunk_count = result.chunk_count
            document.ingest_status = DocumentIngestStatus.COMPLETED.value
            document.error_message = None
            await self.session.commit()
            logger.info(
                "Document lifecycle ingest completed",
                extra={
                    "document_id": str(document.id),
                    "source_id": normalized_source_id,
                    "version": version,
                    "chunk_count": result.chunk_count,
                },
            )
            return DocumentLifecycleIngestResult(
                collection_name=collection_name,
                source_id=normalized_source_id,
                document_id=str(document.id),
                version=version,
                chunk_count=result.chunk_count,
                chunk_ids=result.chunk_ids,
            )
        except ValueError:
            await self.session.rollback()
            logger.exception("Document lifecycle ingest validation failed")
            raise
        except Exception as exc:
            await self.session.rollback()
            logger.exception("Document lifecycle ingest failed", extra={"source_id": normalized_source_id})
            raise RuntimeError(f"Document lifecycle ingest failed: {exc}") from exc

    async def delete_by_source(
        self,
        *,
        source_id: str,
        collection_name: str | None = None,
        workspace_id: str | None = None,
    ) -> DocumentDeleteResult:
        """按 source_id 软删除文档和 chunks，并删除 Qdrant points。"""

        try:
            documents = await self.document_repository.list_documents_for_source(
                source_id=source_id,
                collection_name=collection_name,
                workspace_id=workspace_id,
                statuses=[DocumentStatus.ACTIVE.value, DocumentStatus.OUTDATED.value],
            )
            document_ids = [document.id for document in documents]
            points_by_collection = await self.document_repository.list_qdrant_point_ids_by_collection(document_ids)
            deleted_documents = await self.document_repository.mark_documents_status(document_ids, DocumentStatus.DELETED)
            deleted_chunks = await self.document_repository.mark_chunks_status_by_documents(document_ids, DocumentStatus.DELETED)
            qdrant_deleted_points = 0
            for grouped_collection_name, grouped_point_ids in points_by_collection.items():
                self.ingestion_pipeline.vector_store.collection_name = grouped_collection_name
                qdrant_deleted_points += await self.ingestion_pipeline.vector_store.delete_points(grouped_point_ids)
            await self.session.commit()
            logger.info(
                "Document lifecycle delete completed",
                extra={"source_id": source_id, "deleted_documents": deleted_documents, "deleted_chunks": deleted_chunks},
            )
            return DocumentDeleteResult(
                source_id=source_id,
                collection_name=collection_name,
                deleted_documents=deleted_documents,
                deleted_chunks=deleted_chunks,
                qdrant_deleted_points=qdrant_deleted_points,
            )
        except Exception as exc:
            await self.session.rollback()
            logger.exception("Document lifecycle delete failed", extra={"source_id": source_id})
            raise RuntimeError(f"Document lifecycle delete failed: {exc}") from exc

    async def _ensure_collection_metadata(self, *, collection_name: str, workspace_id: str | None) -> None:
        """确保 collection 元数据存在且向量维度一致。"""

        provider = self.ingestion_pipeline.embedding_client.provider
        await self.collection_repository.ensure_collection_metadata(
            collection_name=collection_name,
            workspace_id=workspace_id,
            embedding_provider=provider.provider_name,
            embedding_model_name=provider.model,
            embedding_dimension=provider.dimension,
            distance_metric="cosine",
        )

    def _hash_text(self, text: str) -> str:
        """计算文本哈希，用于后续重复内容判断预留。"""

        return hashlib.sha256(text.encode("utf-8")).hexdigest()
