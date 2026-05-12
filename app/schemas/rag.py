"""RAG API 数据模型模块。

定义文档写入、Dense/Keyword/Hybrid 检索、collection 健康检查和 debug 接口的数据结构。
"""

from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator

SearchMode = Literal["dense", "keyword", "hybrid"]


class IngestRequest(BaseModel):
    """RAG 文档写入请求。"""

    text: str = Field(min_length=1, description="待写入知识库的文本")
    metadata: dict[str, Any] = Field(default_factory=dict, description="文档元数据")
    source_id: str | None = Field(default=None, description="外部来源 ID，不传则自动生成")
    source_name: str | None = Field(default=None, max_length=255, description="来源名称")
    source_type: str = Field(default="text", min_length=1, max_length=64, description="来源类型")
    workspace_id: str | None = Field(default=None, max_length=128, description="预留工作区 ID")
    user_id: str | None = Field(default=None, max_length=128, description="预留用户 ID")
    chunk_size: int = Field(default=500, ge=1, le=10000, description="字符切分长度")
    chunk_overlap: int = Field(default=50, ge=0, le=9999, description="相邻 chunk 重叠字符数")
    collection_name: str | None = Field(default=None, min_length=1, max_length=128, description="可选 collection 名称")

    @model_validator(mode="after")
    def validate_chunk_options(self) -> Self:
        """校验 chunk overlap 必须小于 chunk size。"""

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return self


class IngestResponse(BaseModel):
    """RAG 文档写入响应。"""

    collection_name: str
    source_id: str
    document_id: str | None = None
    version: int | None = None
    chunk_count: int
    chunk_ids: list[str]


class SearchRequest(BaseModel):
    """RAG 检索请求。"""

    query: str = Field(min_length=1, description="检索查询文本")
    top_k: int = Field(default=5, ge=1, le=50, description="兼容旧接口的返回数量")
    search_mode: SearchMode | None = Field(default=None, description="检索模式：dense / keyword / hybrid")
    dense_top_k: int | None = Field(default=None, ge=1, le=100, description="Dense 检索候选数量")
    keyword_top_k: int | None = Field(default=None, ge=1, le=100, description="Keyword 检索候选数量")
    final_top_k: int | None = Field(default=None, ge=1, le=50, description="最终返回数量")
    collection_name: str | None = Field(default=None, min_length=1, max_length=128, description="可选 collection 名称")
    source_id: str | None = Field(default=None, min_length=1, max_length=255, description="可选来源 ID 过滤")
    workspace_id: str | None = Field(default=None, max_length=128, description="可选工作区 ID 过滤")


class RetrievedChunk(BaseModel):
    """检索命中的 chunk。"""

    id: str
    text: str
    similarity_score: float = Field(ge=0, le=1, description="归一化相似度分数")
    raw_score: float = Field(description="检索层返回的原始分数")
    rerank_score: float | None = Field(default=None, ge=0, le=1, description="Reranker 精排分数")
    original_similarity_score: float | None = Field(default=None, ge=0, le=1, description="精排前原始相似度分数")
    dense_score: float | None = Field(default=None, ge=0, le=1, description="Dense 检索分数")
    keyword_score: float | None = Field(default=None, ge=0, le=1, description="Keyword 检索分数")
    hybrid_score: float | None = Field(default=None, ge=0, le=1, description="Hybrid 合并分数")
    metadata: dict[str, Any] = Field(default_factory=dict)
    chunk_index: int | None = None


class SearchResponse(BaseModel):
    """RAG 检索响应。"""

    collection_name: str
    query: str
    search_mode: SearchMode = "hybrid"
    items: list[RetrievedChunk]


class CollectionHealthResponse(BaseModel):
    """Collection 健康检查响应。"""

    collection_name: str
    exists: bool
    status: str
    points_count: int | None
    vectors_count: int | None
    embedding_dimension: int | None


class CollectionListResponse(BaseModel):
    """Collection 列表响应。"""

    collections: list[CollectionHealthResponse]


class DebugScore(BaseModel):
    """RAG Debug 分数信息。"""

    id: str
    similarity_score: float
    raw_score: float
    dense_score: float | None = None
    keyword_score: float | None = None
    hybrid_score: float | None = None


class RAGDebugResponse(BaseModel):
    """RAG Debug 响应。"""

    query: str
    query_embedding_dimension: int
    collection_name: str
    retrieved_chunks: list[RetrievedChunk]
    scores: list[DebugScore]


class EmbeddingHealthResponse(BaseModel):
    """Embedding Provider 健康检查响应。"""

    provider: str
    model: str
    reachable: bool
    dimension: int | None = None
    error: str | None = None
