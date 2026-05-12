"""RAG 检索流水线模块。

流水线负责 query embedding 和 Qdrant Top-K 检索，不拼接 Prompt，也不调用 LLM。
"""

import logging

from app.rag.embedding_client import EmbeddingClient
from app.rag.vector_store import QdrantVectorStore, VectorSearchResult

logger = logging.getLogger(__name__)


class RetrievalPipeline:
    """RAG 基础检索流水线。"""

    def __init__(self, embedding_client: EmbeddingClient, vector_store: QdrantVectorStore) -> None:
        self.embedding_client = embedding_client
        self.vector_store = vector_store

    async def search(
        self,
        query: str,
        top_k: int = 5,
        source_id: str | None = None,
        workspace_id: str | None = None,
        status: str = "active",
    ) -> list[VectorSearchResult]:
        """根据 query 检索相关 chunk。"""

        try:
            query_embedding = await self.embedding_client.embed_query(query)
            self.vector_store.embedding_dimension = len(query_embedding)
            results = await self.vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=top_k,
                source_id=source_id,
                workspace_id=workspace_id,
                status=status,
            )
            logger.info(
                "RAG retrieval completed",
                extra={
                    "collection": self.vector_store.collection_name,
                    "top_k": top_k,
                    "count": len(results),
                },
            )
            return results
        except ValueError:
            logger.exception("RAG retrieval validation failed")
            raise
        except Exception as exc:
            logger.exception("RAG retrieval failed")
            raise RuntimeError("RAG retrieval failed") from exc
