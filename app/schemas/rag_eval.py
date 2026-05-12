"""RAG Eval API 数据模型模块。"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.rag_eval import RAGEvalItem, RAGEvalRun


class RAGEvalRunCreateRequest(BaseModel):
    """创建 RAG Eval Run 请求。"""

    name: str = Field(min_length=1, max_length=255, description="评估名称")
    description: str | None = Field(default=None, description="评估描述")
    collection_name: str = Field(min_length=1, max_length=128, description="评估 collection")


class RAGEvalRunResponse(BaseModel):
    """RAG Eval Run 响应。"""

    id: UUID
    workspace_id: str
    name: str
    description: str | None
    collection_name: str
    embedding_provider: str
    embedding_model_name: str
    llm_provider: str
    llm_model: str
    reranker_provider: str | None = None
    reranker_model: str | None = None
    created_at: datetime

    @classmethod
    def from_model(cls, run: RAGEvalRun) -> "RAGEvalRunResponse":
        """从 ORM 对象构建响应。"""

        return cls(
            id=run.id,
            workspace_id=run.workspace_id,
            name=run.name,
            description=run.description,
            collection_name=run.collection_name,
            embedding_provider=run.embedding_provider,
            embedding_model_name=run.embedding_model_name,
            llm_provider=run.llm_provider,
            llm_model=run.llm_model,
            reranker_provider=run.reranker_provider,
            reranker_model=run.reranker_model,
            created_at=run.created_at,
        )


class RAGEvalRunListResponse(BaseModel):
    """RAG Eval Run 列表响应。"""

    items: list[RAGEvalRunResponse]


class RAGEvalItemCreateRequest(BaseModel):
    """创建 RAG Eval Item 请求。"""

    query: str = Field(min_length=1, description="查询问题")
    expected_answer: str | None = Field(default=None, description="期望答案")
    retrieved_chunks: list[dict[str, Any]] = Field(default_factory=list, description="最终使用的 chunks")
    final_prompt: str | None = Field(default=None, description="最终 Prompt")
    final_answer: str | None = Field(default=None, description="最终答案")
    similarity_scores: list[float] = Field(default_factory=list, description="最终上下文相似度分数")
    eval_mode: str = Field(default="retrieval_rerank", description="retrieval_only 或 retrieval_rerank")
    reranker_provider: str | None = Field(default=None, description="Reranker Provider")
    reranker_model: str | None = Field(default=None, description="Reranker 模型")
    reranked_chunks: list[dict[str, Any]] = Field(default_factory=list, description="Reranker 精排后的 chunks")
    rerank_scores: list[float] = Field(default_factory=list, description="Reranker 精排分数")
    retrieval_before_rerank: list[dict[str, Any]] = Field(default_factory=list, description="Rerank 前候选 chunks")
    retrieval_after_rerank: list[dict[str, Any]] = Field(default_factory=list, description="Rerank 后上下文 chunks")
    latency_ms: int | None = Field(default=None, ge=0, description="链路耗时毫秒")
    notes: str | None = Field(default=None, description="备注")


class RAGEvalItemResponse(BaseModel):
    """RAG Eval Item 响应。"""

    id: UUID
    run_id: UUID
    query: str
    expected_answer: str | None
    retrieved_chunks: list[dict[str, Any]]
    final_prompt: str | None
    final_answer: str | None
    similarity_scores: list[float]
    eval_mode: str
    reranker_provider: str | None
    reranker_model: str | None
    reranked_chunks: list[dict[str, Any]]
    rerank_scores: list[float]
    retrieval_before_rerank: list[dict[str, Any]]
    retrieval_after_rerank: list[dict[str, Any]]
    latency_ms: int | None
    manual_score: float | None
    notes: str | None
    created_at: datetime

    @classmethod
    def from_model(cls, item: RAGEvalItem) -> "RAGEvalItemResponse":
        """从 ORM 对象构建响应。"""

        return cls(
            id=item.id,
            run_id=item.run_id,
            query=item.query,
            expected_answer=item.expected_answer,
            retrieved_chunks=item.retrieved_chunks,
            final_prompt=item.final_prompt,
            final_answer=item.final_answer,
            similarity_scores=item.similarity_scores,
            eval_mode=item.eval_mode,
            reranker_provider=item.reranker_provider,
            reranker_model=item.reranker_model,
            reranked_chunks=item.reranked_chunks,
            rerank_scores=item.rerank_scores,
            retrieval_before_rerank=item.retrieval_before_rerank,
            retrieval_after_rerank=item.retrieval_after_rerank,
            latency_ms=item.latency_ms,
            manual_score=item.manual_score,
            notes=item.notes,
            created_at=item.created_at,
        )


class RAGEvalItemListResponse(BaseModel):
    """RAG Eval Item 列表响应。"""

    items: list[RAGEvalItemResponse]


class RAGEvalScoreUpdateRequest(BaseModel):
    """人工评分更新请求。"""

    manual_score: float = Field(ge=0, le=1, description="人工评分：0-1")
    notes: str | None = Field(default=None, description="评分备注")
