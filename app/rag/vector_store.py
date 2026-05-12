"""Qdrant Vector Store 模块。

该模块封装 collection 管理、chunk 写入和相似度检索，是 RAG 基础层访问 Qdrant 的唯一业务入口。
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from app.db.qdrant import get_qdrant_client
from app.rag.document_chunker import DocumentChunk
from app.rag.result_normalizer import RetrievalResultNormalizer

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class VectorSearchResult:
    """向量检索结果。"""

    id: str
    text: str
    similarity_score: float
    raw_score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    chunk_index: int | None = None
    dense_score: float | None = None
    keyword_score: float | None = None
    hybrid_score: float | None = None

    @property
    def score(self) -> float:
        """兼容旧调用方的 score 字段，语义等同 similarity_score。"""

        return self.similarity_score


@dataclass(frozen=True, slots=True)
class CollectionHealth:
    """Qdrant collection 健康信息。"""

    collection_name: str
    exists: bool
    status: str
    points_count: int | None
    vectors_count: int | None
    embedding_dimension: int | None


class QdrantVectorStore:
    """Qdrant Collection 操作层。"""

    def __init__(
        self,
        collection_name: str,
        embedding_dimension: int,
        client: AsyncQdrantClient | None = None,
        allow_collection_delete: bool = False,
    ) -> None:
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension
        self._client = client
        self.allow_collection_delete = allow_collection_delete
        self.result_normalizer = RetrievalResultNormalizer()

    @property
    def client(self) -> AsyncQdrantClient:
        """获取 Qdrant 客户端。"""

        try:
            return self._client or get_qdrant_client()
        except Exception as exc:
            logger.exception("Failed to get Qdrant vector store client")
            raise RuntimeError("Qdrant vector store client is unavailable") from exc

    async def collection_exists(self) -> bool:
        """检查 collection 是否存在。"""

        try:
            exists = await self.client.collection_exists(self.collection_name)
            logger.info(
                "Qdrant collection existence checked",
                extra={"collection": self.collection_name, "exists": exists},
            )
            return exists
        except Exception as exc:
            logger.exception("Failed to check Qdrant collection", extra={"collection": self.collection_name})
            raise RuntimeError("Failed to check Qdrant collection") from exc

    async def ensure_collection(self) -> None:
        """确保 collection 存在，不存在则创建。"""

        try:
            if await self.collection_exists():
                info = await self.client.get_collection(self.collection_name)
                existing_dimension = self._extract_embedding_dimension(info)
                if existing_dimension is not None and existing_dimension != self.embedding_dimension:
                    raise ValueError(
                        "Qdrant collection embedding dimension mismatch: "
                        f"{self.collection_name} existing={existing_dimension}, requested={self.embedding_dimension}"
                    )
                return
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_dimension,
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info(
                "Qdrant collection created",
                extra={"collection": self.collection_name, "dimension": self.embedding_dimension},
            )
        except ValueError:
            logger.exception("Qdrant collection validation failed", extra={"collection": self.collection_name})
            raise
        except Exception as exc:
            logger.exception("Failed to ensure Qdrant collection", extra={"collection": self.collection_name})
            raise RuntimeError("Failed to ensure Qdrant collection") from exc

    async def list_collection_names(self) -> list[str]:
        """列出当前 Qdrant 中的 collection 名称。"""

        try:
            response = await self.client.get_collections()
            names = [collection.name for collection in response.collections]
            logger.info("Qdrant collections listed", extra={"count": len(names)})
            return names
        except Exception as exc:
            logger.exception("Failed to list Qdrant collections")
            raise RuntimeError("Failed to list Qdrant collections") from exc

    async def get_collection_health(self) -> CollectionHealth:
        """获取 collection 健康信息。"""

        try:
            if not await self.collection_exists():
                return CollectionHealth(
                    collection_name=self.collection_name,
                    exists=False,
                    status="missing",
                    points_count=None,
                    vectors_count=None,
                    embedding_dimension=None,
                )

            info = await self.client.get_collection(self.collection_name)
            status = getattr(info, "status", "unknown")
            health = CollectionHealth(
                collection_name=self.collection_name,
                exists=True,
                status=str(getattr(status, "value", status)),
                points_count=getattr(info, "points_count", None),
                vectors_count=getattr(info, "vectors_count", None),
                embedding_dimension=self._extract_embedding_dimension(info),
            )
            logger.info("Qdrant collection health checked", extra={"collection": self.collection_name})
            return health
        except Exception as exc:
            logger.exception("Failed to get Qdrant collection health", extra={"collection": self.collection_name})
            raise RuntimeError("Failed to get Qdrant collection health") from exc

    async def delete_collection(self) -> bool:
        """删除 collection，仅允许测试环境显式启用。"""

        try:
            if not self.allow_collection_delete:
                raise PermissionError("Collection deletion is only allowed in test environment")
            if not await self.collection_exists():
                return False
            deleted = await self.client.delete_collection(self.collection_name)
            logger.warning("Qdrant collection deleted", extra={"collection": self.collection_name})
            return bool(deleted)
        except PermissionError:
            logger.exception("Qdrant collection deletion denied")
            raise
        except Exception as exc:
            logger.exception("Failed to delete Qdrant collection", extra={"collection": self.collection_name})
            raise RuntimeError("Failed to delete Qdrant collection") from exc

    async def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> list[str]:
        """写入文档 chunk 和对应向量。"""

        try:
            if len(chunks) != len(embeddings):
                raise ValueError("Chunk count and embedding count must match")
            for embedding in embeddings:
                if len(embedding) != self.embedding_dimension:
                    raise ValueError("Embedding dimension does not match collection dimension")

            await self.ensure_collection()
            points = [
                models.PointStruct(
                    id=chunk.id,
                    vector=embedding,
                    payload={
                        "text": chunk.text,
                        "metadata": chunk.metadata,
                        "chunk_index": chunk.chunk_index,
                        "document_id": chunk.metadata.get("document_id"),
                        "source_id": chunk.metadata.get("source_id", chunk.source_id),
                        "version": chunk.metadata.get("version"),
                        "workspace_id": chunk.metadata.get("workspace_id"),
                        "user_id": chunk.metadata.get("user_id"),
                        "status": chunk.metadata.get("status", "active"),
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                    },
                )
                for chunk, embedding in zip(chunks, embeddings, strict=True)
            ]
            await self.client.upsert(collection_name=self.collection_name, points=points, wait=True)
            chunk_ids = [chunk.id for chunk in chunks]
            logger.info(
                "Qdrant chunks upserted",
                extra={"collection": self.collection_name, "count": len(chunk_ids)},
            )
            return chunk_ids
        except ValueError:
            logger.exception("Qdrant upsert validation failed")
            raise
        except Exception as exc:
            logger.exception("Failed to upsert Qdrant chunks", extra={"collection": self.collection_name})
            raise RuntimeError("Failed to upsert Qdrant chunks") from exc

    async def delete_points(self, point_ids: list[str]) -> int:
        """按 point ID 删除 Qdrant chunks。"""

        try:
            if not point_ids:
                return 0
            if not await self.collection_exists():
                return 0
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=point_ids),
                wait=True,
            )
            logger.info(
                "Qdrant points deleted",
                extra={"collection": self.collection_name, "count": len(point_ids)},
            )
            return len(point_ids)
        except Exception as exc:
            logger.exception("Failed to delete Qdrant points", extra={"collection": self.collection_name})
            raise RuntimeError("Failed to delete Qdrant points") from exc

    async def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        source_id: str | None = None,
        workspace_id: str | None = None,
        status: str = "active",
    ) -> list[VectorSearchResult]:
        """执行相似度检索。"""

        try:
            if top_k <= 0:
                raise ValueError("top_k must be positive")
            if len(query_embedding) != self.embedding_dimension:
                raise ValueError("Query embedding dimension does not match collection dimension")
            if not await self.collection_exists():
                logger.info("Qdrant collection missing during search", extra={"collection": self.collection_name})
                return []

            response = await self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                query_filter=self._build_query_filter(
                    status=status,
                    source_id=source_id,
                    workspace_id=workspace_id,
                ),
                limit=top_k,
                with_payload=True,
                with_vectors=False,
            )
            results = [self._build_search_result(point) for point in response.points]
            logger.info(
                "Qdrant similarity search completed",
                extra={"collection": self.collection_name, "top_k": top_k, "count": len(results)},
            )
            return results
        except ValueError:
            logger.exception("Qdrant search validation failed")
            raise
        except Exception as exc:
            logger.exception("Failed to search Qdrant collection", extra={"collection": self.collection_name})
            raise RuntimeError("Failed to search Qdrant collection") from exc

    def _build_query_filter(
        self,
        *,
        status: str | None,
        source_id: str | None,
        workspace_id: str | None,
    ) -> models.Filter | None:
        """构建 Qdrant 检索过滤器，默认只返回 active 文档 chunk。"""

        conditions: list[models.FieldCondition] = []
        if status is not None:
            conditions.append(
                models.FieldCondition(key="status", match=models.MatchValue(value=status))
            )
        if source_id is not None:
            conditions.append(
                models.FieldCondition(key="source_id", match=models.MatchValue(value=source_id))
            )
        if workspace_id is not None:
            conditions.append(
                models.FieldCondition(key="workspace_id", match=models.MatchValue(value=workspace_id))
            )
        if not conditions:
            return None
        return models.Filter(must=conditions)

    def _build_search_result(self, point: Any) -> VectorSearchResult:
        """将 Qdrant point 转换为业务检索结果。"""

        payload = dict(point.payload or {})
        metadata = dict(payload.get("metadata") or {})
        normalized_score = self.result_normalizer.normalize_score(float(point.score))
        return VectorSearchResult(
            id=str(point.id),
            text=str(payload.get("text") or ""),
            similarity_score=normalized_score.similarity_score,
            raw_score=normalized_score.raw_score,
            metadata=metadata,
            chunk_index=payload.get("chunk_index"),
            dense_score=normalized_score.similarity_score,
            keyword_score=None,
            hybrid_score=normalized_score.similarity_score,
        )

    def _extract_embedding_dimension(self, collection_info: Any) -> int | None:
        """从 Qdrant collection 信息中尽量提取向量维度。"""

        config = getattr(collection_info, "config", None)
        params = getattr(config, "params", None)
        vectors = getattr(params, "vectors", None)
        if vectors is None:
            return self.embedding_dimension
        if isinstance(vectors, dict):
            first_vector = next(iter(vectors.values()), None)
            return getattr(first_vector, "size", self.embedding_dimension)
        return getattr(vectors, "size", self.embedding_dimension)
