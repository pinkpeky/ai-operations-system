"""RAG 写入流水线模块。

流水线负责文本切分、embedding 生成和 Qdrant 写入，不接入 LLM 和 Scheduler。
"""

import logging
from dataclasses import dataclass
from typing import Any

from app.rag.document_chunker import DocumentChunker
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
            embeddings = await self.embedding_client.embed_texts([chunk.text for chunk in chunks])
            chunk_ids = await self.vector_store.upsert_chunks(chunks=chunks, embeddings=embeddings)
            result = IngestionResult(
                collection_name=self.vector_store.collection_name,
                source_id=chunks[0].source_id,
                chunk_count=len(chunks),
                chunk_ids=chunk_ids,
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
