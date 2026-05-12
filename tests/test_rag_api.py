"""RAG API 测试模块。

通过替换 pipeline 和 vector store 工厂验证 API 层请求和响应，不依赖真实 Qdrant。
"""

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import rag as rag_routes
from app.core.errors import AppError, app_error_handler
from app.db.postgres import get_session
from app.middleware.workspace_middleware import WorkspaceContextMiddleware
from app.rag.hybrid_search import HybridSearchBundle
from app.rag.ingestion import IngestionResult
from app.rag.vector_store import CollectionHealth, VectorSearchResult
from app.reranker.providers.base import RerankedChunk
from app.services.document_lifecycle import DocumentLifecycleIngestResult


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


class FakeDocumentLifecycleService:
    """文档生命周期服务替身。"""

    async def ingest_text(
        self,
        text: str,
        metadata: dict[str, object] | None = None,
        source_id: str | None = None,
        source_name: str | None = None,
        source_type: str = "text",
        workspace_id: str | None = None,
        user_id: str | None = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> DocumentLifecycleIngestResult:
        """返回固定生命周期写入结果。"""

        return DocumentLifecycleIngestResult(
            collection_name="api_test_collection",
            source_id=source_id or "generated-source",
            document_id="11111111-1111-4111-8111-111111111111",
            version=1,
            chunk_count=1,
            chunk_ids=["aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa"],
        )


class FakeRetrievalPipeline:
    """RAG 检索流水线替身。"""

    def __init__(self) -> None:
        self.vector_store = type("VectorStoreRef", (), {"collection_name": "api_test_collection"})()

    async def search(
        self,
        query: str,
        top_k: int = 5,
        source_id: str | None = None,
        workspace_id: str | None = None,
        status: str = "active",
    ) -> list[VectorSearchResult]:
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


class FakeHybridSearchPipeline:
    """Hybrid Search Pipeline 替身。"""

    def __init__(self) -> None:
        self.vector_store = type("VectorStoreRef", (), {"collection_name": "api_test_collection"})()

    async def search(
        self,
        *,
        query: str,
        search_mode: str,
        dense_top_k: int,
        keyword_top_k: int,
        workspace_id: str,
        source_id: str | None = None,
        status: str = "active",
    ) -> HybridSearchBundle:
        """返回固定 Hybrid Search 中间结果。"""

        result = VectorSearchResult(
            id="aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
            text="matched knowledge chunk",
            similarity_score=0.9,
            raw_score=0.9,
            metadata={"source_id": "source-1"},
            chunk_index=0,
            dense_score=0.9,
            keyword_score=0.7,
            hybrid_score=0.86,
        )
        return HybridSearchBundle(
            search_mode=search_mode,  # type: ignore[arg-type]
            dense_results=[result] if search_mode in {"dense", "hybrid"} else [],
            keyword_results=[result] if search_mode in {"keyword", "hybrid"} else [],
            merged_results=[result],
        )


class FakeRerankerClient:
    """RerankerClient 替身。"""

    def __init__(self, settings=None) -> None:  # type: ignore[no-untyped-def]
        self.settings = settings

    async def rerank(
        self,
        *,
        query: str,
        chunks: list[VectorSearchResult],
        top_n: int | None = None,
    ) -> list[RerankedChunk]:
        """透传候选结果并附加 rerank_score。"""

        return [
            RerankedChunk(
                id=chunk.id,
                text=chunk.text,
                similarity_score=chunk.similarity_score,
                raw_score=chunk.raw_score,
                rerank_score=0.8,
                metadata=chunk.metadata,
                chunk_index=chunk.chunk_index,
                dense_score=chunk.dense_score,
                keyword_score=chunk.keyword_score,
                hybrid_score=chunk.hybrid_score,
            )
            for chunk in chunks[: top_n or len(chunks)]
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

    async def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        source_id: str | None = None,
        workspace_id: str | None = None,
        status: str = "active",
    ) -> list[VectorSearchResult]:
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


class FakeCollectionRepository:
    """CollectionRepository 替身。"""

    def __init__(self, session: object) -> None:
        self.session = session

    async def list_by_workspace(self, workspace_id: str, limit: int = 200) -> list[SimpleNamespace]:
        """返回当前 workspace 下的 collection 元数据。"""

        return [SimpleNamespace(collection_name="api_test_collection")]

    async def get_by_name(self, collection_name: str, workspace_id: str | None = None) -> SimpleNamespace | None:
        """返回固定 collection 元数据。"""

        return SimpleNamespace(collection_name=collection_name, workspace_id=workspace_id)


def create_test_client() -> TestClient:
    """创建只包含 RAG 路由的测试应用。"""

    app = FastAPI()
    app.add_middleware(WorkspaceContextMiddleware)
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(rag_routes.router, prefix="/api/v1")

    async def fake_get_session():  # type: ignore[no-untyped-def]
        yield object()

    app.dependency_overrides[get_session] = fake_get_session
    return TestClient(app)


def test_rag_ingest_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """RAG ingest API 应返回写入结果。"""

    monkeypatch.setattr(
        rag_routes,
        "create_document_lifecycle_service",
        lambda settings, session, collection_name=None: FakeDocumentLifecycleService(),
    )
    client = create_test_client()

    response = client.post(
        "/api/v1/rag/ingest",
        headers={"X-Workspace-Id": "workspace-api", "X-User-Id": "user-api"},
        json={
            "text": "knowledge text for ingest",
            "metadata": {"category": "demo"},
            "source_id": "source-1",
            "collection_name": "api_test_collection",
        },
    )

    assert response.status_code == 200
    assert response.json()["collection_name"] == "api_test_collection"
    assert response.json()["document_id"] == "11111111-1111-4111-8111-111111111111"
    assert response.json()["version"] == 1
    assert response.json()["chunk_count"] == 1


def test_rag_search_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """RAG search API 应返回归一化分数。"""

    monkeypatch.setattr(
        rag_routes,
        "create_hybrid_search_pipeline",
        lambda settings, session, collection_name=None: FakeHybridSearchPipeline(),
    )
    monkeypatch.setattr(rag_routes, "RerankerClient", FakeRerankerClient)
    client = create_test_client()

    response = client.post(
        "/api/v1/rag/search",
        headers={"X-Workspace-Id": "workspace-api"},
        json={
            "query": "knowledge query",
            "top_k": 1,
            "search_mode": "hybrid",
            "collection_name": "api_test_collection",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["collection_name"] == "api_test_collection"
    assert body["search_mode"] == "hybrid"
    assert body["items"][0]["text"] == "matched knowledge chunk"
    assert body["items"][0]["similarity_score"] == 0.9
    assert body["items"][0]["raw_score"] == 0.9
    assert body["items"][0]["dense_score"] == 0.9
    assert body["items"][0]["keyword_score"] == 0.7
    assert body["items"][0]["hybrid_score"] == 0.86


def test_rag_search_requires_workspace_header(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """RAG search 缺少 workspace header 时必须返回清晰错误，不能查全库。"""

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

    assert response.status_code == 400
    assert response.json()["detail"] == "X-Workspace-Id header is required"


def test_rag_collections_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """RAG collections API 应返回 collection 健康信息。"""

    monkeypatch.setattr(
        rag_routes,
        "create_vector_store",
        lambda settings, collection_name=None: FakeVectorStore(),
    )
    monkeypatch.setattr(rag_routes, "CollectionRepository", FakeCollectionRepository)
    client = create_test_client()

    response = client.get("/api/v1/rag/collections", headers={"X-Workspace-Id": "workspace-api"})

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
        headers={"X-Workspace-Id": "workspace-api"},
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
