"""RAG Search 内置工具。"""

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.api.routes.rag import build_retrieved_chunk_from_reranked, create_hybrid_search_pipeline
from app.reranker.reranker_client import RerankerClient
from app.tools.base import BaseTool, ToolExecutionContext


class RagSearchToolInput(BaseModel):
    """RAG Search 工具输入。"""

    query: str = Field(min_length=1, description="检索查询")
    collection_name: str | None = Field(default=None, min_length=1, max_length=128, description="可选 collection")
    search_mode: Literal["dense", "keyword", "hybrid"] | None = Field(default=None, description="检索模式")
    top_k: int | None = Field(default=None, ge=1, le=50, description="兼容旧接口的返回数量")
    dense_top_k: int | None = Field(default=None, ge=1, le=100, description="Dense 候选数")
    keyword_top_k: int | None = Field(default=None, ge=1, le=100, description="Keyword 候选数")
    final_top_k: int | None = Field(default=None, ge=1, le=50, description="最终返回数")
    source_id: str | None = Field(default=None, min_length=1, max_length=255, description="可选 source_id 过滤")


class RagSearchToolOutput(BaseModel):
    """RAG Search 工具输出。"""

    collection_name: str
    query: str
    search_mode: str
    dense_results_count: int
    keyword_results_count: int
    merged_results_count: int
    items: list[dict[str, Any]]


class RagSearchTool(BaseTool):
    """调用当前 Hybrid Search + Reranker 的工具。"""

    name = "rag_search_tool"
    description = "Search workspace knowledge with Dense/Keyword/Hybrid retrieval and reranker."
    input_schema = RagSearchToolInput
    output_schema = RagSearchToolOutput
    permission_scopes = ["rag:read"]

    async def execute(self, tool_input: BaseModel, context: ToolExecutionContext) -> BaseModel:
        """执行 workspace 隔离的 RAG 检索。"""

        request = RagSearchToolInput.model_validate(tool_input.model_dump())
        settings = context.effective_settings
        session = context.require_session()
        search_mode = request.search_mode or settings.default_search_mode
        legacy_top_k = request.top_k
        dense_top_k = request.dense_top_k or legacy_top_k or settings.dense_top_k
        keyword_top_k = request.keyword_top_k or legacy_top_k or settings.keyword_top_k
        final_top_k = request.final_top_k or legacy_top_k or settings.final_top_k
        pipeline = create_hybrid_search_pipeline(
            settings=settings,
            session=session,
            collection_name=request.collection_name,
        )
        bundle = await pipeline.search(
            query=request.query,
            search_mode=search_mode,  # type: ignore[arg-type]
            dense_top_k=dense_top_k,
            keyword_top_k=keyword_top_k,
            workspace_id=context.require_workspace(),
            source_id=request.source_id,
        )
        reranker = RerankerClient(settings=settings)
        reranked = await reranker.rerank(query=request.query, chunks=bundle.merged_results, top_n=final_top_k)
        return RagSearchToolOutput(
            collection_name=pipeline.vector_store.collection_name,
            query=request.query,
            search_mode=search_mode,
            dense_results_count=len(bundle.dense_results),
            keyword_results_count=len(bundle.keyword_results),
            merged_results_count=len(bundle.merged_results),
            items=[build_retrieved_chunk_from_reranked(item).model_dump(mode="json") for item in reranked],
        )
