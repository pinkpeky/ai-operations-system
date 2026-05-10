"""Agentic RAG 单一编排器模块。

该编排器只负责 query -> retrieval -> prompt assembly -> LLM 的基础流程，不引入多 Agent、Scheduler 或真实 LLM 依赖。
"""

import logging
from dataclasses import dataclass
from typing import Protocol

from app.agents.llm_client import LLMClient
from app.rag.retrieval import RetrievalPipeline
from app.rag.vector_store import VectorSearchResult
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

    async def search(self, query: str, top_k: int = 5) -> list[VectorSearchResult]:
        """执行 RAG 检索。"""


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
    ) -> None:
        self.llm_client = llm_client or LLMClient()
        self.retrieval_pipeline = retrieval_pipeline

    async def query(self, request: AgenticRAGRequest) -> AgenticRAGResponse:
        """执行 Agentic RAG 查询流程。"""

        try:
            analysis = self.analyze_query(request.query)
            retrieved_results: list[VectorSearchResult] = []
            if analysis.needs_retrieval:
                if self.retrieval_pipeline is None:
                    raise RuntimeError("Retrieval pipeline is required when retrieval is needed")
                retrieved_results = await self.retrieval_pipeline.search(
                    query=request.query,
                    top_k=request.top_k,
                )

            prompt = self.build_context_prompt(
                query=request.query,
                retrieved_results=retrieved_results,
                used_retrieval=analysis.needs_retrieval,
            )
            llm_response = await self.llm_client.generate(
                LLMRequest(
                    system_prompt="你是 AI Operations System 的 Agentic RAG 编排器，必须基于给定上下文回答。",
                    user_prompt=prompt,
                )
            )
            collection_name = self._get_collection_name(request)
            retrieved_chunks = [self._to_retrieved_chunk(result) for result in retrieved_results]
            debug_info = (
                AgenticRAGDebugInfo(
                    query=request.query,
                    query_analysis=analysis.summary,
                    retrieval_decision=analysis.decision_reason,
                    collection_name=collection_name,
                    top_k=request.top_k,
                    retrieved_count=len(retrieved_results),
                    prompt_preview=prompt[:1000],
                )
                if request.debug
                else None
            )
            logger.info(
                "Agentic RAG query completed",
                extra={
                    "used_retrieval": analysis.needs_retrieval,
                    "retrieved_count": len(retrieved_results),
                    "provider": llm_response.provider,
                    "model": llm_response.model,
                },
            )
            return AgenticRAGResponse(
                answer=llm_response.content,
                used_retrieval=analysis.needs_retrieval,
                retrieved_chunks=retrieved_chunks,
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
        retrieved_results: list[VectorSearchResult],
        used_retrieval: bool,
    ) -> str:
        """构建带检索上下文的 LLM Prompt。"""

        if not used_retrieval:
            return f"用户问题：\n{query}\n\n请直接简洁回答。"

        context_blocks = []
        for index, result in enumerate(retrieved_results, start=1):
            context_blocks.append(
                "\n".join(
                    [
                        f"[Chunk {index}]",
                        f"similarity_score: {result.similarity_score}",
                        f"raw_score: {result.raw_score}",
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
            metadata=result.metadata,
            chunk_index=result.chunk_index,
        )

    def _get_collection_name(self, request: AgenticRAGRequest) -> str:
        """从 retrieval pipeline 或请求中获取 collection 名称。"""

        vector_store = getattr(self.retrieval_pipeline, "vector_store", None)
        collection_name = getattr(vector_store, "collection_name", None)
        return str(collection_name or request.collection_name or "unknown")
