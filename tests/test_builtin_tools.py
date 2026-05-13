"""内置工具测试。"""

from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.enums import DocumentIngestStatus, DocumentStatus, TaskStatus
from app.models.task import Task
from app.rag.hybrid_search import HybridSearchBundle
from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.base import RerankedChunk
from app.tools.base import ToolExecutionContext
from app.tools.builtin.create_task_tool import CreateTaskTool
from app.tools.builtin.current_runtime_tool import CurrentRuntimeTool
from app.tools.builtin.file_search_tool import FileSearchTool
from app.tools.builtin.get_task_status_tool import GetTaskStatusTool
from app.tools.builtin.rag_search_tool import RagSearchTool


class FakeHybridSearchPipeline:
    """RAG Search 工具测试用 Hybrid Pipeline。"""

    def __init__(self) -> None:
        self.vector_store = SimpleNamespace(collection_name="tool_collection")

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
        """返回固定检索结果。"""

        result = VectorSearchResult(
            id="aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
            text=f"{workspace_id}:{query}",
            similarity_score=0.9,
            raw_score=0.9,
            metadata={"source_id": source_id or "source-tool"},
            chunk_index=0,
            dense_score=0.9,
            keyword_score=0.8,
            hybrid_score=0.88,
        )
        return HybridSearchBundle(
            search_mode=search_mode,  # type: ignore[arg-type]
            dense_results=[result],
            keyword_results=[result],
            merged_results=[result],
        )


class FakeRerankerClient:
    """RAG Search 工具测试用 Reranker。"""

    def __init__(self, settings=None) -> None:  # type: ignore[no-untyped-def]
        self.settings = settings

    async def rerank(
        self,
        *,
        query: str,
        chunks: list[VectorSearchResult],
        top_n: int | None = None,
    ) -> list[RerankedChunk]:
        """透传候选结果。"""

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


@pytest.mark.asyncio
async def test_current_runtime_tool_returns_provider_settings() -> None:
    """current_runtime_tool 应返回当前 provider/search 配置。"""

    output = await CurrentRuntimeTool().execute(
        CurrentRuntimeTool().validate_input({"include_document": False}),
        ToolExecutionContext(workspace_id="workspace-a"),
    )

    assert output.runtime["LLM_PROVIDER"] == "mock"
    assert output.runtime["DEFAULT_SEARCH_MODE"] == "hybrid"


@pytest.mark.asyncio
async def test_file_search_tool_filters_by_workspace(session: AsyncSession) -> None:
    """file_search_tool 只能返回当前 workspace 文档。"""

    session.add_all(
        [
            Document(
                workspace_id="workspace-a",
                user_id="user-a",
                source_id="source-a",
                source_name="Doc A",
                source_type="text",
                file_hash="hash-a",
                version=1,
                status=DocumentStatus.ACTIVE.value,
                collection_name="collection-a",
                document_metadata={"kind": "visible"},
                chunk_count=1,
                ingest_status=DocumentIngestStatus.COMPLETED.value,
            ),
            Document(
                workspace_id="workspace-b",
                user_id="user-b",
                source_id="source-b",
                source_name="Doc B",
                source_type="text",
                file_hash="hash-b",
                version=1,
                status=DocumentStatus.ACTIVE.value,
                collection_name="collection-a",
                document_metadata={"kind": "hidden"},
                chunk_count=1,
                ingest_status=DocumentIngestStatus.COMPLETED.value,
            ),
        ]
    )
    await session.commit()

    output = await FileSearchTool().execute(
        FileSearchTool().validate_input({"collection_name": "collection-a"}),
        ToolExecutionContext(workspace_id="workspace-a", session=session),
    )

    assert len(output.items) == 1
    assert output.items[0]["source_id"] == "source-a"


@pytest.mark.asyncio
async def test_create_and_get_task_tools(session: AsyncSession) -> None:
    """create_task_tool 和 get_task_status_tool 应能创建并查询任务。"""

    context = ToolExecutionContext(workspace_id="workspace-a", user_id="user-a", session=session)
    created = await CreateTaskTool().execute(
        CreateTaskTool().validate_input(
            {
                "title": "tool task",
                "task_type": "content_generation",
                "payload": {"topic": "AI"},
            }
        ),
        context,
    )

    status = await GetTaskStatusTool().execute(
        GetTaskStatusTool().validate_input({"task_id": created.task["id"]}),
        context,
    )

    assert created.task["workspace_id"] == "workspace-a"
    assert status.task["status"] == TaskStatus.PENDING.value


@pytest.mark.asyncio
async def test_rag_search_tool_uses_hybrid_pipeline(monkeypatch, session: AsyncSession) -> None:  # type: ignore[no-untyped-def]
    """rag_search_tool 应调用 Hybrid Search 并返回 rerank 后结果。"""

    from app.tools.builtin import rag_search_tool as rag_tool_module

    monkeypatch.setattr(
        rag_tool_module,
        "create_hybrid_search_pipeline",
        lambda settings, session, collection_name=None: FakeHybridSearchPipeline(),
    )
    monkeypatch.setattr(rag_tool_module, "RerankerClient", FakeRerankerClient)

    output = await RagSearchTool().execute(
        RagSearchTool().validate_input({"query": "hello", "final_top_k": 1}),
        ToolExecutionContext(workspace_id="workspace-a", session=session),
    )

    assert output.collection_name == "tool_collection"
    assert output.items[0]["text"] == "workspace-a:hello"
    assert output.items[0]["rerank_score"] == 0.7
