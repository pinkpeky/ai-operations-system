"""Agentic RAG API 数据模型模块。

该模块定义单一 Agentic RAG 编排器的请求、响应和 debug 信息结构。
"""

from pydantic import BaseModel, Field

from app.schemas.rag import RetrievedChunk


class AgenticRAGRequest(BaseModel):
    """Agentic RAG 查询请求。"""

    query: str = Field(min_length=1, description="用户问题")
    collection_name: str | None = Field(default=None, min_length=1, max_length=128, description="可选知识库 collection")
    top_k: int = Field(default=3, ge=1, le=20, description="检索返回 chunk 数量")
    debug: bool = Field(default=False, description="是否返回调试信息")


class AgenticRAGDebugInfo(BaseModel):
    """Agentic RAG 调试信息。"""

    query: str
    workspace_id: str | None = None
    query_analysis: str
    retrieval_decision: str
    collection_name: str
    top_k: int
    retrieved_count: int
    prompt_preview: str
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    similarity_scores: list[float] = Field(default_factory=list)
    search_mode: str = "hybrid"
    dense_results_count: int = 0
    keyword_results_count: int = 0
    merged_results_count: int = 0
    final_results_count: int = 0
    dense_scores: list[float] = Field(default_factory=list)
    keyword_scores: list[float] = Field(default_factory=list)
    hybrid_scores: list[float] = Field(default_factory=list)
    reranker_provider: str | None = None
    reranker_model: str | None = None
    reranked_chunks: list[RetrievedChunk] = Field(default_factory=list)
    rerank_scores: list[float] = Field(default_factory=list)
    retrieval_before_rerank: list[RetrievedChunk] = Field(default_factory=list)
    retrieval_after_rerank: list[RetrievedChunk] = Field(default_factory=list)
    final_prompt: str
    final_answer: str
    llm_provider: str
    llm_model: str
    embedding_provider: str | None = None
    embedding_model_name: str | None = None
    latency_ms: int


class AgenticRAGResponse(BaseModel):
    """Agentic RAG 查询响应。"""

    answer: str
    used_retrieval: bool
    retrieved_chunks: list[RetrievedChunk]
    provider: str
    model: str
    debug: AgenticRAGDebugInfo | None = None
