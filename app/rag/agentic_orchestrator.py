"""Agentic RAG 单一编排器模块。

该编排器只负责 query -> retrieval -> prompt assembly -> LLM 的基础流程，不引入多 Agent、Scheduler 或真实 LLM 依赖。
"""

import logging
import time
from dataclasses import dataclass
from typing import Protocol

from app.agents.llm_client import LLMClient
from app.rag.hybrid_search import HybridSearchBundle, SearchMode
from app.rag.retrieval import RetrievalPipeline
from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.base import RerankedChunk
from app.reranker.reranker_client import RerankerClient
from app.schemas.agentic_rag import AgenticRAGDebugInfo, AgenticRAGRequest, AgenticRAGResponse
from app.schemas.llm import LLMRequest, LLMResponse
from app.schemas.rag import RetrievedChunk

logger = logging.getLogger(__name__)


class LLMClientProtocol(Protocol):
    """编排器依赖的 LLM Client 协议，便于单元测试替换。"""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """执行 LLM 生成。"""


class RetrievalPipelineProtocol(Protocol):
    """编排器依赖的 Retrieval Pipeline 协议，便于单元测试替换。"""

    vector_store: object

    async def search(
        self,
        query: str,
        top_k: int = 5,
        source_id: str | None = None,
        workspace_id: str | None = None,
        status: str = "active",
    ) -> list[VectorSearchResult]:
        """执行 RAG 检索。"""


class RerankerClientProtocol(Protocol):
    """编排器依赖的 Reranker Client 协议，便于单元测试替换。"""

    provider: object

    async def rerank(
        self,
        *,
        query: str,
        chunks: list[VectorSearchResult],
        top_n: int | None = None,
    ) -> list[RerankedChunk]:
        """执行候选 chunk 精排。"""

class HybridSearchPipelineProtocol(Protocol):
    """编排器依赖的 Hybrid Search 协议，便于单元测试替换。"""

    vector_store: object
    embedding_client: object

    async def search(
        self,
        *,
        query: str,
        search_mode: SearchMode,
        dense_top_k: int,
        keyword_top_k: int,
        workspace_id: str,
        source_id: str | None = None,
        status: str = "active",
    ) -> HybridSearchBundle:
        """执行 Dense / Keyword / Hybrid 检索。"""


@dataclass(frozen=True, slots=True)
class QueryAnalysis:
    """用户问题分析结果。"""

    summary: str
    needs_retrieval: bool
    decision_reason: str


class AgenticRAGOrchestrator:
    """Agentic RAG 单一编排器。"""

    def __init__(
        self,
        llm_client: LLMClientProtocol | None = None,
        retrieval_pipeline: RetrievalPipelineProtocol | None = None,
        hybrid_search_pipeline: HybridSearchPipelineProtocol | None = None,
        reranker_client: RerankerClientProtocol | None = None,
        retrieval_top_k: int = 20,
        keyword_top_k: int = 20,
        search_mode: SearchMode = "hybrid",
        rerank_top_n: int | None = None,
    ) -> None:
        self.llm_client = llm_client or LLMClient()
        self.retrieval_pipeline = retrieval_pipeline
        self.hybrid_search_pipeline = hybrid_search_pipeline
        self.reranker_client = reranker_client or RerankerClient()
        self.retrieval_top_k = retrieval_top_k
        self.keyword_top_k = keyword_top_k
        self.search_mode: SearchMode = search_mode
        settings = getattr(self.reranker_client, "settings", None)
        configured_top_n = getattr(settings, "rerank_top_n", 5)
        self.rerank_top_n = rerank_top_n or int(configured_top_n)

    async def query(self, request: AgenticRAGRequest, workspace_id: str | None = None) -> AgenticRAGResponse:
        """执行 Agentic RAG 查询流程。"""

        try:
            started_at = time.perf_counter()
            analysis = self.analyze_query(request.query)
            retrieved_results: list[VectorSearchResult] = []
            dense_results: list[VectorSearchResult] = []
            keyword_results: list[VectorSearchResult] = []
            merged_results: list[VectorSearchResult] = []
            reranked_results: list[RerankedChunk] = []
            if analysis.needs_retrieval:
                if self.hybrid_search_pipeline is not None:
                    bundle = await self.hybrid_search_pipeline.search(
                        query=request.query,
                        search_mode=self.search_mode,
                        dense_top_k=self.retrieval_top_k,
                        keyword_top_k=self.keyword_top_k,
                        workspace_id=workspace_id or "",
                    )
                    dense_results = bundle.dense_results
                    keyword_results = bundle.keyword_results
                    merged_results = bundle.merged_results
                    retrieved_results = merged_results
                elif self.retrieval_pipeline is not None:
                    # 兼容任务执行器等暂未注入 DB session 的调用方，保留 dense-only 路径。
                    dense_results = await self.retrieval_pipeline.search(
                        query=request.query,
                        top_k=self.retrieval_top_k,
                        workspace_id=workspace_id,
                    )
                    merged_results = dense_results
                    retrieved_results = merged_results
                else:
                    raise RuntimeError("Retrieval pipeline is required when retrieval is needed")
                reranked_results = await self.reranker_client.rerank(
                    query=request.query,
                    chunks=merged_results,
                    top_n=self.rerank_top_n,
                )

            retrieval_before_rerank = [self._to_retrieved_chunk(result) for result in merged_results]
            reranked_chunks = [self._to_retrieved_chunk_from_reranked(result) for result in reranked_results]
            context_chunks = reranked_chunks if analysis.needs_retrieval else []
            prompt = self.build_context_prompt(
                query=request.query,
                context_chunks=context_chunks,
                used_retrieval=analysis.needs_retrieval,
            )
            llm_response = await self.llm_client.generate(
                LLMRequest(
                    system_prompt="你是 AI Operations System 的 Agentic RAG 编排器，必须基于给定上下文回答。",
                    user_prompt=prompt,
                )
            )
            collection_name = self._get_collection_name(request)
            latency_ms = int((time.perf_counter() - started_at) * 1000)
            debug_info = (
                AgenticRAGDebugInfo(
                    query=request.query,
                    workspace_id=workspace_id,
                    query_analysis=analysis.summary,
                    retrieval_decision=analysis.decision_reason,
                    collection_name=collection_name,
                    top_k=request.top_k,
                    retrieved_count=len(retrieved_results),
                    prompt_preview=prompt[:1000],
                    retrieved_chunks=context_chunks,
                    similarity_scores=[chunk.similarity_score for chunk in context_chunks],
                    search_mode=self.search_mode if self.hybrid_search_pipeline is not None else "dense",
                    dense_results_count=len(dense_results),
                    keyword_results_count=len(keyword_results),
                    merged_results_count=len(merged_results),
                    final_results_count=len(context_chunks),
                    dense_scores=[result.dense_score or result.similarity_score for result in dense_results],
                    keyword_scores=[result.keyword_score or result.similarity_score for result in keyword_results],
                    hybrid_scores=[result.hybrid_score or result.similarity_score for result in merged_results],
                    reranker_provider=self._get_reranker_provider_name(),
                    reranker_model=self._get_reranker_model_name(),
                    reranked_chunks=reranked_chunks,
                    rerank_scores=[chunk.rerank_score or 0.0 for chunk in reranked_chunks],
                    retrieval_before_rerank=retrieval_before_rerank,
                    retrieval_after_rerank=reranked_chunks,
                    final_prompt=prompt,
                    final_answer=llm_response.content,
                    llm_provider=llm_response.provider,
                    llm_model=llm_response.model,
                    embedding_provider=self._get_embedding_provider_name(),
                    embedding_model_name=self._get_embedding_model_name(),
                    latency_ms=latency_ms,
                )
                if request.debug
                else None
            )
            logger.info(
                "Agentic RAG query completed",
                extra={
                    "used_retrieval": analysis.needs_retrieval,
                    "retrieved_count": len(retrieved_results),
                    "dense_count": len(dense_results),
                    "keyword_count": len(keyword_results),
                    "merged_count": len(merged_results),
                    "reranked_count": len(reranked_results),
                    "provider": llm_response.provider,
                    "model": llm_response.model,
                },
            )
            return AgenticRAGResponse(
                answer=llm_response.content,
                used_retrieval=analysis.needs_retrieval,
                retrieved_chunks=context_chunks,
                provider=llm_response.provider,
                model=llm_response.model,
                debug=debug_info,
            )
        except ValueError:
            logger.exception("Agentic RAG request validation failed")
            raise
        except Exception as exc:
            logger.exception("Agentic RAG query failed")
            raise RuntimeError(str(exc) or "Agentic RAG query failed") from exc

    def analyze_query(self, query: str) -> QueryAnalysis:
        """分析用户问题并判断是否需要检索。"""

        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("Query cannot be empty")

        lowered_query = normalized_query.lower()
        low_value_queries = {"hi", "hello", "hey", "ping", "thanks", "thank you", "你好", "谢谢"}
        if lowered_query in low_value_queries:
            return QueryAnalysis(
                summary="用户输入是简单寒暄或连通性测试。",
                needs_retrieval=False,
                decision_reason="query is greeting or ping, retrieval skipped",
            )

        return QueryAnalysis(
            summary="用户问题需要结合知识库上下文回答。",
            needs_retrieval=True,
            decision_reason="query is knowledge-seeking, retrieval enabled",
        )

    def build_context_prompt(
        self,
        query: str,
        context_chunks: list[RetrievedChunk],
        used_retrieval: bool,
    ) -> str:
        """构建带检索上下文的 LLM Prompt。"""

        if not used_retrieval:
            return f"用户问题：\n{query}\n\n请直接简洁回答。"

        context_blocks = []
        for index, result in enumerate(context_chunks, start=1):
            context_blocks.append(
                "\n".join(
                    [
                        f"[Chunk {index}]",
                        f"similarity_score: {result.similarity_score}",
                        f"raw_score: {result.raw_score}",
                        f"rerank_score: {result.rerank_score}",
                        f"metadata: {result.metadata}",
                        f"text: {result.text}",
                    ]
                )
            )
        context = "\n\n".join(context_blocks) if context_blocks else "未检索到相关上下文。"
        return (
            "请基于以下检索上下文回答用户问题。如果上下文不足，请说明信息不足。\n\n"
            f"用户问题：\n{query}\n\n"
            f"检索上下文：\n{context}"
        )

    def _to_retrieved_chunk(self, result: VectorSearchResult) -> RetrievedChunk:
        """将内部检索结果转换为响应 chunk。"""

        return RetrievedChunk(
            id=result.id,
            text=result.text,
            similarity_score=result.similarity_score,
            raw_score=result.raw_score,
            dense_score=result.dense_score,
            keyword_score=result.keyword_score,
            hybrid_score=result.hybrid_score,
            metadata=result.metadata,
            chunk_index=result.chunk_index,
        )

    def _to_retrieved_chunk_from_reranked(self, result: RerankedChunk) -> RetrievedChunk:
        """将 rerank 结果转换为响应 chunk，并保留原始相似度。"""

        return RetrievedChunk(
            id=result.id,
            text=result.text,
            similarity_score=result.similarity_score,
            raw_score=result.raw_score,
            rerank_score=result.rerank_score,
            original_similarity_score=result.similarity_score,
            dense_score=result.dense_score,
            keyword_score=result.keyword_score,
            hybrid_score=result.hybrid_score,
            metadata=result.metadata,
            chunk_index=result.chunk_index,
        )

    def _get_collection_name(self, request: AgenticRAGRequest) -> str:
        """从 retrieval pipeline 或请求中获取 collection 名称。"""

        pipeline = self.hybrid_search_pipeline or self.retrieval_pipeline
        vector_store = getattr(pipeline, "vector_store", None)
        collection_name = getattr(vector_store, "collection_name", None)
        return str(collection_name or request.collection_name or "unknown")

    def _get_embedding_provider_name(self) -> str | None:
        """从 retrieval pipeline 中读取 embedding provider 名称。"""

        pipeline = self.hybrid_search_pipeline or self.retrieval_pipeline
        embedding_client = getattr(pipeline, "embedding_client", None)
        provider = getattr(embedding_client, "provider", None)
        provider_name = getattr(provider, "provider_name", None)
        return str(provider_name) if provider_name is not None else None

    def _get_embedding_model_name(self) -> str | None:
        """从 retrieval pipeline 中读取 embedding 模型名称。"""

        pipeline = self.hybrid_search_pipeline or self.retrieval_pipeline
        embedding_client = getattr(pipeline, "embedding_client", None)
        provider = getattr(embedding_client, "provider", None)
        model = getattr(provider, "model", None)
        return str(model) if model is not None else None

    def _get_reranker_provider_name(self) -> str | None:
        """从 reranker client 中读取 provider 名称。"""

        provider = getattr(self.reranker_client, "provider", None)
        provider_name = getattr(provider, "provider_name", None)
        return str(provider_name) if provider_name is not None else None

    def _get_reranker_model_name(self) -> str | None:
        """从 reranker client 中读取模型名称。"""

        provider = getattr(self.reranker_client, "provider", None)
        model = getattr(provider, "model", None)
        return str(model) if model is not None else None
