"""RAG 写入流水线模块。

流水线负责文本切分、embedding 生成和 Qdrant 写入，不接入 LLM 和 Scheduler。
"""

import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from app.rag.document_chunker import DocumentChunk, DocumentChunker
from app.rag.embedding_client import EmbeddingClient
from app.rag.vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class IngestionResult:
    """写入结果。"""

    collection_name: str
    source_id: str
    chunk_count: int
    chunk_ids: list[str]
    document_id: str | None = None
    version: int | None = None
    chunks: list[DocumentChunk] = field(default_factory=list)


class IngestionPipeline:
    """RAG 文档写入流水线。"""

    def __init__(
        self,
        embedding_client: EmbeddingClient,
        vector_store: QdrantVectorStore,
        chunker: DocumentChunker | None = None,
    ) -> None:
        self.embedding_client = embedding_client
        self.vector_store = vector_store
        self.chunker = chunker or DocumentChunker()

    async def ingest_text(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
        source_id: str | None = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        document_id: str | None = None,
        version: int | None = None,
        workspace_id: str | None = None,
        user_id: str | None = None,
        status: str = "active",
    ) -> IngestionResult:
        """写入一段文本到向量库。"""

        try:
            chunks = self.chunker.chunk_text(
                text=text,
                metadata=metadata,
                source_id=source_id,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            enriched_chunks = self._enrich_chunks(
                chunks=chunks,
                document_id=document_id,
                version=version,
                workspace_id=workspace_id,
                user_id=user_id,
                status=status,
            )
            embeddings = await self.embedding_client.embed_texts([chunk.text for chunk in enriched_chunks])
            self.vector_store.embedding_dimension = len(embeddings[0])
            chunk_ids = await self.vector_store.upsert_chunks(chunks=enriched_chunks, embeddings=embeddings)
            result = IngestionResult(
                collection_name=self.vector_store.collection_name,
                source_id=enriched_chunks[0].source_id,
                chunk_count=len(enriched_chunks),
                chunk_ids=chunk_ids,
                document_id=document_id,
                version=version,
                chunks=enriched_chunks,
            )
            logger.info(
                "RAG ingestion completed",
                extra={
                    "collection": result.collection_name,
                    "source_id": result.source_id,
                    "chunk_count": result.chunk_count,
                },
            )
            return result
        except ValueError:
            logger.exception("RAG ingestion validation failed")
            raise
        except Exception as exc:
            logger.exception("RAG ingestion failed")
            raise RuntimeError("RAG ingestion failed") from exc

    def _enrich_chunks(
        self,
        *,
        chunks: list[DocumentChunk],
        document_id: str | None,
        version: int | None,
        workspace_id: str | None,
        user_id: str | None,
        status: str,
    ) -> list[DocumentChunk]:
        """为 chunk 注入文档生命周期 metadata，并为不同版本生成独立 point ID。"""

        version_value = version or 1
        enriched_chunks: list[DocumentChunk] = []
        for chunk in chunks:
            point_namespace = document_id or chunk.source_id
            point_id = str(
                uuid5(
                    NAMESPACE_URL,
                    f"{point_namespace}:v{version_value}:{chunk.chunk_index}:{chunk.start_char}:{chunk.end_char}",
                )
            )
            chunk_metadata = {
                **chunk.metadata,
                "document_id": document_id,
                "source_id": chunk.source_id,
                "version": version_value,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "status": status,
            }
            enriched_chunks.append(
                DocumentChunk(
                    id=point_id,
                    text=chunk.text,
                    metadata=chunk_metadata,
                    chunk_index=chunk.chunk_index,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                    source_id=chunk.source_id,
                )
            )
        return enriched_chunks
