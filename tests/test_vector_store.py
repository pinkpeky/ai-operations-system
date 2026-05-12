"""QdrantVectorStore 测试模块。

使用内存 fake client 验证 collection、upsert、search、幂等创建和测试环境删除能力。
"""

from types import SimpleNamespace
from typing import Any

import pytest

from app.rag.document_chunker import DocumentChunk
from app.rag.embedding_client import EmbeddingClient
from app.rag.ingestion import IngestionPipeline
from app.rag.providers.mock_embedding_provider import MockEmbeddingProvider
from app.rag.retrieval import RetrievalPipeline
from app.rag.vector_store import QdrantVectorStore


class FakeQdrantClient:
    """用于单元测试的最小 Qdrant 替身。"""

    def __init__(self) -> None:
        self.collections: dict[str, dict[str, Any]] = {}
        self.create_count = 0

    async def collection_exists(self, collection_name: str) -> bool:
        """模拟 collection_exists。"""

        return collection_name in self.collections

    async def create_collection(self, collection_name: str, vectors_config: Any) -> bool:
        """模拟 create_collection。"""

        self.create_count += 1
        self.collections[collection_name] = {
            "vectors_config": vectors_config,
            "points": [],
        }
        return True

    async def get_collections(self) -> SimpleNamespace:
        """模拟 get_collections。"""

        return SimpleNamespace(
            collections=[SimpleNamespace(name=name) for name in self.collections.keys()]
        )

    async def get_collection(self, collection_name: str) -> SimpleNamespace:
        """模拟 get_collection。"""

        collection = self.collections[collection_name]
        vectors_config = collection["vectors_config"]
        return SimpleNamespace(
            status="green",
            points_count=len(collection["points"]),
            vectors_count=len(collection["points"]),
            config=SimpleNamespace(
                params=SimpleNamespace(
                    vectors=SimpleNamespace(size=vectors_config.size),
                )
            ),
        )

    async def delete_collection(self, collection_name: str) -> bool:
        """模拟 delete_collection。"""

        self.collections.pop(collection_name, None)
        return True

    async def delete(self, collection_name: str, points_selector: Any, wait: bool = True) -> None:
        """模拟按 point ID 删除。"""

        points = self.collections[collection_name]["points"]
        selected_ids = {str(point_id) for point_id in points_selector.points}
        self.collections[collection_name]["points"] = [point for point in points if str(point.id) not in selected_ids]

    async def upsert(self, collection_name: str, points: list[Any], wait: bool = True) -> None:
        """模拟 upsert。"""

        existing_points = self.collections[collection_name]["points"]
        point_map = {str(point.id): point for point in existing_points}
        for point in points:
            point_map[str(point.id)] = point
        self.collections[collection_name]["points"] = list(point_map.values())

    async def query_points(
        self,
        collection_name: str,
        query: list[float],
        query_filter: Any | None = None,
        limit: int = 10,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> SimpleNamespace:
        """模拟 query_points，使用点积排序。"""

        points = self.collections[collection_name]["points"]
        scored_points = []
        for point in points:
            if not self._matches_filter(point.payload, query_filter):
                continue
            score = sum(left * right for left, right in zip(point.vector, query, strict=True))
            scored_points.append(SimpleNamespace(id=point.id, payload=point.payload, score=score))
        scored_points.sort(key=lambda item: item.score, reverse=True)
        return SimpleNamespace(points=scored_points[:limit])

    def _matches_filter(self, payload: dict[str, Any], query_filter: Any | None) -> bool:
        """模拟 Qdrant must 过滤。"""

        if query_filter is None:
            return True
        for condition in getattr(query_filter, "must", []) or []:
            expected = getattr(condition.match, "value", None)
            if payload.get(condition.key) != expected:
                return False
        return True


@pytest.mark.asyncio
async def test_vector_store_upserts_and_searches_chunks() -> None:
    """VectorStore 应能创建 collection、写入 chunk 并检索。"""

    client = FakeQdrantClient()
    store = QdrantVectorStore(
        collection_name="test_collection",
        embedding_dimension=3,
        client=client,  # type: ignore[arg-type]
    )
    chunks = [
        DocumentChunk(id="aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa", text="alpha", metadata={"tag": "a"}, chunk_index=0),
        DocumentChunk(id="bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb", text="beta", metadata={"tag": "b"}, chunk_index=1),
    ]

    chunk_ids = await store.upsert_chunks(chunks=chunks, embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    results = await store.similarity_search(query_embedding=[1.0, 0.0, 0.0], top_k=1)

    assert await store.collection_exists() is True
    assert chunk_ids == [chunk.id for chunk in chunks]
    assert len(results) == 1
    assert results[0].text == "alpha"
    assert results[0].metadata["tag"] == "a"
    assert results[0].similarity_score == 1.0
    assert results[0].raw_score == 1.0


@pytest.mark.asyncio
async def test_collection_creation_is_idempotent() -> None:
    """collection 创建必须幂等，多次 ensure 不应重复创建。"""

    client = FakeQdrantClient()
    store = QdrantVectorStore(
        collection_name="idempotent_collection",
        embedding_dimension=3,
        client=client,  # type: ignore[arg-type]
    )

    await store.ensure_collection()
    await store.ensure_collection()

    assert client.create_count == 1


@pytest.mark.asyncio
async def test_collection_dimension_mismatch_raises_error() -> None:
    """已存在 collection 维度不一致时必须报错，避免向量混写。"""

    client = FakeQdrantClient()
    store = QdrantVectorStore(
        collection_name="dimension_collection",
        embedding_dimension=3,
        client=client,  # type: ignore[arg-type]
    )
    await store.ensure_collection()
    mismatched_store = QdrantVectorStore(
        collection_name="dimension_collection",
        embedding_dimension=4,
        client=client,  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError):
        await mismatched_store.ensure_collection()


@pytest.mark.asyncio
async def test_collection_health_lists_existing_collection() -> None:
    """collection health check 应返回维度和计数。"""

    client = FakeQdrantClient()
    store = QdrantVectorStore(
        collection_name="health_collection",
        embedding_dimension=3,
        client=client,  # type: ignore[arg-type]
    )

    await store.ensure_collection()
    names = await store.list_collection_names()
    health = await store.get_collection_health()

    assert names == ["health_collection"]
    assert health.exists is True
    assert health.embedding_dimension == 3
    assert health.points_count == 0


@pytest.mark.asyncio
async def test_ingestion_then_search_returns_results() -> None:
    """ingestion 后 search 必须能返回结果。"""

    client = FakeQdrantClient()
    embedding_client = EmbeddingClient(provider=MockEmbeddingProvider(dimension=32))
    store = QdrantVectorStore(
        collection_name="pipeline_collection",
        embedding_dimension=32,
        client=client,  # type: ignore[arg-type]
    )
    ingestion = IngestionPipeline(embedding_client=embedding_client, vector_store=store)
    retrieval = RetrievalPipeline(embedding_client=embedding_client, vector_store=store)

    await ingestion.ingest_text(
        text="Phase 3.5 improves embedding pipeline quality and Qdrant retrieval validation.",
        metadata={"phase": "3.5"},
        source_id="pipeline-source",
        chunk_size=80,
        chunk_overlap=10,
    )
    results = await retrieval.search(query="embedding pipeline Qdrant retrieval", top_k=3)

    assert len(results) >= 1
    assert results[0].similarity_score >= 0.0
    assert results[0].raw_score >= 0.0


@pytest.mark.asyncio
async def test_vector_store_deletes_collection_only_when_allowed() -> None:
    """删除 collection 必须显式允许，避免误删真实数据。"""

    client = FakeQdrantClient()
    protected_store = QdrantVectorStore(
        collection_name="protected",
        embedding_dimension=3,
        client=client,  # type: ignore[arg-type]
    )
    await protected_store.ensure_collection()

    with pytest.raises(PermissionError):
        await protected_store.delete_collection()

    test_store = QdrantVectorStore(
        collection_name="protected",
        embedding_dimension=3,
        client=client,  # type: ignore[arg-type]
        allow_collection_delete=True,
    )

    assert await test_store.delete_collection() is True
    assert await test_store.collection_exists() is False
