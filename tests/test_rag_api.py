"""RAG API 测试模块。

通过替换 pipeline 和 vector store 工厂验证 API 层请求和响应，不依赖真实 Qdrant。
"""

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import rag as rag_routes
from app.rag.ingestion import IngestionResult
from app.rag.vector_store import CollectionHealth, VectorSearchResult


class FakeIngestionPipeline:
    """RAG 写入流水线替身。"""

    async def ingest_text(
        self,
        text: str,
        metadata: dict[str, object] | None = None,
        source_id: str | None = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> IngestionResult:
        """返回固定写入结果。"""

        return IngestionResult(
            collection_name="api_test_collection",
            source_id=source_id or "generated-source",
            chunk_count=1,
            chunk_ids=["aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa"],
        )


class FakeRetrievalPipeline:
    """RAG 检索流水线替身。"""

    def __init__(self) -> None:
        self.vector_store = type("VectorStoreRef", (), {"collection_name": "api_test_collection"})()

    async def search(self, query: str, top_k: int = 5) -> list[VectorSearchResult]:
        """返回固定检索结果。"""

        return [
            VectorSearchResult(
                id="aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
                text="matched knowledge chunk",
                similarity_score=0.9,
                raw_score=0.9,
                metadata={"source_id": "source-1"},
                chunk_index=0,
            )
        ]


class FakeEmbeddingClient:
    """EmbeddingClient 替身。"""

    async def embed_query(self, query: str) -> list[float]:
        """返回固定查询向量。"""

        return [1.0, 0.0, 0.0]


class FakeVectorStore:
    """VectorStore 替身。"""

    collection_name = "api_test_collection"

    async def list_collection_names(self) -> list[str]:
        """返回固定 collection 列表。"""

        return ["api_test_collection"]

    async def get_collection_health(self) -> CollectionHealth:
        """返回固定 collection 健康信息。"""

        return CollectionHealth(
            collection_name=self.collection_name,
            exists=True,
            status="green",
            points_count=1,
            vectors_count=1,
            embedding_dimension=384,
        )

    async def similarity_search(self, query_embedding: list[float], top_k: int = 5) -> list[VectorSearchResult]:
        """返回固定检索结果。"""

        return [
            VectorSearchResult(
                id="aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
                text="debug knowledge chunk",
                similarity_score=0.8,
                raw_score=0.8,
                metadata={"source_id": "debug-source"},
                chunk_index=0,
            )
        ]


def create_test_client() -> TestClient:
    """创建只包含 RAG 路由的测试应用。"""

    app = FastAPI()
    app.include_router(rag_routes.router, prefix="/api/v1")
    return TestClient(app)


def test_rag_ingest_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """RAG ingest API 应返回写入结果。"""

    monkeypatch.setattr(
        rag_routes,
        "create_ingestion_pipeline",
        lambda settings, collection_name=None: FakeIngestionPipeline(),
    )
    client = create_test_client()

    response = client.post(
        "/api/v1/rag/ingest",
        json={
            "text": "knowledge text for ingest",
            "metadata": {"category": "demo"},
            "source_id": "source-1",
            "collection_name": "api_test_collection",
        },
    )

    assert response.status_code == 200
    assert response.json()["collection_name"] == "api_test_collection"
    assert response.json()["chunk_count"] == 1


def test_rag_search_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """RAG search API 应返回归一化分数。"""

    monkeypatch.setattr(
        rag_routes,
        "create_retrieval_pipeline",
        lambda settings, collection_name=None: FakeRetrievalPipeline(),
    )
    client = create_test_client()

    response = client.post(
        "/api/v1/rag/search",
        json={
            "query": "knowledge query",
            "top_k": 1,
            "collection_name": "api_test_collection",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["collection_name"] == "api_test_collection"
    assert body["items"][0]["text"] == "matched knowledge chunk"
    assert body["items"][0]["similarity_score"] == 0.9
    assert body["items"][0]["raw_score"] == 0.9


def test_rag_collections_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """RAG collections API 应返回 collection 健康信息。"""

    monkeypatch.setattr(
        rag_routes,
        "create_vector_store",
        lambda settings, collection_name=None: FakeVectorStore(),
    )
    client = create_test_client()

    response = client.get("/api/v1/rag/collections")

    assert response.status_code == 200
    body = response.json()
    assert body["collections"][0]["collection_name"] == "api_test_collection"
    assert body["collections"][0]["embedding_dimension"] == 384


def test_rag_debug_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """RAG debug API 应返回 query embedding 维度和分数细节。"""

    monkeypatch.setattr(rag_routes, "EmbeddingClient", lambda settings=None: FakeEmbeddingClient())
    monkeypatch.setattr(
        rag_routes,
        "create_vector_store",
        lambda settings, collection_name=None: FakeVectorStore(),
    )
    client = create_test_client()

    response = client.post(
        "/api/v1/rag/debug",
        json={
            "query": "debug query",
            "top_k": 1,
            "collection_name": "api_test_collection",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["query_embedding_dimension"] == 3
    assert body["retrieved_chunks"][0]["similarity_score"] == 0.8
    assert body["scores"][0]["raw_score"] == 0.8
