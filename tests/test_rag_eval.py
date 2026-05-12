"""RAG Eval Service 和 API 测试模块。"""

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import rag_eval as rag_eval_routes
from app.core.config import Settings
from app.core.errors import AppError, app_error_handler
from app.db.postgres import get_session
from app.middleware.workspace_middleware import WorkspaceContextMiddleware
from app.repositories.collection_repository import CollectionRepository
from app.schemas.rag_eval import RAGEvalItemCreateRequest, RAGEvalRunCreateRequest, RAGEvalScoreUpdateRequest
from app.services.rag_eval_service import RAGEvalService


@pytest.mark.asyncio
async def test_rag_eval_service_records_config_and_items(session) -> None:  # type: ignore[no-untyped-def]
    """Eval run 应记录 collection/embedding/LLM 配置，item 应保存 trace 数据和人工评分。"""

    await CollectionRepository(session).ensure_collection_metadata(
        collection_name="eval_collection",
        workspace_id="workspace-a",
        embedding_provider="local",
        embedding_model_name="bge-m3",
        embedding_dimension=1024,
    )
    service = RAGEvalService(
        session=session,
        settings=Settings(
            EMBEDDING_PROVIDER="local",
            LOCAL_EMBEDDING_MODEL="bge-m3",
            LLM_PROVIDER="local",
            LOCAL_LLM_MODEL="mistral",
        ),
    )

    run = await service.create_run(
        workspace_id="workspace-a",
        request=RAGEvalRunCreateRequest(
            name="phase8 eval",
            description="trace validation",
            collection_name="eval_collection",
        ),
    )
    item = await service.create_item(
        workspace_id="workspace-a",
        run_id=run.id,
        request=RAGEvalItemCreateRequest(
            query="RAG trace 包含哪些字段？",
            expected_answer="包含 prompt、答案、分数和耗时。",
            retrieved_chunks=[{"text": "trace chunk", "metadata": {"source_id": "trace"}}],
            final_prompt="final prompt",
            final_answer="final answer",
            similarity_scores=[0.91],
            eval_mode="retrieval_rerank",
            reranker_provider="mock",
            reranker_model="mock-reranker",
            reranked_chunks=[{"text": "trace chunk", "rerank_score": 0.88}],
            rerank_scores=[0.88],
            retrieval_before_rerank=[{"text": "trace chunk", "similarity_score": 0.91}],
            retrieval_after_rerank=[{"text": "trace chunk", "rerank_score": 0.88}],
            latency_ms=123,
            notes="initial",
        ),
    )
    updated = await service.update_score(
        workspace_id="workspace-a",
        item_id=item.id,
        request=RAGEvalScoreUpdateRequest(manual_score=0.8, notes="good enough"),
    )

    assert run.workspace_id == "workspace-a"
    assert run.embedding_provider == "local"
    assert run.embedding_model_name == "bge-m3"
    assert run.llm_provider == "local"
    assert run.llm_model == "mistral"
    assert run.reranker_provider == "mock"
    assert run.reranker_model == "mock-reranker"
    assert item.retrieved_chunks[0]["text"] == "trace chunk"
    assert item.similarity_scores == [0.91]
    assert item.eval_mode == "retrieval_rerank"
    assert item.reranker_provider == "mock"
    assert item.rerank_scores == [0.88]
    assert item.retrieval_before_rerank[0]["similarity_score"] == 0.91
    assert item.retrieval_after_rerank[0]["rerank_score"] == 0.88
    assert updated.manual_score == 0.8
    assert updated.notes == "good enough"


@pytest.mark.asyncio
async def test_rag_eval_service_keeps_workspace_isolation(session) -> None:  # type: ignore[no-untyped-def]
    """不同 workspace 不能读取或更新彼此的 eval run/item。"""

    service = RAGEvalService(session=session, settings=Settings())
    run = await service.create_run(
        workspace_id="workspace-a",
        request=RAGEvalRunCreateRequest(
            name="workspace scoped eval",
            description=None,
            collection_name="isolated_collection",
        ),
    )
    item = await service.create_item(
        workspace_id="workspace-a",
        run_id=run.id,
        request=RAGEvalItemCreateRequest(query="isolated query"),
    )

    assert await service.list_runs(workspace_id="workspace-b") == []
    with pytest.raises(AppError):
        await service.create_item(
            workspace_id="workspace-b",
            run_id=run.id,
            request=RAGEvalItemCreateRequest(query="cross workspace query"),
        )
    with pytest.raises(AppError):
        await service.update_score(
            workspace_id="workspace-b",
            item_id=item.id,
            request=RAGEvalScoreUpdateRequest(manual_score=0.5),
        )


class FakeRAGEvalService:
    """RAG Eval API 测试替身，避免依赖真实数据库。"""

    def __init__(self) -> None:
        self.run_id = uuid4()
        self.item_id = uuid4()
        self.created_at = datetime.now(UTC)

    async def create_run(self, *, workspace_id: str, request: RAGEvalRunCreateRequest) -> SimpleNamespace:
        """返回固定 eval run。"""

        return self._run(workspace_id=workspace_id, request=request)

    async def list_runs(self, *, workspace_id: str, limit: int = 100) -> list[SimpleNamespace]:
        """返回当前 workspace 的固定 eval run。"""

        return [
            self._run(
                workspace_id=workspace_id,
                request=RAGEvalRunCreateRequest(name="listed", collection_name="eval_collection"),
            )
        ][:limit]

    async def create_item(
        self,
        *,
        workspace_id: str,
        run_id: UUID,
        request: RAGEvalItemCreateRequest,
    ) -> SimpleNamespace:
        """返回固定 eval item。"""

        return self._item(run_id=run_id, request=request, manual_score=None)

    async def list_items(self, *, workspace_id: str, run_id: UUID) -> list[SimpleNamespace]:
        """返回固定 eval item 列表。"""

        return [self._item(run_id=run_id, request=RAGEvalItemCreateRequest(query="listed query"), manual_score=None)]

    async def update_score(
        self,
        *,
        workspace_id: str,
        item_id: UUID,
        request: RAGEvalScoreUpdateRequest,
    ) -> SimpleNamespace:
        """返回更新后的固定 eval item。"""

        return self._item(
            run_id=self.run_id,
            request=RAGEvalItemCreateRequest(query="scored query", notes=request.notes),
            manual_score=request.manual_score,
        )

    def _run(self, *, workspace_id: str, request: RAGEvalRunCreateRequest) -> SimpleNamespace:
        """构造 run 响应模型需要的属性。"""

        return SimpleNamespace(
            id=self.run_id,
            workspace_id=workspace_id,
            name=request.name,
            description=request.description,
            collection_name=request.collection_name,
            embedding_provider="local",
            embedding_model_name="bge-m3",
            llm_provider="local",
            llm_model="mistral",
            reranker_provider="mock",
            reranker_model="mock-reranker",
            created_at=self.created_at,
        )

    def _item(
        self,
        *,
        run_id: UUID,
        request: RAGEvalItemCreateRequest,
        manual_score: float | None,
    ) -> SimpleNamespace:
        """构造 item 响应模型需要的属性。"""

        return SimpleNamespace(
            id=self.item_id,
            run_id=run_id,
            query=request.query,
            expected_answer=request.expected_answer,
            retrieved_chunks=request.retrieved_chunks,
            final_prompt=request.final_prompt,
            final_answer=request.final_answer,
            similarity_scores=request.similarity_scores,
            eval_mode=request.eval_mode,
            reranker_provider=request.reranker_provider,
            reranker_model=request.reranker_model,
            reranked_chunks=request.reranked_chunks,
            rerank_scores=request.rerank_scores,
            retrieval_before_rerank=request.retrieval_before_rerank,
            retrieval_after_rerank=request.retrieval_after_rerank,
            latency_ms=request.latency_ms,
            manual_score=manual_score,
            notes=request.notes,
            created_at=self.created_at,
        )


def create_test_client() -> TestClient:
    """创建只包含 RAG Eval 路由的测试应用。"""

    app = FastAPI()
    app.add_middleware(WorkspaceContextMiddleware)
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(rag_eval_routes.router, prefix="/api/v1")

    async def fake_get_session():  # type: ignore[no-untyped-def]
        yield object()

    app.dependency_overrides[get_session] = fake_get_session
    return TestClient(app)


def test_rag_eval_api_flow(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Eval API 应支持 run 创建、查询、item 创建、查询和人工评分更新。"""

    fake_service = FakeRAGEvalService()
    monkeypatch.setattr(rag_eval_routes, "create_rag_eval_service", lambda session: fake_service)
    client = create_test_client()
    headers = {"X-Workspace-Id": "workspace-api"}

    run_response = client.post(
        "/api/v1/rag/eval/runs",
        headers=headers,
        json={
            "name": "swagger eval",
            "description": "api flow",
            "collection_name": "eval_collection",
        },
    )
    assert run_response.status_code == 201
    run_body = run_response.json()
    assert run_body["workspace_id"] == "workspace-api"
    assert run_body["embedding_model_name"] == "bge-m3"
    assert run_body["reranker_provider"] == "mock"

    list_runs_response = client.get("/api/v1/rag/eval/runs", headers=headers)
    assert list_runs_response.status_code == 200
    assert list_runs_response.json()["items"][0]["workspace_id"] == "workspace-api"

    item_response = client.post(
        f"/api/v1/rag/eval/runs/{run_body['id']}/items",
        headers=headers,
        json={
            "query": "trace query",
            "expected_answer": "trace answer",
            "retrieved_chunks": [{"text": "chunk"}],
            "final_prompt": "prompt",
            "final_answer": "answer",
            "similarity_scores": [0.9],
            "eval_mode": "retrieval_rerank",
            "reranker_provider": "mock",
            "reranker_model": "mock-reranker",
            "reranked_chunks": [{"text": "chunk", "rerank_score": 0.82}],
            "rerank_scores": [0.82],
            "retrieval_before_rerank": [{"text": "chunk", "similarity_score": 0.9}],
            "retrieval_after_rerank": [{"text": "chunk", "rerank_score": 0.82}],
            "latency_ms": 100,
            "notes": "from trace",
        },
    )
    assert item_response.status_code == 201
    item_body = item_response.json()
    assert item_body["similarity_scores"] == [0.9]
    assert item_body["rerank_scores"] == [0.82]

    list_items_response = client.get(f"/api/v1/rag/eval/runs/{run_body['id']}/items", headers=headers)
    assert list_items_response.status_code == 200
    assert list_items_response.json()["items"][0]["query"] == "listed query"

    score_response = client.patch(
        f"/api/v1/rag/eval/items/{item_body['id']}/score",
        headers=headers,
        json={"manual_score": 0.75, "notes": "verified"},
    )
    assert score_response.status_code == 200
    assert score_response.json()["manual_score"] == 0.75
    assert score_response.json()["notes"] == "verified"
