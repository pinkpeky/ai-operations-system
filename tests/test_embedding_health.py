"""Embedding health API 测试模块。"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import rag as rag_routes
from app.schemas.rag import EmbeddingHealthResponse


class FakeEmbeddingClient:
    """EmbeddingClient 替身。"""

    def __init__(self, settings=None) -> None:  # type: ignore[no-untyped-def]
        self.settings = settings

    async def health_check(self) -> EmbeddingHealthResponse:
        """返回固定健康检查结果。"""

        return EmbeddingHealthResponse(
            provider="local",
            model="bge-m3",
            reachable=True,
            dimension=1024,
            error=None,
        )


def test_embedding_health_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """GET /rag/embedding/health 应返回 Provider 状态和维度。"""

    monkeypatch.setattr(rag_routes, "EmbeddingClient", FakeEmbeddingClient)
    app = FastAPI()
    app.include_router(rag_routes.router, prefix="/api/v1")
    client = TestClient(app)

    response = client.get("/api/v1/rag/embedding/health")

    assert response.status_code == 200
    assert response.json() == {
        "provider": "local",
        "model": "bge-m3",
        "reachable": True,
        "dimension": 1024,
        "error": None,
    }
