"""Agentic RAG API 测试模块。

验证 /api/v1/agentic-rag/query 的响应结构，不依赖真实 Qdrant 或真实 LLM。
"""

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import agentic_rag as agentic_rag_routes
from app.db.postgres import get_session
from app.rag.hybrid_search import HybridSearchBundle
from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.base import RerankedChunk
from app.schemas.llm import LLMRequest, LLMResponse


class FakeLLMClient:
    """Agentic RAG API 测试用 LLM Client 替身。"""

    def __init__(self, settings=None) -> None:  # type: ignore[no-untyped-def]
        self.settings = settings

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """返回固定 Mock 响应。"""

        return LLMResponse(
            provider="mock",
            model="mock-llm",
            content="api fake agentic rag answer",
        )


class FakeRetrievalPipeline:
    """Agentic RAG API 测试用 Retrieval Pipeline 替身。"""

    def __init__(self) -> None:
        self.vector_store = SimpleNamespace(collection_name="agentic_api_collection")
        self.embedding_client = SimpleNamespace(
            provider=SimpleNamespace(provider_name="mock", model="mock-embedding-model")
        )

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
                id="bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb",
                text="Agentic RAG uses retrieval context before calling the mock LLM.",
                similarity_score=0.77,
                raw_score=0.769,
                metadata={"source_id": "api-source"},
                chunk_index=1,
            )
        ]


class FakeHybridSearchPipeline:
    """Agentic RAG API 测试用 Hybrid Search Pipeline 替身。"""

    def __init__(self) -> None:
        self.vector_store = SimpleNamespace(collection_name="agentic_api_collection")
        self.embedding_client = SimpleNamespace(
            provider=SimpleNamespace(provider_name="mock", model="mock-embedding-model")
        )

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
        """返回固定 hybrid 候选结果。"""

        result = VectorSearchResult(
            id="bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb",
            text="Agentic RAG uses retrieval context before calling the mock LLM.",
            similarity_score=0.77,
            raw_score=0.769,
            metadata={"source_id": "api-source", "workspace_id": workspace_id},
            chunk_index=1,
            dense_score=0.77,
            keyword_score=0.6,
            hybrid_score=0.752,
        )
        return HybridSearchBundle(
            search_mode=search_mode,  # type: ignore[arg-type]
            dense_results=[result],
            keyword_results=[result],
            merged_results=[result],
        )


class FakeRerankerClient:
    """Agentic RAG API 测试用 Reranker Client 替身。"""

    def __init__(self, settings=None) -> None:  # type: ignore[no-untyped-def]
        self.settings = settings
        self.provider = SimpleNamespace(provider_name="mock", model="mock-reranker")

    async def rerank(
        self,
        *,
        query: str,
        chunks: list[VectorSearchResult],
        top_n: int | None = None,
    ) -> list[RerankedChunk]:
        """返回固定 rerank 结果。"""

        return [
            RerankedChunk(
                id=chunk.id,
                text=chunk.text,
                similarity_score=chunk.similarity_score,
                raw_score=chunk.raw_score,
                rerank_score=0.7,
                metadata=chunk.metadata,
                chunk_index=chunk.chunk_index,
                dense_score=chunk.dense_score,
                keyword_score=chunk.keyword_score,
                hybrid_score=chunk.hybrid_score,
            )
            for chunk in chunks[: top_n or len(chunks)]
        ]


def create_test_client() -> TestClient:
    """创建只包含 Agentic RAG 路由的测试应用。"""

    app = FastAPI()
    app.include_router(agentic_rag_routes.router, prefix="/api/v1")

    async def fake_get_session():  # type: ignore[no-untyped-def]
        yield object()

    app.dependency_overrides[get_session] = fake_get_session
    return TestClient(app)


def test_agentic_rag_query_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Agentic RAG API 应返回答案、检索结果和 debug 信息。"""

    monkeypatch.setattr(agentic_rag_routes, "LLMClient", FakeLLMClient)
    monkeypatch.setattr(agentic_rag_routes, "RerankerClient", FakeRerankerClient)
    monkeypatch.setattr(
        agentic_rag_routes,
        "create_hybrid_search_pipeline",
        lambda settings, session, collection_name=None: FakeHybridSearchPipeline(),
    )
    client = create_test_client()

    response = client.post(
        "/api/v1/agentic-rag/query",
        headers={"X-Workspace-Id": "workspace-api"},
        json={
            "query": "Phase 3.5 做了哪些 RAG 增强？",
            "collection_name": "agentic_api_collection",
            "top_k": 3,
            "debug": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "api fake agentic rag answer"
    assert body["used_retrieval"] is True
    assert body["provider"] == "mock"
    assert body["model"] == "mock-llm"
    assert body["retrieved_chunks"][0]["similarity_score"] == 0.77
    assert body["debug"]["retrieved_count"] == 1
    assert body["debug"]["workspace_id"] == "workspace-api"
    assert body["debug"]["collection_name"] == "agentic_api_collection"
    assert body["debug"]["similarity_scores"] == [0.77]
    assert body["debug"]["search_mode"] == "hybrid"
    assert body["debug"]["dense_results_count"] == 1
    assert body["debug"]["keyword_results_count"] == 1
    assert body["debug"]["merged_results_count"] == 1
    assert body["debug"]["final_results_count"] == 1
    assert body["debug"]["hybrid_scores"] == [0.752]
    assert body["debug"]["reranker_provider"] == "mock"
    assert body["debug"]["reranker_model"] == "mock-reranker"
    assert len(body["debug"]["retrieval_before_rerank"]) == 1
    assert len(body["debug"]["retrieval_after_rerank"]) == 1
    assert body["debug"]["rerank_scores"] == [0.7]
    assert body["debug"]["final_answer"] == "api fake agentic rag answer"
    assert body["debug"]["llm_provider"] == "mock"
    assert body["debug"]["llm_model"] == "mock-llm"
    assert body["debug"]["embedding_provider"] == "mock"
    assert body["debug"]["embedding_model_name"] == "mock-embedding-model"
    assert body["debug"]["latency_ms"] >= 0
