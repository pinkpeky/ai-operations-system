"""Agentic RAG API 测试模块。

验证 /api/v1/agentic-rag/query 的响应结构，不依赖真实 Qdrant 或真实 LLM。
"""

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import agentic_rag as agentic_rag_routes
from app.rag.vector_store import VectorSearchResult
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

    async def search(self, query: str, top_k: int = 5) -> list[VectorSearchResult]:
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


def create_test_client() -> TestClient:
    """创建只包含 Agentic RAG 路由的测试应用。"""

    app = FastAPI()
    app.include_router(agentic_rag_routes.router, prefix="/api/v1")
    return TestClient(app)


def test_agentic_rag_query_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Agentic RAG API 应返回答案、检索结果和 debug 信息。"""

    monkeypatch.setattr(agentic_rag_routes, "LLMClient", FakeLLMClient)
    monkeypatch.setattr(
        agentic_rag_routes,
        "create_retrieval_pipeline",
        lambda settings, collection_name=None: FakeRetrievalPipeline(),
    )
    client = create_test_client()

    response = client.post(
        "/api/v1/agentic-rag/query",
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
    assert body["debug"]["collection_name"] == "agentic_api_collection"
